import os
import json
import requests

from github import Github, GithubException

USERNAME = 'akmadian'
CREATEBRANCH = True
AUTOMERGEPR = False

class ConfigParser:
    def __init__(self, path):
        self.path = path
        self.config = self.loadConfig()

    def loadConfig(self):
        with open(self.path) as f:
            contents = json.load(f)
            return contents

class Repository:
    def __init__(self, repoObject):
        self.repoObject = repoObject
        self.hasDotGithub = self.hasDotGithub()
        self.repoConfig = self.hasRepoConfig()
        self.EXEMPT = self.isExempt()
        self.CHANGESMADE = True

    def hasDotGithub(self):
        try:
            self.repoObject.get_contents('.github')
        except GithubException:
            print('Could not find .github')
            return False

        print('.github exists')
        return True

    def hasRepoConfig(self):
        try:
            self.repoObject.get_contents('.github/standardize.config.json')
            contents = requests.get('https://raw.githubusercontent.com/akmadian/TESTREPO/master/.github/standardize.config.json')
            return json.loads(contents.text)
        except GithubException:
            return None
            print('Repo does not have custom config file')

    def isExempt(self):
        try:
            if self.repoConfig is not None:
                return self.repoConfig.EXEMPT
        except AttributeError:
            return False

    def existingLabels(self, labels):
        existingLabels = {}
        for label in labels:
            existingLabels[label.name] = {
                'color': label.color,
                'description': label.description,
                'label_object': label
            }
        return existingLabels

    def editLabel(self, labelObject, name, color, description):
        labelObject.edit(name=name, color=color, description=description)

    def createLabel(self, name, color, description):
        self.repoObject.create_label(name=name, color=color, description=description)

    def fileExists(self, fileName):
        try:
            return self.repoObject.get_contents(fileName)
        except Exception: return False

        return True

    def createChangesPR(self, head, base):
        print('Creating PR with changes. head={}, base={}'.format(head, base))
        self.repoObject.create_pull(
            title="Repo Standardization Changes",
            body="TEST BODY",
            head=head,
            base=base
        )

class Standardize:
    def __init__(self, APItoken, configPath):
        self.APItoken = APItoken
        self.config = ConfigParser(configPath)
        self.repos = []
        self.CHANGESMADE = False # were changes made with commits?
        self.setGHInstance()
        self.printRepos()
        self.standardize()

    def setGHInstance(self):
        self.github = Github(self.APItoken)

    def printRepos(self):
        self.repos.append(Repository(self.github.get_repo('akmadian/TESTREPO')))

    def standardize(self):
        for repo in self.repos:
            if repo.repoObject.archived:
                print('Repo is archived, skipping...')
                continue
            if repo.EXEMPT:
                print('Repo marked as EXEMPT in config, skipping...')
                continue
            
            self.standardizeLabels(repo)
            self.standardizeFiles(repo)

            if (repo.CHANGESMADE):
                repo.createChangesPR(
                    head=self.config.config['PRHEAD'],
                    base=self.config.config['PRBASE']
                )

    def standardizeLabels(self, repo):
        labels = repo.repoObject.get_labels()
        existingLabels = repo.existingLabels(labels)
        for labelName in self.config.config['LABELS'].keys():
            requiredLabel = self.config.config['LABELS'][labelName]
            if labelName in existingLabels.keys():
                existingLabel = existingLabels[labelName]
                if (requiredLabel['color'] != existingLabel['color']) or \
                    (requiredLabel['description']
                        != existingLabel['description']):
                    repo.editLabel(
                        labelObject=existingLabel['label_object'],
                        name=labelName,
                        color=requiredLabel['color'],
                        description=requiredLabel['description']
                    )
            else:
                # If user has ignored current label in repo config
                if labelName in repo.repoConfig['IGNORE']['LABELS']: continue
                repo.createLabel(
                    name=labelName,
                    color=requiredLabel['color'],
                    description=requiredLabel['description']
                )

    def standardizeFiles(self, repo):
        print('Standardizing Files')
        for template in self.config.config['TEMPLATES']:
            if template['name'] not in repo.repoConfig['IGNORE']['TEMPLATES']:
                path = '{}{}'.format(
                        template['targetPath'] if template['targetPath'] != './' else '',
                        template['name']
                    )
                file = repo.fileExists(path)

                if not file:
                    print('Adding File "{}"'.format(template['name']))
                    repo.repoObject.create_file(
                        path=path,
                        message='Create {}'.format(template['name']),
                        content=open(template['localPath'], 'r').read()
                        #branch=self.config.config['PRHEAD']
                    )
                    repo.CHANGESMADE = True
                else:
                    print('Updating File "{}"'.format(template['name']))
                    repo.repoObject.update_file(
                        path=path,
                        message='Update {}'.format(template['name']),
                        content=open(template['localPath'], 'r').read(),
                        sha=file.sha
                    )

# ARG options
# Create PR with file changes y/n
#   Auto-merge? y/n
# org/ user
        
st = Standardize('77b1917c31f01762ca6f0ce6c8bbd6bbd0c51ced', 'config.example.json')
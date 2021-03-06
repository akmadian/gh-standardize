import os
import json
import requests
import argparse

from configparser import ConfigParser
from repository import Repository
from ghapi import GithubAPI
from utils import GITHUB_RAW_URL_TEMPLATE

from github import Github, GithubException

LOGIN = 'akmadian'
CREATEBRANCH = True
AUTOMERGEPR = False

class Standardize:
    def __init__(self, APItoken, configPath):
        self.APItoken = APItoken
        self.config = ConfigParser(configPath)
        self.repos = []
        self.CHANGESMADE = False # were changes made with commits?
        self.github = Github(self.APItoken)
        self.printRepos()
        self.standardize()

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
                    PRCONFIG=self.config.config['PR']
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
                    if (
                        requests.get(
                            GITHUB_RAW_URL_TEMPLATE(
                                LOGIN, 
                                repo.repoObject.name, 
                                self.config.config['PR']['PRHEAD'], 
                                template['name']
                            )
                        ).text == template['content']):
                        print('{} - Current and local version have same contents. Skipping...'.format(template['name']))
                        continue

                    print('Updating File "{}"'.format(template['name']))
                    repo.repoObject.update_file(
                        path=path,
                        message='Update {}'.format(template['name']),
                        content=template['content'],
                        sha=file.sha
                    )
        
    def standardizeBranchProtection(self, repo):
        print('Standardizing Branch Protection...')
        for branchName in self.config.config['PROTECTIONS']:
            if branchName in repo.repoConfig['IGNORE']['BRANCHPROTECTION'] or \
                repo.repoObject.name in self.config.config['EXEMPT']['BRANCHPROTECTION']: continue

            branch = repo.get_branch(branchName)
            


# ARG options
# Create PR with file changes y/n
#   Auto-merge? y/n
# org/ user
"""
parser = argparse.ArgumentParser(description='gh-standardize - A python tool for standardizing GitHub repos')
parser.add_argument('configpath', type=str, nargs=1,
                    help='The full or relative path to your gh-standardize config file')

args = parser.parse_args()"""

st = Standardize(open('apikey.txt', 'r').read().strip(), 'config.example.json')
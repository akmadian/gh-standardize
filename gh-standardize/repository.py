import requests
import json
from github import GithubException

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

    def createChangesPR(self, PRCONFIG):
        hasExistingChangesPR = self.hasExistingChangesPR(PRCONFIG)
        if hasExistingChangesPR:
            print('EXISTING CHANGES PR FOUND, CLOSING.')
            hasExistingChangesPR.edit(state='closed')

        PR = None
        try:
            print('Creating PR with changes. head={}, base={}'.format(PRCONFIG['PRHEAD'], PRCONFIG['PRBASE']))
            PR = self.repoObject.create_pull(
                title="[gh-standardize] Repo Standardization Changes",
                body="TEST BODY",
                head=PRCONFIG['PRHEAD'],
                base=PRCONFIG['PRBASE']
            )
        except GithubException as e:
            print("An exception occurred when creating PR. API Message: {}".format(e.data['errors'][0]['message']))

        self.assignChangesPR(PR, PRCONFIG)
        self.requestReviewOnChangesPR(PR, PRCONFIG)
        self.addLabelstoChangesPR(PR, PRCONFIG)

    def requestReviewOnChangesPR(self, PR, PRCONFIG):
        print("Requesting reviews on changes PR...")
        # Create Review Requests
        USERS = PRCONFIG['REQUESTREVIEWFROM']['USERS']
        TEAMS = PRCONFIG['REQUESTREVIEWFROM']['USERS']
        if USERS or TEAMS: # If at least one review is requested
            try:
                PR.create_review_request(
                    reviewers=USERS if USERS else None,
                    team_reviewers=TEAMS if TEAMS else None
                )
            except Exception as e:
                print(e)

    def assignChangesPR(self, PR, PRCONFIG):
        print("Adding assignees to changes PR...")
        if PRCONFIG['AUTOASSIGN']:
            for assignee in PRCONFIG['AUTOASSIGN']:
                PR.add_to_assignees(assignee)

    def addLabelstoChangesPR(self, PR, PRCONFIG):
        print("Adding labels to changes PR...")
        if PRCONFIG['LABELS']:
            for label in PRCONFIG['LABELS']:
                PR.add_to_labels(label)

    def hasExistingChangesPR(self, PRCONFIG):
        openPulls = self.repoObject.get_pulls(
            state='open',
            base=PRCONFIG['PRBASE'],
            head=PRCONFIG['PRHEAD']
        )

        for pull in openPulls:
            if '[gh-standardize]' in pull.title:
                return pull

        return False


from github import Github, GithubException

class GithubAPI:
    def __init__(self, auth):
        self.auth = auth
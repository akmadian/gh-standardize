import re

def GITHUB_RAW_URL_TEMPLATE(login, repo, branch, fileName):
    return "https://raw.githubusercontent.com/{}/{}/{}/{}".format(login, repo, branch, fileName)

def PATH_IS_URL(path):
    URLRegex = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    match = re.search(URLRegex, path)
    return match is not None

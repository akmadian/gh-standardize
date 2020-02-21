import requests
import json
from utils import PATH_IS_URL

class ConfigParser:
    def __init__(self, path):
        self.path = path
        self.config = self.loadConfig()
        self.addTemplateContents()
        print('Config Parsed and template contents added')

    def loadConfig(self):
        with open(self.path) as f:
            contents = json.load(f)
            return contents

    def addTemplateContents(self):
        for template in self.config['TEMPLATES']:
            isUrl = PATH_IS_URL(template['localPath'])
            if isUrl:
                content = requests.get(template['localPath'])
                template['content'] = content.text
            else:
                content = open(template['localPath'], 'r').read()
                template['content'] = content
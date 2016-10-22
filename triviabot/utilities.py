import imp
import re
from HTMLParser import HTMLParser


def make_module(name):
    moduleName, fileName, description = imp.find_module(name)
    module = imp.load_module(name, moduleName, fileName, description)
    return module


def separate_name(user):
    nameregex = re.compile(r'(\S*)!(\S*)@(\S*)')
    nameregexed = nameregex.search(user)
    nameparts = (nameregexed.group(1),  # Nickname
                 nameregexed.group(2),  # Identifier
                 nameregexed.group(3))  # Hostname
    return nameparts


# HTML Tags Stripper
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    html = html.replace('<br />', ' ')
    html = html.replace('<br/>', ' ')
    html = html.replace('<br>', ' ')

    s = MLStripper()
    s.feed(html)
    return s.get_data()
# / HTML Tags Stripper

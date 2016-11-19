import imp
import re
import logging
import os
from HTMLParser import HTMLParser


def make_module(name, module_path):
    moduleName, fileName, description = imp.find_module(name, [module_path])
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


# Custom File Handler for Logging.
class customFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, fileName, when='h',interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        path = '/'.join(fileName.split('/')[:-1])
        if not os.path.exists(path):
            os.mkdir(path)
        logging.handlers.TimedRotatingFileHandler.__init__(self, fileName, when,interval, backupCount, encoding, delay, utc)

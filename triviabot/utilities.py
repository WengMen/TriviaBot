import imp
import re


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

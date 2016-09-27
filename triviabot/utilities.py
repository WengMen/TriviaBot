import imp

def make_module(name):
    moduleName, fileName, description = imp.find_module(name)
    module = imp.load_module(name, moduleName, fileName, description)
    return module

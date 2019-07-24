#from baidu import DotDict
class DotDict(dict):

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self, name):
        value = self[name]
        if isinstance(value, DotDict):
            return value
        elif isinstance(value, dict):
            value = DotDict(value)
            self[name] = value
        return value
    
    def __setattr__(self, key, value):
        if isinstance(value, dict):
            value = DotDict(value)
        self[key] = value
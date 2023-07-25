import json


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class Convert:

    @staticmethod
    def toDict(obj):
        if isinstance(obj, dict):
            return {k: Convert.toDict(v) for k, v in obj.items()}
        elif hasattr(obj, "_ast"):
            return Convert.toDict(obj._ast())
        elif not isinstance(obj, str) and hasattr(obj, "__iter__"):
            return [Convert.toDict(v) for v in obj]
        elif hasattr(obj, "__dict__"):
            return {
                k: Convert.toDict(v)
                for k, v in obj.__dict__.items()
                if not callable(v) and not k.startswith('_')
            }
        else:
            return obj

    @staticmethod
    def toJson(obj):
        if isinstance(obj, dict):
            return json.dumps(obj)
        elif isinstance(obj, object):
            return json.dumps(Convert.toDict(obj))
        else:
            return obj

    @staticmethod
    def toObj(obj):
        if isinstance(obj, list):
            obj = [Convert.toObj(x) for x in obj]
        if not isinstance(obj, dict):
            return obj

        class C(object):
            pass

        o = C()
        for k in obj:
            o.__dict__[k] = Convert.toObj(obj[k])
        return o

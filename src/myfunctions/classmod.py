class ModClassStr:

    def __init__(self, prop):
        self.prop = prop

    def __str__(self):
        return self.prop

    def mod(self, cls):
        cls.__str__ = self.__str__
        return cls
    
    
class _PickledDF:
    def __init__(self, tag, df, attributes):
        self.df = df
        self._tag = tag
        self._file_tag = tag.replace(' ', '_')
        self._attributes = attributes
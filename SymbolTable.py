class SymbolTable(object):
    def __init__(self, symbolTable = None):
        self.enclosingSymbolTable = symbolTable
        self.dictionary = {}
    
    def add(self, name, obj):
        self.dictionary[name] = obj
    
    def lookupCurrLevelOnly(self, name):
        if name in self.dictionary:
            return self.dictionary[name]
        else:
            return None
        
    def lookupCurrLevelAndEnclosingLevels(self, name):
        S = self
        while S != None:
            obj = S.lookupCurrLevelOnly(name)
            if obj:
                return obj
            S = S.enclosingSymbolTable
        return None

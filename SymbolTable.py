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
    
    def __str__(self):
        S = self
        indent = ""
        additional_indent = "    "
        output = ""
        
        while S != None:
            output += indent + "ST(" + S.dictionary.__str__() + ")\n"
            indent += additional_indent
            S = S.enclosingSymbolTable
        return output

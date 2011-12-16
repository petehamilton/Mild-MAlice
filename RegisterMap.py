import re
"""class RegisterMap(dict):
    def __init__(self):
        super(RegisterMap, self).__init__()
        self.toPush = []
        self.toPop = []
        self.registersToPush = []
        self.registersToPop = []
        
    def isInMemory(self, value):
        return re.match('\[\w+\]', value)
        
    # Takes a list of temporary pass by reference argument registers.
    def setPushPopRegs(self, argumentRegs):
        argumentRealRegs = set([ self.get(temp) for temp in argumentRegs ])
        registers = set([ v for v in self.values() if not self.isInMemory(v)])
        registersToPush = list(registers - argumentRealRegs)
        self.registersToPush = registersToPush
        registersToPop = registersToPush[0:]
        registersToPop.reverse()
        self.registersToPop = registersToPop
        
    def getPushRegisters(self):
        return self.registersToPush
        
    def getPopRegisters(self):
        return self.registersToPop
"""        
class RegisterMap(object):
    def __init__(self, registerMap = None):
        self.enclosingRegisterMap = registerMap
        self.dictionary = {}
        self.registersToPush = []
        self.registersToPop = []
    
    def add(self, name, obj):
        self.dictionary[name] = obj
    
    def lookupCurrLevelOnly(self, name):
        if name in self.dictionary:
            return self.dictionary[name]
        else:
            return None
        
    def lookupCurrLevelAndEnclosingLevels(self, name):
        R = self
        while R != None:
            obj = R.lookupCurrLevelOnly(name)
            if obj:
                return obj
            R = R.enclosingRegisterMap
        return None
        
        
    def isInMemory(self, value):
        return re.match('\[\w+\]', value)
        
    # Takes a list of temporary pass by reference argument registers.
    def setPushPopRegs(self, argumentRegs):
        argumentRealRegs = set([ self.dictionary.get(temp) for temp in argumentRegs ])
        registers = set([ v for v in self.dictionary.values() if not self.isInMemory(v)])
        registersToPush = list(registers - argumentRealRegs)
        self.registersToPush = registersToPush
        registersToPop = registersToPush[0:]
        registersToPop.reverse()
        self.registersToPop = registersToPop
        
    def getPushRegisters(self):
        return self.registersToPush
        
    def getPopRegisters(self):
        return self.registersToPop

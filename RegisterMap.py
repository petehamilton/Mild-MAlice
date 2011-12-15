import re
class RegisterMap(dict):
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

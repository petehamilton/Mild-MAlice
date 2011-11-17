class IntermediateNode(object):
    def __init__(self, parents):
        self.parents = parents

    def parentsToString(self):
        return [x.generateCode() for x in self.parents]
            

    #TODO: MAKE THIS ABSTRACT
    def generateCode(self):
        pass
        
    def alteredRegisters(self):
        return []
        
class InstructionNode(IntermediateNode):
    def __init__(self, instruction, parents):
        super(InstructionNode, self).__init__(parents)
        self.instruction = instruction
    
    def generateCode(self):
        return "%s " %(self.instruction) + (', ').join(["T%d" %r for r in self.registers])
    
    def alteredRegisters():
        return [self.registers[0]]
        
class MovNode(InstructionNode):
    def __init__(self, reg1, reg2, parents):
        super(MovNode, self).__init__("mov", parents)
        self.registers = [reg1, reg2]
    
class ImmMovNode(InstructionNode):  
    def __init__(self, reg, imm, parents):
        super(ImmMovNode, self).__init__("imov", parents)  
        self.registers = [reg]
        self.imm = imm
        
    def generateCode(self):
        return "%s T%d, %s" %(self.instruction, self.registers[0], self.imm)
    
    
#TODO MAKE THIS ABSTRACT
class BinOpNode(InstructionNode):
    def __init__(self, instruction, reg1, reg2, parents):
        super(BinOpNode, self).__init__(instruction, parents)  
        self.registers = [reg1, reg2]

class AddNode(BinOpNode):
    def __init__(self, reg1, reg2, parents):
        super(AddNode, self).__init__("add", reg1, reg2, parents)  
        
class SubNode(BinOpNode):
    def __init__(self, reg1, reg2, parents):
        super(SubNode, self).__init__("sub", reg1, reg2, parents) 
         
class MulNode(BinOpNode):
    def __init__(self, reg1, reg2, parents):
        super(MulNode, self).__init__("imul", reg1, reg2, parents)
          
class DivNode(BinOpNode):
    def __init__(self, reg1, reg2, parents):
        super(DivNode, self).__init__("idiv", reg1, reg2, parents)  
        
class ModNode(BinOpNode):
    def __init__(self, reg1, reg2, parents):
        super(ModNode, self).__init__("idiv", reg1, reg2, parents) 
         
class OrNode(BinOpNode):
    def __init__(self, reg1, reg2, parents):
        super(OrNode, self).__init__("or", reg1, reg2, parents)  
        
class XORNode(BinOpNode):
    def __init__(self, reg1, reg2, parents):
        super(XORNode, self).__init__("xor", reg1, reg2, parents) 
         
class AndNode(BinOpNode):
    def __init__(self, reg1, reg2, parents):
        super(AndNode, self).__init__("and", reg1, reg2, parents)  

class UnOpNode(InstructionNode):
    def __init__(self, instruction, reg, parents):
        super(UnOpNode, self).__init__(instruction, parents)  
        self.registers = [reg]
        
class IncNode(UnOpNode):
    def __init__(self, reg, parents):
        super(IncNode, self).__init__("inc", reg, parents)
        
class DecNode(UnOpNode):
    def __init__(self, reg, parents):
        super(DecNode, self).__init__("dec", reg, parents)
        
class NotNode(UnOpNode):
    def __init__(self, reg, parents):
        super(NotNode, self).__init__("not", reg, parents)

class SpokeNode(IntermediateNode):
    def __init__(self, reg, parents):
        super(SpokeNode, self).__init__(parents)
        self.registers = [reg]
        
    def generateCode(self):
        return "PRINT %s" %self.registers[0]
    

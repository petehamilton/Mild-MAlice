class IntermediateNode(object):
    def __init__(self):
        pass
    #TODO: MAKE THIS ABSTRACT
    def generateCode():
        pass

class InstructionNode(object):
    def __init__(self, instruction):
        super(InstructionNode, self).__init__()
        self.instruction = instruction
          
        
class MovNode(InstructionNode):
    def __init__(self, reg1, reg2):
        super(MovNode, self).__init__("mov")
        self.reg1 = reg1
        self.reg2 = reg2
    
class ImmMovNode(InstructionNode):  
    def __init__(self, reg, immediateValue):
        super(ImmMovNode, self).__init__("imov")  
        self.reg = reg
        self.imm = immediateValue
    
#TODO MAKE THIS ABSTRACT
class BinOpNode(InstructionNode):
    def __init__(self, instruction, reg1, reg2):
        super(BinOpNode, self).__init__(instruction)  
        self.reg1 = reg1
        self.reg2 = reg2

 
class AddNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(AddNode, self).__init__("add", reg1, reg2)  
        
class SubNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(SubNode, self).__init__("sub", reg1, reg2) 
         
class MulNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(MulNode, self).__init__("imul", reg1, reg2)
          
class DivNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(DivNode, self).__init__("idiv", reg1, reg2)  
        
class ModNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(ModNode, self).__init__("idiv", reg1, reg2) 
         
class OrNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(OrNode, self).__init__("or", reg1, reg2)  
        
class XORNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(XORNode, self).__init__("xor", reg1, reg2) 
         
class AndNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(AndNode, self).__init__("and", reg1, reg2)  

class UnOpNode(InstructionNode):
    def __init__(self, instruction, reg):
        super(UnOpNode, self).__init__(instruction)  
        self.reg = reg
        
class IncNode(UnOpNode):
    def __init__(self, reg):
        super(IncNode, self).__init__("inc", reg)
        
class DecNode(UnOpNode):
    def __init__(self, reg):
        super(DecNode, self).__init__("dec", reg)
        
class NotNode(UnOpNode):
    def __init__(self, reg):
        super(NotNode, self).__init__("not", reg)

class SpokeNode(ImmediateNode):
    def __init__(self, reg):
        super(SpokeNode, self).__init__(reg)
        self.reg = reg
    

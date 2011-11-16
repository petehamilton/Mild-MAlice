class IntermediateNode(object):
    def __init__(self, instruction):
        self.instruction = instruction
    
    #TODO: MAKE THIS ABSTRACT
    def generateCode():
        pass
        
class MovNode(IntermediateNode):
    def __init__(self, reg1, reg2):
        super(MovNode, self).__init__("mov")
        self.reg1 = reg1
        self.reg2 = reg2
    
class ImmMovNode(IntermediateNode):  
    def __init__(self, reg, immediateValue):
        super(ImmMovNode, self).__init__("imov")  
        self.reg = reg
        self.imm = immediateValue
    
#TODO MAKE THIS ABSTRACT
class BinOpNode(IntermediateNode):
    def __init__(self, instruction, reg1, reg2):
        super(BinOpNode, self).__init__(instruction)  
        this.reg1 = reg1
        this.reg2 = reg2

 
class AddNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(AddNode, self).__init__("add", reg1, reg2)  
        
class SubNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(SubNode, self).__init__("sub", reg1, reg2) 
         
class ImulNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(ImulNode, self).__init__("imul", reg1, reg2)
          
class IdivNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(IdivNode, self).__init__("idiv", reg1, reg2)  
        
class ModNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(ModNode, self).__init__("idiv", reg1, reg2) 
         
class OrNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(OrNode, self).__init__("or", reg1, reg2)  
        
class XorNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(XorNode, self).__init__("xor", reg1, reg2) 
         
class AndNode(BinOpNode):
    def __init__(self, reg1, reg2):
        super(AndNode, self).__init__("and", reg1, reg2)  

class UnOpNode(IntermediateNode):
    def __init__(self, instruction, reg):
        super(UnOpNode, self).__init__(instruction)  
        this.reg = reg
        
class IncNode(UnOpNode):
    def __init__(self, reg):
        super(IncNode, self).__init__("inc", reg)
        
class DecNode(UnOpNode):
    def __init__(self, reg):
        super(DecNode, self).__init__("dec", reg)
        
class NotNode(UnOpNode):
    def __init__(self, reg):
        super(NotNode, self).__init__("not", reg)
    
    

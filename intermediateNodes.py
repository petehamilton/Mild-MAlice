import re

################################################################################
# UNIQUE LABEL ID GENERATOR
################################################################################
currentUniqueID = 1

def makeUniqueLabel(label):
    global currentUniqueID
    uniqueID = currentUniqueID
    currentUniqueID += 1
    return "%s_%d" % (label, uniqueID)
    
################################################################################
# NODES
################################################################################

def makeUniqueLabel(label):
    global currentUniqueID
    uniqueID = currentUniqueID
    currentUniqueID += 1
    return "%s_%d" % (label, uniqueID)

class IntermediateNode(object):
    def __init__(self, parents):
        self.parents = parents

    def generateCode(self, registerMap):
        pass
        
    def alteredRegisters(self):
        return []

    def uses(self):
        return self.registers
        
    def pushRegs(self, registersToPush):
        return ["push %s" %x for x in registersToPush]
        
    def popRegs(self, registersToPop):
        return ["pop %s" %x for x in registersToPop]
    
    def setParents(self, parents):
        self.parents = parents
        
class InstructionNode(IntermediateNode):
    def __init__(self, instruction, parents):
        super(InstructionNode, self).__init__(parents)
        self.instruction = instruction
        
    def generateCode(self, registerMap):
        return ["%s " %(self.instruction) + (', ').join(["%s" % registerMap[r] for r in self.registers])]
    
    def alteredRegisters(self):
        return [self.registers[0]]
        
    # Works out if a given value for an instruction is in memory by using 
    # regular expressions. 
    def isInMemory(self, value):
        return re.match('\[\w+\]', value)
        
class MovNode(InstructionNode):
    def __init__(self, reg1, reg2, parents):
        super(MovNode, self).__init__("mov", parents)
        self.registers = [reg1, reg2]
    
    def uses(self):
        return [self.registers[1]]
    
    def generateCode(self, registerMap):
        # TODO: COULD HAVE REGISTER CLASS SO KNOW IF ITS MEMORY OR REG
        if self.registers[1] in registerMap:
            if registerMap[self.registers[0]] == registerMap[self.registers[1]]:
                return []
            return ["%s " %(self.instruction) + (', ').join(["%s" % registerMap[r] for r in self.registers])]
        else:
            return ["%s %s, %s" %(self.instruction, registerMap[self.registers[0]], self.registers[1])]

class ImmMovNode(InstructionNode):  
    def __init__(self, reg, imm, parents):
        super(ImmMovNode, self).__init__("mov", parents)  
        self.registers = [reg]
        self.imm = imm
        
    # Chosen to move into rax as it is a given in assembly that this register will
    # get overwritten in function calls.
    def generateCode(self, registerMap):
        destReg = registerMap[self.registers[0]]
        if self.isInMemory(destReg):
            return ["mov rax, %s \n%s %s, rax" %(self.imm, self.instruction, destReg)]
            
        return ["%s %s, %s" %(self.instruction, registerMap[self.registers[0]], self.imm)]

    def uses(self):
        return []
    
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
        self.regToReturn = "rax"
        self.idivRegisters = ["rdx", "rcx"]
    
    # Preserves registers that could get overwritten by the div instruction
    # unless it's the desintation register.
    # Puts registers in relevant registers required by idiv instruction.
    def generateCode(self, registerMap):
        destReg, nextReg = map(lambda x: registerMap[x], self.registers)
        registersToPreserve = list(set(self.idivRegisters) - set([destReg]))
        registersToPreserveReverse = registersToPreserve[0:]
        registersToPreserveReverse.reverse()
        
        if self.isInMemory(nextReg):
            compCode = "mov rax, %s \ncmp rax, 0" %(nextReg)
        else:
            compCode = "cmp %s, 0" %nextReg
        
        return ([compCode,
                 "jz os_return" ] +
                self.pushRegs(registersToPreserve) +
                ["mov rax, %s" %destReg,
                 "mov rcx, %s" %nextReg,
                 "mov rdx, %d" %0,
                 "idiv rcx",
                 "mov %s, %s"%(destReg, self.regToReturn)] +
               self.popRegs(registersToPreserveReverse))
        
class ModNode(DivNode):
    def __init__(self, reg1, reg2, parents):
        super(ModNode, self).__init__(reg1, reg2, parents) 
        self.regToReturn = "rdx"
         
class OrNode(BinOpNode):
    def __init__(self, reg1, reg2, parents):
        super(OrNode, self).__init__("or", reg1, reg2, parents)  
        
class XORNode(BinOpNode):
    def __init__(self, reg1, reg2, parents):
        super(XORNode, self).__init__("xor", reg1, reg2, parents) 
         
class AndNode(BinOpNode):
    def __init__(self, reg1, reg2, parents):
        super(AndNode, self).__init__("and", reg1, reg2, parents)          
        
class LogicalOpNode(BinOpNode):
    # Could/should(?) use nested nodes instead of labels?
    # Also, instruction not used really so should probably inherit from intermediateNode?
    def __init__(self, instruction, reg1, reg2, parents):
        super(LogicalOpNode, self).__init__(instruction, reg1, reg2, parents)
    
    def generateCode(self, registerMap):
        destReg, nextReg = map(lambda x: registerMap[x], self.registers)
        
        # What happens if they're memory addresses?
        start_label = makeUniqueLabel("logical_eval_start")
        true_label = makeUniqueLabel("logical_eval_true")
        end_label = makeUniqueLabel("logical_eval_end")
        return [
                start_label + ":",
                "cmp %s, %s" % (destReg, nextReg),
                self.instruction + " " + true_label,
                "mov %s, 0" % destReg,
                "jmp " + end_label,
                true_label + ":",
                "mov %s, 1" % destReg,
                end_label + ":"
        ]
        
class EqualNode(LogicalOpNode):
    def __init__(self, reg1, reg2, parents):
        super(EqualNode, self).__init__('je', reg1, reg2, parents)

class NotEqualNode(LogicalOpNode):
    def __init__(self, reg1, reg2, parents):
        super(NotEqualNode, self).__init__('jne', reg1, reg2, parents)
        
class LessThanNode(LogicalOpNode):
    def __init__(self, reg1, reg2, parents):
        super(LessThanNode, self).__init__('jl', reg1, reg2, parents)
        
class LessThanEqualNode(LogicalOpNode):
    def __init__(self, reg1, reg2, parents):
        super(LessThanEqualNode, self).__init__('jle', reg1, reg2, parents)
        
class GreaterThanNode(LogicalOpNode):
    def __init__(self, reg1, reg2, parents):
        super(GreaterThanNode, self).__init__('jg', reg1, reg2, parents)
        
class GreaterThanEqualNode(LogicalOpNode):
    def __init__(self, reg1, reg2, parents):
        super(GreaterThanEqualNode, self).__init__('jge', reg1, reg2, parents)
        
class LAndNode(LogicalOpNode):
    def __init__(self, reg1, reg2, parents):
        super(AndNode, self).__init__('jge', reg1, reg2, parents)

    def generateCode(self, registerMap):
        destReg, nextReg = map(lambda x: registerMap[x], self.registers)
    
        # What happens if they're memory addresses?
        start_label = makeUniqueLabel("logical_eval_start")
        false_label = makeUniqueLabel("logical_eval_false")
        end_label = makeUniqueLabel("logical_eval_end")
        return [
            start_label + ":",
            "cmp %s, 1" % destReg,
            "jne " + false_label,
            "cmp %s, 1" % nextReg,
            "jne " + false_label,
            "mov %s, 1" % destReg,
            "jmp " + end_label,
            false_label + ":",
            "mov %s, 0" % destReg,
            end_label + ":"
        ]
        
class LOrNode(LogicalOpNode):
    def __init__(self, reg1, reg2, parents):
        super(OrNode, self).__init__('jge', reg1, reg2, parents)

    def generateCode(self, registerMap):
        destReg, nextReg = map(lambda x: registerMap[x], self.registers)
    
        # What happens if they're memory addresses?
        start_label = makeUniqueLabel("logical_eval_start")
        true_label = makeUniqueLabel("logical_eval_true")
        end_label = makeUniqueLabel("logical_eval_end")
        return [
            start_label + ":",
            "cmp %s, 1" % destReg,
            "je " + true_label,
            "cmp %s, 1" % nextReg,
            "je " + true_label,
            "mov %s, 0" % destReg,
            "jmp " + end_label,
            true_label + ":",
            "mov %s, 1" % destReg,
            end_label + ":"
        ]
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
   
# TODO: Added on the fly, review later.
class NegativeNode(UnOpNode):
    def __init__(self, reg, parents):
        super(NegativeNode, self).__init__("negative", reg, parents)

class LabelNode(IntermediateNode):
    def __init__(self, label, parents):
        super(LabelNode, self).__init__(parents)
        self.label = label
    
    def uses(self):
        return []
    
    def alteredRegisters(self):
        return []
    
    def getLabel(self):
        return self.label
    
    def generateCode(self, registerMap):
        return ["%s:" % self.label]

class TrueCheckNode(IntermediateNode):
    def __init__(self, reg, falseLabelNode, parents):
        super(TrueCheckNode, self).__init__(parents)
        self.falseLabelNode = falseLabelNode
        self.registers = [reg]
    
    def uses(self):
        return [self.registers[0]]
    
    def alteredRegisters(self):
        return []
        
    def getFalseLabel(self):
        return self.falseLabelNode.getLabel()
    
    def generateCode(self, registerMap):
        reg = registerMap[self.registers[0]]
        return ["cmp %s, 0" % reg, "jne %s" % self.getFalseLabel()]

class LoopNode(IntermediateNode):
    def __init__(self, usedRegisters, parents):
        super(LoopNode, self).__init__(parents)
        self.registers = usedRegisters
    
    def uses(self):
        return self.registers
    
    def alteredRegisters(self):
        return []
    
    def generateCode(self, registerMap):
        return []

class JumpNode(IntermediateNode):
    def __init__(self, labelNode, parents):
        super(JumpNode, self).__init__(parents)
        self.labelNode = labelNode
    
    def uses(self):
        return []
    
    def alteredRegisters(self):
        return []
        
    def getLabel(self):
        return self.labelNode.getLabel()
    
    def generateCode(self, registerMap):
        return ["jmp %s" % self.getLabel()]
    

class IONode(IntermediateNode):
    def __init__(self, reg, parents, formatting):
        super(IONode, self).__init__(parents)
        self.registers = [reg]
        self.formatting = formatting
        self.ioRegisters = ['rsi', 'rdi', 'r8', 'r9', 'r10']
    
    def preserveRegisters(self, destReg):
        if not destReg:
            registersToPreserve = list(set(self.ioRegisters))
        else:
            registersToPreserve = list(set(self.ioRegisters) - set([destReg]))
        registersToPreserveReverse = registersToPreserve[0:]
        registersToPreserveReverse.reverse()
        return self.pushRegs(registersToPreserve), self.popRegs(registersToPreserveReverse)

        
class SpokeNode(IONode):
    def __init__(self, reg, parents, formatting):
        super(SpokeNode, self).__init__(reg, parents, formatting)
            
    # Puts registers in the relevant registers required for printf call and
    # preserves the registers which may be overwritten.
    def generateCode(self, registerMap):
        destReg = registerMap[self.registers[0]]
        pushedRegs, poppedRegs = self.preserveRegisters(destReg) 

        return (pushedRegs +
                ["mov rsi, %s" %destReg,
                "mov rdi, %s" %self.formatting,
                "xor rax, rax",
                "call printf"] +
                poppedRegs)

class InputNode(IONode):
    def __init__(self, reg, parents, formatting):
        super(InputNode, self).__init__(reg, parents, formatting)
    
    def getMemoryLocAndMessageLoc(self):
        memoryLoc = ""
        message = self.formatting + "_message"
        if "char" in self.formatting:
            memoryLoc = "charinput"
        elif "int" in self.formatting:
            memoryLoc = "intinput"
        return memoryLoc, message
    
    #TODO: TIDY THIS UP SO NOT WASTED CODE
    
    def printMessage(self, messageLoc):
        pushedRegs, poppedRegs = self.preserveRegisters(None)
        return(pushedRegs+
                ["mov rsi, %s" %messageLoc,
                "mov rdi, outputstringfmt",
                "xor rax, rax",
                "call printf"] +
               poppedRegs)
               
    def generateCode(self, registerMap):
        destReg = registerMap[self.registers[0]]
        memoryLoc, messageLoc = self.getMemoryLocAndMessageLoc()
        pushedRegs, poppedRegs = self.preserveRegisters(destReg) 
        printMessageCode = self.printMessage(messageLoc)
        return ( printMessageCode +
                 pushedRegs +
                ["mov rsi, %s" %(memoryLoc),
                "mov rdi, %s" %("input" + self.formatting),
                "xor rax, rax",
                "call scanf",
                "mov %s, [%s]" %(destReg, memoryLoc)] +
                poppedRegs)

                
class FunctionDeclarationNode(IntermediateNode):
    def __init__(self, parents, name, arguments, body):
        super(FunctionDeclarationNode, self).__init__(parents)
        self.body = arguments + body
        self.name = name
        self.registers = []
        for b in self.body:
            self.registers.extend(b.uses())
        
    def generateCode(self, registerMap):
            
        bodyCode = []
        for body in self.body:
            bodyCode.extend(body.generateCode(registerMap))
        #TODO: Not sure how to deal with passing by reference??
        return ( ["%s:" %self.name, 
                 'push rbp',
                 "mov rbp, rsp", ] +
                 self.pushRegs(list(set(registerMap.values()))) +
                  bodyCode )

class ReturnNode(IntermediateNode):
    def __init__(self, reg, parents):
        super(ReturnNode, self).__init__(parents)
        self.registers = [reg]
        
    def generateCode(self, registerMap):
        registersReverse = list(set(registerMap.values()))[0:]
        registersReverse.reverse()
        return ([ "mov rax, %s" %(registerMap[self.registers[0]]) ] +
                self.popRegs(registersReverse) +
                [ "pop rbp", 
                 "ret" ])
 
class ArgumentNode(IntermediateNode):
    def __init__(self, reg, parents, argNumber, reference = False ):
         super(ArgumentNode, self).__init__(parents)
         self.registers = [reg]
         self.reference = reference
         self.argNumber = argNumber 

    def generateCode(self, registerMap):
        if self.reference:
            return []
        else:
            return [ "mov %s, [rbp + %d]" %(registerMap[self.registers[0]], self.argNumber*8 + 8) ]
            
class FunctionArgumentNode(IntermediateNode):
    def __init__(self, reg, parents):
         super(FunctionArgumentNode, self).__init__(parents)
         self.registers = [reg]

    def generateCode(self, registerMap):
            return [ "push %s" %(registerMap[self.registers[0]]) ]  
            
class FunctionCallNode(IntermediateNode):
    def __init__(self, reg, parents, registersPushed, name):
        super(FunctionCallNode, self).__init__(parents)
        self.registersPushed = registersPushed
        self.registers = [reg]
        self.functionName = name
    
    def generateCode(self, registerMap):
        return ["call %s" %self.functionName,
                "add rsp, %d" %(8*self.registersPushed),
                "mov %s, rax" %(registerMap[self.registers[0]])]
        
        

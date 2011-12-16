import re
import ASTNodes
import labels
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

class IntermediateNode(object):
    def __init__(self, parents):
        self.parents = parents
        self.registers = []

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
        
    # Works out if a given value for an instruction is in memory by using 
    # regular expressions. 
    def isInMemory(self, value):
        return re.match('\[\w+\]', value)
    
    def preventBadRegisters(self, op, dest, src):
        instructions = []
        if dest == src and op == "mov":
            return []
        if op == "mov":
            if self.isInMemory(dest) and self.isInMemory(src):
                instructions = ["mov rax, %s" % src,
                                 "%s %s, rax" % (op, dest)]
        else:
            if self.isInMemory(dest):
                instructions = ["mov rax, %s" % dest,
                                 "%s rax, %s" % (op, src),
                                 "mov %s, rax" % dest]
        if not instructions:
            instructions = ["%s %s, %s" %(op, dest, src)]
        return instructions
    
    def preserveRegisters(self, destReg):
        preserveRegisters = ['rsi', 'rdi', 'r8', 'r9', 'r10']
        if not destReg:
            registersToPreserve = list(set(preserveRegisters))
        else:
            registersToPreserve = list(set(preserveRegisters) - set([destReg]))
        registersToPreserveReverse = registersToPreserve[0:]
        registersToPreserveReverse.reverse()
        return self.pushRegs(registersToPreserve), self.popRegs(registersToPreserveReverse)
        
class InstructionNode(IntermediateNode):
    def __init__(self, instruction, parents):
        super(InstructionNode, self).__init__(parents)
        self.instruction = instruction
        
    def generateCode(self, registerMap):
        return ["%s " %(self.instruction) + (', ').join(["%s" % registerMap[r] for r in self.registers])]
    
    def alteredRegisters(self):
        return [self.registers[0]]
        
class MovNode(InstructionNode):
    def __init__(self, reg1, reg2, parents):
        super(MovNode, self).__init__("mov", parents)
        self.registers = [reg1, reg2]
    
    def uses(self):
        return [self.registers[1]]
    
    def generateCode(self, registerMap):
        return self.preventBadRegisters("mov", registerMap[self.registers[0]], registerMap[self.registers[1]] )

class ImmMovNode(InstructionNode):  
    def __init__(self, reg, imm, parents):
        super(ImmMovNode, self).__init__("mov", parents)  
        self.registers = [reg]
        self.imm = imm
        
    # Chosen to move into rax as it is a given in assembly that this register will
    # get overwritten in function calls.
    def generateCode(self, registerMap):
        destReg = registerMap[self.registers[0]]
        return self.preventBadRegisters(self.instruction, registerMap[self.registers[0]], self.imm)

    def uses(self):
        return []
  
class BinOpNode(InstructionNode):
    def __init__(self, instruction, reg1, reg2, parents):
        super(BinOpNode, self).__init__(instruction, parents)  
        self.registers = [reg1, reg2]
        
class PossibleBinaryOverFlowNode(BinOpNode):
    def __init__(self, instruction, reg1, reg2, parents):
        super(PossibleBinaryOverFlowNode, self).__init__(instruction, reg1, reg2, parents)
        
    def generateCode(self, registerMap):
        code = super(PossibleBinaryOverFlowNode, self).generateCode(registerMap)
        overFlowTest = ["jo %s" %labels.overFlowLabel]
        return code + overFlowTest

class AddNode(PossibleBinaryOverFlowNode):
    def __init__(self, reg1, reg2, parents):
        super(AddNode, self).__init__("add", reg1, reg2, parents)  
        
class SubNode(PossibleBinaryOverFlowNode):
    def __init__(self, reg1, reg2, parents):
        super(SubNode, self).__init__("sub", reg1, reg2, parents) 
         
class MulNode(PossibleBinaryOverFlowNode):
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
                 "je %s" %labels.divisionByZeroLabel] +
                self.pushRegs(registersToPreserve) +
                ["mov rax, %s" %destReg,
                 "mov rcx, %s" %nextReg,
                 "mov rdx, %d" %0,
                 "idiv rcx"] +
                 self.preventBadRegisters("mov", destReg, self.regToReturn) +
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
    def __init__(self, exp1, exp2, parents):
        super(AndNode, self).__init__("and", exp1, exp2, parents)          
        
class LogicalOpNode(BinOpNode):
    def __init__(self, instruction, reg1, reg2, parents):
        super(LogicalOpNode, self).__init__(instruction, reg1, reg2, parents)
    
    def generateCode(self, registerMap):
        destReg, nextReg = map(lambda x: registerMap[x], self.registers)
        start_label = makeUniqueLabel("logical_eval_start")
        true_label = makeUniqueLabel("logical_eval_true")
        end_label = makeUniqueLabel("logical_eval_end")
        return ([start_label + ":"] + 
                self.preventBadRegisters("cmp", destReg, nextReg) +
                [self.instruction + " " + true_label,
                "mov %s, 0" % destReg,
                "jmp " + end_label,
                true_label + ":",
                "mov %s, 1" % destReg,
                end_label + ":"])
        
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
        
class PossibleUnaryOverFlowNode(UnOpNode):
    def __init__(self, instruction, reg, parents):
        super(PossibleUnaryOverFlowNode, self).__init__(instruction, reg, parents)
    
    def generateCode(self, registerMap):
        code = super(PossibleUnaryOverFlowNode, self).generateCode(registerMap)
        overFlowTest = ["jo %s" %labels.overFlowLabel]
        return code + overFlowTest    

class IncNode(PossibleUnaryOverFlowNode):
    def __init__(self, reg, parents):
        super(IncNode, self).__init__("inc", reg, parents)
        
class DecNode(PossibleUnaryOverFlowNode):
    def __init__(self, reg, parents):
        super(DecNode, self).__init__("dec", reg, parents)
        
class NotNode(UnOpNode):
    def __init__(self, reg, parents):
        super(NotNode, self).__init__("not", reg, parents)
   
class NegativeNode(UnOpNode):
    def __init__(self, reg, parents):
        super(NegativeNode, self).__init__("neg", reg, parents)

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

class JumpBooleanNode(IntermediateNode):
    def __init__(self, instruction, reg, labelNode, parents):
        super(JumpBooleanNode, self).__init__(parents)
        self.labelNode = labelNode
        self.registers = [reg]
        self.instruction = instruction
    
    def uses(self):
        return [self.registers[0]]
    
    def alteredRegisters(self):
        return []
        
    def getLabel(self):
        return self.labelNode.getLabel()
    
    def generateCode(self, registerMap):
        reg = registerMap[self.registers[0]]
        return ["cmp %s, 0" % reg, "%s %s" % (self.instruction, self.getLabel())]
        
class JumpTrueNode(JumpBooleanNode):
    def __init__(self, reg, trueLabelNode, parents):
        super(JumpTrueNode, self).__init__('jne', reg, trueLabelNode, parents)

class JumpFalseNode(JumpBooleanNode):
    def __init__(self, reg, falseLabelNode, parents):
        super(JumpFalseNode, self).__init__('je', reg, falseLabelNode, parents)

class SpokeNode(IntermediateNode):
    def __init__(self, reg, parents, printFunction):
        super(SpokeNode, self).__init__(parents)
        self.printFunction = printFunction
        self.registers = [reg]
            
    # Puts registers in the relevant registers required for printf call and
    # preserves the registers which may be overwritten.
    def generateCode(self, registerMap):
        destReg = registerMap[self.registers[0]]
        return ["push %s" %destReg,
                "call %s" %self.printFunction,
                "add rsp, 8"]

class InputNode(IntermediateNode):
    def __init__(self, reg, parents, formatting):
        super(InputNode, self).__init__(parents)
        self.formatting = formatting
        self.registers = [reg]
        self.ioRegisters = ['rsi', 'rdi', 'r8', 'r9', 'r10']
    
    def preserveRegisters(self, destReg):
        if not destReg:
            registersToPreserve = list(set(self.ioRegisters))
        else:
            registersToPreserve = list(set(self.ioRegisters) - set([destReg]))
        registersToPreserveReverse = registersToPreserve[0:]
        registersToPreserveReverse.reverse()
        return self.pushRegs(registersToPreserve), self.popRegs(registersToPreserveReverse)
    
    def getMemoryLoc(self):
        if "char" in self.formatting:
            memoryLoc = "charinput"
        elif "int" in self.formatting:
            memoryLoc = "intinput"
        return memoryLoc
               
    def generateCode(self, registerMap):
        destReg = registerMap[self.registers[0]]
        memoryLoc = self.getMemoryLoc()
        pushedRegs, poppedRegs = self.preserveRegisters(destReg) 
        return (pushedRegs +
                ["mov rsi, %s" %(memoryLoc),
                "mov rdi, %s" %(self.formatting),
                "xor rax, rax",
                "call scanf",
                "mov %s, [%s]" %(destReg, memoryLoc)] +
                poppedRegs)

                
class FunctionDeclarationNode(IntermediateNode):
    def __init__(self, parents, name, arguments, body, symbolTable, registersDict):
        super(FunctionDeclarationNode, self).__init__(parents)
        self.arguments = arguments
        self.body = arguments + body
        self.name = name
        self.registers = []
        self.returnLabel = "%s_end" %name

        #Set jump label in return node.
        returnCodeParents = []
        for node in (self.body):
            self.registers.extend(node.uses())
            if isinstance(node, ReturnNode):
               node.setJumpLabel(self.returnLabel)
               returnCodeParents.append(node)
        
        # set deallocation of any arrays created
        returnNode = FunctionReturnCode(returnCodeParents, self.returnLabel)            
        deallocStartLabelNode = LabelNode(makeUniqueLabel(labels.deallocationLabel), returnCodeParents)
        deallocNodes = generateDeallocationNodes(symbolTable, registersDict, deallocStartLabelNode)
        for node in deallocNodes:
             returnNode.addReturnInstruction(node)
        self.body.append(returnNode)
            
    def defined(self):
        return [b.registers[0] for b in (self.body) if len(b.registers)]
    
    def generateCode(self, registerMap):
        referenceArguments = [node.getRegister() for node in self.arguments if node.isReference()]
        registerMap.setPushPopRegs(referenceArguments)
        bodyCode = []
        for body in self.body:
            bodyCode.extend(body.generateCode(registerMap))
        return ( ["%s:" %self.name, 
                 'push rbp',
                 "mov rbp, rsp", ] +
                  self.pushRegs(registerMap.getPushRegisters()) +
                  bodyCode )

class ReturnNode(IntermediateNode):
    def __init__(self, reg, parents):
        super(ReturnNode, self).__init__(parents)
        self.extraInstructions = []
        self.registers = [reg]
        self.jumpLabel = None

    def setJumpLabel(self, label):
        self.jumpLabel = label    
    
    def generateCode(self, registerMap):
        moveCode = "mov rax, %s" %(registerMap[self.registers[0]])
        if self.jumpLabel:
            return [ moveCode, "jmp %s" %self.jumpLabel ]
        return [moveCode]
 
class ReferenceMovNode(InstructionNode):  
    def __init__(self, imm, reg, parents):
        super(ReferenceMovNode, self).__init__("mov", parents)  
        self.registers = [reg]
        self.imm = imm
        
    def generateCode(self, registerMap):
        destReg = registerMap[self.registers[0]]
        return ["mov %s, %s" %(self.imm, destReg)] 
        
class FunctionReturnCode(IntermediateNode):
    def __init__(self, parents, label):
        super(FunctionReturnCode, self).__init__(parents)
        self.label = label
        self.regsUsed = []
        self.returnInstructions = []
        
    def addReturnInstruction(self, node):
        self.returnInstructions.append(node)
        self.regsUsed.extend(node.uses())
        
    def uses(self):
        return self.regsUsed

    def generateCode(self, registerMap):
        argumentsCode = []
        for node in self.returnInstructions:
            argumentsCode.extend(node.generateCode(registerMap))
        return ( ["%s:" %self.label]+
                argumentsCode + 
                self.popRegs(registerMap.getPopRegisters()) +
                [ "pop rbp", 
                 "ret" ])
 
class ArgumentNode(IntermediateNode):
    def __init__(self, reg, parents, argNumber, array = False ):
         super(ArgumentNode, self).__init__(parents)
         self.registers = [reg]
         self.array = array
         self.argNumber = argNumber 

    def isArray(self):
        return self.array

    def uses(self):
        return []

    def getRegister(self):
        return self.registers[0]

    def alteredRegisters(self):
        return [self.registers[0]]

    def returnCode(self, parents):
        if self.reference:
            return ReferenceMovNode( "[reference%d]" %self.argNumber, self.getRegister(), parents)
    
    def generateCode(self, registerMap):
        return [ "mov %s, [rbp + %d]" %(registerMap[self.registers[0]], (self.argNumber + 1)*8 + 8) ]
            
class FunctionArgumentNode(IntermediateNode):
    def __init__(self, reg, parents):
         super(FunctionArgumentNode, self).__init__(parents)
         self.registers = [reg]
    
    def getRegister(self, registerMap):
        return (registerMap[self.registers[0]])

    def generateCode(self, registerMap):
            register = (registerMap[self.registers[0]])
            return [ "push %s" %register ]  
            
class FunctionCallNode(IntermediateNode):
    def __init__(self, reg, parents, registersPushed, name):
        super(FunctionCallNode, self).__init__(parents)
        self.registersPushed = registersPushed
        self.registers = [reg]
        self.functionName = name
    
    def generateCode(self, registerMap):
        return (["call %s" %self.functionName,
                "add rsp, %d" %(8*self.registersPushed),
                "mov %s, rax" %(registerMap[self.registers[0]])])


class MallocNode(IntermediateNode):
    def __init__(self, destReg, parents, lengthRegister):
        super(MallocNode, self).__init__(parents)
        self.registers = [destReg, lengthRegister]
        
    def uses(self):
        return [self.registers[1]]
    
    def alteredRegisters(self):
        return [self.registers[0]]
    
    def generateCode(self, registerMap):
        destReg, indexReg = registerMap[self.registers[0]], registerMap[self.registers[1]]
        pushedRegs, poppedRegs = self.preserveRegisters("rax")
        
        return ([""] + pushedRegs +
                ["mov rdi, %s" % indexReg,
                "imul rdi, 8",
                "xor rax, rax",
                "call malloc"] +
                poppedRegs +
                ["test rax, rax",
                 "mov %s, rax" % destReg,
                "jz malloc_failure"] + [""])

class DeallocNode(IntermediateNode):
    def __init__(self, arrayBaseReg, parents):
        super(DeallocNode, self).__init__(parents)
        self.registers = [arrayBaseReg]
    
    def uses(self):
        return [self.registers[0]]
    
    def alteredRegisters(self):
        return []
    
    def generateCode(self, registerMap):
        baseReg = registerMap[self.registers[0]]
        pushedRegs, poppedRegs = self.preserveRegisters(None)
        
        return ([""] + ["%s:" % (makeUniqueLabel("dealloc"))] +
                pushedRegs +
                ["mov rdi, %s" % (baseReg),
                "xor rax, rax",
                "call free"] + 
                poppedRegs + [""])

class ArrayAccessNode(IntermediateNode):
    def __init__(self, destReg, arrayBaseReg, indexReg, parents):
        super(ArrayAccessNode, self).__init__(parents)
        self.registers = [destReg, arrayBaseReg, indexReg]
    
    def uses(self):
        return [self.registers[1],self.registers[2]]
    
    def alteredRegisters(self):
        return [self.registers[0]]
    
    def generateCode(self, registerMap):
        # Add the push/pop to this for volatile registers
        movInstr = self.preventBadRegisters("mov", registerMap[self.registers[0]], registerMap[self.registers[2]])
        subInstr = self.preventBadRegisters("sub", registerMap[self.registers[0]], 1)
        mulInstr = self.preventBadRegisters("imul", registerMap[self.registers[0]], 8)
        return (movInstr + 
                subInstr + 
                mulInstr +
               ["add %s, %s" % (registerMap[self.registers[0]], registerMap[self.registers[1]])])
               
class ArrayMovNode(InstructionNode):
    def __init__(self, reg1, reg2, setsValue, parents):
        super(ArrayMovNode, self).__init__("mov", parents)
        self.registers = [reg1, reg2]
        self.setsValue = setsValue
    
    def uses(self):
        return [self.registers[0],self.registers[1]]
        
    def alteredRegisters(self):
        return []
    
    def generateCode(self, registerMap):
        if self.setsValue:
            return self.preventBadRegisters("mov", "[%s]" % registerMap[self.registers[0]], registerMap[self.registers[1]] )
        else:
            return self.preventBadRegisters("mov", registerMap[self.registers[0]], "[%s]" % registerMap[self.registers[1]] )

def generateDeallocationNodes(symbolTable, registerDict, startLabelNode):
    deallocNodes = []
    deallocNodes.append(startLabelNode)
    lastINode = [startLabelNode]
    for var, decNode in symbolTable.dictionary.iteritems():
        if decNode.getNodeType() == ASTNodes.ARRAY_DEC:
            reg, inMem = registerDict.lookupCurrLevelOnly(var)
            deallocNode = DeallocNode(reg, lastINode)
            deallocNodes.append(deallocNode)
            lastINode = [deallocNode]
    return deallocNodes

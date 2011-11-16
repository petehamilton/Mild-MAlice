import re
import tokrules
import Node as ASTNode
import IntermediateNodes as INodes


intfmt = 'db "%ld", 10, 0'
charfmt = 'db "%c", 10, 0'
idivRegisters = ["rax", "rdx", "rcx" ]
newline = "\n"

def indent( string, indentation = "    "):
    return indentation + string

#change list of registers later
def generate( node, variables, registers, flags ):
    reg, exp = intTransExp( node, {}, 0 )
    solveDataFlow(exp)
    #return setup(variables, flags) + exp + finish()
    return None

def solveDataFlow( tempCode ):
    for row in tempCode:
        print row


def intTransExp( node, registersDict, reg ):
    if node.tokType == ASTNode.FACTOR:
        if node.children[0] == ASTNode.ID:
            return reg + 1, [INodes.MovNode(reg, registersDict[node.children[1]])]
        return reg + 1, [INodes.ImmMovNode(reg, str(node.children[1]))]
    
    if node.tokType == ASTNode.STATEMENT_LIST:
        reg, exp1 = intTransExp( node.children[0], registersDict, reg )
        reg, exp2 = intTransExp( node.children[1], registersDict, reg )
        return reg, exp1 + exp2

    if node.tokType == ASTNode.SPOKE:
        reg1, exp = intTransExp( node.children[0], registersDict, reg )
        return reg1, exp + [INodes.SpokeNode(reg)]

    #TODO MAKE SURE YOU GET REGISTERS RIGHT!
    if node.tokType == ASTNode.BINARY_OP:
        reg1, exp1 = intTransExp( node.children[1], registersDict, reg )
        reg2, exp2 = intTransExp( node.children[2], registersDict, reg1 )
        reg, exp3 = intTransBinOp( node.children[0], reg, reg1 )
        return reg, (exp1 + exp2 + exp3)

    if node.tokType == ASTNode.UNARY_OP:
        reg, exp1 = intTransExp( node.children[1], registersDict, reg )
        reg, exp2 = intTransUnOp( node.children[0], reg )
        return reg + 1, (exp1 + exp2)

    if node.tokType == ASTNode.ASSIGNMENT:
        registersDict[node.children[0]] = reg
        reg, exp = intTransExp( node.children[1], registersDict, reg )
        return reg, exp

    if node.tokType == ASTNode.DECLARATION:
        return reg, []

# Return the assembly code needed to print the value in the given register to 
# the console.
def intAssemblyForOutput(register):
    return register + 1, [ ["mov", "rsi", register],
                         ["mov", "rdi", intfmt ],
                         ["xor", "rax", "rax"],
                         ["call", "printf"]]

# Returns the assembly code for dividing the destReg register by the reg one.
# Leaves the integer division in rax and the modulus in rcx
def iDiv( destReg, reg, resultReg ):
    registersToPreserve = list( set(idivRegisters) - set([destReg, reg]) )
    return  [["cmp", reg, 0],
             ["jz", os_return] +
             [["push", x] for x in registersToPreserve] +
             ["mov", "rax", destReg],
             ["mov", "rcx", reg],
             ["mov", "rdx", 0],
             ["idiv," "rcx"],
             ["mov", destReg, resultReg] +
             [["pop", x] for x in registersToPreserve]]

# Return assembly code for destReg / reg
def div( destReg, reg ):
    return iDiv( destReg, reg, "rax" )

# Return assembly code for destReg % reg
def mod( destReg, reg ):
    return iDiv( destReg, reg, "rdx" )


# Returns the assembly code needed to perform the given binary 'op' operation on 
# the two provided registers
def intTransBinOp(op, dest_reg, next_reg):
    if re.match( tokrules.t_PLUS, op ):
        return dest_reg, [INodes.AddNode(dest_reg, next_reg)]
        
    elif re.match( tokrules.t_MINUS, op ):
        return dest_reg, [INodes.SubNode(dest_reg, next_reg)]
        
    elif re.match( tokrules.t_MULTIPLY, op ):
        return dest_reg, [INodes.MulNode(dest_reg, next_reg)]
        
    elif re.match( tokrules.t_DIVIDE, op ):
        return dest_reg, [INodes.DivNode(dest_reg, next_reg)]
        
    elif re.match( tokrules.t_MOD, op ):
        return dest_reg, [INodes.ModNode(dest_reg, next_reg)]
        
    elif re.match( tokrules.t_B_OR, op ):
        return dest_reg, [INodes.OrNode(dest_reg, next_reg)]
        
    elif re.match( tokrules.t_B_XOR, op ):
        return dest_reg, [INodes.XORNode(dest_reg, next_reg)]
        
    elif re.match( tokrules.t_B_AND, op ):
        return dest_reg, [INodes.AndNode(dest_reg, next_reg)]
     

# Returns the assembly code needed to perform the given unary 'op' operation on 
# the provided register
def intTransUnOp(op, dest_reg):
    if op == "ate":
        return dest_reg, [INodes.IncNode(dest_reg)]
    elif op == "drank":
        return dest_reg, [INodes.DecNode(dest_reg)]
    elif re.match( tokrules.t_B_NOT, op ):
        return dest_reg, [INodes.NotNode(dest_reg)]

# Node types are:
# statement_list, spoke, assignment, declaration, 
# binary_op, unary_op, type, factor
def weight( node ):
    if node.tokType == ASTNode.FACTOR:
        return 1

    elif node.tokType == ASTNode.BINARY_OP:
        cost1 = max( weight(node.children[1]), weight(node.children[2]) + 1 )
        cost2 = max( weight(node.children[2]), weight(node.children[1]) + 1 )
        return min( cost1, cost2 )

    elif node.tokType == ASTNode.UNARY_OP:
        return weight(node.children[1])

    elif node.tokType == ASTNode.SPOKE:
        return weight(node.children[1])

    elif node.tokType == ASTNode.ASSIGNMENT:
        return 1

    elif node.tokType == ASTNode.STATEMENT_LIST:
        return max( weight(node.children[0]), weight(node.children[1]) )

    #is this right? Dont need to store anything in register yet
    elif node.tokType == ASTNode.DECLARATION or node.tokType == ASTNode.TYPE:
        pass

def setup(variables, flags):
    externSection = []
    dataSection = []
    variableSection = []
    globalSection = []
    textSection = []

    if ASTNode.SPOKE in flags:
        externSection.append("extern printf")
        dataSection.append("section .data")
        for printType in flags[ASTNode.SPOKE]:
            if printType == ASTNode.LETTER:     
                dataSection.append(ident("charfmt: ") + charfmt)
            elif printType == ASTNode.NUMBER:
                dataSection.append(indent("intfmt: ") + intfmt)

    globalSection.extend(["LINUX        equ     80H      ; interupt number for entering Linux kernel",
                          "EXIT         equ     60       ; Linux system call 1 i.e. exit ()"])
    
    textSection.extend(["segment .text", 
                        indent("global	main"),
                        newline,
                        "main:"])
    
    if len(variables) != 0:
        variableSection.append("section .bss")
        variableSection.extend([ indent("%s: resq 1" % x) for x in variables])

    return ( externSection   +
             [newline]       +
             globalSection   +
             [newline]       +
             dataSection     +
             [newline]       +
             variableSection +
             [newline]       +
             textSection
           )

def finish():
    return ([indent("call os_return		; return to operating system")] +
            [newline] +
            ["os_return:"] +
            [indent("mov  rax, EXIT		; Linux system call 1 i.e. exit ()")] +
            [indent("mov  rdi, 0		; Error code 0 i.e. no errors")] +
            [indent("int  LINUX		; Interrupt Linux kernel")])





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
    reg, exp, parents = intTransExp( node, {}, 0, [] )
    solveDataFlow(exp, reg, registers)
    #return setup(variables, flags) + exp + finish()
    return None

#TODO POSSIBLY MAKE THIS A FUNCTION LATER
def uses(node):
    return node.uses()
    
def defs(node):
    return node.alteredRegisters()
    
def succs(node):
    return None

# Reversing intermediateNodes for bottom up parsing. See slide 32 ch 6 PK Notes
def solveDataFlow( intermediateNodes, maxTempReg, availableRegisters):
    liveIn = {}
    liveOut = {}
    intermediateNodes.reverse()
    
    #TODO MAP THIS?
    for node in intermediateNodes:
        liveIn[node] = set()
        liveOut[node] = set()
        
    while True:
        
        previousLiveIn = liveIn
        previousLiveOut = liveOut
        
        for n in intermediateNodes:
            liveIn[n]  = set(uses(n)) | (set(liveOut[n]) - set(defs(n)))
            
            #TODO: Map this with lambda
            for p in n.parents:
                liveOut[p] = liveIn[n]
            
        if liveIn == previousLiveIn and liveOut == previousLiveOut:
            break
    
    print "Live In"
    print "#######################################"
    for k, v in liveIn.items():
        print k.generateCode(), "\t: ", v
        pass
    
    print
    print "Live Out"
    print "#######################################"
    for k, v in liveOut.items():
        print k.generateCode(), "\t: ", v
        pass
    
    #Generate interference graph
    interferenceGraph = {}
    for t in range(maxTempReg):
        interferenceGraph[t] = set()
        for n in intermediateNodes:
            if t in liveOut[n]:
                interferenceGraph[t] = interferenceGraph[t] | set(liveOut[n])
    
    print
    print "Interference Graph"
    print "#######################################"
    for k, v in interferenceGraph.items():
        print k, "\t:", v

    colors = {}
    #TODO, MAP ME
    for k, v in interferenceGraph.items():
        colors[k] = None
    for k, v in interferenceGraph.items():
        colors[k] = getColorForReg(k, maxTempReg, interferenceGraph, colors)
    
    print
    print "Graph Colouring"
    print "#######################################"
    for k, v in colors.items():
        print "T" + str(k), "\t:", v
    
    registerMap = {}
    for k, v in colors.items():
        registerMap[k] = availableRegisters[v]

    print
    print "Register Mapping"
    print "#######################################"
    for k, v in colors.items():
        print "T" + str(k), "\t:", registerMap[v]
    
    print
    print "Generating Final Code"
    print "#######################################"
    intermediateNodes.reverse()

    for n in intermediateNodes:
        print n.generateCode(registerMap)

def getColorForReg(tReg, maxColor, interferenceGraph, registerColors):
    for color in range(maxColor):
        if promising(tReg, color, interferenceGraph, registerColors):
            return color

def promising(tReg, color, interferenceGraph, registerColors):
    for reg in interferenceGraph[tReg]:
        colorOfNeighbourReg = registerColors[reg]
        if colorOfNeighbourReg == color:
            return False
    return True
    
#EXPLAIN PARENTS WILL BE MORE THAN ONE LATER. WRITING REUSABLE CODE
# Returns take format (nextAvailableRegister, instructions, callees children)
def intTransExp( node, registersDict, reg, parents ):
    if node.tokType == ASTNode.FACTOR:
        if node.children[0] == ASTNode.ID:
            intermediateNode = INodes.MovNode(reg, registersDict[node.children[1]], parents)
        else:
            intermediateNode = INodes.ImmMovNode(reg, str(node.children[1]), parents)    
        return reg + 1, [intermediateNode], [intermediateNode]
    
    #TODO DOUBLE CHECK CHILDREN
    if node.tokType == ASTNode.STATEMENT_LIST:
        reg, exp1, parents = intTransExp( node.children[0], registersDict, reg, parents )
        reg, exp2, parents = intTransExp( node.children[1], registersDict, reg, parents )
        return reg, exp1 + exp2, parents

#    if node.tokType == ASTNode.IF_STATMENT:
        #reg, exp, node = create if node
        #reg, exp, node2 = create then node = create node ( node )
        #reg, exp, node3 = create else node ( node )
        # return [ node2, node3 ]
        

    if node.tokType == ASTNode.SPOKE:
        reg1, exp, parents = intTransExp( node.children[0], registersDict, reg, parents )
        intermediateNode = INodes.SpokeNode(reg, parents)
        return reg1, exp + [intermediateNode], [intermediateNode]

    #TODO MAKE SURE YOU GET REGISTERS RIGHT!
    if node.tokType == ASTNode.BINARY_OP:
        reg1, exp1, parents = intTransExp( node.children[1], registersDict, reg, parents)
        reg2, exp2, parents = intTransExp( node.children[2], registersDict, reg1, parents )
        reg, exp3, parents = intTransBinOp( node.children[0], reg, reg1, parents )
        reg = reg + (reg2 - reg1)
        return reg + 1, (exp1 + exp2 + exp3), parents

    if node.tokType == ASTNode.UNARY_OP:
        reg, exp1, parents = intTransExp( node.children[1], registersDict, reg, parents )
        reg, exp2, parents = intTransUnOp( node.children[0], reg, parents )
        return reg + 1, (exp1 + exp2), parents

    if node.tokType == ASTNode.ASSIGNMENT:
        registersDict[node.children[0]] = reg
        reg, exp, parents = intTransExp( node.children[1], registersDict, reg, parents)
        return reg, exp, parents

    if node.tokType == ASTNode.DECLARATION:
        return reg, [], parents

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
def intTransBinOp(op, dest_reg, next_reg, parents):
    if re.match( tokrules.t_PLUS, op ):
        intermediateNode = INodes.AddNode(dest_reg, next_reg, parents)
        
    elif re.match( tokrules.t_MINUS, op ):
        intermediateNode = INodes.SubNode(dest_reg, next_reg, parents)
        
    elif re.match( tokrules.t_MULTIPLY, op ):
        intermediateNode = INodes.MulNode(dest_reg, next_reg, parents)
        
    elif re.match( tokrules.t_DIVIDE, op ):
        intermediateNode = INodes.DivNode(dest_reg, next_reg, parents)
        
    elif re.match( tokrules.t_MOD, op ):
        intermediateNode = INodes.ModNode(dest_reg, next_reg, parents)
        
    elif re.match( tokrules.t_B_OR, op ):
        intermediateNode = INodes.OrNode(dest_reg, next_reg, parents)
        
    elif re.match( tokrules.t_B_XOR, op ):
        intermediateNode = INodes.XORNode(dest_reg, next_reg, parents)
        
    elif re.match( tokrules.t_B_AND, op ):
        intermediateNode = INodes.AndNode(dest_reg, next_reg, parents)
    return dest_reg, [intermediateNode], [intermediateNode]
     

# Returns the assembly code needed to perform the given unary 'op' operation on 
# the provided register
def intTransUnOp(op, dest_reg, parents):
    if op == "ate":
        intermediateNode = INodes.IncNode(dest_reg, parents)
        
    elif op == "drank":
        intermediateNode = INodes.DecNode(dest_reg, parents)
        
    elif re.match( tokrules.t_B_NOT, op ):
        intermediateNode = INodes.NotNode(dest_reg, parents)
        
    return dest_reg, [intermediateNode], [intermediateNode]

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





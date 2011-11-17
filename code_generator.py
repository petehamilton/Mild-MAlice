import re
import tokrules
import Node as ASTNode
import IntermediateNodes as INodes
from collections import defaultdict

class CodeGenerator(object):
    intfmt = 'db "%ld", 10, 0'
    charfmt = 'db "%c", 10, 0'
    idivRegisters = ["rax", "rdx", "rcx" ]
    newline = "\n"
    
    def __init__(self, symbolTable):
        self.symbolTable = symbolTable

    def indent(self, string, indentation = "    "):
        return indentation + string

    #change list of registers later
    def generate(self, node, registers, flags):
        # solveDataFlow takes a list of intermediate nodes, the last temporary
        # register number and a list of available registers.
        # It returns an dictionary of register numbers to actual Intel registers.
        def solveDataFlow(intermediateNodes, lastReg, availableRegisters):
            def uses(node):
                return node.uses()
            
            def defs(node):
                return node.alteredRegisters()
            
            # Parses the list of intermediate notes to calculate their live
            # in and live out.
            # Returns a dictionary containing key value pairs of node to a set
            # of integer register values.
            def calculateLiveRange( intermediateNodes ):
                liveIn = defaultdict(set)
                liveOut = defaultdict(set)
                while True:
                    previousLiveIn = liveIn
                    previousLiveOut = liveOut
                    for n in intermediateNodes:
                        liveIn[n]  = set(uses(n)) | (set(liveOut[n]) - set(defs(n)))
                        #TODO: Map this with lambda - EDIT - cant have assignment in Lambda :(
                        for p in n.parents:
                            liveOut[p] = liveIn[n]
                    if liveIn == previousLiveIn and liveOut == previousLiveOut:
                        break
                return liveOut
             
             # Performs a graph coloring algorithm to work out which nodes
             # can share registers.
            def calculateRealRegisters( liveOut, lastReg ):
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
                 
                interferenceGraph = {}
                for t in range(lastReg):
                    interferenceGraph[t] = set()
                    for n in intermediateNodes:
                        if t in liveOut[n]:
                            interferenceGraph[t] = interferenceGraph[t] | set(liveOut[n])

                colors = {}
                for k in interferenceGraph.keys():
                    colors[k] = None
                    
                for k, v in interferenceGraph.items():
                    colors[k] = getColorForReg(k, lastReg, interferenceGraph, colors)
            
                registerMap = {}
                for k, v in colors.items():
                    registerMap[k] = availableRegisters[v]
                
                return registerMap
            
            
            intermediateNodes.reverse()
            liveOut = calculateLiveRange(intermediateNodes)
            registerMap = calculateRealRegisters( liveOut, lastReg )
            intermediateNodes.reverse() #Put nodes back in right order.
            return registerMap
            
        def generateFinalCode(intermediateNodes, registerMap):
            code = []
            for n in intermediateNodes:
                code.extend(n.generateCode(registerMap))
            return code
            
            
        reg, intermediateNodes, parents = self.intTransExp( node, {}, 0, [] )
        for node in intermediateNodes:
            print node.generateIntermediateCode()

        registerMap = solveDataFlow(intermediateNodes, reg, registers)
        finalCode = generateFinalCode( intermediateNodes, registerMap )
        return self.setup(flags) + finalCode + self.finish()
    
    #EXPLAIN PARENTS WILL BE MORE THAN ONE LATER. WRITING REUSABLE CODE
    # Returns take format (nextAvailableRegister, instructions, callees children)
    def intTransExp(self, node, registersDict, reg, parents ):
        if node.tokType == ASTNode.FACTOR:
            if node.children[0] == ASTNode.ID:
                intermediateNode = INodes.MovNode(reg, registersDict[node.children[1]], parents)
            else:
                intermediateNode = INodes.ImmMovNode(reg, str(node.children[1]), parents)    
            return reg + 1, [intermediateNode], [intermediateNode]
    
        #TODO DOUBLE CHECK CHILDREN
        if node.tokType == ASTNode.STATEMENT_LIST:
            reg, exp1, parents = self.intTransExp( node.children[0], registersDict, reg, parents )
            reg, exp2, parents = self.intTransExp( node.children[1], registersDict, reg, parents )
            return reg, exp1 + exp2, parents

        if node.tokType == ASTNode.SPOKE:
            reg1, exp, parents = self.intTransExp( node.children[0], registersDict, reg, parents )
        
            # spokeChild = node.children[0]
            # if spokeChild.children[0] == node.ID:
            #     (idType, lineNo, assigned) = symbolTable[spokeChild.children[1]]
            # else:
            #     idType = spokeChild.children[0]
            # 
            # if idType == n.NUMBER:
            #     format = "intfmt"
            # elif idType == n.LETTER:
            #     format = "charfmt"
            #TODO: CHANGE ME!!!
            format = "intfmt"
            
            intermediateNode = INodes.SpokeNode(reg, parents, format)
            return reg1, exp + [intermediateNode], [intermediateNode]

        #TODO MAKE SURE YOU GET REGISTERS RIGHT!
        if node.tokType == ASTNode.BINARY_OP:
            reg1, exp1, parents = self.intTransExp( node.children[1], registersDict, reg, parents)
            reg2, exp2, parents = self.intTransExp( node.children[2], registersDict, reg1, parents )
            reg, exp3, parents = self.intTransBinOp( node.children[0], reg, reg1, parents )
            reg = reg + (reg2 - reg1)
            return reg + 1, (exp1 + exp2 + exp3), parents
        
        # return reg not reg + 1 as we know unary op won't create any new registers
        if node.tokType == ASTNode.UNARY_OP:
            reg1, exp1, parents = self.intTransExp( node.children[1], registersDict, reg, parents )
            reg, exp2, parents = self.intTransUnOp( node.children[0], reg, parents )
            return reg, (exp1 + exp2), parents

        if node.tokType == ASTNode.ASSIGNMENT:
            registersDict[node.children[0]] = reg
            reg, exp, parents = self.intTransExp( node.children[1], registersDict, reg, parents)
            return reg, exp, parents

        if node.tokType == ASTNode.DECLARATION:
            return reg, [], parents

    # Returns the assembly code needed to perform the given binary 'op' operation on 
    # the two provided registers
    def intTransBinOp(self, op, dest_reg, next_reg, parents):
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
    def intTransUnOp(self, op, dest_reg, parents):
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
    def weight(self, node ):
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

    def setup(self, flags):
        externSection = []
        dataSection = []
        globalSection = []
        textSection = []

        if ASTNode.SPOKE in flags:
            externSection.append("extern printf")
            dataSection.append("section .data")
            for printType in flags[ASTNode.SPOKE]:
                if printType == ASTNode.LETTER:     
                    dataSection.append(ident("charfmt: ") + self.charfmt)
                elif printType == ASTNode.NUMBER:
                    dataSection.append(self.indent("intfmt: ") + self.intfmt)

        globalSection.extend(["LINUX        equ     80H      ; interupt number for entering Linux kernel",
                              "EXIT         equ     60       ; Linux system call 1 i.e. exit ()"])
    
        textSection.extend(["segment .text", 
                            self.indent("global	main"),
                            self.newline,
                            "main:"])

        return ( externSection   +
                 [self.newline]  +
                 globalSection   +
                 [self.newline]  +
                 dataSection     +
                 [self.newline]  +
                 textSection
               )

    def finish(self):
        return ([self.indent("call os_return		; return to operating system")] +
                [self.newline] +
                ["os_return:"] +
                [self.indent("mov  rax, EXIT		; Linux system call 1 i.e. exit ()")] +
                [self.indent("mov  rdi, 0		; Error code 0 i.e. no errors")] +
                [self.indent("int  LINUX		; Interrupt Linux kernel")])

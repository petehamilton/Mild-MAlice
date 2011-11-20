import re
import tokrules
import Node as ASTNode
import IntermediateNodes as INodes
from collections import defaultdict

class CodeGenerator(object):
    intfmt = 'db "%ld", 10, 0'
    charfmt = 'db "%c", 10, 0'
    newline = "\n"
    
    def __init__(self, symbolTable, registers, flags):
        self.symbolTable = symbolTable
        self.availableRegisters = registers
        self.flags = flags
        
    def indent(self, string, indentation = "    "):
        return indentation + string

    def generate(self, node):
        # solveDataFlow takes a list of intermediate nodes, the last temporary
        # register number and a list of available registers.
        # It returns an dictionary of register numbers to actual Intel registers.
        def solveDataFlow(intermediateNodes, lastReg):
            def uses(node):
                return node.uses()
            
            def defs(node):
                return node.alteredRegisters()
            
            # Parses the list of intermediate notes to calculate their live
            # in and live out.
            # Returns a dictionary containing key value pairs of node to a set
            # of integer register values.
            # TODO: Should we make liveIn and liveRange variables in IntermediateNodes?
            def calculateLiveRange( intermediateNodes ):
                liveIn = defaultdict(set)
                liveOut = defaultdict(set)
                while True:
                    previousLiveIn = liveIn
                    previousLiveOut = liveOut
                    for n in intermediateNodes:
                        liveIn[n]  = set(uses(n)) | (set(liveOut[n]) - set(defs(n)))
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
                
                def calculateInterferenceGraph(liveOut):
                    interferenceGraph = {}
                    for t in range(lastReg):
                        interferenceGraph[t] = set()
                        for n in intermediateNodes:
                            if t in liveOut[n]:
                                interferenceGraph[t] = interferenceGraph[t] | set(liveOut[n])
                    return interferenceGraph
                
                def calculateColors(interferenceGraph, lastReg):
                    colors = {}
                    for k in interferenceGraph.keys():
                        colors[k] = None
                        
                    for k, v in interferenceGraph.items():
                        colors[k] = getColorForReg(k, lastReg, interferenceGraph, colors)
                    return colors
                    
                def mapToRegisters(colors):
                    registerMap = {}
                    overflowValues = []
                    for k, v in colors.items():
                        if v >= len(self.availableRegisters):
                            overflowValues.append("overflow%d"%k)
                            registerMap[k] = "[overflow%d]"%k
                        else:
                            registerMap[k] = self.availableRegisters[v]
                    
                    return registerMap, overflowValues
                
                interferenceGraph = calculateInterferenceGraph(liveOut)
                colors = calculateColors(interferenceGraph, lastReg)
                return mapToRegisters( colors )
                
                
            # Modifies intermediateNodes which is passed in by reference
            # TODO: Is this Pythonesque?
            def removeUnusedInstructions(intermediateNodes, liveOut):
                for node in intermediateNodes:
                    used = False
                    #TODO: Is there a nicer way to do this isinstance?
                    for node1, liveOutRegs in liveOut.items():
                        used |= len(set(defs(node)) & liveOutRegs) > 0
                        used |= isinstance(node, INodes.SpokeNode)
                    if not used:
                        intermediateNodes.remove(node)
                        
                        
            intermediateNodes.reverse()
            liveOut = calculateLiveRange(intermediateNodes)
            removeUnusedInstructions(intermediateNodes, liveOut)
            registerMap, overflowValues = calculateRealRegisters( liveOut, lastReg )
            intermediateNodes.reverse() #Put nodes back in right order.
            return registerMap, overflowValues
            
        def generateFinalCode(intermediateNodes, registerMap):
            code = []
            for n in intermediateNodes:
                code.extend(n.generateCode(registerMap))
            return code
            
            
        reg, intermediateNodes, parents = self.transExp( node, {}, 0, [] )
        registerMap, overflowValues = solveDataFlow(intermediateNodes, reg)
        finalCode = generateFinalCode( intermediateNodes, registerMap )
        return self.setup(overflowValues) + finalCode + self.finish()
    
    #EXPLAIN PARENTS WILL BE MORE THAN ONE LATER. WRITING REUSABLE CODE
    # Returns take format (nextAvailableRegister, instructions, callees children)
    def transExp(self, node, registersDict, reg, parents ):
        if node.tokType == ASTNode.FACTOR:
            if node.children[0] == ASTNode.ID:
                intermediateNode = INodes.MovNode(reg, registersDict[node.children[1]], parents)
            else:
                intermediateNode = INodes.ImmMovNode(reg, str(node.children[1]), parents)    
            return reg + 1, [intermediateNode], [intermediateNode]
    
        #TODO DOUBLE CHECK CHILDREN
        if node.tokType == ASTNode.STATEMENT_LIST:
            reg, exp1, parents = self.transExp( node.children[0], registersDict, reg, parents )
            reg, exp2, parents = self.transExp( node.children[1], registersDict, reg, parents )
            return reg, exp1 + exp2, parents

        if node.tokType == ASTNode.SPOKE:
            reg1, exp, parents = self.transExp( node.children[0], registersDict, reg, parents )
            
            spokeChild = node.children[0]
            
            if spokeChild.children[0] == ASTNode.ID:
                (idType, lineNo, assigned) = self.symbolTable[spokeChild.children[1]]
            else:
                idType = spokeChild.children[0]
            
            if idType == ASTNode.NUMBER:
                format = "intfmt"
            elif idType == ASTNode.LETTER:
                format = "charfmt"
            
            intermediateNode = INodes.SpokeNode(reg, parents, format)
            return reg1, exp + [intermediateNode], [intermediateNode]

        #TODO MAKE SURE YOU GET REGISTERS RIGHT!
        if node.tokType == ASTNode.BINARY_OP:
            reg1, exp1, parents = self.transExp( node.children[1], registersDict, reg, parents)
            reg2, exp2, parents = self.transExp( node.children[2], registersDict, reg1, parents )
            reg, exp3, parents = self.transBinOp( node.children[0], reg, reg1, parents )
            reg = reg + (reg2 - reg1)
            return reg + 1, (exp1 + exp2 + exp3), parents
        
        if node.tokType == ASTNode.UNARY_OP:
            #reg1, exp1, parents = self.transExp( node.children[1], registersDict, reg, parents )
            reg, exp2, parents = self.transUnOp( node.children[0], reg, node.children[1], registersDict, parents )
            return reg, exp2, parents

        if node.tokType == ASTNode.ASSIGNMENT:
            assignmentReg = reg
            reg, exp, parents = self.transExp( node.children[1], registersDict, reg, parents)
            registersDict[node.children[0]] = assignmentReg
            return reg, exp, parents

        if node.tokType == ASTNode.DECLARATION:
            return reg, [], parents

    # Returns the assembly code needed to perform the given binary 'op' operation on 
    # the two provided registers
    def transBinOp(self, op, destReg, nextReg, parents):
        if re.match( tokrules.t_PLUS, op ):
            intermediateNode = INodes.AddNode(destReg, nextReg, parents)
        
        elif re.match( tokrules.t_MINUS, op ):
            intermediateNode = INodes.SubNode(destReg, nextReg, parents)
        
        elif re.match( tokrules.t_MULTIPLY, op ):
            intermediateNode = INodes.MulNode(destReg, nextReg, parents)
        
        elif re.match( tokrules.t_DIVIDE, op ):
            intermediateNode = INodes.DivNode(destReg, nextReg, parents)
        
        elif re.match( tokrules.t_MOD, op ):
            intermediateNode = INodes.ModNode(destReg, nextReg, parents)
        
        elif re.match( tokrules.t_B_OR, op ):
            intermediateNode = INodes.OrNode(destReg, nextReg, parents)
        
        elif re.match( tokrules.t_B_XOR, op ):
            intermediateNode = INodes.XORNode(destReg, nextReg, parents)
        
        elif re.match( tokrules.t_B_AND, op ):
            intermediateNode = INodes.AndNode(destReg, nextReg, parents)
        return destReg, [intermediateNode], [intermediateNode]
   

    # Returns the assembly code needed to perform the given unary 'op' operation on 
    # the provided register
    def transUnOp(self, op, destReg, node, registersDict, parents):
        if re.match( "ate", op ):
            intermediateNode = [INodes.IncNode(registersDict[node.children[1]], parents)]
            parents = intermediateNode
        
        elif re.match( "drank", op ):
            intermediateNode = [INodes.DecNode(registersDict[node.children[1]], parents)]
            parents = intermediateNode
            
        elif re.match( tokrules.t_B_NOT, op ):
            reg1, exp, parents = self.transExp( node, registersDict, destReg, parents )
            intermediateNode = [INodes.NotNode(destReg, parents)]
            parents = intermediateNode
            intermediateNode = exp + intermediateNode
            
        return destReg, intermediateNode, parents

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

        elif node.tokType == ASTNode.DECLARATION or node.tokType == ASTNode.TYPE:
            pass

    def setup(self, overflowValues):
        externSection = []
        dataSection = []
        bssSection = []
        globalSection = []
        textSection = []
        
        if ASTNode.SPOKE in self.flags:
            externSection.append("extern printf")
            dataSection.append("section .data")
            for printType in self.flags[ASTNode.SPOKE]:
                if printType == ASTNode.LETTER:     
                    dataSection.append(self.indent("charfmt: ") + self.charfmt)
                elif printType == ASTNode.NUMBER:
                    dataSection.append(self.indent("intfmt: ") + self.intfmt)

        globalSection.extend(["LINUX        equ     80H      ; interupt number for entering Linux kernel",
                              "EXIT         equ     60       ; Linux system call 1 i.e. exit ()"])

        if overflowValues:
            bssSection.append("section .bss")
            bssSection.extend([ self.indent("%s: resq 1") %name for name in overflowValues])
    
        textSection.extend(["segment .text", 
                            self.indent("global	main"),
                            self.newline,
                            "main:"])

        return ( externSection   +
                 [self.newline]  +
                 globalSection   +
                 [self.newline]  +
                 bssSection      +
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

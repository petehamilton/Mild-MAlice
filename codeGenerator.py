import re
import tokRules
import ASTNodes
import intermediateNodes as INodes
from collections import defaultdict

class CodeGenerator(object):
    intfmt = 'db "%ld", 10, 0'
    charfmt = 'db "%c", 10, 0'
    newline = "\n"
    
    def __init__(self, symbolTable, registers, flags):
        self.symbolTable = symbolTable
        self.availableRegisters = registers
        self.flags = flags
     
    # This function indents a string with four spaces. It is used in our assembly
    # code generation to format the .asm file.
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
            def calculateRealRegisters(liveOut, lastReg):
                
                # Returns the first available colouring for the given temporary 
                # register depending on it's neighbours and whether they can 
                # potentially share registers to optimise code
                def getColorForReg(tReg, maxColor, interferenceGraph, registerColors):
                    if len(interferenceGraph[tReg]) == 0:
                        usedRegisters = [k for k, v in registerColors.items() if v != None]
                        unusedSet = (set(range(maxColor)) - set(usedRegisters))
                        if unusedSet:
                            return unusedSet.pop(), maxColor
                        else:
                            return maxColor, maxColor + 1
                    
                    for color in range(maxColor):
                        if promising(tReg, color, interferenceGraph, registerColors):
                            return color, maxColor
                
                # Returns whether the given color can be applied to the given 
                # temporary register. True when none of the registers it 
                # interferes with have already been assigned the color
                def promising(tReg, color, interferenceGraph, registerColors):
                    for reg in interferenceGraph[tReg]:
                        colorOfNeighbourReg = registerColors[reg]
                        if colorOfNeighbourReg == color:
                            return False
                    return True
                
                # Calculates which registers have live ranges which overlap. 
                # i.e. is it connected to any of the other registers.
                def calculateInterferenceGraph(liveOut, lastReg):
                    interferenceGraph = {}
                    for tReg in range(lastReg + 1):
                        interferenceGraph[tReg] = set()
                        for n in intermediateNodes:
                            if tReg in liveOut[n]:
                                interferenceGraph[tReg] = interferenceGraph[tReg] | set(liveOut[n])
                    return interferenceGraph
                
                # Works out which temporary registers can share real registers 
                # by using graph colouring. Returns a dictionary of the colours 
                # and a corresponding index to be used with a register/memory 
                # location mapping
                def calculateColors(interferenceGraph, lastReg):
                    colors = {}
                    for k in interferenceGraph.keys():
                        colors[k] = None
                        
                    for k in interferenceGraph.keys():
                        colors[k], lastReg = getColorForReg(k, lastReg, interferenceGraph, colors)
                    return colors
                    
                # This function takes a colors dictionary of format { tempReg : finalRegisterIndex }
                # it returns a register map of  { tempReg : realRegister } and a list of overflowed registers
                # to be used in the setup.
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
                
                interferenceGraph = calculateInterferenceGraph(liveOut, lastReg)
                colors = calculateColors(interferenceGraph, lastReg)
                return mapToRegisters( colors )
                
            intermediateNodes.reverse()
            liveOut = calculateLiveRange(intermediateNodes)
            registerMap, overflowValues = calculateRealRegisters( liveOut, lastReg )
            intermediateNodes.reverse() #Put nodes back in right order.
            return registerMap, overflowValues
            
        def generateFinalCode(intermediateNodes, registerMap):
            code = []
            for n in intermediateNodes:
                code.extend(n.generateCode(registerMap))
            return code
        
        def generateFunctionCode(functionNode, registerMap):
            return functionNode.generateCode(registerMap)
            
            
        functionCode = []
        if ASTNodes.FUNCTION in self.flags:
            reg, intermediateNodes, functionNodes, parents = node.translate( {}, 0, [] )
            for function in functionNodes:
                fRegMap, fOverFlowValues = solveDataFlow( function.body, max(function.uses()) )
                functionCode.extend(generateFunctionCode(function, fRegMap))
        else:
            reg, intermediateNodes, parents = node.translate( {}, 0, [] )

        registerMap, overflowValues = solveDataFlow(intermediateNodes, reg)
        finalCode = generateFinalCode( intermediateNodes, registerMap )
        return self.setup(overflowValues) + finalCode + self.finish() + functionCode

    # This function generates the set up code needed at the top of an assembly file.
    def setup(self, overflowValues):
        externSection = []
        dataSection = []
        bssSection = []
        globalSection = []
        textSection = []
        
        if ASTNodes.SPOKE in self.flags:
            externSection.append("extern printf")
            dataSection.append("section .data")
            for printType in self.flags[ASTNodes.SPOKE]:
                if printType == ASTNodes.LETTER:     
                    dataSection.append(self.indent("charfmt: ") + self.charfmt)
                elif printType == ASTNodes.NUMBER:
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

    # This function generates the code that remains the same for each assembly file at the bottom
    # of the file.
    def finish(self):
        return ([self.indent("call os_return		; return to operating system")] +
                [self.newline] +
                ["os_return:"] +
                [self.indent("mov  rax, EXIT		; Linux system call 1 i.e. exit ()")] +
                [self.indent("mov  rdi, 0		; Error code 0 i.e. no errors")] +
                [self.indent("int  LINUX		; Interrupt Linux kernel")])

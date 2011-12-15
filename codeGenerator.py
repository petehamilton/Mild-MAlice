import re
import tokRules
import labels
import ASTNodes
import intermediateNodes as INodes
from RegisterMap import RegisterMap
from collections import defaultdict

class CodeGenerator(object):
    output_int_fmt = 'outputintfmt: db "%ld", 0'
    output_char_fmt = 'outputcharfmt: db "%c", 0'
    output_string_fmt = 'outputstringfmt: db "%s", 0'
    int_message = 'intfmt_message: db "Please enter an integer and press enter: ", 0'
    char_message = 'charfmt_message: db "Please enter a character and press enter: ", 0'
    input_int_fmt = 'inputintfmt: db "%ld", 0'
    input_char_fmt = 'inputcharfmt: db "%c", 0'
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
                    previousLiveIn = liveIn.copy()
                    previousLiveOut = liveOut.copy()
                    for n in intermediateNodes:
                        liveIn[n]  = set(uses(n)) | ((liveOut[n].copy()) - set(defs(n)))
                        for p in n.parents:
                            liveOut[p] = liveOut[p] | liveIn[n].copy()
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
                    registerMap = RegisterMap()
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
    
            #print "***************************************"
            #for n in intermediateNodes:
            #    print n, n.parents, liveOut[n]
            #print "***************************************"

            # Code which prints out the intermediate nodes nd their parents, each
            # with a unique number
            # i = 0
            # nodeDict = {}
            # for n in intermediateNodes:
            #     if n not in nodeDict:
            #         nodeDict[n] = "%d (%s)"%(i, n.__class__.__name__)
            #         i += 1
            # 
            # for i in intermediateNodes:
            #     print nodeDict[i], [nodeDict[n] for n in i.parents]
            # End of parent inspection code
            
            # Uncomment to generate temporary code, 
            # same assembly but uses T0,T1,T2 etc
            # Start of Temp Code Outputter
            # for k, v in registerMap.iteritems():
            #     registerMap[k] = "T%d"%k
            # End of Temp Code Outputter
            
            return registerMap, overflowValues
            
        def generateFinalCode(intermediateNodes, registerMap):
            code = []
            for n in intermediateNodes:
                code.extend(n.generateCode(registerMap))
            return code
        
        def generateFunctionCode(functionNode, registerMap):
            return functionNode.generateCode(registerMap)
            
        functionCode = []
        functionOverflow = []
        if len(self.flags[ASTNodes.FUNCTION]):
            reg, intermediateNodes, functionNodes, parents = node.translate( {}, 0, [] )
            for function in functionNodes:
                lastReg = max(function.uses()) + 1 
                fRegMap, fOverFlowValues = solveDataFlow( function.body, lastReg )
                functionCode.extend(generateFunctionCode(function, fRegMap))
                functionOverflow.extend(fOverFlowValues)
        else:
            reg, intermediateNodes, parents = node.translate( {}, 0, [] )
        registerMap, overflowValues = solveDataFlow(intermediateNodes, reg)
        finalCode = generateFinalCode( intermediateNodes, registerMap )
        return self.setup(overflowValues + functionOverflow) + map(self.indent, finalCode) + self.finish(self.flags) + functionCode

    # This function generates the set up code needed at the top of an assembly file.
    def setup(self, overflowValues):
        externSection = []
        dataSection = []
        bssSection = []
        globalSection = []
        textSection = []
        
        # Hashing values for efficiency to check they aren't redefined.
        inDataSection = {}        
        if (ASTNodes.SPOKE in self.flags or ASTNodes.INPUT in self.flags):
            externSection.extend(["extern printf", "extern fflush"])
        
        # if (ASTNodes.INPUT in self.flags or ASTNodes.FUNCTION in self.flags):
        #             bssSection.append("section .bss")
        
        if (ASTNodes.SPOKE in self.flags or ASTNodes.INPUT in self.flags or ASTNodes.SENTENCE in self.flags or ASTNodes.BINARY_OP in self.flags):
            dataSection.append("section .data")
        
        
        if ASTNodes.BINARY_OP in self.flags:
            for label in self.flags[ASTNodes.BINARY_OP]:
                name, message = labels.overFlowMessageDict[label]
                inDataSection[label] = True
                dataSection.append(self.indent('%s: db "%s", 0' %(name, message)))
            
        if ASTNodes.SPOKE in self.flags:
            for printType in self.flags[ASTNodes.SPOKE]:
                if printType == ASTNodes.LETTER:     
                    dataSection.append(self.indent(self.output_char_fmt))
                    inDataSection[self.output_char_fmt] = True
                elif printType == ASTNodes.NUMBER:
                    dataSection.append(self.indent(self.output_int_fmt))
                    inDataSection[self.output_int_fmt] = True
                elif printType == ASTNodes.SENTENCE:
                    dataSection.append(self.indent(self.output_string_fmt))
                    inDataSection[self.output_string_fmt] = True
        
        if ASTNodes.INPUT in self.flags:
            externSection.append("extern scanf")
            bssSection.append("section .bss")
            for printType in self.flags[ASTNodes.INPUT]:
                if printType == ASTNodes.LETTER:
                    if self.output_int_fmt not in inDataSection: 
                        dataSection.append(self.indent(self.output_int_fmt))
                elif printType == ASTNodes.NUMBER:
                    if self.output_char_fmt not in inDataSection: 
                        dataSection.append(self.indent(self.output_char_fmt))
            if self.output_string_fmt not in inDataSection:
                dataSection.append(self.indent(self.output_string_fmt))
            for printType in self.flags[ASTNodes.INPUT]:
                if printType == ASTNodes.LETTER:     
                    dataSection.append(self.indent(self.input_char_fmt))
                    dataSection.append(self.indent(self.char_message))
                    bssSection.append("charinput resq 1")
                elif printType == ASTNodes.NUMBER:
                    dataSection.append(self.indent(self.input_int_fmt))
                    dataSection.append(self.indent(self.int_message))
                    bssSection.append("intinput resq 1")
             
        if ASTNodes.SENTENCE in self.flags:
            for memoryLocation, sentence in self.flags[ASTNodes.SENTENCE]:
                dataSection.append(self.indent("%s: db %s, 10, 0" %(memoryLocation, sentence)))

        
        # if ASTNodes.FUNCTION in self.flags:
        #            maxReferences = max(map(lambda (x,y):y, self.flags[ASTNodes.FUNCTION]))
        #            # add one because maxReferences is the maximum argument position from 0.
        #            for count in range(maxReferences + 1):
        #                bssSection.append("reference%d resq 1" %(count))


        globalSection.extend(["LINUX        equ     80H      ; interupt number for entering Linux kernel",
                              "EXIT         equ     60       ; Linux system call 1 i.e. exit ()"])

        if overflowValues:
            if len(bssSection) == 0:
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
    def finish(self, flags):
        finishLine = [self.indent("jmp %s" %labels.deallocationLabel)]
        runTimeErrors = []
        if ASTNodes.BINARY_OP in self.flags:
            pushRegs = ['rsi', 'rdi', 'r8', 'r9', 'r10']
            popRegs = pushRegs[0:]
            popRegs.reverse()
            for label in self.flags[ASTNodes.BINARY_OP]:
                name, message = labels.overFlowMessageDict[label]
                runTimeErrors.append("%s:"%label)
                for reg in pushRegs:
                    runTimeErrors.append(self.indent("push %s" %reg))
                runTimeErrors.extend(map(self.indent, ["mov rsi, [%s]" %name,
                                      "mov rdi, outputstringfmt",
                                      "xor rax, rax",
                                      "call printf"]))
                for reg in popRegs:
                    runTimeErrors.append(self.indent("pop %s" %reg))
            
        deallocationCode = ["%s:" %labels.deallocationLabel]
        # Add deallocation code here?
        deallocationCode.extend( ([self.indent("call %s		; return to operating system"%labels.osReturnLabel)] +
                [self.newline] +
                ["%s:"%labels.osReturnLabel] +
                [self.indent("mov  rax, EXIT		; Linux system call 1 i.e. exit ()")] +
                [self.indent("mov  rdi, 0		; Error code 0 i.e. no errors")] +
                [self.indent("syscall		; Interrupt Linux kernel 64-bit")]))
                
        return finishLine + [self.newline] + runTimeErrors + [self.newline] + deallocationCode

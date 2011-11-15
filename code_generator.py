import re
import tokrules
import Node


intfmt = 'db "%ld", 10, 0'
charfmt = 'db "%c", 10, 0'
idivRegisters = ["rax", "rdx", "rcx" ]
newline = "\n"

def indent( string, indentation = "    "):
    return indentation + string

#change list of registers later
def generate( node, variables, registers, flags ):
    return setup(variables, flags) + transExp( node, registers ) + finish()

# Swaps first two elements of a list around
def swap( registers ):
    tmp = registers[0]
    registers[0] = registers[1]
    registers[1] =  tmp
    return registers

# Translate the given node to assembly code
def transExp( node, registers ):
    # cast to string incase number? 
    if node.tokType == Node.FACTOR:
        if node.children[0] == "ID":
            return [ indent("mov %s, [%s]" %( registers[0], str(node.children[1])))] 
        return [ indent("mov %s, %s" %( registers[0], str(node.children[1])))] 

    if node.tokType == Node.STATEMENT_LIST:
        return ( transExp( node.children[0], registers ) +
                 transExp( node.children[1], registers ) )

    if node.tokType == Node.SPOKE:
        return ( transExp( node.children[0], registers ) + 
                 assemblyForOutput(registers[0]) )    

    if node.tokType == Node.BINARY_OP:
        if weight( node.children[1] ) <= weight( node.children[2] ):
            return ( transExp( node.children[1], registers ) +
                     transExp( node.children[2], registers[1:] ) +
                     transBinOp( node.children[0], registers[0], registers[1] ) )
        else:
            #registers = swap(registers)
            return ( transExp( node.children[2], [registers[1]]+[registers[0]]+registers[2:] )  +
                     transExp( node.children[1], [registers[0]] + registers[2:] ) + 
                     transBinOp( node.children[0], registers[0], registers[1] ) )
    
    if node.tokType == Node.UNARY_OP:
        return ( transExp( node.children[1], registers ) + 
                 transUnOp( node.children[0], registers[0] ) )

    if node.tokType == Node.ASSIGNMENT:
        return ( transExp( node.children[1], registers ) + 
                 [indent("mov [%s], %s" %(node.children[0], registers[0]))])

    if node.tokType == Node.DECLARATION:
        return []
        
# Return the assembly code needed to print the value in the given register to 
# the console.
def assemblyForOutput(register):
    return [ indent("mov rsi, %s" % register),
             indent("mov rdi, intfmt"),
             indent("xor rax, rax"),
             indent("call printf")]

# Returns the assembly code for dividing the destReg register by the nextReg one.
# Leaves the integer division in rax and the modulus in rcx
def iDiv( destReg, nextReg, resultReg ):
    registersToPreserve = list( set(idivRegisters) - set([destReg, nextReg]) )
    return  map(indent, (["cmp %s, 0" % nextReg] +
                         ["jz os_return"] + 
                         ["push %s" % x for x in registersToPreserve] + 
                         ["mov rax, %s" % destReg] +
                         ["mov rcx, %s" % nextReg] +
                         ["mov rdx, 0"] +
                         ["idiv rcx"] +
                         ["mov %s, %s" % (destReg, resultReg)] + 
                         ["pop %s" % x for x in registersToPreserve]))

# Return assembly code for destReg / nextReg
def div( destReg, nextReg ):
    return iDiv( destReg, nextReg, "rax" )

# Return assembly code for destReg % nextReg
def mod( destReg, nextReg ):
    return iDiv( destReg, nextReg, "rdx" )

# Returns the assembly code needed to perform the given binary 'op' operation on 
# the two provided registers
def transBinOp(op, dest_reg, next_reg):
    if re.match( tokrules.t_PLUS, op ):
        return [indent("add %s, %s" % (dest_reg, next_reg))]
        
    elif re.match( tokrules.t_MINUS, op ):
        return [indent("sub %s, %s" % (dest_reg, next_reg))]
        
    elif re.match( tokrules.t_MULTIPLY, op ):
        return [indent("imul %s, %s" % (dest_reg, next_reg))]
        
    elif re.match( tokrules.t_DIVIDE, op ):
        return div( dest_reg, next_reg )
        
    elif re.match( tokrules.t_MOD, op ):
        return mod( dest_reg, next_reg )
        
    elif re.match( tokrules.t_B_OR, op ):
        return [indent("or %s, %s" % (dest_reg, next_reg))]
        
    elif re.match( tokrules.t_B_XOR, op ):
        return [indent("xor %s, %s" % (dest_reg, next_reg))]
        
    elif re.match( tokrules.t_B_AND, op ):
        return [indent("and %s, %s" % (dest_reg, next_reg))]
    
            
# Returns the assembly code needed to perform the given unary 'op' operation on 
# the provided register
def transUnOp(op, dest_reg):
    if op == "ate":
        return ["inc %s" % dest_reg]
    elif op == "drank":
        return ["dec %s" % dest_reg]
    elif re.match( tokrules.t_B_NOT, op ):
        return ["not %s" % dest_reg]

# Node types are:
# statement_list, spoke, assignment, declaration, 
# binary_op, unary_op, type, factor
def weight( node ):
    if node.tokType == Node.FACTOR:
        return 1

    elif node.tokType == Node.BINARY_OP:
        cost1 = max( weight(node.children[1]), weight(node.children[2]) + 1 )
        cost2 = max( weight(node.children[2]), weight(node.children[1]) + 1 )
        return min( cost1, cost2 )

    elif node.tokType == Node.UNARY_OP:
        return weight(node.children[1])

    elif node.tokType == Node.SPOKE:
        return weight(node.children[1])

    elif node.tokType == Node.ASSIGNMENT:
        return 1

    elif node.tokType == Node.STATEMENT_LIST:
        return max( weight(node.children[0]), weight(node.children[1]) )

    #is this right? Dont need to store anything in register yet
    elif node.tokType == Node.DECLARATION or node.tokType == Node.TYPE:
        pass

def setup(variables, flags):
    externSection = []
    dataSection = []
    variableSection = []
    globalSection = []
    textSection = []

    if Node.SPOKE in flags:
        externSection.append("extern printf")
        dataSection.append("section .data")
        for printType in flags[Node.SPOKE]:
            if printType == Node.LETTER:     
                dataSection.append(ident("charfmt: ") + charfmt)
            elif printType == Node.NUMBER:
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
            ["\n"] +
            ["os_return:"] +
            [indent("mov  rax, EXIT		; Linux system call 1 i.e. exit ()")] +
            [indent("mov  rdi, 0		; Error code 0 i.e. no errors")] +
            [indent("int  LINUX		; Interrupt Linux kernel")])





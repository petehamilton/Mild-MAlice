import re
import tokrules
import Node


intfmt = 'db "%ld", 10, 0'
charfmt = 'db "%c", 10, 0'
idivRegisters = ["rax", "rdx", "rcx" ]

def indent( string, indentation = "    "):
    return indentation + string

#change list of registers later
def generate( node, variables ):
    return setup(variables) + transExp( node, ["rax", "rdx", "rcx", "rbx", "rsi", "rdi"] ) + finish()

# Swaps first two elements of a list around
def swap( registers ):
    tmp = registers[0]
    registers[0] = registers[1]
    registers[1] =  tmp
    return registers

def transExp( node, registers ):
    # cast to string incase number? 
    if node.tokType == Node.FACTOR:
        if node.children[0] == "ID":
            return [ indent("mov %s, [%s]" %( registers[0], str(node.children[1])))] 
        return [ indent("mov %s, %s" %( registers[0], str(node.children[1])))] 

    if node.tokType == Node.STATEMENT_LIST:
        return ( transExp( node.children[0], registers ) +
        transExp( node.children[1], registers ) )

    # Translate expression and put in dst then put dst in eax and return
    # TODO: Maybe move this to function? push/pop rsi/rdi
    if node.tokType == Node.SPOKE:
        translated = transExp( node.children[0], registers )
        instr = [indent("mov rsi, %s" %registers[0]),
                 indent("mov rdi, intfmt"),
                 indent("xor rax, rax"),
                 indent("call printf"),
                ]
        return ( translated + instr )    

    if node.tokType == Node.BINARY_OP:
        if weight( node.children[1] ) > weight( node.children[2] ):
            return ( transExp( node.children[1], registers ) +
            transExp( node.children[2], registers[1:] ) +
            transBinOp( node.children[0], registers[0], registers[1] ) )
        else:
            registers = swap(registers)
            return ( transExp( node.children[2], registers )  +
            transExp( node.children[1], registers[1:] ) + 
            transBinOp( node.children[0], registers[0], registers[1] ) )
    
    if node.tokType == Node.UNARY_OP:
        return ( transExp( node.children[1], registers ) + 
        transUnOp( node.children[0], registers[0] ) )

    if node.tokType == Node.ASSIGNMENT:
        return ( transExp( node.children[1], registers ) + 
                 [indent("mov [%s], %s" %(node.children[0], registers[0]))])

    if node.tokType == Node.DECLARATION:
        return []



def preserveRegisters( registers, dest, next ):
    preserved = []
    for register in registers:
        if register not in [dest, next]:
            preserved.append(register)
    return preserved

def iDiv( destReg, nextReg, resultReg ):
    registers = preserveRegisters( idivRegisters, destReg, nextReg )
    return  map(indent, (["push %s" %x for x in registers] + 
                ["mov rax, %s" % destReg,
                "mov rcx, %s" % nextReg,
                "mov rdx, 0",
                "idiv rcx",
                "mov %s, %s" %(destReg, resultReg)] 
                + ["pop %s" %x for x in registers]))

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
        return iDiv( dest_reg, next_reg, "rax" )
    elif re.match( tokrules.t_MOD, op ):
        return iDiv( dest_reg, next_reg, "rdx" )
    elif re.match( tokrules.t_B_OR, op ):
        return [indent("or %s, %s" % (dest_reg, next_reg))]
    elif re.match( tokrules.t_B_XOR, op.tokType ):
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

def setup(variables):
    data = ["section .bss"]
    data.extend( [ indent("%s: resq 1" %x) for x in variables])
    data.append("\n")
    return (["extern printf", #potentially move this out if don't use spoke?
            "LINUX  	equ     80H		; interupt number for entering Linux kernel",
            "EXIT   	equ     1		; Linux system call 1 i.e. exit ()",
            "WRITE	equ	4		; Linux system call 4 i.e. write ()",
            "STDOUT	equ	1		; File descriptor 1 i.e. standard output",
            "\n"
            ] +
            data +
            [
            "section .data",
            indent("intfmt: ") + intfmt,
            indent("charfmt: ") + charfmt,
            "\n",
            "segment .text",
	        indent("global	main"),
            "\n",
            "main:"
            ])

def finish():
    return [indent("call os_return		; return to operating system"),
            "\n",
            "os_return:",
	        indent("mov  rax, EXIT		; Linux system call 1 i.e. exit ()"),
	        indent("mov  rbx, 0		; Error code 0 i.e. no errors"),
	        indent("int  LINUX		; Interrupt Linux kernel")
            ]





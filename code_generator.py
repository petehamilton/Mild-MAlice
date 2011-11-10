# toktype consts
UNARY_OP = "unary_op"
BINARY_OP = "binary_op"
FACTOR = "factor"
ASSIGNMENT = "assignment"
DECLARATION = "declaration"
SPOKE = "spoke"
STATEMENT_LIST = "statement_list"
TYPE = "type"


intfmt = 'db "%ld", 10, 0'
charfmt = 'db "%c", 10, 0'

#change list of registers later
def generate( node, variables ):
    return setup(variables) + transExp( node, ["rax", "rdx", "rcx", "rbx", "rsi", "rdi"] ) + finish()

# Swaps first two elements of a list around
def swap( registers ):
    tmp = registers[0]
    registers[0] = registers[1]
    registers[1] =  registers[0]
    return registers

def transExp( node, registers ):
    # cast to string incase number? 
    if node.tokType == FACTOR:
        if node.children[0] == "ID":
            return [ "mov %s, [%s]" %( registers[0], str(node.children[1]))] 
        return [ "mov %s, %s" %( registers[0], str(node.children[1]))] 

    if node.tokType == STATEMENT_LIST:
        return ( transExp( node.children[0], registers ) +
        transExp( node.children[1], registers[1:] ) )

    # Translate expression and put in dst then put dst in eax and return
    if node.tokType == SPOKE:
        translated = transExp( node.children[0], registers )
        instr = ["mov rsi, %s" %registers[0],
                 "mov rdi, intfmt",
                 "xor rax, rax",
                 "call printf",
                ]
        return ( translated + instr )    

    if node.tokType == BINARY_OP:
        if weight( node.children[1] ) > weight( node.children[2] ):
            return ( transExp( node.children[1], registers ) +
            transExp( node.children[2], registers[1:] ) +
            transBinop( node.children[0], registers[0], registers[1] ) )
        else:
            registers = swap(registers)
            return ( transExp( node.children[2], registers )  +
            transExp( node.children[1], registers[1:] ) + 
            transBinop( node.children[0], registers[1], registers[0] ) )
    
    if node.tokType == UNARY_OP:
        return ( transExp( node.children[1], registers ) + 
        transUnop( node.children[0], registers[0] ) )

    if node.tokType == ASSIGNMENT:
        return ( transExp( node.children[1], registers ) + 
                 ["mov [%s], %s" %(node.children[0], registers[0])])

    if node.tokType == DECLARATION:
        return []



# Returns the assembly code needed to perform the given binary 'op' operation on 
# the two provided registers
def transBinOp(op, dest_reg, next_reg):
    if   op.tokType == "PLUS":
        return ["add %s, %s" % (dest_reg, next_reg)]
    elif op.tokType == "MINUS":
        return ["sub %s, %s" % (dest_reg, next_reg)]
    elif op.tokType == "MULTIPLY":
        return ["mul %s, %s" % (dest_reg, next_reg)]
    elif op.tokType == "DIVIDE":
        return  ((["mov rax, %s" % dest_reg]) +
                (["div %s" % next_reg]) +
                (["mov %s, rax" % dest_reg]))
    elif op.tokType == "MOD":
        return  ((["mov rax, %s" % dest_reg]) +
                (["div %s" % next_reg]) +
                (["mov %s, rdx" % dest_reg]))
    elif op.tokType == "B_OR":
        return ["or %s, %s" % (dest_reg, next_reg)]
    elif op.tokType == "B_XOR":
        return ["xor %s, %s" % (dest_reg, next_reg)]
    elif op.tokType == "B_AND":
        return ["and %s, %s" % (dest_reg, next_reg)]
    
            
# Returns the assembly code needed to perform the given unary 'op' operation on 
# the provided register
def transUnOp(op, dest_reg):
    if   op.tokType == "INCREMENT":
        return ["inc %s" % dest_reg]
    elif op.tokType == "DECREMENT":
        return ["dec %s" % dest_reg]
    elif op.tokType == "B_NOT":
        return ["not %s" % dest_reg]

# Node types are:
# statement_list, spoke, assignment, declaration, 
# binary_op, unary_op, type, factor
def weight( node ):
    if node.tokType == FACTOR:
        return 1

    elif node.tokType == BINARY_OP:
        cost1 = max( weight(node.children[1]), weight(node.children[2]) + 1 )
        cost2 = max( weight(node.children[2]), weight(node.children[1]) + 1 )
        return min( cost1, cost2 )

    elif node.tokType == UNARY_OP:
        return weight(node.children[1])

    elif node.tokType == SPOKE:
        return weight(node.children[1])

    elif node.tokType == ASSIGNMENT:
        return 1

    elif node.tokType == STATEMENT_LIST:
        return max( weight(node.children[0]), weight(node.children[1]) )

    #is this right? Dont need to store anything in register yet
    elif node.tokType == DECLARATION or node.tokType == TYPE:
        pass

def setup(variables):
    data = ["section .bss"]
    data.extend( [ "\t%s: resq 1" %x for x in variables])
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
            "\tintfmt: " + intfmt,
            "\tcharfmt: " + charfmt,
            "\n",
            "segment .text",
	        "\tglobal	main",
            "\n",
            "main:"
            ])

def finish():
    return ["call os_return		; return to operating system",
            "\n",
            "os_return:",
	        "\tmov  rax, EXIT		; Linux system call 1 i.e. exit ()",
	        "\tmov  rbx, 0		; Error code 0 i.e. no errors",
	        "\tint  LINUX		; Interrupt Linux kernel"
            ]





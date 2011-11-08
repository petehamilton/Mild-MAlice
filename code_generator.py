def generate( node ):



def transExp( node, registers ):
    if node.tokType == "binary_op":
        if weight( node.children[1] ) > weight( node.children[2] ):
            transExp( node.children[1], registers )
            transExp( node.children[2], registers[1:]
            transBinop( node.)
        else:
            transExp(

# Returns the assembly code needed to perform the given binary 'op' operation on 
# the two provided registers
def transBinOp(op, dest_reg, next_reg):
    if   op.tokType == "PLUS"
        return ["add %s %s"] % (dest_reg, next_reg)
    elif op.tokType == "MINUS"
        return ["sub %s %s"] % (dest_reg, next_reg)
    elif op.tokType == "MULTIPLY"
        return ["mul %s %s"] % (dest_reg, next_reg)
    elif op.tokType == "DIVIDE"
        return  (["mov eax %s"] % dest_reg) +
                (["div %s"] % next_reg) +
                (["mov %s eax"] % dest_reg)
    elif op.tokType == "MOD"
        return  (["mov eax %s"] % dest_reg) +
                (["div %s"] % next_reg) +
                (["mov %s edx"] % dest_reg)
    elif op.tokType == "B_OR"
        return ["or %s %s"] % (dest_reg, next_reg)
    elif op.tokType == "B_XOR"
        return ["xor %s %s"] % (dest_reg, next_reg)
    elif op.tokType == "B_AND"
        return ["and %s %s"] % (dest_reg, next_reg)

# Returns the assembly code needed to perform the given unary 'op' operation on 
# the provided register
def transUnOp(op, dest_reg):
    if   op.tokType == "INCREMENT"
        return ["inc %s"] % dest_reg
    elif op.tokType == "DECREMENT"
        return ["dec %s"] % dest_reg
    elif op.tokType == "B_NOT"
        return ["not %s"] % dest_reg

# Node types are:
# statement_list, spoke, assignment, declaration, 
# binary_op, unary_op, type, factor
#
#
#
#
def weight( node ):
    if node.tokType == "factor":
        return 1

    elif node.tokType == "binary_op":
        cost1 = max( weight(node.children[1]), weight(node.children[2]) + 1 )
        cost2 = max( weight(node.children[2]), weight(node.children[1]) + 1 )
        return min( cost1, cost2 )

    elif node.tokType == "unary_op":
        return weight(node.children[1])

    elif node.tokType == "spoke":
        return weight(node.children[1])

    elif node.tokType == "assignment":

    elif node.tokType == "statement_list":
        return max( weight(node.children[0]), weight(node.children[1]) )

    #is this right? Dont need to store anything in register yet
    elif node.tokType == "declaration" or node.tokType == "type":
        pass




def generate( node ):



def transExp( node, registers ):
    if node.tokType == "binary_op":
        if weight( node.children[1] ) > weight( node.children[2] ):
            transExp( node.children[1], 
        else:
        



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
    elif node.tokType == "declaration" or node.tokType == "type:
        pass




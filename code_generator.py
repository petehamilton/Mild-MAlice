def generate( node ):



#def transExp( 


def weight( node ):
    if node.tokType == "factor":
        return 1

    elif node.tokType == "binary_op"
        cost1 = max( weight(node.children[1]), weight(node.children[2]) + 1 )
        cost2 = max( weight(node.children[2]), weight(node.children[1]) + 1 )
        return min( 

    elif node.tokType == "unary_op"

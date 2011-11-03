import sys
def analyse( symbolTable, node ):
    if node.tokType == "statement_list":
        analyse( symbolTable, node.children[0] )
        analyse( symbolTable, node.children[1] )
        
    elif node.tokType == "assignment":
        (identifier, expression) = node.children
        type1 = analyse( symbolTable, expression )
        if type1 == symbolTable[identifier][0]:
            symbolTable[identifier][2] = True
        else:
            print "Error can't assign wrong type idiot!"   

    elif node.tokType == "type":
        return node.children[0]

    elif node.tokType == "unary_op":
        type1 = analyse( symboLTable, node.children[1])
        if type1 == "NUMBER":
            return "NUMBER"
        else:
            print "Error can't use unop on things that aren't numbers"
            exit(1)
    
    elif node.tokType == "binary_op":
        type1 = analyse( symbolTable, node.children[1])
        type2 = analyse( symbolTable, node.children[2])
        if type1 == type2 == "NUMBER":
            return "NUMBER"
        else:
            print "Error can't use binop on things that aren't numbers"
            exit(1)

    elif node.tokType == "factor":
        if node.children[0] == 'ID':
            (idType, lineNo, assigned ) = symbolTable[node.children[1]]
            if assigned:
                return idType
            else:
                print "Error you haven't assigned your identifier"
                exit(1)
        return node.children[0]
        

     


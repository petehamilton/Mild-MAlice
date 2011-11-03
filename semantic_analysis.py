import sys
def analyse( symbolTable, node ):
    if node.tokType == "statement_list":
        analyse( symbolTable, node.children[0] )
        analyse( symbolTable, node.children[1] )

    elif node.tokType == "spoke":
        type1 = analyse( symbolTable, node.children[0])
        if type1[0] == 'ID':
            (idType, lineNo, assigned ) = symbolTable[node.children[0]]
            if not assigned:
                print "Error you haven't assigned your identifier"
                print "Paragraph %d" %node.lineno
                exit(1)

    elif node.tokType == "assignment":
        (identifier, expression) = node.children
        type1 = analyse( symbolTable, expression )
        if type1 == symbolTable[identifier][0]:
            symbolTable[identifier][2] = True
        else:
            print "Error can't assign wrong type idiot!"
            print "Paragraph %d" %node.lineno

    elif node.tokType == "type":
        return node.children[0]
        
    elif node.tokType == "unary_op":
        type1 = analyse( symbolTable, node.children[1])
        if type1 == "number":
            return "number"
        else:
            print "Oh No Silly you!"
            #print "Error can't use unop on things that aren't numbers"
            print "Paragraph %d" %Node.lineno
            exit(1)
    
    elif node.tokType == "binary_op":
        type1 = analyse( symbolTable, node.children[1])
        type2 = analyse( symbolTable, node.children[2])
        if type1 == type2 == "number":
            return "number"
        else:
            print "Oh No Silly you!"
            #print "Error can't use binop on things that aren't numbers"
            print "Paragraph %d" %node.lineno
            exit(1)

    elif node.tokType == "factor":
        if node.children[0] == 'ID':
            (idType, lineNo, assigned ) = symbolTable[node.children[1]]
            if assigned:
                return idType
            else:
                print "Oh No Silly you!"
                #print "Error you haven't assigned your identifier"
                print "Paragraph %d" %node.lineno
                exit(1)
        return node.children[0]
        

     


import sys

from grammar_exceptions import SemanticException

def analyse( symbolTable, node ):
    if node.tokType == "statement_list":
        analyse( symbolTable, node.children[0] )
        analyse( symbolTable, node.children[1] )

    elif node.tokType == "spoke":
        type1 = analyse( symbolTable, node.children[0])
        if type1[0] == 'ID':
            (idType, lineNo, assigned ) = symbolTable[node.children[0]]
            if not assigned:
                raise SemanticException( node.lineno, node.clauseno)

    elif node.tokType == "assignment":
        (identifier, expression) = node.children
        type1 = analyse( symbolTable, expression )
        if type1 == symbolTable[identifier][0]:
            symbolTable[identifier][2] = True
        else:
            raise SemanticException( node.lineno, node.clauseno)

    elif node.tokType == "type":
        return node.children[0]
        
    elif node.tokType == "unary_op":
        type1 = analyse( symbolTable, node.children[1])
        if type1 == "number":
            return "number"
        else:
            raise SemanticException( node.lineno, node.clauseno)
    
    elif node.tokType == "binary_op":
        type1 = analyse( symbolTable, node.children[1])
        type2 = analyse( symbolTable, node.children[2])
        if type1 == type2 == "number":
            return "number"
        else:
            raise SemanticException( node.lineno, node.clauseno)

    elif node.tokType == "factor":
        if node.children[0] == 'ID':
            (idType, lineNo, assigned ) = symbolTable[node.children[1]]
            if assigned:
                return idType
            else:
                raise SemanticException( node.lineno, node.clauseno)
        return node.children[0]
        
    elif node.tokType == "declaration":
        if node.children[0] in symbolTable:
            raise SemanticException( node.lineno, node.clauseno, "You already told me what '%s' was on line %d" %(node.children[0],  symbolTable[node.children[0]][1]) )
        else:    
            symbolTable[node.children[0]] = [node.children[1].children[0], node.lineno, True]
        

#class SemanticException(Exception):
#    pass
  


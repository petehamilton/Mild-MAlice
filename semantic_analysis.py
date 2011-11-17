import sys
import Node as n #TODO: Should be ASTNode

from grammar_exceptions import SemanticException

def analyse( symbolTable, node, flags ):
    if node.tokType == n.STATEMENT_LIST:
        analyse( symbolTable, node.children[0], flags  )
        analyse( symbolTable, node.children[1], flags  )

    elif node.tokType == n.SPOKE:
        type1 = analyse( symbolTable, node.children[0], flags )
        spokeChild = node.children[0]
        if spokeChild.children[0] == n.ID:
            (idType, lineNo, assigned ) = symbolTable[spokeChild.children[1]]
            if not assigned:
                raise SemanticException( node.lineno, node.clauseno )
        else:
            idType = spokeChild.children[0]            
        flags[n.SPOKE].add( idType )
            

    elif node.tokType == n.ASSIGNMENT:
        (identifier, expression) = node.children
        type1 = analyse( symbolTable, expression, flags  )
        if type1 == symbolTable[identifier][0]:
            symbolTable[identifier][2] = True
        else:
            raise SemanticException( node.lineno, node.clauseno )

    elif node.tokType == n.TYPE:
        return node.children[0]
        
    elif node.tokType == n.UNARY_OP:
        type1 = analyse( symbolTable, node.children[1], flags )
        if type1 == n.NUMBER:
            return n.NUMBER
        else:
            raise SemanticException( node.lineno, node.clauseno)
    
    elif node.tokType == n.BINARY_OP:
        type1 = analyse( symbolTable, node.children[1], flags )
        type2 = analyse( symbolTable, node.children[2], flags )
        if type1 == type2 == n.NUMBER:
            return n.NUMBER
        else:
            raise SemanticException( node.lineno, node.clauseno)

    elif node.tokType == n.FACTOR:
        if node.children[0] == n.ID:
            (idType, lineNo, assigned ) = symbolTable[node.children[1]]
            if assigned:
                return idType
            else:
                raise SemanticException( node.lineno, node.clauseno)
        return node.children[0]
        
    elif node.tokType == n.DECLARATION:
        if node.children[0] in symbolTable:
            raise SemanticException( node.lineno, node.clauseno, "You already told me what '%s' was on line %d" %(node.children[0],  symbolTable[node.children[0]][1]) )
        else:    
            symbolTable[node.children[0]] = [node.children[1].children[0], node.lineno, True]  





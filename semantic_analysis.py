import sys
import ASTNode #TODO: Should be ASTNode

from grammar_exceptions import SemanticException

def analyse( symbolTable, node, flags ):
    if node.tokType == ASTNode.STATEMENT_LIST:
        analyse( symbolTable, node.children[0], flags  )
        analyse( symbolTable, node.children[1], flags  )

    elif node.tokType == ASTNode.SPOKE:
        type1 = analyse( symbolTable, node.children[0], flags )
        spokeChild = node.children[0]
        if spokeChild.children[0] == ASTNode.ID:
            (idType, lineNo, assigned ) = symbolTable[spokeChild.children[1]]
            if not assigned:
                raise SemanticException( node.lineno, node.clauseno )
        else:
            idType = spokeChild.children[0]            
        flags[ASTNode.SPOKE].add( idType )
            

    elif node.tokType == ASTNode.ASSIGNMENT:
        (identifier, expression) = node.children
        type1 = analyse( symbolTable, expression, flags  )
        if type1 == symbolTable[identifier][0]:
            symbolTable[identifier][2] = True
        else:
            raise SemanticException( node.lineno, node.clauseno )

    elif node.tokType == ASTNode.TYPE:
        return node.children[0]
        
    elif node.tokType == ASTNode.UNARY_OP:
        type1 = analyse( symbolTable, node.children[1], flags )
        if type1 == ASTNode.NUMBER:
            return ASTNode.NUMBER
        else:
            raise SemanticException( node.lineno, node.clauseno)
    
    elif node.tokType == ASTNode.BINARY_OP:
        type1 = analyse( symbolTable, node.children[1], flags )
        type2 = analyse( symbolTable, node.children[2], flags )
        if type1 == type2 == ASTNode.NUMBER:
            return ASTNode.NUMBER
        else:
            raise SemanticException( node.lineno, node.clauseno)

    elif node.tokType == ASTNode.FACTOR:
        if node.children[0] == ASTNode.ID:
            if node.children[1] in symbolTable:
                (idType, lineNo, assigned ) = symbolTable[node.children[1]]
                if assigned:
                    return idType
            raise SemanticException( node.lineno, node.clauseno)
        return node.children[0]
        
    elif node.tokType == ASTNode.DECLARATION:
        if node.children[0] in symbolTable:
            raise SemanticException( node.lineno, node.clauseno, "You already told me what '%s' was on line %d" %(node.children[0],  symbolTable[node.children[0]][1]) )
        else:    
            symbolTable[node.children[0]] = [node.children[1].children[0], node.lineno, True]  





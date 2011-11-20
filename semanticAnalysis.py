import sys

import ASTNodes
from grammarExceptions import SemanticException

# Analyses the abstract syntax tree.
# Inputs are a symbolTable dictionary of form { id : ( id type, line number, assigned bool ) },
# the starting AST node and a flags dictionary of form { nodeType : info } where any relevant information
# for the particular node is set.
# Does not return anything. Will throw a semantic error if the code breaks the rules.
def analyse( symbolTable, node, flags ):
    if node.getNodeType() == ASTNodes.STATEMENT_LIST:
        analyse( symbolTable, node.getStatement(), flags  )
        analyse( symbolTable, node.getStatementList(), flags  )

    elif node.getNodeType() == ASTNodes.SPOKE:    
        spokeExpression = node.getExpression()
        expType = analyse( symbolTable, spokeExpression, flags )
        if spokeExpression.getNodeType() == ASTNodes.Factor:
            if spokeExpression.getFactorType() == ASTNodes.ID:
                (idType, lineNo, assigned) = symbolTable[spokeExpression.getValue()]
                if not assigned:
                    raise SemanticException( node.lineno, node.clauseno )
            else:
                idType = spokeExpression.getFactorType()
        else:
            # If not a factor, must be of type number since letters are only 
            # valid as factors and not as part of operations or expressions.
            idType = ASTNodes.NUMBER
        flags[ASTNodes.SPOKE].add( idType )

    elif node.getNodeType() == ASTNodes.ASSIGNMENT:
        (identifier, expression) = node.children
        expType = analyse( symbolTable, node.getExpression(), flags  )
        if expType == symbolTable[node.getVariable()][0]:
            symbolTable[node.getVariable()][2] = True
        else:
            raise SemanticException( node.lineno, node.clauseno )

    elif node.getNodeType() == ASTNodes.TYPE:
        return node.getType()
        
    elif node.getNodeType() == ASTNodes.UNARY_OP:
        expType = analyse( symbolTable, node.getExpression(), flags )
        if expType == ASTNodes.NUMBER:
            return expType
        else:
            raise SemanticException( node.lineno, node.clauseno)
    
    elif node.getNodeType() == ASTNodes.BINARY_OP:
        leftExpType = analyse( symbolTable, node.getLeftExpression(), flags )
        rightExpType = analyse( symbolTable, node.getRightExpression(), flags )
        if leftExpType == rightExpType == ASTNodes.NUMBER:
            return leftExpType
        else:
            raise SemanticException( node.lineno, node.clauseno)

    elif node.getNodeType() == ASTNodes.FACTOR:
        if node.getFactorType() == ASTNodes.ID:
            symbol = node.getValue()
            if symbol in symbolTable:
                (idType, lineNo, assigned ) = symbolTable[symbol]
                if assigned:
                    return idType
            raise SemanticException( node.lineno, node.clauseno)
        return node.getFactorType()
        
    elif node.getNodeType() == ASTNodes.DECLARATION:
        variable = node.getVariable()
        if variable in symbolTable:
            raise SemanticException( node.lineno, node.clauseno, " You already told me what '%s' was on line %d" %(variable,  symbolTable[variable][1]) )
        else:
            symbolTable[variable] = [node.getExpression().getType(), node.lineno, True]  

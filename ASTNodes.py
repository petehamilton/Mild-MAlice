# This module contains the nodes created by the parser.
from grammarExceptions import SemanticException

UNARY_OP = "unary_op"
BINARY_OP = "binary_op"
FACTOR = "factor"
ASSIGNMENT = "assignment"
DECLARATION = "declaration"
SPOKE = "spoke"
STATEMENT_LIST = "statement_list"
TYPE = "type"
NUMBER = "number"
LETTER = "letter"
ID = "ID"

class ASTNode(object):
    def __init__(self, nodeType, lineno, clauseno, children):
        self.nodeType = nodeType
        self.lineno = lineno
        self.clauseno = clauseno
        self.children = children
        self.type = None
        
    def getNodeType(self):
        return self.nodeType

class OperatorNode(ASTNode):
    def __init__(self, nodeType, lineno, clauseno, operator, children ):
        super(OperatorNode, self).__init__( nodeType, lineno, clauseno, children )
        self.operator = operator
        
    def getOperator(self):
        return self.operator

class BinaryNode(OperatorNode):
    def __init__(self, lineno, clauseno, operator, children ):
        super(BinaryNode, self).__init__( BINARY_OP, lineno, clauseno, operator, children )
        self.operator = operator
        
    def getLeftExpression(self):
        return self.children[0]
        
    def getRightExpression(self):
        return self.children[1]

    def check(self, symbolTable):
        self.getLeftExpression().check(symbolTable)
        self.getRightExpression().check(symbolTable)
        if self.getLeftExpression().type == self.getRightExpression().type == NUMBER:
            self.type = self.getLeftExpression().type
        else:
            raise SemanticException(self.lineno, self.clauseno)
    
class UnaryNode(OperatorNode):
    def __init__(self, lineno, clauseno, operator, child ):
        super(UnaryNode, self).__init__( UNARY_OP, lineno, clauseno, operator, [child] )

    def getExpression(self):
        return self.children[0]

    def check(self, symbolTable):
        self.getExpression.check(symbolTable)
        if self.getExpression().type == NUMBER:
            self.type = self.getExpression().type
        else:
            raise SemanticException(self.lineno, self.clauseno)

class StatementNode(ASTNode):
    def __init__(self, nodeType, lineno, clauseno, children ):
        super(StatementNode, self).__init__( nodeType, lineno, clauseno, children )
    
    def getVariable(self):
        return self.children[0]
        
    def getExpression(self):
        return self.children[1]
        
        
class AssignmentNode(StatementNode):
    def __init__(self, lineno, clauseno, varName, expression ):
        super(AssignmentNode, self).__init__( ASSIGNMENT, lineno, clauseno, [varName, expression] )
        self.variableName = varName
        self.expression = expression
        
    def check(self, symbolTable):
        V = symbolTable.lookupCurrLevelAndEnclosingLevels(self.variableName)
        self.expression.check(symbolTable)
        if  not V:
            raise SemanticException(self.lineno, self.clauseno)
        else:
            self.expression.check(symbolTable)
            if V.type == self.expression.type:
                self.type = self.expression.type
            else:
                raise SemanticException(self.lineno, self.clauseno)
            
class DeclarationNode(StatementNode):
    def __init__(self, lineno, clauseno, variableName, typeNode ):
        super(DeclarationNode, self).__init__( DECLARATION, lineno, clauseno, [variableName, typeNode] )
        self.variableName = variableName

    def check(self, symbolTable):
        # T = symbolTable.lookupCurrLevelAndEnclosingLevels(self.type)
        V = symbolTable.lookupCurrLevelOnly(self.variableName)
        # if T == None:
            # error("Unknown Type")
        if V:    
            raise SemanticException(self.lineno, self.clauseno)
        else:   
            self.children[1].check(symbolTable)
            self.type = self.children[1].type
            symbolTable.add(self.variableName, self)
            
class StatementListNode(ASTNode):
    def __init__(self, lineno, clauseno, children ):
        super(StatementListNode, self).__init__( STATEMENT_LIST, lineno, clauseno, children )
    
    def getStatement(self):
        return self.children[0]
        
    def getStatementList(self):
        return self.children[1]

    def check(self, symbolTable):
        self.getStatement().check(symbolTable)
        self.getStatementList().check(symbolTable)
        
class Factor(ASTNode):
    def __init__(self, nodeType, lineno, clauseno, child ):
        super(Factor, self).__init__( FACTOR, lineno, clauseno, [child] )
        self.factorType = nodeType

    def getFactorType(self):
        return self.factorType
    
    def getValue(self):
        return self.children[0]

    def check(self, symbolTable):
        self.type = self.factorType
        
class NumberNode(Factor):
    def __init__(self, lineno, clauseno, child ):
        super(NumberNode, self).__init__( NUMBER, lineno, clauseno, child )
    
class LetterNode(Factor):
    def __init__(self, lineno, clauseno, child ):
        super(LetterNode, self).__init__( LETTER, lineno, clauseno, child )
        
class IDNode(Factor):
    def __init__(self, lineno, clauseno, child ):
        super(IDNode, self).__init__( ID, lineno, clauseno, child )
    
    def check(self, symbolTable):
        self.type = symbolTable.lookupCurrLevelAndEnclosingLevels(self.getValue()).type
        
class SpokeNode(ASTNode):
    def __init__(self, lineno, clauseno, child ):
        super(SpokeNode, self).__init__( SPOKE, lineno, clauseno, [child] )
    
    def getExpression(self):
        return self.children[0]

    def check(self, symbolTable):
        self.getExpression().check(symbolTable)
        self.type = self.getExpression().type
        
class TypeNode(ASTNode):
    def __init__(self, lineno, clauseno, typeType ):
        super(TypeNode, self).__init__( TYPE, lineno, clauseno, [] )
        self.typeType = typeType
        
    def getType(self):
        return self.typeType

    def check(self, symbolTable):
        self.type = self.typeType
        
class NumberTypeNode(TypeNode):
    def __init__(self, lineno, clauseno ):
        super(NumberTypeNode, self).__init__( lineno, clauseno, NUMBER )
    
class LetterTypeNode(TypeNode):
    def __init__(self, lineno, clauseno ):
        super(LetterTypeNode, self).__init__( lineno, clauseno, LETTER )


# class FunctionDelcaration(ASTNode):
#   def __init__(self, lineno, clauseno, returnType, funcName, parameters):
#       super(FunctionDeclaration, self).__init__(lineno, clauseno, "FUNCTION")
#       self.returnType =  returnType
#       self.funcName = funcName
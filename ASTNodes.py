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
        
    def getNodeType():
        return self.nodeType

class OperatorNode(ASTNode):
    def __init__(self, lineno, clauseno, operator, children ):
        super(OperatorNode, self).__
        init__( nodeType, lineno, clauseno, children )
        self.operator = operator
        
    def getOperator():
        return self.operator

class BinaryNode(OperatorNode):
    def __init__(self, lineno, clauseno, operator, children ):
        super(BinaryNode, self).__init__( BINARY_OP, lineno, clauseno, operator, children )
        self.operator = operator
        
    def getLeftExpression():
        return self.children[0]
        
    def getRightExpression():
        return self.children[1]
    
class UnaryNode(OperatorNode):
    def __init__(self, nodeType, lineno, clauseno, operator, child ):
        super(UnaryNode, self).__init__( UNARY_OP, lineno, clauseno, operator, [child] )

    def getExpression():
        return self.children[0]

class StatementNode(ASTNode):
    def __init__(self, nodeType, lineno, clauseno, children ):
        super(StatementNode, self).__init__( nodeType, lineno, clauseno, children )
    
    def getVariable():
        return self.children[0]
        
    def getExpression():
        return self.children[1]
        
class AssignmentNode(StatementNode):
    def __init__(self, lineno, clauseno, children ):
        super(AssignmentNode, self).__init__( ASSIGNMENT, lineno, clauseno, children )

class DeclarationNode(StatementNode):
    def __init__(self, lineno, clauseno, child ):
        super(DeclarationNode, self).__init__( DECLARATION, lineno, clauseno, children )
    
class StatementListNode(ASTNode):
    def __init__(self, lineno, clauseno, children ):
        super(StatementListNode, self).__init__( STATEMENT_LIST, lineno, clauseno, children )
    
    def getStatement():
        return self.children[0]
        
    def getStatementList():
        return self.children[1]
        
class Factor(ASTNode):
    def __init__(self, nodeType, lineno, clauseno, child ):
        super(Factor, self).__init__( FACTOR, lineno, clauseno, [child] )
        self.factorType = nodeType
        
    def getFactorType():
        return self.factorType
    
    def getValue():
        return self.children[0]
        
class NumberNode(Factor):
    def __init__(self, lineno, clauseno, child ):
        super(NumberNode, self).__init__( NUMBER, lineno, clauseno, child )
    
class LetterNode(Factor):
    def __init__(self, lineno, clauseno, child ):
        super(LetterNode, self).__init__( LETTER, lineno, clauseno, child )
        
class IDNode(Factor):
    def __init__(self, lineno, clauseno, child ):
        super(IDNode, self).__init__( ID, lineno, clauseno, child )
    
class SpokeNode(ASTNode):
    def __init__(self, lineno, clauseno, child ):
        super(SpokeNode, self).__init__( SPOKE, lineno, clauseno, [child] )
    
    def getVariable():
        return self.children[0]
        
class TypeNode(ASTNode):
    def __init__(self, lineno, clauseno, typeType ):
        super(TypeNode, self).__init__( TYPE, lineno, clauseno, [] )
        self.typeType = typeType
        
    def getType():
        return self.typeType
        
        
class NumberTypeNode(TypeNode):
    def __init__(self, lineno, clauseno ):
        super(NumberTypeNode, self).__init__( lineno, clauseno, NUMBER )
    
class LetterTypeNode(TypeNode):
    def __init__(self, lineno, clauseno ):
        super(LetterTypeNode, self).__init__( lineno, clauseno, LETTER )
    
    

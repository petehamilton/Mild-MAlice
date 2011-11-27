# This module contains the nodes created by the parser.
from grammarExceptions import SemanticException
from SymbolTable import SymbolTable

UNARY_OP = "unary_op"
BINARY_OP = "binary_op"
LOGICAL_OP = "logical_op"
FACTOR = "factor"
ASSIGNMENT = "assignment"
DECLARATION = "declaration"
SPOKE = "spoke"
STATEMENT_LIST = "statement_list"
TYPE = "type"
NUMBER = "number"
LETTER = "letter"
SENTENCE = "sentence"
ID = "ID"
RETURN = "return"
INPUT = "input"
LOOP = "loop"
IF = "if"
ELSEIF = "elseif"
ELSE = "else"
LOGICALCLAUSE = "logical_clause"
LOGICALCLAUSES = "logical_clauses"
ARGUMENT = 'argument'
ARGUMENTS = 'arguments'
FUNCTION_ARGUMENT = 'f_argument'
FUNCTION_ARGUMENTS = 'f_arguments'
FUNCTION_CALL = 'f_call'
FUNCTIONS = 'functions'
CODE_SEP = 'c_sep'

# Main AST Node class from which all other AST nodes inherit
class ASTNode(object):
    def __init__(self, nodeType, lineno, clauseno, children):
        self.nodeType = nodeType
        self.lineno = lineno
        self.clauseno = clauseno
        self.children = children
        self.type = None
        
    def getNodeType(self):
        return self.nodeType

    def __str__(self):
        return "Node(%s,%r,%s,%s)" % (self.nodeType,self.lineno,self.clauseno,self.children)
    
    def display(self, depth = 0):
        print ("  " * (depth-1)) + \
              ("|> " if (depth > 0) else "") + self.nodeType
        
        for child in self.children:
            if isinstance(child, ASTNode):
                child.display(depth + 1)
            else:
                print ("  " * (depth)) + "|> '" + str(child) + "'"

################################################################################
# OPERATOR NODES
################################################################################
class OperatorNode(ASTNode):
    def __init__(self, nodeType, lineno, clauseno, operator, children ):
        super(OperatorNode, self).__init__( nodeType, lineno, clauseno, children )
        self.operator = operator
        
    def getOperator(self):
        return self.operator
        
    def display(self, depth = 0):
        print ("  " * (depth-1)) + \
              ("|> " if (depth > 0) else "") + self.nodeType
        for child in [self.children[0], self.operator]:
            if isinstance(child, ASTNode):
                child.display(depth + 1)
            else:
                print ("  " * (depth)) + "|> '" + str(child) + "'"

class BinaryOperatorNode(ASTNode):
    def __init__(self, nodeType, lineno, clauseno, operator, children ):
        super(BinaryOperatorNode, self).__init__( nodeType, lineno, clauseno, children )
        self.operator = operator
    
    def getLeftExpression(self):
        return self.children[0]

    def getRightExpression(self):
        return self.children[1]
    
    def check(self, symbolTable):
        self.getLeftExpression().check(symbolTable)
        self.getRightExpression().check(symbolTable)

    def getOperator(self):
        return self.operator
    
    def display(self, depth = 0):
        print ("  " * (depth-1)) + \
              ("|> " if (depth > 0) else "") + self.nodeType
        for child in [self.children[0], self.operator, self.children[1]]:
            if isinstance(child, ASTNode):
              child.display(depth + 1)
            else:
              print ("  " * (depth)) + "|> '" + str(child) + "'"

class BinaryNode(BinaryOperatorNode):
    def __init__(self, lineno, clauseno, operator, children ):
        super(BinaryNode, self).__init__( BINARY_OP, lineno, clauseno, operator, children )

    def check(self, symbolTable):
        super(BinaryNode, self).check( symbolTable )
        if self.getLeftExpression().type == self.getRightExpression().type == NUMBER:
            self.type = self.getLeftExpression().type
        else:
            print "RAISE BINARY"
            raise SemanticException(self.lineno, self.clauseno)

class LogicalNode(BinaryOperatorNode):
    def __init__(self, lineno, clauseno, operator, children ):
        super(LogicalNode, self).__init__( LOGICAL_OP, lineno, clauseno, operator, children )
            
    def check(self, symbolTable):
        super(LogicalNode, self).check( symbolTable )
        if self.getLeftExpression().type == self.getRightExpression().type: # Don't need to be a specific type, just need to both be the same
            self.type = self.getLeftExpression().type
        else:
            print "RAISE LOGICAL"
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
            print "Raise UNARY"
            raise SemanticException(self.lineno, self.clauseno)

################################################################################
# END OF OPERATOR NODES
################################################################################



################################################################################
# STATEMENT/STATEMENT LIST NODES
################################################################################
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

class StatementNode(ASTNode):
    def __init__(self, nodeType, lineno, clauseno, children ):
        super(StatementNode, self).__init__( nodeType, lineno, clauseno, children )
    
    def getVariable(self):
        return self.children[0]
        
    def getExpression(self):
        return self.children[1]

################################################################################
# VARIABLE MODIFIER NODES
################################################################################
class AssignmentNode(StatementNode):
    def __init__(self, lineno, clauseno, varName, expression ):
        super(AssignmentNode, self).__init__( ASSIGNMENT, lineno, clauseno, [varName, expression] )
        self.variableName = varName
        self.expression = expression
        
    def check(self, symbolTable):
        V = symbolTable.lookupCurrLevelAndEnclosingLevels(self.variableName.getValue())
        self.expression.check(symbolTable)
        if not V:
            print "RAISE ASSIGNMENT 1"
            raise SemanticException(self.lineno, self.clauseno)
        else:
            self.expression.check(symbolTable)
            if V.type == self.expression.type:
                self.type = self.expression.type
            else:
                print "RAISE ASSIGNMENT 2"
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
            print "RAISE DECLARATION"
            raise SemanticException(self.lineno, self.clauseno)
        else:   
            self.children[1].check(symbolTable)
            self.type = self.children[1].type
            symbolTable.add(self.variableName, self)


################################################################################
# FACTOR/PRIMATIVE NODES
################################################################################
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

class SentenceNode(Factor):
    def __init__(self, lineno, clauseno, child ):
        super(SentenceNode, self).__init__( SENTENCE, lineno, clauseno, child )

class IDNode(Factor):
    def __init__(self, lineno, clauseno, child ):
        super(IDNode, self).__init__( ID, lineno, clauseno, child )
    
    def check(self, symbolTable):
        self.type = symbolTable.lookupCurrLevelAndEnclosingLevels(self.getValue()).type


################################################################################
# PRINT NODE
################################################################################
class SpokeNode(ASTNode):
    def __init__(self, lineno, clauseno, child ):
        super(SpokeNode, self).__init__( SPOKE, lineno, clauseno, [child] )
    
    def getExpression(self):
        return self.children[0]

    def check(self, symbolTable):
        self.getExpression().check(symbolTable)
        self.type = self.getExpression().type


################################################################################
# RETURN NODE
################################################################################
class ReturnNode(ASTNode):
    def __init__(self, lineno, clauseno, exp ):
        super(ReturnNode, self).__init__( RETURN, lineno, clauseno, [exp] )
        
    def getReturnExpression(self):
        return self.children[0]
        
    def check(self, symbolTable):
        self.getReturnExpression().check(symbolTable)
        self.type = self.getReturnExpression().type


################################################################################
# INPUT NODE
################################################################################
class InputNode(ASTNode):
    def __init__(self, lineno, clauseno, variable ):
        super(InputNode, self).__init__( INPUT, lineno, clauseno, [variable] )
        
    def getVariable(self):
        return self.children[0]
        
    #TODO: CHECK IF ID    
    def check(self, symbolTable):
        self.getVariable().check(symbolTable)
        self.type = self.getVariable().type

################################################################################
# TYPE NODES
################################################################################
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
        
class SentenceTypeNode(TypeNode):
    def __init__(self, lineno, clauseno ):
        super(SentenceTypeNode, self).__init__( lineno, clauseno, SENTENCE )


################################################################################
# ARRAY NODES
################################################################################
class ArrayAccessNode(ASTNode):
    def __init__(self, lineno, clauseno, variable, index ):
        super(ArrayAccessNode, self).__init__( INPUT, lineno, clauseno, [variable] )
        self.index = index
        
    def getVariable(self):
        return self.children[0]
        
    #TODO: CHECK IF ID    
    def check(self, symbolTable):
        self.getVariable().check(symbolTable)
        self.type = self.getVariable().type
        
        # Can't raise out of upper bounds exception til runtime?
        if self.index < 0:
            print "RAISE ARRAY ACCESS"
            raise SemanticException()

class ArrayDeclarationNode(DeclarationNode):
    def __init__(self, lineno, clauseno, variableName, typeNode,  length):
        super(ArrayDeclarationNode, self).__init__( lineno, clauseno, variableName, typeNode )
        self.length = length
    
    def check(self,symbolTable):
        self.length.check(symbolTable)
        if self.length.type != NUMBER:
            print "RAISE ARRAY DECLARATION"
            raise SemanticException()
        super(ArrayDeclarationNode, self).check(symbolTable)


################################################################################
# CONDITIONAL NODES
################################################################################
class ConditionalNode(ASTNode):
    def __init__(self, nodeType, lineno, clauseno, children ):
        super(ConditionalNode, self).__init__(nodeType, lineno, clauseno, children) #Children always come in expr, body, other

    def getExpression(self):
        return self.children[0]

    def getBody(self):
        return self.children[1]

    def check(self, symbolTable):
        self.getExpression().check(symbolTable)
        self.getBody().check(symbolTable)
        
class LoopNode(ConditionalNode):
    def __init__(self, lineno, clauseno, exp, body ):
        super(LoopNode, self).__init__(LOOP, lineno, clauseno, [exp, body])
        
class IfNode(ConditionalNode):
    def __init__(self, lineno, clauseno, exp, thenBody, nextLogicalClause = None ):
        super(IfNode, self).__init__(IF, lineno, clauseno, [exp, thenBody, nextLogicalClause])

        def getNextLogicalClause(self):
            return self.children[2]

        def check(self, symbolTable):
            super(IfNode, self).check(symbolTable)
            nextLogicalClause = self.getNextLogicalClause();
            if nextLogicalClause != None:
                nextLogicalClause.check(symbolTable)

class ElseIfNode(ConditionalNode):
    def __init__(self, lineno, clauseno, exp, thenBody):
        super(ElseIfNode, self).__init__(ELSEIF, lineno, clauseno, [exp, thenBody])

# Some way to inherit this from conditionalNode as well? Although I suppose it's
# not that conditional in that there is no logical check?
class ElseNode(ASTNode):
    def __init__(self, lineno, clauseno, thenBody):
        super(ElseNode, self).__init__(ELSE, lineno, clauseno, [thenBody])
    
    def getBody(self):
        return self.children[0]
    
    def check(self, symbolTable):
        self.getBody().check(symbolTable)

class LogicalClausesNode(ASTNode):
    def __init__(self, lineno, clauseno, logicalClause, logicalClauses):
        super(LogicalClausesNode, self).__init__(LOGICALCLAUSES, lineno, clauseno, [logicalClause, logicalClauses])
    
    def getLogicalClause(self):
        return self.children[0]

    def getLogicalClauses(self):
        return self.children[1]

    def check(self, symbolTable):
        self.getLogicalClause().check(symbolTable)
        
        logicalClauses = self.getLogicalClauses();
        if logicalClauses != None:
            logicalClauses.check(symbolTable)


################################################################################
# FUNCTION DECLARATION NODES
################################################################################
class FunctionDeclarationNode(DeclarationNode):
    def __init__(self, lineno, clauseno, functionName, arguments, returnType, body, returnValue ):
        super(FunctionDeclarationNode, self).__init__( lineno, clauseno, functionName, returnType )
        self.arguments = arguments
        self.body = body
        self.returnValue = returnValue
    
    def getName(self):
        return self.children[0]
        
    def getArguments(self):
        return self.arguments
        
    def getBody(self):
        return self.body
    
    def getReturnType(self):
        return self.children[1]
    
    def getReturnValue(self):
        return self.returnValue
        
    def check(self, symbolTable):    
        super(FunctionDeclarationNode, self).check(symbolTable)
        newSymbolTable = SymbolTable(symbolTable)
        self.getArguments().check(newSymbolTable)
        if self.getBody():
            self.getBody().check(newSymbolTable)
        self.getReturnValue().check(newSymbolTable)

class ArgumentsNode(ASTNode):
    def __init__(self, lineno, clauseno, argument, arguments ):
        super(ArgumentsNode, self).__init__( ARGUMENTS, lineno, clauseno, [argument, arguments])
        
    def getArgument(self):
        return self.children[0]
    
    def getArguments(self):
        return self.children[1]

    def getLength(self):
        return 1 + self.getArguments().getLength()
    
    def check(self, symbolTable):
        self.getArgument().check(symbolTable)
        if self.getArguments():
            self.getArguments().check(symbolTable)

class ArgumentNode(ASTNode):
    def __init__(self, lineno, clauseno, argumentDeclaration, reference = False):
        super(ArgumentNode, self).__init__( ARGUMENT, lineno, clauseno, [argumentDeclaration])
        self.reference = reference
    
    def getArgument(self):
        return self.children[0]
    
    def getLength(self):
        return 1
        
    def check(self, symbolTable):
        self.getArgument().check(symbolTable)


################################################################################
# FUNCTION CALL NODES
################################################################################
    
class FunctionCallNode(ASTNode):
    def __init__(self, lineno, clauseno, functionName, arguments):
        super(FunctionCallNode, self).__init__( FUNCTION_CALL, lineno, clauseno, [functionName, arguments] )
        
    def getName(self):
        return self.children[0]
        
    def getArguments(self):
        return self.children[1]
        
    def check(self, symbolTable):
        func = symbolTable.lookupCurrLevelAndEnclosingLevels(self.getName())
        self.getArguments().check(symbolTable)
        if not func:
            print "RAISE NOT FUNC"
            raise SemanticException(self.lineno, self.clauseno)
        elif func.getArguments().getLength() != self.getArguments().getLength():
            print "Arguments:", self.getArguments().children[0].children[0].children[0],self.getArguments().children[1].children[0].children[0]
            print func.getArguments().getLength() , self.getArguments().getLength() 
            print "RAISE WRONG ARGUMENTS FUNC"  
            raise SemanticException(self.lineno, self.clauseno)
        else:
            
            # TODO CHECK COMPATABILITY
            self.type = func.type

class FunctionArgumentsNode(ASTNode):
    def __init__(self, lineno, clauseno, argument, arguments = None):
        super(FunctionArgumentsNode, self).__init__( FUNCTION_ARGUMENTS, lineno, clauseno, [argument, arguments] )
        
    def getArgument(self):
        return self.children[0]
        
    def getArguments(self):
        return self.children[1]
    
    def getLength(self):
        return 1 + self.getArguments().getLength()
        
    def check(self, symbolTable):    
        self.getArgument().check(symbolTable)
        if self.getArguments():
            self.getArguments().check(symbolTable)        
        
class FunctionArgumentNode(ASTNode):
    def __init__(self, lineno, clauseno, exp):
        super(FunctionArgumentNode, self).__init__( FUNCTION_ARGUMENT, lineno, clauseno, [exp] )
        
    def getExpression(self):
        return self.children[0]
    
    def getLength(self):
        return 1
        
    def check(self, symbolTable):
        self.getExpression().check(symbolTable)
        self.type = self.getExpression().type



################################################################################
# FUNCTION LIST NODE - List of functions at end of file
################################################################################
class FunctionsNode(ASTNode):
    def __init__(self, lineno, clauseno, function, functions):
        super(FunctionsNode, self).__init__( FUNCTIONS, lineno, clauseno, [function, functions])
    
    def getFunction(self):
        return self.children[0]
        
    def getFunctions(self):
        return self.children[1]    
    
    def check(self, symbolTable):  
        self.getFunction().check(symbolTable)
        if self.getFunctions():
            self.getFunctions().check(symbolTable)


################################################################################
# CODE SEPERATOR NODE - Seperates code from the functions declared at the end
################################################################################
class CodeSeperatorNode(ASTNode):
    def __init__(self, lineno, clauseno, statementList, functions = None ):
        super(CodeSeperatorNode, self).__init__( CODE_SEP, lineno, clauseno, [statementList, functions])
        
    def getStatementList(self):
        return self.children[0]
        
    def getFunctions(self):
        return self.children[1]
        
    def check(self, symbolTable):
        functions = self.getFunctions()
        if functions:
            functions.check(symbolTable)
        
        self.getStatementList().check(symbolTable)
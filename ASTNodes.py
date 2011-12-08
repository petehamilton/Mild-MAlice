# This module contains the nodes created by the parser.
from grammarExceptions import SemanticException, BinaryException, LogicalException, UnaryException, AssignmentNullException, AssignmentTypeException, DeclarationException, ArrayIndexOutOfBoundsException, ArrayDeclarationException, FunctionMissingException, FunctionArgumentCountException
from SymbolTable import SymbolTable
import tokRules
import intermediateNodes as INodes
import re

################################################################################
# NODE TYPES
################################################################################
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
FUNCTION_BODY = 'function_body'
FUNCTION_ARGUMENT = 'f_argument'
FUNCTION_ARGUMENTS = 'f_arguments'
FUNCTION_CALL = 'f_call'
FUNCTIONS = 'functions'
CODE_SEP = 'c_sep'
COMMENT = 'comment'



################################################################################
# MAIN AST NODE
################################################################################

class ASTNode(object):
    def __init__(self, nodeType, lineno, clauseno, children):
        self.nodeType = nodeType
        self.lineno = lineno
        self.clauseno = clauseno
        self.children = children
        self.type = None
        self.symbolTable = None
        
    def setSymbolTable(self, symbolTable):
        self.symbolTable = symbolTable
        
    def getNodeType(self):
        return self.nodeType

    def __str__(self):
        return "%s(%s,%r,%s,%s)" % (self.__class__.__name__, self.nodeType,self.lineno,self.clauseno,self.children)
    
    def display(self, depth = 0):
        print ("  " * (depth-1)) + \
              ("|> " if (depth > 0) else "") + self.nodeType
        for child in self.children:
            if isinstance(child, ASTNode):
                child.display(depth + 1)
            else:
                print ("  " * (depth)) + "|> '" + str(child) + "'"
    
    def translate(self, registersDict, reg, parents):
        return reg, [], parents



################################################################################
# OPERATOR NODES - Binary, Logical Binary and Unary
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
        children = [self.children[0], self.operator]
        if self.children[1]:
            children += [self.children[1]]
        for child in children:
            if isinstance(child, ASTNode):
                child.display(depth + 1)
            else:
                print ("  " * (depth)) + "|> '" + str(child) + "'"

class BinaryNode(OperatorNode):
    def __init__(self, lineno, clauseno, operator, children ):
        super(BinaryNode, self).__init__( BINARY_OP, lineno, clauseno, operator, children )
    
    def getLeftExpression(self):
        return self.children[0]

    def getRightExpression(self):
        return self.children[1]
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        leftExpression = self.getLeftExpression()
        rightExpression = self.getRightExpression()
        
        leftExpression.check(symbolTable, flags)
        rightExpression.check(symbolTable, flags)
        
        if leftExpression.type == rightExpression.type == NUMBER:
            self.type = leftExpression.type
        else:
            print "Binary Exception"
            raise BinaryException(self.lineno, self.clauseno)
    
    def translate(self, registersDict, reg, parents):
        def translateOperation(destReg, nextReg, parents):
            op = self.getOperator()
            if re.match( tokRules.t_PLUS, op ):
                intermediateNode = INodes.AddNode(destReg, nextReg, parents)
            
            elif re.match( tokRules.t_MINUS, op ):
                intermediateNode = INodes.SubNode(destReg, nextReg, parents)

            elif re.match( tokRules.t_MULTIPLY, op ):
                intermediateNode = INodes.MulNode(destReg, nextReg, parents)

            elif re.match( tokRules.t_DIVIDE, op ):
                intermediateNode = INodes.DivNode(destReg, nextReg, parents)

            elif re.match( tokRules.t_MOD, op ):
                intermediateNode = INodes.ModNode(destReg, nextReg, parents)

            elif re.match( tokRules.t_B_OR, op ):
                intermediateNode = INodes.OrNode(destReg, nextReg, parents)

            elif re.match( tokRules.t_B_XOR, op ):
                intermediateNode = INodes.XORNode(destReg, nextReg, parents)
                
            elif re.match( tokRules.t_B_AND, op ):
                intermediateNode = INodes.AndNode(destReg, nextReg, parents)
            
            elif re.match( tokRules.t_L_EQUAL, op ):
                intermediateNode = INodes.EqualNode(destReg, nextReg, parents)
                
            elif re.match( tokRules.t_L_LESS_THAN, op ):
                intermediateNode = INodes.LessThanNode(destReg, nextReg, parents)
                
            elif re.match( tokRules.t_L_LESS_THAN_EQUAL, op ):
                intermediateNode = INodes.LessThanEqualNode(destReg, nextReg, parents)
                
            elif re.match( tokRules.t_L_GREATER_THAN, op ):
                intermediateNode = INodes.GreaterThanNode(destReg, nextReg, parents)
                
            elif re.match( tokRules.t_L_GREATER_THAN_EQUAL, op ):
                intermediateNode = INodes.GreaterThanEqualNode(destReg, nextReg, parents)
                
            elif re.match( tokRules.t_L_NOT_EQUAL, op ):
                intermediateNode = INodes.NotEqualNode(destReg, nextReg, parents)
                
            elif re.match( tokRules.t_L_AND, op ):
                intermediateNode = INodes.AndNode(destReg, nextReg, parents)
                
            elif re.match( tokRules.t_L_OR, op ):
                intermediateNode = INodes.OrNode(destReg, nextReg, parents)
            
            return destReg, [intermediateNode], [intermediateNode]
            
            
        reg1, exp1, parents = self.getLeftExpression().translate(registersDict, reg, parents)
        reg2, exp2, parents = self.getRightExpression().translate(registersDict, reg, parents)
        reg, exp3, parents = translateOperation(reg, reg1, parents)
        reg = reg + (reg2 - reg1)
        return reg + 1, (exp1 + exp2 + exp3), parents

class UnaryNode(OperatorNode):
    def __init__(self, lineno, clauseno, operator, child ):
        super(UnaryNode, self).__init__( UNARY_OP, lineno, clauseno, operator, [child] )

    def getExpression(self):
        return self.children[0]

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getExpression().check(symbolTable, flags)
        if self.getExpression().type == NUMBER:
            self.type = self.getExpression().type
        else:
            print "Unary Exception"
            raise UnaryException(self.lineno, self.clauseno)
    
    def translate( self, registersDict, reg, parents ):
        def transUnOp(destReg, node, registersDict, parents):
            op = self.getOperator()
            if re.match( "ate", op ):
                intermediateNode = [INodes.IncNode(registersDict[node.getValue()], parents)]
                parents = intermediateNode
            elif re.match( "drank", op ):
                intermediateNode = [INodes.DecNode(registersDict[node.getValue()], parents)]
                parents = intermediateNode
            elif re.match( tokRules.t_B_NOT, op ):
                reg1, exp, parents = node.translate(registersDict, destReg, parents)
                intermediateNode = [INodes.NotNode(destReg, parents)]
                parents = intermediateNode
                destReg = reg1
                intermediateNode = exp + intermediateNode
            elif re.match( tokRules.t_MINUS, op ):
                reg1, exp, parents = node.translate(registersDict, destReg, parents)
                intermediateNode = [INodes.NegativeNode(destReg, parents)]
                parents = intermediateNode
                destReg = reg1
                intermediateNode = exp + intermediateNode
            return destReg, intermediateNode, parents
            
        reg, exp2, parents = transUnOp( reg, self.getExpression(), registersDict, parents )
        return reg, exp2, parents
        
        


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

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getStatement().check(symbolTable, flags)
        self.getStatementList().check(symbolTable, flags)
    
    def translate(self, registersDict, reg, parents):
        reg, exp1, parents = self.getStatement().translate(registersDict, reg, parents)
        reg, exp2, parents = self.getStatementList().translate(registersDict, reg, parents)
        return reg, exp1 + exp2, parents

class StatementNode(ASTNode):
    def __init__(self, nodeType, lineno, clauseno, children ):
        super(StatementNode, self).__init__( nodeType, lineno, clauseno, children )
    
    def getVariable(self):
        return self.children[0]
        
    def getExpression(self):
        return self.children[1]



################################################################################
# VARIABLE MODIFIER NODES - Assignment and declaration for id
################################################################################

#TODO: Maybe not dest, use something more appropriate
class AssignmentNode(StatementNode):
    def __init__(self, lineno, clauseno, dest, expression ):
        super(AssignmentNode, self).__init__( ASSIGNMENT, lineno, clauseno, [dest, expression] )
    
    def getDestination(self):
        return self.children[0]
    
    def getExpression(self):
        return self.children[1]
        
    def variableCheck(self, symbolTable, flags, variable):
        expr = self.getExpression()
        V = symbolTable.lookupCurrLevelAndEnclosingLevels(variable)
        expr.check(symbolTable, flags)
        if not V:
            raise AssignmentNullException(self.lineno, self.clauseno)
        else:
            expr.check(symbolTable, flags)
            if V.type == expr.type:
                self.type = expr.type
            else:
                print "Assignment Exception"
                raise AssignmentTypeException(self.lineno, self.clauseno)

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.variableCheck(symbolTable, flags, self.getDestination())
        
    def translate(self, registersDict, reg, parents):    
        assignmentReg = reg
        reg, exp, parents = self.getExpression().translate(registersDict, reg, parents)
        registersDict[self.getVariable()] = assignmentReg
        return reg, exp, parents
        
class DeclarationNode(StatementNode):
    def __init__(self, lineno, clauseno, variableName, typeNode ):
        super(DeclarationNode, self).__init__( DECLARATION, lineno, clauseno, [variableName, typeNode] )
        self.variableName = variableName
        
    # Returns type node's type.
    def getType(self):
        return self.children[1].getType()

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        # T = symbolTable.lookupCurrLevelAndEnclosingLevels(self.type)
        V = symbolTable.lookupCurrLevelOnly(self.variableName)
        # if T == None:
            # error("Unknown Type")
        if V:
            print "Declaration Exception"
            raise DeclarationException(self.lineno, self.clauseno)
        else:   
            self.children[1].check(symbolTable, flags)
            self.type = self.children[1].type
            symbolTable.add(self.variableName, self)
    
    def translate( self, registersDict, reg, parents ):
        return reg, [], parents


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

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.type = self.factorType
    
    def translate(self, registersDict, reg, parents):
        intermediateNode = INodes.ImmMovNode(reg, str(self.getValue()), parents)    
        return reg + 1, [intermediateNode], [intermediateNode]
        
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
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.type = symbolTable.lookupCurrLevelAndEnclosingLevels(self.getValue()).type
    
    def translate(self, registersDict, reg, parents):
        intermediateNode = INodes.MovNode(reg, registersDict[self.getValue()], parents)
        return reg + 1, [intermediateNode], [intermediateNode]



################################################################################
# PRINT NODE
################################################################################

class SpokeNode(ASTNode):
    def __init__(self, lineno, clauseno, child ):
        super(SpokeNode, self).__init__( SPOKE, lineno, clauseno, [child] )
    
    def getExpression(self):
        return self.children[0]

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.symbolTable = symbolTable
        self.getExpression().check(symbolTable, flags)
        self.type = self.getExpression().type
        flags[SPOKE].add( self.getIDType() )
    
    def getIDType(self):
        spokeExpression = self.getExpression()
        if spokeExpression.getNodeType() == FACTOR:
            if spokeExpression.getFactorType() == ID:
                node = self.symbolTable.lookupCurrLevelAndEnclosingLevels(spokeExpression.getValue())
                idType = node.getType()
            else:
                idType = spokeExpression.getFactorType()
        else:
            # If not a factor, must be of type number since letters are only 
            # valid as factors and not as part of operations or expressions
            idType = NUMBER
    
    def translate(self, registersDict, reg, parents):
        spokeExpression = self.getExpression()
        reg1, exp, parents = spokeExpression.translate(registersDict, reg, parents)
        
        idType = self.getIDType()
        
        formatting = ""
        if idType == NUMBER:
            formatting = "intfmt"
        elif idType == LETTER:
            formatting = "charfmt"
        elif idType == SENTENCE: #TODO, IS THIS RIGHT?
            formatting = "charfmt"
        
        # Should catch error here if formatting not set...
        intermediateNode = INodes.SpokeNode(reg, parents, formatting)
        
        return reg1, exp + [intermediateNode], [intermediateNode]



################################################################################
# RETURN NODE
################################################################################

class ReturnNode(ASTNode):
    def __init__(self, lineno, clauseno, exp ):
        super(ReturnNode, self).__init__( RETURN, lineno, clauseno, [exp] )
        
    def getReturnExpression(self):
        return self.children[0]
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getReturnExpression().check(symbolTable, flags)
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
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getVariable().check(symbolTable, flags)
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

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
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
    
    def getValue(self):
        return self.children[0]
    
    #TODO: CHECK IF ID
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getValue().check(symbolTable, flags)
        self.type = self.getValue().type
        
        # Can't raise out of upper bounds exception til runtime?
        # maybe just do all at runtime? This won't work since index is a node/factor
        # maybe (index.getFactorType() == NUMBER and self.index.getValue() < 0)
        
        if self.index < 0:
            print "Array Index Out Of Bounds"
            raise ArrayIndexOutOfBoundsException(self.lineno, self.clauseno)

class ArrayAssignmentNode(AssignmentNode):
    def __init__(self, lineno, clauseno, array_access, expression ):
        super(ArrayAssignmentNode, self).__init__(lineno, clauseno, array_access, expression)
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        idNode = self.getDestination().getValue()
        self.variableCheck(symbolTable, flags, idNode.getValue())

class ArrayDeclarationNode(DeclarationNode):
    def __init__(self, lineno, clauseno, variableName, typeNode,  length):
        super(ArrayDeclarationNode, self).__init__( lineno, clauseno, variableName, typeNode )
        self.length = length
    
    def check(self, symbolTable, flags):
        self.length.check(symbolTable, flags)
        if self.length.type != NUMBER:
            print "Array declaration exception"
            raise ArrayDeclarationException(self.lineno, self.clauseno)
        super(ArrayDeclarationNode, self).check(symbolTable, flags)



################################################################################
# CONDITIONAL NODES - Loops and If statements
################################################################################

class ConditionalNode(ASTNode):
    def __init__(self, nodeType, lineno, clauseno, children ):
        super(ConditionalNode, self).__init__(nodeType, lineno, clauseno, children) #Children always come in expr, body, other

    def getExpression(self):
        return self.children[0]

    def getBody(self):
        return self.children[1]

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getExpression().check(symbolTable, flags)
        self.getBody().check(symbolTable, flags)
        
class LoopNode(ConditionalNode):
    def __init__(self, lineno, clauseno, exp, body ):
        super(LoopNode, self).__init__(LOOP, lineno, clauseno, [exp, body])
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        newSymbolTable = SymbolTable(symbolTable)
        super(LoopNode, self).check(newSymbolTable, flags)
        
class IfNode(ConditionalNode):
    def __init__(self, lineno, clauseno, exp, thenBody, nextLogicalClause = None ):
        super(IfNode, self).__init__(IF, lineno, clauseno, [exp, thenBody, nextLogicalClause])

        def getNextLogicalClause(self):
            return self.children[2]

        def check(self, symbolTable, flags):
            self.setSymbolTable(symbolTable)
            newSymbolTable = SymbolTable(symbolTable)
            super(IfNode, self).check(newSymbolTable)
            nextLogicalClause = self.getNextLogicalClause();
            if nextLogicalClause != None:
                nextLogicalClause.check(newSymbolTable)

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
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getBody().check(symbolTable, flags)

class LogicalClausesNode(ASTNode):
    def __init__(self, lineno, clauseno, logicalClause, logicalClauses):
        super(LogicalClausesNode, self).__init__(LOGICALCLAUSES, lineno, clauseno, [logicalClause, logicalClauses])
    
    def getLogicalClause(self):
        return self.children[0]

    def getLogicalClauses(self):
        return self.children[1]

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getLogicalClause().check(symbolTable, flags)
        
        logicalClauses = self.getLogicalClauses();
        if logicalClauses != None:
            logicalClauses.check(symbolTable, flags)



################################################################################
# FUNCTION DECLARATION NODES
################################################################################

class FunctionDeclarationNode(DeclarationNode):
    def __init__(self, lineno, clauseno, functionName, arguments, returnType, body ):
        super(FunctionDeclarationNode, self).__init__( lineno, clauseno, functionName, returnType )
        self.arguments = arguments
        self.body = body
    
    def getName(self):
        return self.children[0]
        
    def getArguments(self):
        return self.arguments
        
    def getBody(self):
        return self.body
    
    def getReturnType(self):
        return self.children[1]
    
    # TODO CHECK RETURN VALUE SAME AS RETURN TYPE
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)        
        super(FunctionDeclarationNode, self).check(symbolTable, flags)
        newSymbolTable = SymbolTable(symbolTable)
        self.getArguments().check(newSymbolTable, flags)
        if self.getBody():
            self.getBody().check(newSymbolTable, flags)
        # self.getReturnValue().check(newSymbolTable)

class ArgumentsNode(ASTNode):
    def __init__(self, lineno, clauseno, argument, arguments ):
        super(ArgumentsNode, self).__init__( ARGUMENTS, lineno, clauseno, [argument, arguments])
        
    def getArgument(self):
        return self.children[0]
    
    def getArguments(self):
        return self.children[1]

    def getLength(self):
        return 1 + self.getArguments().getLength()
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getArgument().check(symbolTable, flags)
        if self.getArguments():
            self.getArguments().check(symbolTable, flags)

class ArgumentNode(ASTNode):
    def __init__(self, lineno, clauseno, argumentDeclaration, reference = False):
        super(ArgumentNode, self).__init__( ARGUMENT, lineno, clauseno, [argumentDeclaration])
        self.reference = reference
    
    def getArgument(self):
        return self.children[0]
    
    def getLength(self):
        return 1
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getArgument().check(symbolTable, flags)



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
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        func = symbolTable.lookupCurrLevelAndEnclosingLevels(self.getName())
        self.getArguments().check(symbolTable, flags)
        if not func:
            print "Function not in symbol table"
            raise FunctionMissingException(self.lineno, self.clauseno)
        elif func.getArguments().getLength() != self.getArguments().getLength():
            print "Function Argument Count Exception"
            raise FunctionArgumentCountException(self.lineno, self.clauseno)
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
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)    
        self.getArgument().check(symbolTable, flags)
        if self.getArguments():
            self.getArguments().check(symbolTable, flags)        
        
class FunctionArgumentNode(ASTNode):
    def __init__(self, lineno, clauseno, exp):
        super(FunctionArgumentNode, self).__init__( FUNCTION_ARGUMENT, lineno, clauseno, [exp] )
        
    def getExpression(self):
        return self.children[0]
    
    def getLength(self):
        return 1
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)    
        self.getExpression().check(symbolTable, flags)
        self.type = self.getExpression().type

class FunctionBodyNode(ASTNode):
    def __init__(self, lineno, clauseno, statementList, functionBody):
        super(FunctionBodyNode, self).__init__( FUNCTION_BODY, lineno, clauseno, [statementList, functionBody])
    
    def getStatementList(self):
        return self.children[0]
        
    def getFunctionBody(self):
        return self.children[1]
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getStatementList().check(symbolTable, flags)
        self.getFunctionBody().check(symbolTable, flags)
        


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
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)  
        self.getFunction().check(symbolTable, flags)
        if self.getFunctions():
            self.getFunctions().check(symbolTable, flags)



################################################################################
# CODE SEPERATOR NODE - Seperates code from the functions declared at the end
################################################################################

class CodeSeparatorNode(ASTNode):
    def __init__(self, lineno, clauseno, statementList, functions = None ):
        super(CodeSeparatorNode, self).__init__( CODE_SEP, lineno, clauseno, [statementList, functions])
        
    def getStatementList(self):
        return self.children[0]
        
    def getFunctions(self):
        return self.children[1]
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        functions = self.getFunctions()
        if functions:
            functions.check(symbolTable, flags)
        self.getStatementList().check(symbolTable, flags)
        
        
class CommentNode(ASTNode):
    def __init__(self, lineno, clauseno, comment):
        super(CommentNode, self).__init__( COMMENT, lineno, clauseno, [comment])
    
    def getComment(self):
        return self.children[0]
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        pass    
    
# This module contains the nodes created by the parser.
import grammarExceptions as exception
from SymbolTable import SymbolTable
from RegisterMap import RegisterMap
import tokRules
import intermediateNodes as INodes
import re
import labels

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
FUNCTION = 'function'
ARRAY_DEC = 'array_declaration'
ARRAY_ASS = 'array_assignment'

################################################################################
# GLOBALS
################################################################################
IN_MEMORY = True
IN_REGISTER = False

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
            raise exception.BinaryException(self.lineno, self.clauseno)
        
        op = self.getOperator()
        if re.match( tokRules.t_PLUS, op ) or re.match( tokRules.t_MINUS, op ) or re.match( tokRules.t_MULTIPLY, op ):
            flags[BINARY_OP].add(('%s' %labels.overFlowLabel))
        elif re.match( tokRules.t_DIVIDE, op ) or re.match( tokRules.t_MOD, op ):
            flags[BINARY_OP].add(('%s' %labels.divisionByZeroLabel))
    
    def translate(self, registersDict, reg, parents):
        def translateOperation(destReg, nextReg, parents):
            op = self.getOperator()
            if re.match( "%s$"%tokRules.t_PLUS, op ):
                intermediateNode = INodes.AddNode(destReg, nextReg, parents)
            
            elif re.match( "%s$"%tokRules.t_MINUS, op ):
                intermediateNode = INodes.SubNode(destReg, nextReg, parents)

            elif re.match( "%s$"%tokRules.t_MULTIPLY, op ):
                intermediateNode = INodes.MulNode(destReg, nextReg, parents)

            elif re.match( "%s$"%tokRules.t_DIVIDE, op ):
                intermediateNode = INodes.DivNode(destReg, nextReg, parents)

            elif re.match( "%s$"%tokRules.t_MOD, op ):
                intermediateNode = INodes.ModNode(destReg, nextReg, parents)

            elif re.match("%s$"%tokRules.t_B_OR, op ):
                intermediateNode = INodes.OrNode(destReg, nextReg, parents)

            elif re.match( "%s$"%tokRules.t_B_XOR, op ):
                intermediateNode = INodes.XORNode(destReg, nextReg, parents)
                
            elif re.match( "%s$"%tokRules.t_B_AND, op ):
                intermediateNode = INodes.AndNode(destReg, nextReg, parents)
            
            elif re.match( "%s$"%tokRules.t_L_EQUAL, op ):
                intermediateNode = INodes.EqualNode(destReg, nextReg, parents)
                
            elif re.match( "%s$"%tokRules.t_L_LESS_THAN, op ):
                intermediateNode = INodes.LessThanNode(destReg, nextReg, parents)
                
            elif re.match( "<=", op ):
                intermediateNode = INodes.LessThanEqualNode(destReg, nextReg, parents)
                
            elif re.match( "%s$"%tokRules.t_L_GREATER_THAN, op ):
                intermediateNode = INodes.GreaterThanNode(destReg, nextReg, parents)
                
            elif re.match( ">=", op ):
                intermediateNode = INodes.GreaterThanEqualNode(destReg, nextReg, parents)
                
            elif re.match( "%s$"%tokRules.t_L_NOT_EQUAL, op ):
                intermediateNode = INodes.NotEqualNode(destReg, nextReg, parents)
                
            # elif re.match( "%s$"%tokRules.t_L_AND, op ):
            #                intermediateNode = INodes.AndNode(destReg, nextReg, parents)
            #                
            #            elif re.match( "%s$"%tokRules.t_L_OR, op ):
            #                intermediateNode = INodes.OrNode(destReg, nextReg, parents)
            
            return destReg, [intermediateNode], [intermediateNode]
            
            
        reg1, exp1, parents = self.getLeftExpression().translate(registersDict, reg, parents)
        reg2, exp2, parents = self.getRightExpression().translate(registersDict, reg1, parents)
        reg, exp3, parents = translateOperation(reg, reg1, parents)
        reg = reg + (reg2 - reg1)
        return reg + 1, (exp1 + exp2 + exp3), parents

class LogicalSeperatorNode(BinaryNode):
    def __init__(self, lineno, clauseno, operator, children ):
        super(LogicalSeperatorNode, self).__init__( lineno, clauseno, operator, children )
    
    def translate(self, registersDict, reg, parents):
        def translateOperation(parents):
            op = self.getOperator()
            logicalExpressionLabelNode = INodes.LabelNode(INodes.makeUniqueLabel("evaluate_start"), parents)
            reg1, exp1, parents = self.getLeftExpression().translate(registersDict, reg, [logicalExpressionLabelNode])
            logicalExpressionEndLabelNode = INodes.LabelNode(INodes.makeUniqueLabel("evaluate_end"), [])
            if re.match( "%s$"%tokRules.t_L_AND, op ):
                checkNode = INodes.JumpTrueNode(reg, logicalExpressionEndLabelNode, parents)
            else:
                checkNode = INodes.JumpFalseNode(reg, logicalExpressionEndLabelNode, parents)
            reg2, exp2, parents = self.getRightExpression().translate(registersDict, reg1, [checkNode])
            jumpNode = INodes.JumpNode( logicalExpressionLabelNode, parents )
            logicalExpressionLabelNode.setParents(parents + [jumpNode])
            logicalExpressionEndLabelNode.setParents([jumpNode]) 
                   
            iNodes = []
            iNodes.append(logicalExpressionLabelNode)
            iNodes += exp1
            iNodes.append(checkNode)
            iNodes += exp2
            iNodes.append(jumpNode)
            iNodes.append(logicalExpressionEndLabelNode)
            return reg2, iNodes, [logicalExpressionEndLabelNode]
        
        reg, exp, parents = translateOperation(parents)
        return reg, exp, parents
        

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
            raise exception.UnaryException(self.lineno, self.clauseno)
        op = self.getOperator()
        if re.match("ate", op) or re.match("drank", op):
            flags[UNARY_OP].add(('%s' %labels.overFlowLabel))
    
    def translate( self, registersDict, reg, parents ):
        def transUnOp(destReg, node, registersDict, parents):
            op = self.getOperator()
            if re.match( "ate", op ):
                register, inMemory = registersDict.lookupCurrLevelAndEnclosingLevels(node.getValue())
                intermediateNode = [INodes.IncNode(register, parents)]
                parents = intermediateNode
            elif re.match( "drank", op ):
                register, inMemory = registersDict.lookupCurrLevelAndEnclosingLevels(node.getValue())
                intermediateNode = [INodes.DecNode(register, parents)]
                parents = intermediateNode
            elif re.match( "%s$"%tokRules.t_B_NOT, op ):
                reg1, exp, parents = node.translate(registersDict, destReg, parents)
                intermediateNode = [INodes.NotNode(destReg, parents)]
                parents = intermediateNode
                destReg = reg1
                intermediateNode = exp + intermediateNode
            elif re.match( "%s$"%tokRules.t_MINUS, op ):
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
    
    def getVariable(self):
        return self.children[0]
    
    def getExpression(self):
        return self.children[1]
        
    def variableCheck(self, symbolTable, flags, variable):
        expr = self.getExpression()
        V = symbolTable.lookupCurrLevelAndEnclosingLevels(variable)
        expr.check(symbolTable, flags)
        if not V:
            raise exception.AssignmentNullException(self.lineno, self.clauseno)
        else:
            expr.check(symbolTable, flags)
            if V.type == expr.type:
                self.type = expr.type
            else:
                raise exception.AssignmentTypeException(self.lineno, self.clauseno)
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.variableCheck(symbolTable, flags, self.getVariable())
        
    def translate(self, registersDict, reg, parents):
        register, inMemory = registersDict.lookupCurrLevelAndEnclosingLevels(self.getVariable())
        if inMemory:
            self.getExpression().memoryLocation
            intermediateNode = INodes.ImmMovNode(register, self.getExpression().memoryLocation, parents)
            return reg, [intermediateNode], [intermediateNode]
        else:
            if isinstance(self.getExpression(), NumberNode) or isinstance(self.getExpression(), LetterNode):
                intermediateNode = INodes.ImmMovNode( register, self.getExpression().getValue(), parents)
                returnExp = [intermediateNode]
            else:
                resultReg = reg 
                reg, exp, parents = self.getExpression().translate(registersDict, reg, parents)
                intermediateNode = INodes.MovNode(register, resultReg, parents)
                returnExp = (exp + [intermediateNode])
            
            return reg, returnExp, [intermediateNode]
        
class DeclarationNode(StatementNode):
    def __init__(self, lineno, clauseno, variableName, typeNode ):
        super(DeclarationNode, self).__init__( DECLARATION, lineno, clauseno, [variableName, typeNode] )
        
    
    def getVariable(self):    
        return self.children[0]
        
    # Returns type node's type.
    def getType(self):
        return self.children[1].getType()

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        # T = symbolTable.lookupCurrLevelAndEnclosingLevels(self.type)
        V = symbolTable.lookupCurrLevelOnly(self.getVariable())
        # if T == None:
            # error("Unknown Type")
        if V:
            raise exception.DeclarationException(self.lineno, self.clauseno)
        else:   
            self.children[1].check(symbolTable, flags)
            self.type = self.children[1].type
            symbolTable.add(self.getVariable(), self)
    
    def translate( self, registersDict, reg, parents ):
        if self.getType() == SENTENCE:
            registersDict.add(self.getVariable(), (reg, IN_MEMORY))
        else:
            registersDict.add(self.getVariable(), (reg, IN_REGISTER))
        return reg+1, [], parents


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
    sentenceCount = 0
    def __init__(self, lineno, clauseno, child ):
        super(SentenceNode, self).__init__( SENTENCE, lineno, clauseno, child )
        self.memoryLocation = None
    
    # Returns list of string and it's newlines
    def newLineSplitter(self, string):
        newline = r'"\n"'
        newlineLen = len(newline)
        copy = string
        splitList = []
        while copy!= "":
            if newline in copy:
                firstOccurance = copy.index(newline)
            else:
                firstOccurance = -1
            if copy[0:firstOccurance]:
                splitList.append(copy[0:firstOccurance])
            if newline in copy:
                splitList.append(newline)
                copy = copy[(firstOccurance+newlineLen):-1]
            else:
                copy = ""
        return splitList
    
    def check(self, symbolTable, flags):
        super(SentenceNode, self).check(symbolTable, flags)
        if not self.memoryLocation:
            split = self.newLineSplitter(self.getValue())
#            split = self.getValue().split
#            newLines = self.getValue().index("\n")
#            for newline in len(newLines):
            
            
            self.memoryLocation = 'sentence%d' %SentenceNode.sentenceCount
            flags[SENTENCE].add((self.memoryLocation, self.getValue()))
            SentenceNode.sentenceCount += 1
    
    def translate(self, registersDict, reg, parents):
        intermediateNode = INodes.ImmMovNode(reg, self.memoryLocation, parents)
        return reg + 1, [intermediateNode], [intermediateNode]

class IDNode(Factor):
    def __init__(self, lineno, clauseno, child ):
        super(IDNode, self).__init__( ID, lineno, clauseno, child )
        self.register = None
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        V = symbolTable.lookupCurrLevelAndEnclosingLevels(self.getValue())
        if V:
            self.type = V.type
        else:
            raise exception.IDNotDeclaredException(self.lineno, self.clauseno)
    
    def getRegister(self, registersDict):
        register, inMemory = registersDict.lookupCurrLevelAndEnclosingLevels(self.getValue())
        return register
        
    def translate(self, registersDict, reg, parents):
        register, inMemory = registersDict.lookupCurrLevelAndEnclosingLevels(self.getValue())
        self.register = register
        intermediateNode = INodes.MovNode(reg, register, parents)
        return reg + 1 , [intermediateNode], [intermediateNode]



################################################################################
# IO NODES
################################################################################

class IONode(ASTNode):
    def __init__(self,  nodeType, lineno, clauseno, child ):
        super(IONode, self).__init__( nodeType, lineno, clauseno, [child] )
    
    def getIDType(self, expression):
        if expression.getNodeType() == FACTOR:
            if expression.getFactorType() == ID:
                node = self.symbolTable.lookupCurrLevelAndEnclosingLevels(expression.getValue())
                idType = node.getType()
            else:
                idType = expression.getFactorType()
        else:
            # If not a factor, must be of type number since letters are only 
            # valid as factors and not as part of operations or expressions
            idType = NUMBER
        return idType


        

class SpokeNode(IONode):
    def __init__(self, lineno, clauseno, child ):
        super(SpokeNode, self).__init__( SPOKE, lineno, clauseno, child )
    
    def getExpression(self):
        return self.children[0]
        
    def getPrintFunction(self, idType):        
        formatting = ""
        if idType == NUMBER:
            formatting = labels.printNumberLabel
        elif idType == LETTER:
            formatting = labels.printLetterLabel
        elif idType == SENTENCE: #TODO, IS THIS RIGHT?
            formatting = labels.printSentenceLabel
        return formatting

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.symbolTable = symbolTable
        self.getExpression().check(symbolTable, flags)
        flags[SPOKE].add( self.getExpression().type )
    
    def translate(self, registersDict, reg, parents):
        spokeExpression = self.getExpression()
        reg1, exp, parents = spokeExpression.translate(registersDict, reg, parents)    
        idType = self.getIDType(self.getExpression())
        # formatting = "output" + self.getFormatting(idType)
        functionCall = self.getPrintFunction(idType)
        # Should catch error here if formatting not set...
        intermediateNode = INodes.SpokeNode(reg, parents, functionCall)
        return reg1, exp + [intermediateNode], [intermediateNode]


class InputNode(IONode):
    def __init__(self, lineno, clauseno, variable ):
        super(InputNode, self).__init__( INPUT, lineno, clauseno, variable )
        
    def getVariable(self):
        return self.children[0]
        
    def getFormatting(self, idType):        
        formatting = ""
        if idType == NUMBER:
            formatting = labels.inputNumberLabel
        elif idType == LETTER:
            formatting = labels.inputLetterLabel
        return formatting
        
    #TODO: CHECK IF ID    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        idType = self.getIDType(self.getVariable())
        flags[INPUT].add(idType)
        self.getVariable().check(symbolTable, flags)
        self.type = self.getVariable().type

    def translate(self, registersDict, reg, parents):
        idType = self.getIDType(self.getVariable())
        # Incase first declaration of variable.
        variable = self.getVariable().getValue()
        V = registersDict.lookupCurrLevelAndEnclosingLevels(variable)
        if not V:
            registersDict.add(variable, (reg, IN_REGISTER))
            register = reg
        else:
            register, inMemory = V
        formatting = self.getFormatting(idType)
        
        # Should catch error here if formatting not set...
        intermediateNode = INodes.InputNode(register, parents, formatting)
        
        return reg+1, [intermediateNode], [intermediateNode]



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
        
    def translate(self, registerDict, reg, parents): 
        returnReg = reg
        reg, exp, parents = self.getReturnExpression().translate(registerDict, reg, parents)
        intermediateNode = INodes.ReturnNode(returnReg, parents)
        return reg, (exp + [intermediateNode]), [intermediateNode]
        


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
    def __init__(self, lineno, clauseno, variable, indexExpression ):
        super(ArrayAccessNode, self).__init__( INPUT, lineno, clauseno, [variable, indexExpression] )
    
    #TODO: CHECK IF ID
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getValue().check(symbolTable, flags)
        self.type = self.getValue().type
        
        # Can't raise out of upper bounds exception til runtime?
        # maybe just do all at runtime? This won't work since index is a node/factor
        # maybe (index.getFactorType() == NUMBER and self.index.getValue() < 0)
        
        if self.index < 0:
            raise exception.ArrayIndexOutOfBoundsException(self.lineno, self.clauseno)
    
    def getVariable(self):
        return self.children[0]
    
    def getIndexExpression(self):
        return self.children[1]
        
    def variableCheck(self, symbolTable, flags, variable):
        expr = self.getIndexExpression()
        V = symbolTable.lookupCurrLevelAndEnclosingLevels(self.getVariable().getValue())
        expr.check(symbolTable, flags)
        if not V:
            raise exception.AssignmentNullException(self.lineno, self.clauseno)
        self.type = V.type
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.variableCheck(symbolTable, flags, self.getVariable())
        
    def translate(self, registersDict, reg, parents):
        baseRegister, inMemory = registersDict.lookupCurrLevelAndEnclosingLevels(self.getVariable().getValue())
        destReg = reg
        reg, indexINodes, indexParents = self.getIndexExpression().translate(registersDict, destReg, parents)
        arrayAccessNode = INodes.ArrayAccessNode(destReg, baseRegister, destReg, indexParents)
        arrayMovNode = INodes.ArrayMovNode(destReg, destReg, False, [arrayAccessNode])
        
        iNodes = []
        iNodes.extend(indexINodes)
        iNodes.append(arrayAccessNode)
        iNodes.append(arrayMovNode)
        return reg, iNodes, [arrayMovNode]

class ArrayAssignmentNode(AssignmentNode):
    def __init__(self, lineno, clauseno, arrayAccess, expression ):
        super(ArrayAssignmentNode, self).__init__(lineno, clauseno, arrayAccess, expression)
        self.arrayAccess = arrayAccess
        self.expression = expression
    
    def getArrayAccess(self):
        return self.arrayAccess
    
    def getExpression(self):
        return self.expression
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getExpression().check(symbolTable, flags)
        self.getArrayAccess().check(symbolTable, flags)
        # TODO: Check for type match here
        # expr.check(symbolTable, flags)
        # print V, expr
        # if V.type == expr.type:
        #     self.type = expr.type
        # else:
        #     raise exception.AssignmentTypeException(self.lineno, self.clauseno)
    
    def translate(self, registersDict, reg, parents):
        arrayAccessReg = reg
        reg, arrayAccessNodes, parents = self.getArrayAccess().translate(registersDict, arrayAccessReg, parents)
        arrayAccessNodes = arrayAccessNodes[:-1] # Remove the last instruction to move the value into the register, maintains base pointer
        parents = [arrayAccessNodes[-1]]
        expressionReg = reg
        reg, expressionNodes, parents = self.getExpression().translate(registersDict, expressionReg, parents)
        movNode = INodes.ArrayMovNode(arrayAccessReg, expressionReg, True,  parents)
        
        iNodes = []
        iNodes.extend(arrayAccessNodes)
        iNodes.extend(expressionNodes)
        iNodes.append(movNode)
        
        return reg, iNodes, [movNode]

class ArrayDeclarationNode(StatementNode):
    def __init__(self, lineno, clauseno, variableName, typeNode,  length):
        super(ArrayDeclarationNode, self).__init__(ARRAY_DEC, lineno, clauseno, [variableName, typeNode] )
        self.length = length
    
    def getVariable(self):    
        return self.children[0]
    
    # Returns the type of the array.
    def getType(self):
        return self.children[1].getType()
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        # T = symbolTable.lookupCurrLevelAndEnclosingLevels(self.type)
        V = symbolTable.lookupCurrLevelOnly(self.getVariable())
        # if T == None:
            # error("Unknown Type")
        if V:
            print "Declaration Exception"
            raise exception.DeclarationException(self.lineno, self.clauseno)
        else:   
            self.children[1].check(symbolTable, flags)
            self.type = self.children[1].type
            symbolTable.add(self.getVariable(), self)
            
        if self.length.factorType != NUMBER:
            print "Array declaration exception"
            # TODO, uncomment me and make me work
            # raise ArrayDeclarationException(self.lineno, self.clauseno)
    
    def translate(self, registersDict, reg, parents):
        lengthReg = reg
        reg, lengthNodes, lengthParents = self.length.translate(registersDict, reg, parents)
        mallocNode = INodes.MallocNode(reg, parents, lengthReg)
        registersDict.add(self.getVariable(), (reg, IN_REGISTER))
        return reg + 1, lengthNodes + [mallocNode], [mallocNode]



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
    
    def translate(self, registersDict, reg, parents):
        newRegistersDict = RegisterMap(registersDict)
        loopStartLabelNode = INodes.LabelNode(INodes.makeUniqueLabel("loop_start"), parents)
        
        reg1, expressionNodes, postExpressionParents = self.getExpression().translate(newRegistersDict, reg, [loopStartLabelNode])
        
        loopEndLabelNode = INodes.LabelNode(INodes.makeUniqueLabel("loop_end"), []) #Defined here and parents set later
        
        falseCheckNode = INodes.JumpFalseNode(reg, loopEndLabelNode, postExpressionParents)
        
        reg2, bodyNodes, postBodyParents = self.getBody().translate(newRegistersDict, reg1, [falseCheckNode])
        
        jumpNode = INodes.JumpNode(loopStartLabelNode, postBodyParents)
        loopStartLabelNode.setParents(parents +[jumpNode])
        loopEndLabelNode.setParents([jumpNode])
        
        
        iNodes = []
        iNodes.append(loopStartLabelNode)
        iNodes += expressionNodes
        iNodes.append(falseCheckNode)
        iNodes += bodyNodes
        iNodes.append(jumpNode)
        iNodes.append(loopEndLabelNode)
        
        return reg2, iNodes, [loopEndLabelNode]


class IfNode(ConditionalNode):
    def __init__(self, lineno, clauseno, exp, thenBody, logicalClauses = None ):
        super(IfNode, self).__init__(IF, lineno, clauseno, [exp, thenBody, logicalClauses])
    
    def getLogicalClauses(self):
        return self.children[2]

    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        newSymbolTable = SymbolTable(symbolTable)
        super(IfNode, self).check(newSymbolTable, flags)
        nextLogicalClause = self.getLogicalClauses();
        if nextLogicalClause != None:
            nextLogicalClause.check(newSymbolTable, flags)
    
    def translate(self, registersDict, reg, parents):
        newRegistersDict = RegisterMap(registersDict)
        # Get a list of all logical sections
        logicalClause = self
        logicalClauses = self.getLogicalClauses() #instance of logicalclausesnode
        logicalNodes = [logicalClause]
        while(logicalClauses != None and logicalClauses.getLogicalClauses() != None):
            logicalClause = logicalClauses.getLogicalClause()
            logicalClauses = logicalClauses.getLogicalClauses()
            logicalNodes.append(logicalClause)
        if logicalClauses != None:
            logicalNodes.append(logicalClauses)
        
        #Iterate over the logical sections
        numLogicalNodes = len(logicalNodes)
        endParents = []
        
        startLabelNode = INodes.LabelNode(INodes.makeUniqueLabel("conditional_start"), parents)
        endLabelNode = INodes.LabelNode(INodes.makeUniqueLabel("conditional_end"), [])
        
        iNodes = [startLabelNode]
        for i, logicalNode in enumerate(logicalNodes):
            if(i < numLogicalNodes - 1):
                falseLabelNode = INodes.LabelNode(INodes.makeUniqueLabel("conditional_next"), [])
            else:
                falseLabelNode = endLabelNode
            
            # Evaluate expression if present
            expression = logicalNode.getExpression()
            if expression != None:
                checkReg = reg
                reg, expressionNodes, postExpressionParents = expression.translate(newRegistersDict, reg, [startLabelNode])
                trueCheckNode = INodes.JumpTrueNode(checkReg, falseLabelNode, postExpressionParents)
                falseLabelNode.setParents([trueCheckNode])
            else:
                trueCheckNode = None
                
            # Evaulate body
            if trueCheckNode:
                reg, bodyNodes, postBodyParents = logicalNode.getBody().translate(newRegistersDict, reg, [trueCheckNode])
            else:
                reg, bodyNodes, postBodyParents = logicalNode.getBody().translate(newRegistersDict, reg, [startLabelNode])
            
            # End of body - jump or nothing if at end
            if falseLabelNode != endLabelNode:
                jumpNode = INodes.JumpNode(endLabelNode, postBodyParents)
                endParents.append(jumpNode)
                falseLabelNode.setParents(falseLabelNode.parents + [jumpNode])
            else:

                jumpNode = None
                endParents.extend(postBodyParents)
            
            # Add all the nodes together into the iNodes list
            if trueCheckNode:
                iNodes += expressionNodes
                iNodes.append(trueCheckNode)
            iNodes += bodyNodes
            if jumpNode:
                iNodes.append(jumpNode)
            iNodes.append(falseLabelNode)
            
            startLabelNode = falseLabelNode
            
        # Set the parents of the end node to also have the end jumps from 
        # previous clauses
        endLabelNode.setParents(endLabelNode.parents + endParents)
        return reg, iNodes, [endLabelNode]
            
class ElseIfNode(ConditionalNode):
    def __init__(self, lineno, clauseno, exp, thenBody):
        super(ElseIfNode, self).__init__(ELSEIF, lineno, clauseno, [exp, thenBody])
    
    def getLogicalClauses(self):
        return None

# Some way to inherit this from conditionalNode as well? Although I suppose it's
# not that conditional in that there is no logical check?
class ElseNode(ASTNode):
    def __init__(self, lineno, clauseno, thenBody):
        super(ElseNode, self).__init__(ELSE, lineno, clauseno, [thenBody])
    
    def getLogicalClauses(self):
        return None
    
    def getExpression(self):
        return None
    
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
        
    # def getArrayLocations(self):
    #     return self.getArguments().getArrayLocations(0)
    
    def getReturnType(self):
        return self.children[1]
    
    # TODO CHECK RETURN VALUE SAME AS RETURN TYPE
    def check(self, symbolTable, flags):    
        super(FunctionDeclarationNode, self).check(symbolTable, flags)
        # referenceCount = 0
        #    referenceLocations = self.getReferenceLocations()
        #    if len(referenceLocations):
        #        referenceCount = max(referenceLocations)
        # flags[FUNCTION].add((self.getName(), referenceCount))
        flags[FUNCTION].add(self.getName())
        self.setSymbolTable(symbolTable)    
        newSymbolTable = SymbolTable(symbolTable)
        self.getArguments().check(newSymbolTable, flags)
        if self.getBody():
            self.getBody().check(newSymbolTable, flags)
        # self.getReturnValue().check(newSymbolTable)
        
    def translate( self, registersDict, reg, parents ):
        reg, argsExp, parents = self.getArguments().translate(registersDict, reg, [], 0)
        reg, bodyExp, parents = self.getBody().translate(registersDict, reg, [argsExp[-1]])
        # It should have no parents?, uses no registers in declaration?
        intermediateNode = INodes.FunctionDeclarationNode( [], self.getName(), argsExp, bodyExp )
        return reg, [intermediateNode], parents

class ArgumentsNode(ASTNode):
    def __init__(self, lineno, clauseno, argument, arguments ):
        super(ArgumentsNode, self).__init__( ARGUMENTS, lineno, clauseno, [argument, arguments])
        
    def getArgument(self):
        return self.children[0]
    
    def getArguments(self):
        return self.children[1]

    def getLength(self):
        return 1 + self.getArguments().getLength() 
    
    def toList(self):
          return self.getArgument().toList() + self.getArguments().toList()
    
    # def getArrayLocations(self, position):
    #        return self.getArgument().getArrayLocations(position) + self.getArguments().getArrayLocations(position+1)
    
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getArgument().check(symbolTable, flags)
        if self.getArguments():
            self.getArguments().check(symbolTable, flags)
    
    def translate( self, registersDict, reg, parents, argNumber):
        reg, exp1, parents = self.getArgument().translate(registersDict, reg, parents, argNumber)
        reg, exp2, parents = self.getArguments().translate(registersDict, reg, parents, argNumber+1)
        return reg, (exp1 + exp2), parents
        
    

class ArgumentNode(ASTNode):
    def __init__(self, lineno, clauseno, argumentDeclaration, array = False):
        super(ArgumentNode, self).__init__( ARGUMENT, lineno, clauseno, [argumentDeclaration])
        self.isArray = array
        self.intermediateNode = None
    
    def getArgument(self):
        return self.children[0]
    
    def getLength(self):
        return 1
        
    def toList(self):
        return [self]
    # def getArrayLocations(self, position):
    #         if self.reference:
    #             return [position]
    #         else:
    #             return []
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getArgument().check(symbolTable, flags)
        self.type = self.getArgument().type
    
    def translate( self, registersDict, reg, parents, argNumber ):
        registersDict.add(self.getArgument().getVariable(), (reg, IN_REGISTER))
        intermediateNode = INodes.ArgumentNode( reg, parents, argNumber, self.isArray )
        self.intermediateNode = intermediateNode
        return reg + 1, [intermediateNode], [intermediateNode]



################################################################################
# FUNCTION CALL NODES
################################################################################

class FunctionCallNode(ASTNode):
    def __init__(self, lineno, clauseno, functionName, arguments):
        super(FunctionCallNode, self).__init__( FUNCTION_CALL, lineno, clauseno, [functionName, arguments] )
        # self.relatedFunction = None
        
    def getName(self):
        return self.children[0]
        
    def getArguments(self):
        return self.children[1]
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        func = symbolTable.lookupCurrLevelAndEnclosingLevels(self.getName())
        self.getArguments().check(symbolTable, flags)
        if not func:
            raise exception.FunctionMissingException(self.lineno, self.clauseno)
        elif func.getArguments().getLength() != self.getArguments().getLength():
            raise exception.FunctionArgumentCountException(self.lineno, self.clauseno)
        else:
            # self.relatedFunction = func
            for passingArg, functionArg in zip(self.getArguments().toList(), func.getArguments().toList()):
                if not passingArg.type == functionArg.type:
                    raise exception.FunctionArgumentTypeMisMatch(self.lineno, self.clauseno)
            self.type = func.type
    
    def translate(self, registerDict, reg, parents):
        argumentReg = reg
        reg, exp, parents = self.getArguments().translate(registerDict, reg, parents)
        # reg, exp, parents = self.getArguments().translate(registerDict, reg, parents, self.relatedFunction.getArrayLocations(), 0)
        registersPushed = self.getArguments().getLength()
        #intermediateNode = INodes.FunctionCallNode( argumentReg, parents, registersPushed, self.getName(), self.getArguments().toList())
        intermediateNode = INodes.FunctionCallNode(argumentReg, parents, registersPushed, self.getName())
        return reg, (exp + [intermediateNode]), [intermediateNode]
        

class FunctionArgumentsNode(ASTNode):
    def __init__(self, lineno, clauseno, argument, arguments = None):
        super(FunctionArgumentsNode, self).__init__( FUNCTION_ARGUMENTS, lineno, clauseno, [argument, arguments] )
    def getArgument(self):
        return self.children[0]
        
    def getArguments(self):
        return self.children[1]
    
    def getLength(self):
        return 1 + self.getArguments().getLength()
        
    def toList(self):
          return self.getArgument().toList() + self.getArguments().toList()
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)    
        self.getArgument().check(symbolTable, flags)
        if self.getArguments():
            self.getArguments().check(symbolTable, flags)
    
    def translate(self, registersDict, reg, parents):        
    # def translate(self, registersDict, reg, parents, refLocations, argument):
        # reg, exp2, parents = self.getArguments().translate(registersDict, reg, parents, refLocations, argument+1)
        # reg, exp1, parents = self.getArgument().translate(registersDict, reg, parents, refLocations, argument)
        reg, exp2, parents = self.getArguments().translate(registersDict, reg, parents)
        reg, exp1, parents = self.getArgument().translate(registersDict, reg, parents)
        return reg, (exp2 + exp1), parents #exp2 + exp1 so that arguments get pushed in reverse order.
        
        
class FunctionArgumentNode(ASTNode):
    def __init__(self, lineno, clauseno, exp):
        super(FunctionArgumentNode, self).__init__( FUNCTION_ARGUMENT, lineno, clauseno, [exp] )
        # self.intermediateNode = None
        
    def getExpression(self):
        return self.children[0]
    
    def getLength(self):
        return 1
        
    def toList(self):
        return [self]
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)    
        self.getExpression().check(symbolTable, flags)
        self.type = self.getExpression().type
        
    # def translate(self, registerDict, reg, parents, refLocations, argument):
    def translate(self, registerDict, reg, parents):
        # reference = False
        pushReg = reg
        # exp = []
        # if isinstance(self.getExpression(), IDNode) :
            # pushReg = self.getExpression().getRegister(registerDict)
        # else:
        reg, exp, parents = self.getExpression().translate(registerDict, reg, parents)
        # if argument in refLocations:
            # reference = True
        # intermediateNode = INodes.FunctionArgumentNode( pushReg, parents, argument, reference )
        intermediateNode = INodes.FunctionArgumentNode( pushReg, parents )
        # self.intermediateNode = intermediateNode
        return reg, (exp + [intermediateNode]), [intermediateNode]

class LookingGlassNode(ASTNode):
    def __init__(self, lineno, clauseno, statementList, returnStatement):
        super(LookingGlassNode, self).__init__( FUNCTION_BODY, lineno, clauseno, [statementList, returnStatement])
    
    def getStatementList(self):
        return self.children[0]
        
    def getReturnStatement(self):
        return self.children[1]
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        self.getStatementList().check(symbolTable, flags)
        self.getReturnStatement().check(symbolTable, flags)
        
    def translate(self, registersDict, reg, parents):
        reg, exp1, parents = self.getStatementList().translate(registersDict, reg, parents)
        reg, exp2, parents = self.getReturnStatement().translate(registersDict, reg, parents)
        return reg, (exp1+ exp2), parents


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
            
    def translate(self, registersDict, reg, parents):
        reg, functionExp, parents = self.getFunction().translate( registersDict, reg, parents )
        reg, functionsExp, parents = self.getFunctions().translate( registersDict, 0, [])
        return reg, (functionExp + functionsExp), parents


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
        
    def translate(self, registersDict, reg, parents):
        statementListReg, statementListExp, parents = self.getStatementList().translate(registersDict, reg, parents)
        functionsReg, functionsExp, parents = self.getFunctions().translate(registersDict, 0, [])
        return statementListReg, statementListExp, functionsExp, parents
        
class CommentNode(ASTNode):
    def __init__(self, lineno, clauseno, comment):
        super(CommentNode, self).__init__( COMMENT, lineno, clauseno, [comment])
    
    def getComment(self):
        return self.children[0]
        
    def check(self, symbolTable, flags):
        self.setSymbolTable(symbolTable)
        pass

class GrammarException(Exception):
    def __init__( self, lineno, clauseno ):
        self.lineno = lineno
        self.clauseno = clauseno
        self.message = ""

################################################################################
# SEMANTIC EXCEPTIONS
################################################################################
class SemanticException(GrammarException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(SemanticException, self).__init__(lineno, clauseno)       
        self.value = "Oh No! Silly you!" + value

class BinaryException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(BinaryException, self).__init__(lineno, clauseno, value)
        self.message = "Can only compute binary expressions that both have type number"

class LogicalException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(LogicalException, self).__init__(lineno, clauseno, value)
        self.message = "Can only compute logical expressions that both have type number"
        
class UnaryException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(UnaryException, self).__init__(lineno, clauseno, value)
        self.message = "Can only compute unary expression on something that has type number"

class AssignmentNullException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(AssignmentNullException, self).__init__(lineno, clauseno, value)
        self.message = "The variable you're trying to use has not been declared yet"

class AssignmentTypeException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(AssignmentTypeException, self).__init__(lineno, clauseno, value)
        self.message = "Assigning wrong type to variable."

class DeclarationException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(DeclarationException, self).__init__(lineno, clauseno, value)
        self.message = "Trying to redefine an already declared variable in this scope."

class ArrayIndexOutOfBoundsException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(ArrayIndexOutOfBoundsException, self).__init__(lineno, clauseno, value)
        self.message = "Trying to access an index that is out of the arrays bounds."

class ArrayDeclarationException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(ArrayDeclarationException, self).__init__(lineno, clauseno, value)
        self.message = "You can only assign a length to an array that is of type number."

class FunctionMissingException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(FunctionMissingException, self).__init__(lineno, clauseno, value)
        self.message = "Function you're trying to call does not exist."

class FunctionArgumentCountException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(FunctionArgumentCountException, self).__init__(lineno, clauseno, value)
        self.message = "Function you're trying to call does not take that number of arguments."
        
class FunctionArgumentTypeMisMatch(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(FunctionArgumentTypeMisMatch, self).__init__(lineno, clauseno, value)
        self.message = "Argument types in function you're trying to call do not match."

class IDNotDeclaredException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(IDNotDeclaredException, self).__init__(lineno, clauseno, value)
        self.message = "Error the variable you're trying to use has not yet been declared."
    

################################################################################
# SYNTAX EXCEPTIONS
################################################################################
class SyntaxException(GrammarException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(SyntaxException, self).__init__(lineno, clauseno)        
        self.value = "Oh No! You started writing utter nonsense." + value



################################################################################
# OTHER EXCEPTIONS
################################################################################
class DivisionByZeroException(GrammarException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(DivisionByZeroException, self).__init__(lineno, clauseno)       
        self.value = "Oops!" + value
    
class LexicalException(GrammarException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(LexicalException, self).__init__(lineno, clauseno)       
        self.value = "Oh No! Silly you!"
       
class NoMatchException(GrammarException):
    def __init__( self, value = "" ):
        super(NoMatchException, self).__init__(0, 0)
        self.value = "Oh No! You were writing such silly things at the start of the story." + value

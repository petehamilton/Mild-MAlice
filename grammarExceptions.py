class GrammarException(Exception):
    def __init__( self, lineno, clauseno ):
        self.lineno = lineno
        self.clauseno = clauseno

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

class LogicalException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(LogicalException, self).__init__(lineno, clauseno, value)

class UnaryException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(UnaryException, self).__init__(lineno, clauseno, value)

class AssignmentNullException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(AssignmentNullException, self).__init__(lineno, clauseno, value)

class AssignmentTypeException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(AssignmentTypeException, self).__init__(lineno, clauseno, value)

class DeclarationException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(AssignmentTypeException, self).__init__(lineno, clauseno, value)

class ArrayIndexOutOfBoundsException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(ArrayIndexOutOfBoundsException, self).__init__(lineno, clauseno, value)

class ArrayDeclarationException(SemanticException):
    def __init__( self, lineno, clauseno, value = "" ):
        super(ArrayDeclarationException, self).__init__(lineno, clauseno, value)

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
    

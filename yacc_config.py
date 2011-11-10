import Node as n
from Node import Node
from tokrules import tokens
import grammar_exceptions as e

UNARY_OP = "unary_op"
BINARY_OP = "binary_op"
FACTOR = "factor"
ASSIGNMENT = "assignment"
DECLARATION = "declaration"
SPOKE = "spoke"
STATEMENT_LIST = "statement_list"
TYPE = "type"



start = 'statement_list' # Optional as uses first rule
symbolTable = {}
class ParseError(Exception): 
    pass

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE', 'MOD'),
    ('left', 'B_AND', 'B_OR', 'B_XOR', 'B_NOT'),
)

def _parse_error(msg, coord):
    raise ParseError("%s: %s" % (coord, msg))  

def p_statement_list_sep_comma(p):
    'statement_list : statement SEP_COMMA statement_list'
    p[0] = Node(n.STATEMENT_LIST, p.lineno(1), p.clauseno(1), [p[1], p[3]])

def p_statement_list_sep_period(p):
    'statement_list : statement SEP_PERIOD statement_list'
    p[0] = Node(n.STATEMENT_LIST, p.lineno(1), p.clauseno(1), [p[1], p[3]])

def p_statement_list_statement(p):
    'statement_list : statement SEP_PERIOD'
    p[0] = p[1]

def p_statement_list_sep_and(p):
    'statement_list : statement SEP_AND statement_list'
    p[0] = Node(n.STATEMENT_LIST, p.lineno(1), p.clauseno(1), [p[1], p[3]])

def p_statement_list_sep_but(p):
    'statement_list : statement SEP_BUT statement_list'
    p[0] = Node(n.STATEMENT_LIST, p.lineno(1), p.clauseno(1), [p[1], p[3]])

def p_statement_list_sep_then(p):
    'statement_list : statement SEP_THEN statement_list'
    p[0] = Node(n.STATEMENT_LIST, p.lineno(1), p.clauseno(1), [p[1], p[3]])

def p_statement_alicespoke(p):
    'statement : expression PRINT_SPOKE'
    p[0] = Node(n.SPOKE, p.lineno(1), p.clauseno(1), [p[1]])

def p_statement_too(p):
    'statement : statement TOO'
    p[0] = p[1]

def p_statement_wasa(p):
    'statement : ID DEC_WAS DEC_A type'
    if p[1] in symbolTable:
        raise e.SemanticException( p.lineno(1), p.clauseno(1), "You already told me what '%s' was on line %d" %(p[1],  symbolTable[p[1]][1]) )
        
    else:    
        symbolTable[p[1]] = [p[4].children[0], p.lineno(1), False]
    p[0] = Node('declaration', p.lineno(1), p.clauseno(1), [p[1], p[4]])

def p_statement_became(p):
    'statement : ID ASSIGNMENT expression'
    p[0] = Node('assignment', p.lineno(1), p.clauseno(1), [p[1], p[3]])

# Have to implement for drank and ate
def p_statement_expression(p):
    'statement : expression'
    p[0] = p[1]

def p_type_number(p):
    'type : TYPE_NUMBER'
    p[0] = Node(n.TYPE, p.lineno(1), p.clauseno(1), [p[1]])

def p_type_letter(p):
    'type : TYPE_LETTER'
    p[0] = Node(n.TYPE, p.lineno(1), p.clauseno(1), [p[1]])

def p_expression_not(p):
    'expression : B_NOT expression'
    p[0] = Node(n.UNARY_OP, p.lineno(2), p.clauseno(2), [p[1], p[2]])

def p_expression_drank(p):
    'expression : ID DECREMENT'
    p[0] = Node(n.UNARY_OP, p.lineno(1), p.clauseno(1), [p[2], Node('factor', p.lineno(1), p.clauseno(1), ["ID", p[1]])])

def p_expression_ate(p):
    'expression : ID INCREMENT'
    p[0] = Node(n.UNARY_OP, p.lineno(1), p.clauseno(1), [p[2], Node('factor', p.lineno(1), p.clauseno(1), ["ID", p[1]])])

def p_expression_or(p):
    'expression : expression B_OR term1'
    p[0] = Node(n.BINARY_OP, p.lineno(1), p.clauseno(1), [p[2], p[1],p[3]])

def p_expression_xor(p):
    'expression : expression B_XOR term1'
    p[0] = Node(n.BINARY_OP, p.lineno(1), p.clauseno(1), [p[2], p[1],p[3]])

def p_expression_and(p):
    'expression : expression B_AND term1'
    p[0] = Node(n.BINARY_OP, p.lineno(1), p.clauseno(1), [p[2], p[1],p[3]])
    
def p_expression_term1(p):
    'expression : term1'
    p[0] = p[1]

def p_term1_plus(p):
    'term1 : term1 PLUS term2'
    p[0] = Node(n.BINARY_OP, p.lineno(1), p.clauseno(1), [p[2], p[1],p[3]])

def p_term1_minus(p):
    'term1 : term1 MINUS term2'
    p[0] = Node(n.BINARY_OP, p.lineno(1), p.clauseno(1), [p[2], p[1],p[3]])

def p_term1_term2(p):
    'term1 : term2'
    p[0] = p[1]

def p_term2_multiply(p):
    'term2 : term2 MULTIPLY factor'
    p[0] = Node(n.BINARY_OP, p.lineno(1), p.clauseno(1), [p[2], p[1],p[3]])

#Handles division by 0 constant
def p_term2_divide(p):
    'term2 : term2 DIVIDE factor'
    if p[3].children[1] == 0:
        print "Oops!"
        raise e.DivisionByZeroException(p.lineno(1), p.clauseno(1))
    p[0] = Node(n.BINARY_OP, p.lineno(1), p.clauseno(1), [p[2], p[1],p[3]])

def p_term2_mod(p):
    'term2 : term2 MOD factor'
    p[0] = Node(n.BINARY_OP, p.lineno(1), p.clauseno(1), [p[2], p[1],p[3]])

def p_term2_factor(p):
    'term2 : factor'
    p[0] = p[1]


def p_factor_number(p):
    'factor : NUMBER'
    p[0] = Node(n.FACTOR, p.lineno(1), p.clauseno(1), ["number", p[1]])

def p_factor_letter(p):
    'factor : LETTER'
    p[0] = Node(n.FACTOR, p.lineno(1), p.clauseno(1), ["letter", p[1]])

def p_factor_id(p):
    'factor : ID'
    p[0] = Node(n.FACTOR, p.lineno(1), p.clauseno(1), ["ID", p[1]])

    
def p_error(p):
    if p == None:
        raise e.NoMatchException()
    else:
        raise e.SyntaxException(p.lineno, p.clauseno)

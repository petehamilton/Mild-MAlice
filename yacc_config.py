import ASTNode
from tokrules import tokens
import grammar_exceptions as e

start = 'statement_list' # Optional as uses first rule
class ParseError(Exception): 
    pass

precedence = (
    ('left', 'B_OR'),
    ('left', 'B_XOR'),
    ('left', 'B_AND'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE', 'MOD'),
    ('right','INCREMENT', 'DECREMENT', 'B_NOT'),
)

def _parse_error(msg, coord):
    raise ParseError("%s: %s" % (coord, msg))  
    

def p_statement_list_sep_comma(p):
    'statement_list : statement SEP_COMMA statement_list'
    p[0] = ASTNode.StatementListNode(p.lineno(1), p.clauseno(1), [p[1], p[3]])

def p_statement_list_sep_period(p):
    'statement_list : statement SEP_PERIOD statement_list'
    p[0] = ASTNode.StatementListNode(p.lineno(1), p.clauseno(1), [p[1], p[3]])

def p_statement_list_statement(p):
    'statement_list : statement SEP_PERIOD'
    p[0] = p[1]

def p_statement_list_sep_and(p):
    'statement_list : statement SEP_AND statement_list'
    p[0] = ASTNode.StatementListNode(p.lineno(1), p.clauseno(1), [p[1], p[3]])

def p_statement_list_sep_but(p):
    'statement_list : statement SEP_BUT statement_list'
    p[0] = ASTNode.StatementListNode(p.lineno(1), p.clauseno(1), [p[1], p[3]])

def p_statement_list_sep_then(p):
    'statement_list : statement SEP_THEN statement_list'
    p[0] = ASTNode.StatementListNode(p.lineno(1), p.clauseno(1), [p[1], p[3]])

def p_statement_alicespoke(p):
    'statement : expression PRINT_SPOKE'
    p[0] = ASTNode.SpokeNode(p.lineno(1), p.clauseno(1), p[1])

def p_statement_too(p):
    'statement : statement TOO'
    p[0] = p[1]

def p_statement_wasa(p):
    'statement : ID DEC_WAS DEC_A type'
    p[0] = ASTNode.DeclarationNode(p.lineno(1), p.clauseno(1), [p[1], p[4]])

def p_statement_became(p):
    'statement : ID ASSIGNMENT expression'
    p[0] = ASTNode.AssignmentNode(p.lineno(1), p.clauseno(1), [p[1], p[3]])

# Have to implement for drank and ate
def p_statement_expression(p):
    'statement : expression'
    p[0] = p[1]

def p_type_number(p):
    'type : TYPE_NUMBER'
    p[0] = ASTNode.NumberTypeNode(p.lineno(1), p.clauseno(1))

def p_type_letter(p):
    'type : TYPE_LETTER'
    p[0] = ASTNode.LetterTypeNode(p.lineno(1), p.clauseno(1))

def p_expression_not(p):
    'expression : B_NOT expression'
    p[0] = ASTNode.UnaryNode(p.lineno(2), p.clauseno(2), p[1], p[2])

def p_expression_drank(p):
    'expression : ID DECREMENT'
    idNode = ASTNode.IDNode(p.lineno(1), p.clauseno(1), p[1])
    p[0] = ASTNode.UnaryNode(p.lineno(2), p.clauseno(2), p[2], idNode)

def p_expression_ate(p):
    'expression : ID INCREMENT'
    idNode = ASTNode.IDNode(p.lineno(1), p.clauseno(1), p[1])
    p[0] = ASTNode.UnaryNode(p.lineno(2), p.clauseno(2), p[2], idNode)

def p_expression_or(p):
    'expression : expression B_OR expression'
    p[0] = ASTNode.BinaryNode(p.lineno(1), p.clauseno(1), p[2], [p[1],p[3]])

def p_expression_xor(p):
    'expression : expression B_XOR expression'
    p[0] = ASTNode.BinaryNode(p.lineno(1), p.clauseno(1), p[2], [p[1],p[3]])

def p_expression_and(p):
    'expression : expression B_AND expression'
    p[0] = ASTNode.BinaryNode(p.lineno(1), p.clauseno(1), p[2], [p[1],p[3]])
    
def p_expression_plus(p):
    'expression : expression PLUS expression'
    p[0] = ASTNode.BinaryNode(p.lineno(1), p.clauseno(1), p[2], [p[1],p[3]])

def p_expression_minus(p):
    'expression : expression MINUS expression'
    p[0] = ASTNode.BinaryNode(p.lineno(1), p.clauseno(1), p[2], [p[1],p[3]])

def p_expression_multiply(p):
    'expression : expression MULTIPLY expression'
    p[0] = ASTNode.BinaryNode(p.lineno(1), p.clauseno(1), p[2], [p[1],p[3]])

#Handles division by 0 constant
def p_expression_divide(p):
    'expression : expression DIVIDE expression'
    if p[3].children[1] == 0:
        raise e.DivisionByZeroException(p.lineno(1), p.clauseno(1))
    p[0] = ASTNode.BinaryNode(p.lineno(1), p.clauseno(1), p[2], [p[1],p[3]])

def p_expression_mod(p):
    'expression : expression MOD expression'
    p[0] = ASTNode.BinaryNode(p.lineno(1), p.clauseno(1), p[2], [p[1],p[3]])

def p_expression_factor(p):
    'expression : factor'
    p[0] = p[1]

def p_factor_number(p):
    'factor : NUMBER'
    p[0] = ASTNode.NumberNode(p.lineno(1), p.clauseno(1), p[1])

def p_factor_letter(p):
    'factor : LETTER'
    p[0] = ASTNode.LetterNode(p.lineno(1), p.clauseno(1), p[1])

def p_factor_id(p):
    'factor : ID'
    p[0] = ASTNode.IDNode(p.lineno(1), p.clauseno(1), p[1])

    
def p_error(p):
    if p == None:
        raise e.NoMatchException()
    else:
        raise e.SyntaxException(p.lineno, p.clauseno)

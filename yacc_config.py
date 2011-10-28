from Node import Node
from tokrules import tokens

start = 'statement_list' # Optional as uses first rule

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('left', 'B_AND', 'B_OR', 'B_XOR', 'B_NOT'),
)


def p_statement_list_alicespoke(p):
    'statement_list : expression PRINT_SPOKE SEP_PERIOD'
    p[0] = Node("statement_list", [p[1]], [p[2], p[3]])


def p_statement_list_sep_comma(p):
    'statement_list : statement SEP_COMMA statement_list'
    p[0] = Node("statement_list", [p[1],p[3]], p[2])

def p_statement_list_sep_period(p):
    'statement_list : statement SEP_PERIOD statement_list'
    p[0] = Node("statement_list", [p[1],p[3]], p[2])


def p_statement_list_sep_and(p):
    'statement_list : statement SEP_AND statement_list'
    p[0] = Node("statement_list", [p[1],p[3]], p[2])

def p_statement_list_sep_but(p):
    'statement_list : statement SEP_BUT statement_list'
    p[0] = Node("statement_list", [p[1],p[3]], p[2])

def p_statement_list_sep_then(p):
    'statement_list : statement SEP_THEN statement_list'
    p[0] = Node("statement_list", [p[1],p[3]], p[2])

def p_statement_too(p):
    'statement : statement TOO'
    p[0] = p[1]

def p_statement_wasa(p):
    'statement : ID DEC_WAS DEC_A type'
    p[0] = Node('statement', [p[4]], [p[1], p[2], p[3]])

def p_statement_became(p):
    'statement : ID ASSIGNMENT expression'
    p[0] = Node('statement', [p[3]], [p[1], p[2]])

def p_type_number(p):
    'type : TYPE_NUMBER'
    p[0] = Node('type', leaves = [p[1]])

def p_type_letter(p):
    'type : TYPE_LETTER'
    p[0] = Node('type', leaves = [p[1]])

def p_expression_not(p):
    'expression : B_NOT expression'
    p[0] = Node('expression', [p[2]], [p[1]])

def p_expression_drank(p):
    'expression : ID DECREMENT'
    p[0] = Node('expression', [p[1]], [p[2]])

def p_expression_ate(p):
    'expression : ID INCREMENT'
    p[0] = Node('expression', [p[1]], [p[2]])

def p_expression_or(p):
    'expression : expression B_OR term1'
    p[0] = Node('expression', [p[1],p[3]], [p[2]])

def p_expression_xor(p):
    'expression : expression B_XOR term1'
    p[0] = Node('expression', [p[1],p[3]], [p[2]])

def p_expression_and(p):
    'expression : expression B_AND term1'
    p[0] = Node('expression', [p[1],p[3]], [p[2]])
    
def p_expression_term1(p):
    'expression : term1'
    p[0] = Node('expression', [p[1]])

def p_term1_plus(p):
    'term1 : term1 PLUS term2'
    p[0] = Node('term1', [p[1],p[3]], [p[2]])

def p_term1_minus(p):
    'term1 : term1 MINUS term2'
    p[0] = Node('term1', [p[1],p[3]], [p[2]])

def p_term1_term2(p):
    'term1 : term2'
    p[0] = Node('term1', [p[1]])

def p_term2_multiply(p):
    'term2 : term2 MULTIPLY factor'
    p[0] = Node('term2', [p[1],p[3]], [p[2]])

def p_term2_divide(p):
    'term2 : term2 DIVIDE factor'
    p[0] = Node('term2', [p[1],p[3]], [p[2]])

def p_term2_factor(p):
    'term2 : factor'
    p[0] = Node('term2', [p[1]])

def p_factor_parentheses(p):
    'factor : LPAREN expression RPAREN'
    p[0] = Node('factor',[p[2]], [p[1],p[3]])

def p_factor_number(p):
    'factor : NUMBER'
    p[0] = Node('factor', leaves = [p[1]])

def p_factor_letter(p):
    'factor : LETTER'
    p[0] = Node('factor', leaves = [p[1]])

def p_factor_id(p):
    'factor : ID'
    p[0] = Node('factor', leaves = [p[1]])

# Error rule for syntax errors
def p_error(p):
    print "Syntax error in input!"





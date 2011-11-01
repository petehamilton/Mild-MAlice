from Node import Node
from tokrules import tokens

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

def p_statement_list_empty(p):
    'statement_list : '
    pass

def p_statement_list_alicespoke(p):
    'statement_list : expression PRINT_SPOKE SEP_PERIOD'
    p[0] = Node("statement_list", [p[2], p[3], p[1]])

def p_statement_list_sep_comma(p):
    'statement_list : statement SEP_COMMA statement_list'
    p[0] = Node("statement_list", [p[2], p[1],p[3]])

def p_statement_list_sep_period(p):
    'statement_list : statement SEP_PERIOD statement_list'
    p[0] = Node("statement_list", [p[2], p[1], p[3]])


def p_statement_list_sep_and(p):
    'statement_list : statement SEP_AND statement_list'
    p[0] = Node("statement_list", [p[2], p[1],p[3]])

def p_statement_list_sep_but(p):
    'statement_list : statement SEP_BUT statement_list'
    p[0] = Node("statement_list", [p[2], p[1],p[3]])

def p_statement_list_sep_then(p):
    'statement_list : statement SEP_THEN statement_list'
    p[0] = Node("statement_list", [p[2], p[1],p[3]])

def p_statement_too(p):
    'statement : statement TOO'
    p[0] = p[1]

def p_statement_wasa(p):
    'statement : ID DEC_WAS DEC_A type'
    if p[1] in symbolTable:
        print "Oh No! Silly you! You already told me what '%s' was on line %d" %(p[1],  symbolTable[p[1]][1])
    else:    
        symbolTable[p[1]] = [p[4].children[0], p.lineno(1)]
    p[0] = Node('statement', [p[1], p[2], p[3], p[4]])

def p_statement_became(p):
    'statement : ID ASSIGNMENT expression'
    p[0] = Node('statement', [p[1], p[2], p[3]])

# Have to implement for drank and ate
def p_statement_expression(p):
    'statement : expression'
    p[0] = Node('statement', [p[1]])

def p_type_number(p):
    'type : TYPE_NUMBER'
    p[0] = Node('type', [p[1]])

def p_type_letter(p):
    'type : TYPE_LETTER'
    p[0] = Node('type', [p[1]])

def p_expression_not(p):
    'expression : B_NOT expression'
    p[0] = Node('expression', [p[1], p[2]])

def p_expression_drank(p):
    'expression : ID DECREMENT'
    p[0] = Node('expression', [p[2], p[1]])

def p_expression_ate(p):
    'expression : ID INCREMENT'
    p[0] = Node('expression', [p[2], p[1]])

def p_expression_or(p):
    'expression : expression B_OR term1'
    p[0] = Node('expression', [p[2], p[1],p[3]])

def p_expression_xor(p):
    'expression : expression B_XOR term1'
    p[0] = Node('expression', [p[2], p[1],p[3]])

def p_expression_and(p):
    'expression : expression B_AND term1'
    p[0] = Node('expression', [p[2], p[1],p[3]])
    
def p_expression_term1(p):
    'expression : term1'
    p[0] = Node('expression', [p[1]])

def p_term1_plus(p):
    'term1 : term1 PLUS term2'
    p[0] = Node('term1', [p[2], p[1],p[3]])

def p_term1_minus(p):
    'term1 : term1 MINUS term2'
    p[0] = Node('term1', [p[2], p[1],p[3]])

def p_term1_term2(p):
    'term1 : term2'
    p[0] = Node('term1', [p[1]])

def p_term2_multiply(p):
    'term2 : term2 MULTIPLY factor'
    p[0] = Node('term2', [p[2], p[1],p[3]])

#Handles division by 0 constant
def p_term2_divide(p):
    'term2 : term2 DIVIDE factor'
    if p[3].tokType == 'factor':
        if p[3].leaves[0] == 0:
            print "Oops!"
    p[0] = Node('term2', [p[2], p[1],p[3]])

def p_term2_mod(p):
    'term2 : term2 MOD factor'
    p[0] = Node('term2', [p[2], p[1],p[3]])

def p_term2_factor(p):
    'term2 : factor'
    p[0] = Node('term2', [p[1]])

def p_factor_parentheses(p):
    'factor : LPAREN expression RPAREN'
    p[0] = Node('factor',[p[1],p[3], p[2]])

def p_factor_number(p):
    'factor : NUMBER'
    p[0] = Node('factor', [p[1]])

def p_factor_letter(p):
    'factor : LETTER'
    p[0] = Node('factor', [p[1]])

def p_factor_id(p):
    'factor : ID'
    p[0] = Node('factor', [p[1]])

# Error rule for syntax errors
#def p_error(p):
#    print "Oh No! You started writing utter nonsense."
    # pass
    # print "An error prevented the program from being compiled :("


# "Oh No! You were writing such silly things at the start of the story." means could
# not match to statement-list so can't start.

def p_error(p):
    if p == None:
        print "Oh No! You were writing such silly things at the start of the story."
    else:
        print "Oh No! You started writing utter nonsense.", p.lineno
    #if p:
    #    _parse_error( 'Oh No! You started writing utter nonsense.', '')#self._coord(p.lineno))
    #else:
    #   _parse_error('At end of input', '')

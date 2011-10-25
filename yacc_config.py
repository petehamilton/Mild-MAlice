start = 'statement_list' # Optional as uses first rule

def p_statement_list_alicefound(p):
    'statement_list : PRINT_ALICE PRINT_SPOKE expression SEP_PERIOD'
    #TODO: write rule for this BNF

def p_statement_list_sep_comma(p):
    'statement_list : statement SEP_COMMA statement_list'
    #TODO: write rule for this BNF

def p_statement_list_sep_period(p):
    'statement_list : statement SEP_PERIOD statement_list'
    #TODO: write rule for this BNF

def p_statement_list_sep_and(p):
    'statement_list : statement SEP_AND statement_list'
    #TODO: write rule for this BNF

def p_statement_list_sep_but(p):
    'statement_list : statement SEP_BUT statement_list'
    #TODO: write rule for this BNF

def p_statement_list_sep_then(p):
    'statement_list : statement SEP_THEN statement_list'
    #TODO: write rule for this BNF

def p_statement_too(p):
    'statement : statement TOO'
    p[0] = p[1]

def p_statement_wasa(p):
    'statement : ID DEC_WAS DEC_A type'
    #TODO: write rule for this BNF

def p_statement_became(p):
    'statement : ID ASSIGNMENT expression'
    #TODO: write rule for this BNF

def p_type_number(p):
    'type : TYPE_NUMBER'
    #TODO: write rule for this BNF

def p_type_letter(p):
    'type : TYPE_LETTER'
    #TODO: write rule for this BNF

def p_expression_factor(p):
    'expression : factor'
    p[0] = p[1]

def p_expression_not(p):
    'expression : B_NOT expression'
    p[0] = !p[2]

def p_expression_drank(p):
    'expression : ID DECREMENT'
    p[0] = p[1]--

def p_expression_ate(p):
    'expression : ID INCREMENT'
    p[0] = p[1]++

def p_expression_pipe(p):
    'expression : expression B_OR term1'
    p[0] = p[1] | p[3]

def p_expression_hat(p):
    'expression : expression B_XOR term1'
    p[0] = p[1] ^ p[3]

def p_expression_ampersand(p):
    'expression : expression B_AND term1'
    p[0] = p[1] & p[3]

def p_expression_term1(p):
    'expression : term1'
    p[0] = p[1]

def p_term1_plus(p):
    'term1 : term1 PLUS term2'
    p[0] = p[1] + p[3]

def p_term1_minus(p):
    'term1 : term1 MINUS term2'
    p[0] = p[1] - p[3]

def p_term1_term2(p):
    'term1 : term2'
    p[0] = p[1]

def p_term2_multiply(p):
    'term2 : term2 MULTIPLY factor'
    p[0] = p[1] * p[3]

def p_term2_divide(p):
    'term2 : term2 DIVIDE factor'
    p[0] = p[1] / p[3]

def p_term2_factor(p):
    'term2 : factor'
    p[0] = p[1]

def p_factor_parentheses(p):
    'term2 : LPAREN expression RPAREN'
    p[0] = p[2]

def p_factor_number(p):
    'factor : NUMBER'
    p[0] = p[1]

def p_factor_letter(p):
    'factor : LETTER'
    p[0] = p[1]

def p_factor_id(p):
    'factor : ID'
    p[0] = p[1]

def p_empty(p):
    'empty :'
    pass

# Error rule for syntax errors
def p_error(p):
    print "Syntax error in input!"

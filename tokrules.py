# module: tokrules.py
# This module just contains the lexing rules
tokens = [
        'NUMBER',
        'LETTER',
        'PLUS',
        'MINUS',
        'MULTIPLY',
        'DIVIDE',
        'LPAREN',
        'RPAREN',
        'SEP_COMMA',
        'SEP_PERIOD',
        'B_AND',
        'B_OR',
        'B_XOR',
        'B_NOT',
        'ID',
    ]

reserved = {
    'spoke'       : 'PRINT_SPOKE',
    'drank'       : 'DECREMENT',
    'ate'         : 'INCREMENT', 
    'and'         : 'SEP_AND',
    'but'         : 'SEP_BUT',
    'then'        : 'SEP_THEN',
    'was'         : 'DEC_WAS',
    'a'           : 'DEC_A',
    'became'      : 'ASSIGNMENT',
    'too'         : 'TOO',
    'number'      : 'TYPE_NUMBER',
    'letter'      : 'TYPE_LETTER',
}

# Tokens 
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEP_COMMA = r'\,'
t_SEP_PERIOD = r'\.'
t_B_AND = r'\&'
t_B_OR = r'\|'
t_B_XOR = r'\^'
t_B_NOT = r'\~'

tokens += list(reserved.values())

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t\n\r'

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

def t_ID(t):
    r'[a-zA-Z][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

def t_TOO(t):
    r'\too'
    pass

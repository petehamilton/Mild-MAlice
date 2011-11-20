# This module contains the lexing rules

from grammarExceptions import LexicalException

tokens = [
        'NUMBER',
        'LETTER',
        'PLUS',
        'MINUS',
        'MULTIPLY',
        'DIVIDE',
        'SEP_COMMA',
        'SEP_PERIOD',
        'B_AND',
        'B_OR',
        'B_XOR',
        'B_NOT',
        'MOD',
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
t_B_AND = r'\&'
t_B_OR = r'\|'
t_B_XOR = r'\^'
t_B_NOT = r'\~'
t_MOD = r'%'
t_LETTER = r'\'[a-zA-Z]\''

tokens.extend(reserved.values())

# A string containing ignored characters.
t_ignore  = ' \t\r'

# A regular expression rule with some action code
def t_NUMBER(t):
    r'-?\d+'
    t.value = int(t.value)    
    return t

def t_SEP_COMMA(t):
    r','
    t.lexer.clauseno += 1
    return t
    
def t_SEP_PERIOD(t):
    r'\.'
    t.lexer.clauseno += 1
    return t    

def t_SEP_AND(t):
    r'and$'
    t.lexer.clauseno += 1
    return t  
    
def t_SEP_BUT(t):
    r'but$'
    t.lexer.clauseno += 1
    return t  
    
def t_SEP_THEN(t):
    r'then$'
    t.lexer.clauseno += 1
    return t  
    
# Define a rule so we can track line numbers
def t_newline(t):
    r'\n'
    t.lexer.lineno += len(t.value)
    t.lexer.clauseno = 0

# Error handling rule
def t_error(t):
    raise LexicalException( t.lexer.lineno, t.lexer.clauseno )
    t.lexer.skip(1)

def t_ID(t):
    r'[a-zA-Z][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

def t_TOO(t):
    r'\too'
    pass

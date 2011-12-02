# This module contains the lexing rules

from grammarExceptions import LexicalException
from ply.lex import TOKEN

tokens = [
        'NUMBER',
        'LETTER',
        'SENTENCE',
        'PLUS',
        'MINUS',
        'MULTIPLY',
        'DIVIDE',
        'SEP_COMMA',
        'SEP_PERIOD',
        'SEP_QUESTION',
        'B_AND',
        'B_OR',
        'B_XOR',
        'B_NOT',
        'L_EQUAL',
        'L_LESS_THAN',
        'L_GREATER_THAN',
        'L_GREATER_THAN_EQUAL',
        'L_LESS_THAN_EQUAL',
        'L_NOT_EQUAL',
        'L_AND',
        'L_OR',
        'MOD',
        'ID',
        'L_PAREN',
        'R_PAREN',
        'FUNCTION_LOOKING_GLASS',
        'ALICE_FOUND',
        'APOSTROPHE',
    ]

reserved = {          
    'Alice'         : 'ALICE',
    'spoke'         : 'PRINT_SPOKE',
    'said'          : 'PRINT_SAID',
    'drank'         : 'DECREMENT',
    'ate'           : 'INCREMENT', 
    'and'           : 'SEP_AND',
    'but'           : 'SEP_BUT',
    'then'          : 'SEP_THEN',
    'what'          : 'INPUT_WHAT',
    'was'           : 'DEC_WAS',
    'a'             : 'DEC_A',
    'became'        : 'ASSIGNMENT',
    'too'           : 'TOO',
    'number'        : 'TYPE_NUMBER',
    'letter'        : 'TYPE_LETTER',
    'sentence'      : 'TYPE_SENTENCE',
    'thought'       : 'COMMENT_THOUGHT',
    'had'           : 'ARRAY_HAD',
    'piece'         : 'ARRAY_PIECE',
    'eventually'    : 'LOOP_EVENTUALLY',
    'because'       : 'LOOP_BECAUSE', 
    'enough'        : 'LOOP_ENOUGH',
    'times'         : 'LOOP_TIMES',
    'either'        : 'IF_EITHER',
    'so'            : 'IF_SO',
    'or'            : 'IF_OR',
    'maybe'         : 'IF_MAYBE',
    'unsure'        : 'IF_UNSURE',
    'which'         : 'IF_WHICH',
    'perhaps'       : 'IF_PERHAPS',
    'went'          : 'FUNCTION_WENT',
    'through'       : 'FUNCTION_THROUGH',
    'The'           : 'FUNCTION_THE',
    'contained'     : 'FUNCTION_CONTAINED',
    'changed'       : 'FUNCTION_CHANGED',
    'room'          : 'FUNCTION_ROOM',
    'spider'        : 'FUNCTION_SPIDER',
}

# Tokens 
t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_B_AND = r'\&'
t_B_OR = r'\|'
t_B_XOR = r'\^'
t_B_NOT = r'\~'
t_MOD = r'%'
t_LETTER = r'\'[a-zA-Z]\''
t_SENTENCE = r'"[^\"]*"'
t_L_PAREN = r'\('
t_R_PAREN = r'\)'
t_L_EQUAL = r'=='
t_L_LESS_THAN = r'<'
t_L_GREATER_THAN = r'>'
t_L_GREATER_THAN_EQUAL = r'>='
t_L_LESS_THAN_EQUAL = r'<='
t_L_NOT_EQUAL = r'!='
t_L_AND = r'&&'
t_L_OR = r'\|\|'
t_APOSTROPHE = r'\'s'
# t_ALICE = r'Alice'



# tokens.extend(reserved.values())
tokens = reserved.values() + tokens
# A string containing ignored characters.
t_ignore  = ' \t\r'

@TOKEN('Alice[\s\t\n]+found')
def t_ALICE_FOUND(t):
    return t

@TOKEN('Looking' + t_MINUS + 'Glass')
def t_FUNCTION_LOOKING_GLASS(t):
    return t


# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
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
    
def t_SEP_QUESTION(t):
    r'\?'
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
    print t
    raise LexicalException( t.lexer.lineno, t.lexer.clauseno )
    t.lexer.skip(1)

def t_ID(t):
    r'[a-zA-Z][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

# TODO: IS THERE A BETTER WAY? Will match on t_ID first
def t_ARRAY_APOSTROPHE(t):
    r'\'s'
    pass

def t_TOO(t):
    r'\too'
    pass

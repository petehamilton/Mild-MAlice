import ply.lex as lex

# This attempts to use the method outlined at: http://www.dabeaz.com/ply/ply.html#ply_nn18

class MAliceLexer:
    tokens = [
        'NUMBER',
        'LETTER',
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'EQUALS',
        'LPAREN',
        'RPAREN',
        'SEP_COMMA',
        'SEP_PERIOD',
        'ID',
    ]

    reserved = {
        'Alice'       : 'PRINT_ALICE',
        'Spoke'       : 'PRINT_SPOKE',
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
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EQUALS = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_SEP_COMMA = r'\,'
    t_SEP_PERIOD = r'\.'

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

    def __init__(self, **kwargs):
        self.lexer = lex.lex(object=self,**kwargs)
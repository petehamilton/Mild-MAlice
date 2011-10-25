import ply.lex as lex

# This attempts to use the method outlined at: http://www.dabeaz.com/ply/ply.html#ply_nn18

class MAliceLexer:
    def __init__(self, **kwargs):
        self.tokens = [
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

        self.reserved = {
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
        self.t_PLUS = r'\+'
        self.t_MINUS = r'-'
        self.t_TIMES = r'\*'
        self.t_DIVIDE = r'/'
        self.t_EQUALS = r'='
        self.t_LPAREN = r'\('
        self.t_RPAREN = r'\)'
        self.t_SEP_COMMA = r'\,'
        self.t_SEP_PERIOD = r'\.'

        self.tokens += list(self.reserved.values())
        # A string containing ignored characters (spaces and tabs)
        self.t_ignore  = ' \t\n\r'
    
    def build(self, **kwargs):
        self.lexer = lex.lex(object=self,**kwargs)

    # A regular expression rule with some action code
    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)    
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Error handling rule
    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def t_ID(self, t):
        r'[a-zA-Z][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value,'ID')    # Check for reserved words
        return t

    def t_TOO(self, t):
        r'\too'
        pass

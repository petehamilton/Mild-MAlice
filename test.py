import ply.lex as lex

def setup():
    tokens = [
        'NAME',
        'NUMBER',
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'EQUALS',
        'LPAREN',
        'RPAREN',
        'WAS',
        'ID',
    ]

    reserved = {
        'Alice Spoke' : 'PRINT',
        'drank'       : 'DECREMENT',
        'ate'         : 'INCREMENT', 
        'and'         : 'SEPARATOR',
        'but'         : 'SEPARATOR',
        'then'        : 'SEPARATOR',
        ','           : 'SEPARATOR',
        '.'           : 'SEPARATOR',
        #'was a'       : 'DECLARATOR',
        'became'      : 'ASSIGNMENT',
        'too'         : 'TOO',
    }
    
    

    # Tokens 
    t_PLUS = r'\+' 
    t_MINUS = r'-' 
    t_TIMES = r'\*' 
    t_DIVIDE = r'/' 
    t_EQUALS = r'=' 
    t_LPAREN = r'\(' 
    t_RPAREN = r'\)' 
    t_NAME = r'[a-zA-Z][a-zA-Z0-9_]*'
    t_WAS = r'was\ a'    

    tokens += list(reserved.values())


    # A regular expression rule with some action code
    def t_NUMBER(t):
        r'\d+'
        t.value = int(t.value)    
        return t

    # Define a rule so we can track line numbers
    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

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

    # Build the lexer
    return lex.lex()

def run():
    lexer = setup()
    data = '''
    x was a number and x became 42.
    y was a number, y became 30.
    '''
    lexer.input(data)
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: break      # No more input
        print tok
        
if __name__ == '__main__':
    run()

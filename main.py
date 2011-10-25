#from malice_lexer import MAliceLexer
import ply.lex as lex
import tokrules

def run():
    #ml = MAliceLexer()
    #ml.build()
    #lexer = ml.lexer
    lexer = lex.lex(module=tokrules)
    data = '''
    x was a number and x became 42.
    y was a number, y became 30.
    '''
    data = data.replace(".", " . ").replace(",", " , ")
    lexer.input(data)
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: break      # No more input
        print tok
        
if __name__ == '__main__':
    run()

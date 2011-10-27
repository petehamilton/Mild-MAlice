#from malice_lexer import MAliceLexer
import ply.lex as lex
import tokrules
from yacc_config import *
import ply.yacc as yacc

import inspect

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
    #while True:
    #    tok = lexer.token()
    #    if not tok: break      # No more input
    #    print tok

def parse():
    from tokrules import tokens
    # Build the parser
    parser = yacc.yacc()
    s = r'x was a number, x became 5. Alice Spoke x.'
    result = parser.parse(s)
    print result
    #while True:
    #   try:
    #       s = raw_input('calc > ')
    #   except EOFError:
    #       break
    #   if not s: continue
    #   result = parser.parse(s)
    #   print result.display()
        
if __name__ == '__main__':
    run()
    parse()

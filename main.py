#from malice_lexer import MAliceLexer
import ply.lex as lex
import ply.yacc as yacc

import tokrules
from yacc_config import *

import Node

if __name__ == '__main__':
    lexer = lex.lex(module=tokrules)
    parser = yacc.yacc()
    s = r'Alice spoke 3 + 5.'
    result = parser.parse(s)
    result.display()
    
    """   
    while True:
       try:
           s = raw_input('Enter statement: ')
       except EOFError:
           break
       if not s: continue
       result = parser.parse(s)
       print result
    """

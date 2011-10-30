#from malice_lexer import MAliceLexer
import ply.lex as lex
import ply.yacc as yacc

import tokrules
from yacc_config import *

import Node

def run():
    tests()
    return 0
    parse_code('''
    x was a number and x became 42.
    y was a number, y became 30.

    z was a number but z became x + y.
    z spoke.
    ''')
    return 0

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

def parse_code(code):
    lexer = lex.lex(module=tokrules)
    parser = yacc.yacc()
    result = parser.parse(code)
    if result:
        pass
        # result.display()

def tests():
    import fnmatch
    import os
    files = os.listdir('./milestone2')
    files.sort()
    for file in files:
        if fnmatch.fnmatch(file, '*.alice'):
            fin = open('./milestone2/' + file, "r");
            print "Parsing", file
            code = fin.read()
            # print code
            parse_code(code)
            print

if __name__ == '__main__':
    run()

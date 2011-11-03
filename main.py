#from malice_lexer import MAliceLexer
import ply.lex as lex
import ply.yacc as yacc

import tokrules
from yacc_config import *
from exceptions import *

import Node

from semantic_analysis import analyse
from semantic_analysis import SemanticException

def run():
    tests()
    return 0
    parse_code('''
    Cat was a number.
    Dog was a number.
    Cat became 7 then Dog became 6 and Cat drank and Dog ate.
    Armagedon was a number and Armagedon became Cat * Dog.
    Armagedon spoke.
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
    try:
        result = parser.parse(code)
        if result:
            #result.display()
            try:
                analyse(symbolTable, result)
            except SemanticException:
                pass
    except SyntaxException:
        pass

def tests():
    import fnmatch
    import os
    files = os.listdir('./milestone2')
    files.sort()
    for file in files:
        if fnmatch.fnmatch(file, '*.alice'):
            symbolTable.clear()
            if os.path.getsize('./milestone2/' + file):
                fin = open('./milestone2/' + file, "r");
                print "Parsing", file
                code = fin.read()
                # print code
                parse_code(code)
                print

if __name__ == '__main__':
    run()

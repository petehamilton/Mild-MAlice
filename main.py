#from malice_lexer import MAliceLexer
import ply.lex as lex
import ply.yacc as yacc

import tokrules
from yacc_config import *

import Node

from semantic_analysis import analyse
from code_generator import generate
import grammar_exceptions as e

def run():
    #tests()
    #return 0
    parse_code('''
    Cat was a number.
    Cat became 5.
    Cat spoke.
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
    try:
        lexer = lex.lex(module=tokrules)
        parser = yacc.yacc()
        result = parser.parse(code)
        if result:
            analyse(symbolTable, result)
            code = generate( result, symbolTable.keys() )
            writeASM( code )
    except (e.SemanticException, e.NoMatchException, e.SyntaxException, e.LexicalException, e.DivisionByZeroException) as exception:
        print exception.value 
        print "(Paragraph : %d Clause: %d)"  %(exception.lineno, exception.clauseno)


def writeASM( result ):
    asmFile = open('output.asm', 'w')
    for line in result:
        asmFile.write(line + "\n")
    asmFile.close()

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

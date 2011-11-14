#from malice_lexer import MAliceLexer
import ply.lex as lex
import ply.yacc as yacc
import sys
import os

import tokrules
from yacc_config import *

import Node

from semantic_analysis import analyse
from code_generator import generate
import grammar_exceptions as e
import sys
def run():
    if len(sys.argv) > 1:
        fName = sys.argv[1]
        if os.path.getsize(fName):
            maliceprogram = open(fName, 'r').read()
        else:
            return 0
    else:
        maliceprogram = '''
    b was a number.
    b became 10 - 7.
    b spoke.
    '''
    parse_code(maliceprogram)
    return 0

def parse_code(code):
    try:
        lexer = lex.lex(module=tokrules)
        parser = yacc.yacc()
        result = parser.parse(code)
        if result:
            symbolTable = {}
            analyse(symbolTable, result)
            code = generate( result, symbolTable.keys(), ["rax", "rdx", "rcx", "rbx", "rsi", "rdi"])
            writeASM( code )
    except (e.SemanticException, e.NoMatchException, e.SyntaxException, e.LexicalException, e.DivisionByZeroException, e.ArithmeticOverflowException) as exception:
        print "----------------"
        print exception.value 
        #print "(Paragraph : %d Clause: %d)"  %(exception.lineno, exception.clauseno)


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

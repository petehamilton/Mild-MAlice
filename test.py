from Node import Node
from semantic_analysis import analyse
import ply.lex as lex
import ply.yacc as yacc

import tokrules
from yacc_config import *

def test( symbolTable, node, msg ):
    print msg 
    analyse( symbolTable, node )
        

def parse_code(code):
    symbolTable.clear()
    lexer = lex.lex(module=tokrules)
    parser = yacc.yacc()
    result = parser.parse(code)
    return result
    
if __name__ == '__main__':
    #test( symbolTable, parse_code('x was a number. x spoke.'), "TEST 1: DECLARATION" )
    test( symbolTable, parse_code('x was a number. x became 5 and x spoke.'), "TEST 2: ASSIGNMENT" )
    #test( symbolTable, parse_code('x was a 

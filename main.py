import sys
import os
from collections import defaultdict

import ply.lex as lex
import ply.yacc as yacc

import tokRules
from yaccConfig import *
from semanticAnalysis import analyse
from codeGenerator import CodeGenerator
import grammarExceptions as e


registers = ['r%d' %r for r in range(8,16)]  + ["rbx", "rcx", "rdx", "rsi", "rdi"]

def run():
    if len(sys.argv) > 1:
        fName = sys.argv[1]
        if os.path.getsize(fName):
            maliceprogram = open(fName, 'r').read()
            base, ext = os.path.splitext(os.path.basename(fName))
            if ext == ".alice":
                code = parse_code(maliceprogram)
                writeASM( code, base )
            else:
                print "Error! Filetype is not of format .alice."
                return 1
        return 0
    else:
        print "Error! No given files."
        return 1

def parse_code(code):
    try:
        lexer = lex.lex(module=tokRules)
        # lexer.input(code)
        # while True:
        #     tok = lexer.token()
        #     if not tok: break
        #     print tok
        parser = yacc.yacc()
        result = parser.parse(code)
        # result.display()
        if result:
            symbolTable = {}
            flags = defaultdict(set)
            analyse(result, flags)
            cg = CodeGenerator(symbolTable, registers, flags)
            code = cg.generate(result)
            return code
        return None
    except (e.SemanticException, e.NoMatchException, e.SyntaxException, e.LexicalException, e.DivisionByZeroException) as exception:
        print exception.value + " " + exception.message 
        print "(Paragraph : %d Clause: %d)"  %(exception.lineno, exception.clauseno)
        sys.exit(1)


def writeASM( result, fileName ):
    asmFile = open(fileName + ".asm", 'w')
    for line in result:
        asmFile.write(line + "\n")
    asmFile.close()

if __name__ == '__main__':
    run()

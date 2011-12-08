from SymbolTable import SymbolTable


def analyse( node, flags ):
    node.check(SymbolTable(), flags)
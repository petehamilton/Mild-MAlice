from Node import Node
from semantic_analysis import analyse


def test_assignment( symbolTable, node ):
    print "TEST 1: ASSIGNMENT"
    analyse( symbolTable, node )
        

#statement1 = Node('assignment', 
#statement = Node( 'binary_op', ['+', Node( 'factor', ["ID", "x" ] ),Node( 'factor', ["NUMBER", 5] ) ])
#node = Node('statementlist', [nodea, nodeb] )



if __name__ == '__main__':
    symbolTable = {"x" : ["NUMBER", 10, False] }
    statement1 = Node('assignment', ['x', Node('factor', ['NUMBER', 6])])
    test_assignment( symbolTable, statement1 )

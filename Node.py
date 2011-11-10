UNARY_OP = "unary_op"
BINARY_OP = "binary_op"
FACTOR = "factor"
ASSIGNMENT = "assignment"
DECLARATION = "declaration"
SPOKE = "spoke"
STATEMENT_LIST = "statement_list"
TYPE = "type"

class Node:
    def __init__(self, tokType, lineno, clauseno, children=None):
        self.tokType = tokType
        self.lineno = lineno
        self.clauseno = clauseno
        self.children = children or []
        
    def __str__(self):
        return "Node(%s,%r,%s,%s)" % (self.tokType,self.lineno,self.clauseno,self.children)
    
    def display(self, depth = 0):
        print ("   " * (depth-1)) + \
              ("|> " if (depth > 0) else "") + \
              self.tokType
        
        for child in self.children:
            if isinstance(child, Node):
                child.display(depth + 1)
            else:    
                print ("   " * (depth)) + "|> '" + str(child) + "'"

class Node:
    def __init__(self, tokType, children=None, leaves=None):
        self.tokType = tokType
        self.children = children or []
        self.leaves = leaves or []
    
    def visit(self, depth):
        print (" "*depth) + self.tokType
        for leaf in self.leaves:
            print (" "*(depth+1)) + str(leaf)
        for child in self.children:
            child.visit(depth+1)

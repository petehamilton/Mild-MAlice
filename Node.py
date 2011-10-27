class Node:
    def __init__(self, tokType, children=None, leaves=None):
        self.tokType = tokType
        self.children = children or []
        self.leaves = leaves or []
    
    def display(self, depth = 0):
        print ("   " * (depth-1)) + \
              ("|> " if (depth > 0) else "") + \
              self.tokType

        for leaf in self.leaves:
            print ("   " * (depth)) + "|> '" + str(leaf) + "'"

        for child in self.children:
            child.display(depth + 1)

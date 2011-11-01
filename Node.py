class Node:
    def __init__(self, tokType, children=None):
        self.tokType = tokType
        self.children = children or []
    
    def display(self, depth = 0):
        print ("   " * (depth-1)) + \
              ("|> *" if (depth > 0) else "**") + \
              self.tokType
        
        for child in self.children:
            if isinstance(child, Node):
                child.display(depth + 1)
            else:    
                print ("   " * (depth)) + "|> '" + str(child) + "'"

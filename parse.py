import re

# Node stores a predicate and the Node objects representing its eventual arguments
# This is basically a tree
class Node:
    def __init__(self, parent=None):
        self.predicate = None
        self.children = []
        self.parent = parent
        if parent is not None:
            self.parent.children += [self]

# Transforms the string representation of the program into an AST
def parse(program):
    # Tokenizing the program
    token_list = [token.strip() for token in re.split("([\(\),])", program) if token.strip() != ""]
    head_node = Node()
    current_node = head_node
    for token in token_list:
        if token == "(": # Creating a new node that will store an argument of the current node
            current_node = Node(current_node)
        elif token == ")": # The parse for a node is done, can move back to its parent
            cpc = current_node.parent.children
            if current_node in cpc and current_node.predicate is None : # If there was no predicate assigned to a node, we replace it by its children in the parent's arguments
                position = cpc.index(current_node)
                current_node.parent.children = cpc[:position] + current_node.children + cpc[position+1:]
            current_node = current_node.parent
        elif token == ",": # Creating a new node that will store another argument for the current node
            current_node = Node(current_node.parent)
        elif token == "all": # "all" is a special predicate that needs to be concatenated to the parent instead, we delete the null node as well
            current_node.parent.predicate += "(all)"
            current_node.parent.children.remove(current_node)
        else: # Otherwise, we just stores the predicate in the current token
            current_node.predicate = token.strip()
    return head_node
import pickle
from utils import token
import sys

class Node():
    def __init__(self, name, type, childs = [], leftChild = None, rightChild = None, params = None):
        self.name = name
        self.type = type
        self.childs = childs
        self.leftChild = leftChild
        self.rightChild = rightChild
        self.params = params
        self.first = set()
        self.nullable = False
    
    def setLeftChild(self, child):
        self.leftChild = child
    
    def setRightChild(self, child):
        self.rightChild = child
    
    def setParams(self,params):
        self.params = params

    def setFirst(self, pos):
        self.first = pos

    def setNullable(self):
        if self.type in ['ident', 'string']:
            self.nullable = False
        elif self.type == 'operadores':
            if self.name in '{[':
                self.nullable = True
            elif self.name == "|":
                self.nullable = self.childs[0].nullable or self.childs[1].nullable
            elif self.name == ".":
                self.nullable = self.childs[0].nullable and self.childs[1].nullable


    def __str__(self):
        return "Name: {name} type: {type}".format(name=self.name, type=self.type, childs=self.childs, leftChild=self.leftChild, rightChild=self.rightChild, params=self.params)

class ProductionCleaner():
    def __init__(self, productions):
        self.productions = productions 
        self.cleanedProductions = self.cleanProductions()
        self.nodesFromCleanedProductions()
        self.addConncatNodes()

    def positionsOfEquals(self):
        i = 0
        positions = []
        while i < len(self.productions):
            if self.productions[i].token_name == "operadores" and self.productions[i].value == "=":
                positions.append(i)
            i += 1
        return positions
    
    def cleanProductions(self):
        productions = self.productions
        equals = self.positionsOfEquals()
        result = {}
        while len(equals) != 0:
            # Get the position of the next equals sign 
            position = equals.pop(0)
            # Check if the position before the equals sign is a parameters token
            # If it is then take the item two tokens behind
            if productions[position - 1].token_name == "parameters":
                key = productions[position - 2]
            else:
                key = productions[position -1]
            productionContent = []
            try:
                nextEqual = equals[0]
                if productions[nextEqual - 1].token_name == "parameters":
                    end = 2
                else:
                    end = 1
                endOfProduction = nextEqual - end
                if productions[position - 1].token_name == "parameters":
                    productionContent.append(productions[position - 1])
                for i in range(position+1, endOfProduction):
                    productionContent.append(productions[i])
                result[key] = productionContent
            except:
                if productions[position - 1].token_name == "parameters":
                    productionContent.append(productions[position - 1])
                for i in productions[position+1:]:
                    if i.token_name == "ident" and i.value == "END":
                        break
                    else:
                        productionContent.append(i)
                result[key] = productionContent
        
        return result
    #Function used to turn the array of tokens into an array of nodes
    #Main use is to remove the params and sintaxis tokens
    def crateNodesFromTokenArray(self, array):
        result = []
        for token in array:
            if token.token_name == "sintaxis":
                nodeToAdd = result.pop()
                nodeToAdd.setRightChild(token.value)
                result.append(nodeToAdd)
            elif token.token_name == "parameters":
                nodeToAdd = result.pop()
                nodeToAdd.setParams(token.value)
                result.append(nodeToAdd)
            else:
                result.append(Node(token.value, token.token_name))
        return result
    
    def nodesFromCleanedProductions(self):
        for key in self.cleanedProductions.keys():
            array = [key] + self.cleanedProductions[key]
            self.cleanedProductions[key] = self.crateNodesFromTokenArray(array)

    def addConncatNodes(self):
        keys = self.cleanedProductions.keys()
        for key in keys:
            j = 1
            productionWithConncat = [self.cleanedProductions[key][0]]
            while j < len(self.cleanedProductions[key]):
                productionWithConncat.append(self.cleanedProductions[key][j])
                if  self.cleanedProductions[key][j].name not in "([{|":
                    if j + 1 < len(self.cleanedProductions[key]): 
                        if self.cleanedProductions[key][j + 1].type in ['ident', 'string']: 
                            productionWithConncat.append(Node('.', 'operadores'))
                        elif self.cleanedProductions[key][j + 1].type == 'operadores' and  self.cleanedProductions[key][j+1].name in ["(","[","{"]:
                            productionWithConncat.append(Node('.', 'operadores'))
                        else:
                            pass
                j += 1
            self.cleanedProductions[key] = productionWithConncat

class ParseTree():
    def __init__(self, production):
        self.production = production
    
    def precedence(self,op):
        if op == "|":
            return 1
        if op == '.':
            return 2
        return 0


    def buildTree(self):
        nodes = []
        ops = []
        production = self.production

        i = 1
        
        while i < len(production):
            if production[i].type == "operadores" and production[i].name in "({[":
                ops.append(production[i])
            
            elif production[i].type in ['ident', 'string']:
                nodes.append(production[i])
            
            elif production[i].type == "operadores" and production[i].name in ']})':
                rightChild = production[i].rightChild
                while len(ops) !=0 and ops[-1].name not in "({[":
                    op = ops.pop()
                    node2 = nodes.pop()
                    node1 = nodes.pop()
                    nodes.append(Node(op.name, op.type, [node1,node2],op.leftChild, op.rightChild, op.params))
                
                final_op = ops.pop()
                if final_op.name in "[{":
                    node = nodes.pop()
                    nodes.append(Node(final_op.name, final_op.type, [node], final_op.leftChild, rightChild, final_op.params))
                else:
                    node = nodes.pop()
                    node.setRightChild(rightChild)
                    nodes.append(node)
            else:
                while len(ops) != 0 and self.precedence(ops[-1].name) >= self.precedence(production[i].name):
                    op = ops.pop()
                    node2 = nodes.pop()
                    node1 = nodes.pop()
                    nodes.append(Node(op.name,op.type, [node1, node2], op.leftChild, op.rightChild, op.params))
                ops.append(production[i])
            i += 1
        while len(ops) != 0:
            op = ops.pop()
            node2 = nodes.pop()
            node1 = nodes.pop()
            nodes.append(Node(op.name, op.type,[node1,node2], op.leftChild, op.rightChild, op.params))

        node2 = nodes.pop()
        node1 = production[0]
        root = Node(node1.name, node1.type, [node2], node1.leftChild, node1.rightChild, node1.params)
        return root

class ParseForest():
    def __init__(self, production_file):
        self.file = production_file
        self.forest = []
        self.noneterminals = []
        
        self.plantForest()
        self.get_nonterminals()
        self.calculate_nullable()
        self.calculate_first()
        
        print(self.forest)
        print(self.noneterminals)
        for i in self.forest:
            display_tree(i)

    def plantForest(self):
        file = open(self.file, 'rb')
        tokens = pickle.load(file)
        file.close()
        cleaner = ProductionCleaner(tokens)

        for key in cleaner.cleanedProductions.keys():
            tree = ParseTree(cleaner.cleanedProductions[key])
            parse_tree = tree.buildTree()
            self.forest.append(parse_tree)
    
    def get_nonterminals(self):
        for tree in self.forest:
            self.noneterminals.append(tree.name)
    
    def get_tree_root_by_name(self, name):
        for tree in self.forest:
            if tree.name == name:
                return tree
        return 0
    
    def post_order(self,root, res=[]):
        if root:
            for child in root.childs:
                self.post_order(child, res)
                res.append(child)
        return res
    
    def calculate_nullable(self):
        for root in reversed(self.forest):
            post_order = self.post_order(root)
            for node in post_order:
                node.setNullable()

    def calculate_first(self):
        for root in reversed(self.forest):
            post_order = self.post_order(root)
            for node in post_order:
                if node.name not in self.noneterminals and len(node.childs) == 0:
                    node.setFirst(set([node.name]))
                elif node.name in self.noneterminals:
                    if node != root:
                        first = self.get_tree_root_by_name(node.name).first
                        node.setFirst(first)
                else:
                    if node.name == '|':
                        child1 = node.childs[0]
                        child2 = node.childs[1]
                        node.setFirst(child1.first | child2.first)
                    elif node.name == '.':
                        child1 = node.childs[0]
                        child2 = node.childs[1]
                        if child1.nullable:
                            node.setFirst(child1.first | child2.first)
                        else:
                            node.setFirst(child1.first)
                    elif node.name in '{[':
                        child = node.childs[0]
                        node.setFirst(child.first)
            root.first = root.childs[0].first


def display_tree(root ,i = 0):
    if i == 0:
        print(root, root.first, root.rightChild)
    for node in root.childs:
        print(" "*(i+2)+ str(node), node.first, node.rightChild)
        display_tree(node, i + 2)

if __name__ == '__main__':
    filename = input("Ingrese el archivo con las tokens de las producciones ->")
    parseForest = ParseForest(filename)
    sys.setrecursionlimit(5000)       
    out_file_name = 'parseForest'
    outfile = open(out_file_name, 'wb')
    pickle.dump(parseForest.forest, outfile)
    outfile.close()
    print(f'Los arboles de parseo se encuentra en el archivo {out_file_name}')


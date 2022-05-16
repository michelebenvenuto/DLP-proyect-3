from Automata.functions import epsilon
from Automata.DFA import DFA
from regexes import any

simboles = any
simboles.add('"')

class Node():
    def __init__(self, name, id,childs = []):
        self.name = name
        self.id = id
        self.childs = childs

    def set_first_pos(self, pos):
        self.firstPos = pos

    def set_last_pos(self, pos):
        self.lastPos = pos
    
    def calculate_nullable(self):
        if isinstance(self.name, int) or self.name.isalnum() or self.name == "ω" or self.name in simboles:
            if self.name == epsilon:
                self.nullable = True
            else:
                self.nullable = False
        elif self.name == '⋅':
            self.nullable = True
        elif self.name == "∥":
            self.nullable = self.childs[0].nullable or self.childs[1].nullable
        elif self.name == '•':
            self.nullable = self.childs[0].nullable and self.childs[1].nullable

    def __str__(self):
        return str(self.id) + ": " +self.name

class Tree():
    def __init__(self, regex, parenthesis_as_simboles = False):
        if isinstance(regex, str):
            regex = list(regex)
        if parenthesis_as_simboles:
            self.regex = self.build_augmented_regex(regex)
        else:
            self.regex = self.build_augmented_regex(self.replace_simbols(regex))
        self.root , self.alphabet = self.build_tree()
        self.postOrder = self.post_order(self.root)
        self.postOrder.append(self.root)
        self.set_nullable()
        self.calculate_pos(True)
        self.calculate_pos(False)
        self.extract_positions()
        self.calculate_follow_pos()

    def replace_simbols(self,regex):
        new_regex = []
        for i in regex:
            if i == '{':
                new_regex.append('≤')
            elif i == '}':
                new_regex.append('≥')
                new_regex.append('⋅')
            elif i == '[':
                new_regex.append('≤')
            elif i == ']':
                new_regex.append('≥')
                new_regex.append('⊕')
            else:
                new_regex.append(i)

        return new_regex
    
    def extract_positions(self):
        positions = {}
        for node in self.postOrder:
            if len(node.firstPos) == 1 and list(node.firstPos)[0] not in positions.keys():
                positions[list(node.firstPos)[0]] = set()
        self.positions = positions          

    def calculate_follow_pos(self):
        for node in self.postOrder:
            if node.name == '•':
                child1 = node.childs[0]
                child2 = node.childs[1]
                for pos1 in child1.lastPos:
                    for pos2 in child2.firstPos:
                        self.positions[pos1].add(pos2)
            elif node.name == '⋅':
                for pos1 in node.lastPos:
                    for pos2 in node.firstPos:
                        self.positions[pos1].add(pos2)

    def set_nullable(self):
        for node in self.postOrder:
            node.calculate_nullable()
    
    def calculate_pos(self, firstPos):
        i = 1
        for node in self.postOrder:
            if isinstance(node.name, int) or node.name.isalnum() or node.name == "ω" or node.name in simboles:
                if node.name == epsilon:
                    node.set_first_pos(set())
                    node.set_last_pos(set())
                else:
                    if firstPos:
                        node.set_first_pos(set([i]))
                    else:
                        node.set_last_pos(set([i]))
                i+=1
            elif node.name == "∥":
                child1 = node.childs[0]
                child2 = node.childs[1]
                if firstPos:
                    node.set_first_pos(child1.firstPos | child2.firstPos)
                else:
                    node.set_last_pos(child1.lastPos | child2.lastPos)
            elif node.name == '•':
                child1 = node.childs[0]
                child2 = node.childs[1]
                if firstPos:
                    if child1.nullable:
                        node.set_first_pos(child1.firstPos | child2.firstPos)
                    else:
                        node.set_first_pos(child1.firstPos)
                else:
                    if child2.nullable:
                        node.set_last_pos(child1.lastPos | child2.lastPos)
                    else:
                        node.set_last_pos(child2.lastPos) 
            elif node.name == '⋅':
                child = node.childs[0]
                if firstPos:
                    node.set_first_pos(child.firstPos)
                else:
                    node.set_last_pos(child.lastPos) 

    def post_order(self,root, res=[]):
        if root:
            for child in root.childs:
                self.post_order(child, res)
                res.append(child)
        return res
    
    def build_augmented_regex(self,regex):
        i = 0
        newregex = ["≤"]
        while i < len(regex):
            newregex.append(regex[i])
            if regex[i] !="≤" and regex[i] != "∥":
                if i + 1< len(regex) and (isinstance(regex[i+1],int) or regex[i + 1].isalnum() or regex[i+1] in simboles or regex[i + 1] == '≤') :
                    newregex.append('•')
            i += 1
        newregex.append("≥")
        newregex.append('•')
        newregex.append("ω")
        return newregex
    
    def build_alphabet(self):
        alphabet = set()
        for char in self.regex:
            if isinstance(char, int) or char.isalnum() or char in simboles and char != epsilon:
                if isinstance(char, int):
                    alphabet.add(char)
                else:
                    alphabet.add(ord(char))
        return alphabet

    def precedence(self,op):
        if op == "∥":
            return 1
        if op == '•':
            return 2
        if op == '⋅' or op =='⊕':
            return 3
        return 0

    def build_tree(self):
        id = 0
        nodes = []
        
        # stack to store Operators 

        ops = []

        i = 0

        regex = self.regex
        while i < len(regex):
            if regex[i] == '≤':
                ops.append(regex[i])
            
            elif isinstance(regex[i],int) or regex[i].isalnum() or regex[i] == "ω" or regex[i] in simboles:
                if isinstance(regex[i], int):  
                    nodes.append(Node(regex[i], id))
                else:
                    nodes.append(Node(ord(regex[i]), id))
                id +=1
            
            elif regex[i] == '≥':
                while len(ops) !=0 and ops[-1] != '≤':
                    op = ops.pop()
                    if op == "⋅":
                        node1 = nodes.pop()
                        newNode = Node(op, id,[node1])
                        id += 1
                        nodes.append(newNode)
                    elif op == "⊕":
                        node1 = nodes.pop()
                        epsilon_node = Node(epsilon, id, [])
                        id +=1
                        nodes.append(Node("∥",id,[node1, epsilon_node]))
                        id +=1
                    else:
                        node2 = nodes.pop()
                        node1 = nodes.pop()
                        nodes.append(Node(op, id ,[node1,node2]))
                        id += 1

                ops.pop()
            else:
                while (len(ops) != 0 and self.precedence(ops[-1]) >= self.precedence(regex[i])):
                    op = ops.pop()
                    if op == "⋅":
                        node1 = nodes.pop()
                        nodes.append(Node(op, id ,[node1]))
                        id += 1
                    elif op == "⊕":
                        node1 = nodes.pop()
                        epsilon_node = Node(epsilon, id, [])
                        id +=1
                        nodes.append(Node("∥",id,[node1, epsilon_node]))
                        id +=1
                    else:
                        node2 = nodes.pop()
                        node1 = nodes.pop()
                        nodes.append(Node(op, id ,[node1,node2]))
                        id += 1
                ops.append(regex[i])
            i +=1
        while len(ops) != 0:
            op = ops.pop()
            if op == "⋅":
                node1 = nodes.pop()
                nodes.append(Node(op, id,[node1]))
                id += 1
            elif op == "⊕":
                node1 = nodes.pop()
                epsilon_node = Node(epsilon, id, [])
                id +=1
                nodes.append(Node("∥",id,[node1, epsilon_node]))
                id +=1
            else:
                node2 = nodes.pop()
                node1 = nodes.pop()
                nodes.append(Node(op,id ,[node1,node2]))
                id += 1

        alphabet = self.build_alphabet()
        return nodes[-1], alphabet

    def get_pos_of_simbol(self,simbol):
        result = set()
        if simbol != epsilon:
            for node in self.postOrder:
                if node.name == simbol:
                    result.add(list(node.firstPos)[0])
        return result
    
    def generate_DFA(self):
        Dstates = set()
        Dtran = {}
        Dstates.add(frozenset(self.root.firstPos))
        DstartState = list(Dstates)[0]
        unmarkedStates = list(Dstates)
        while(len(unmarkedStates)!=0):
            S = frozenset(unmarkedStates.pop(0))
            for a in self.alphabet:
                U = set()
                positionsOfSimbol = list(self.get_pos_of_simbol(a))
                for pos in S:
                    if pos in positionsOfSimbol:
                        U = self.positions[pos] | U
                U = frozenset(U)
                if (U not in Dstates):
                    Dstates.add(U)
                    unmarkedStates.append(U)
                if S in Dtran.keys(): 
                    Dtran[S][a] = U
                else:
                    Dtran[S] = {}
                    Dtran[S][a] = U
        Dalphabet = self.alphabet
        DfinalStates = set()
        position_of_hash = self.get_pos_of_simbol(ord('ω'))
        for stateSet in Dstates:
            for pos in stateSet:
                if pos in position_of_hash:
                    DfinalStates.add(stateSet)
        return DFA(Dstates, Dalphabet, Dtran, DstartState, DfinalStates) 

def display_tree(root ,i = 0):
    if i == 0:
        print(root)
    for node in root.childs:
        print(" "*(i+2)+ str(node))
        display_tree(node, i + 2)

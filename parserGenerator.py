import pickle
from ParseTree import Node

tab = "    "

class parserGenerator():
	def __init__(self, trees):
		self.trees = trees
		self.nonterminals = [i.name for i in trees]
		self.functions = []
		for i in self.trees:
			function = self.writeTreeAsFunction(i)
			self.functions.append(function)

			

	def writeNonTerminal(self,node, functionName = False):
		result = ''
		if functionName:
			result += 'def ' 
		result += node.name
		if node.params != None:
			result += node.params.replace("<","(").replace(">",")")
		else:
			result += "()"
		if functionName:
			result += ':'
		result += '\n'
		return result

	def writeWhile(self,node):
		result =''
		result += 'while currToken.value in ['
		for i in node.first:
			i = i.replace('"','')
			cleaned_string = '"'+ i + '"' + ","
			result += cleaned_string
		result = result[0: -1]
		result += '] or currToken.token_name in ['
		for i in node.first:
			i = i.replace('"','')
			cleaned_string = '"' + i + '"' + ","
			result += cleaned_string
		result = result[0: -1]
		result += ']:'
		return result + '\n'

	def writeExpect(self, node):
		return 'expect(' + '"' +node.name.replace('"','')+ '"' + ')\n'
	
	def writeIf(self, node, id):
		result = ''
		# write an if
		if id == 1:
			result += 'if '
		# write an elif
		elif id == 2:
			result += 'elif '
		# write an else
		else:
			return "else:\n"

		result += 'currToken.value in ['
		for i in node.first:
			i = i.replace('"','')
			cleaned_string = '"'+ i + '"' + ","
			result += cleaned_string
		result = result[0: -1]
		result += '] or currToken.token_name in ['
		for i in node.first:
			i = i.replace('"','')
			cleaned_string = '"' + i + '"' + ","
			result += cleaned_string
		result = result[0: -1]
		result += ']:'
		return result + '\n'

	def writeLine(self,node):
		line = node.rightChild.replace('(.', '').replace('.)', '')
		return line + '\n'

	def writeTreeAsFunction(self, root, lines = [], tabs = 0):
		if root.type == "ident":
			if root.name in self.nonterminals and tabs == 0:
				lines.append(self.writeNonTerminal(root, True))
				tabs += 1
				if root.rightChild:
					lines.append(tab * tabs + self.writeLine(root))

				for child in root.childs:
					self.writeTreeAsFunction(child,lines,tabs)
				if root.params:
					lines.append(tab*1 + 'return ' + root.params.replace('<','').replace('>','')+'\n')
			elif root.name in self.nonterminals and tabs !=0:
				if root.params:
					lines.append(tab * tabs +root.params.replace('<','').replace('>','')+ ' = '+self.writeNonTerminal(root))
				else:
					lines.append(tab * tabs +self.writeNonTerminal(root))
				if root.rightChild:
					lines.append(tab * tabs + self.writeLine(root))
			else:
				lines.append(tab * tabs + self.writeExpect(root))
				if root.rightChild:
					lines.append(tab * tabs + self.writeLine(root))
		elif root.type == "operadores":
			if root.name == "{":
				lines.append(tab * tabs + self.writeWhile(root))
				tabs += 1
				for child in root.childs:
					self.writeTreeAsFunction(child,lines,tabs)
				if root.rightChild:
					lines.append(tab * (tabs - 1) + self.writeLine(root))

			elif root.name == '.':
				for child in root.childs:
					self.writeTreeAsFunction(child,lines,tabs)
			
			elif root.name == '|':
				lines.append(tab * tabs + self.writeIf(root.childs[0], 1))
				tabs +=1
				self.writeTreeAsFunction(root.childs[0],lines, tabs)
				
				tabs -=1
				
				lines.append(tab*tabs + self.writeIf(root.childs[1],2))
				tabs += 1
				self.writeTreeAsFunction(root.childs[1],lines, tabs)
				
				tabs -=1
				lines.append(tab*tabs + self.writeIf(root,3))
				lines.append(tab*(tabs+ 1) + 'print("Error de Parseo")\n')
				lines.append(tab*(tabs+ 1) + 'return 0\n')
				if root.rightChild:
					lines.append(tab * (tabs) + self.writeLine(root))
				
				
			elif root.name == '[':
				lines.append(tab * tabs + self.writeIf(root, 1))
				tabs +=1
				self.writeTreeAsFunction(root.childs[0],lines, tabs)
				if root.rightChild:
					lines.append(tab * tabs + self.writeLine(root))
		else:
			lines.append(tab * tabs + self.writeExpect(root))
			if root.rightChild:
				lines.append(tab * tabs + self.writeLine(root))
		
		return lines
	
	def writeParser(self):
		parserFile = open('Parser.py', 'w')
		parserFile.write(
"""
import pickle
from utils import token

#Funciones y procesos compartidos para todos los parsers

file = open('tokens', 'rb')
tokens = pickle.load(file)
file.close

globalIndex = 0

lastToken = None
currToken = tokens[globalIndex]

def expect(string):
	global currToken
	global tokens
	global globalIndex
	global lastToken
	if currToken.value == string or currToken.token_name == string:
		lastToken = tokens[globalIndex]
		globalIndex +=1
		if globalIndex < len(tokens):
			currToken = tokens[globalIndex]
		else:
			return token('lastToken', None)
	else:
		print('Expected: ' + string + ' got: ', currToken.value )

#Funciones y procesos de este parser

""")
		for func in self.functions[0]:
			for line in func:
				parserFile.write(line)
		parserFile.write(self.nonterminals[0]+ "()")
		parserFile.close()

file = open('parseForest', 'rb')
forest = pickle.load(file)
file.close()
generator = parserGenerator(forest)
generator.writeParser()

import pickle
from ParseTree import Node

tab = "    "

class parserGenerator():
	def __init__(self, trees):
		self.trees = trees
		self.nonterminals = [i.name for i in trees]
		for i in self.trees:
			function = self.writeTreeAsFunction(i)
			for j in function:
				print(j)

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
		result += 'while lookAhead(currToken).value in ['
		for i in node.first:
			i = i.replace('"','')
			cleaned_string = '"'+ i + '"' + ","
			result += cleaned_string
		result = result[0: -1]
		result += '] or lookAhead(currToken).token_name in ['
		for i in node.first:
			i = i.replace('"','')
			cleaned_string = '"' + i + '"' + ","
			result += cleaned_string
		result = result[0: -1]
		result += ']:'
		return result + '\n'

	def writeExpect(self, node):
		return 'expect(' + node.name + ')\n'
	
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
			return 'else:\n'

		result += 'lookAhead(currToken).value in ['
		for i in node.first:
			i = i.replace('"','')
			cleaned_string = '"'+ i + '"' + ","
			result += cleaned_string
		result = result[0: -1]
		result += '] or lookAhead(currToken).token_name in ['
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
			elif root.name in self.nonterminals and tabs !=0:
				lines.append(tab * tabs +self.writeNonTerminal(root))
			else:
				lines.append(tab * tabs + self.writeExpect(root))
		elif root.type == "operadores":
			if root.name == "{":
				lines.append(tab * tabs + self.writeWhile(root))
				tabs += 1
			elif root.name == '.':
				pass
			elif root.name == '|':
				lines.append(tab * tabs + self.writeIf(root, 1))
				tabs +=1
			elif root.name == '[':
				lines.append(tab * tabs + self.writeIf(root, 1))
				tabs +=1

		else:
			lines.append(tab * tabs + self.writeExpect(root))
		for child in root.childs:
			self.writeTreeAsFunction(child,lines, tabs)
		if root.rightChild:
			lines.append(tab * tabs + self.writeLine(root))
		return lines
		

		
				

file = open('parseForest', 'rb')
forest = pickle.load(file)
file.close()
generator = parserGenerator(forest)


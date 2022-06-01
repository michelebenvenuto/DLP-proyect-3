from utils import Tokenizer, cocol_definitions, add_parenthesis, token
from Automata.direct_construction import Tree 
from Automata.functions import epsilon
from regexes import any 
import pickle

simboles = any
simboles.add('"')
class Scanner():
    def __init__(self, file_path):
        self.file_path = file_path
        self.reserved_words = ["COMPILER", "CHARACTERS", "KEYWORDS","TOKENS","PRODUCTIONS", "END"]
        self.curr_index = 0
        self.keywords = {}
        self.tokens = {}
        self.character_definitions = {}
        self.tokens_tokenized = {}
        self.character_definitions_tokenized = {}
        self.tokenizer = Tokenizer(cocol_definitions)
        self.read_clean_file(file_path)
        self.clean_file_lines()
        self.get_next_line()
        self.read_file_content()
        self.tokenize_chars()
        self.tokenize_tokens()
        self.build_characters()
        self.char_definitions_to_regex()
        self.clean_keywords_definitions()
        self.build_tokens_from_regex()
    
    #Save file content in the buffer self.file_content

    def read_clean_file(self,path):
        lines = []
        for line in open(path, 'r').readlines():
            if line == '\n':
                pass
            else:
                lines.append([char for char in line.strip('\r\t\n').split(' ')
                if char != '' or char])
        self.file_lines = lines
    
    def check_if_word_is_reserved(self,word):
        if word in self.reserved_words:
            return True
        return False

    def clean_file_lines(self):
        new_lines = []
        for line in self.file_lines:
            if len(line) == 0:
                pass
            else:
                new_lines.append(line)
        self.file_lines = new_lines

    def get_next_line(self):
        if self.curr_index < len(self.file_lines):
            self.curr_line = self.file_lines[self.curr_index]
            self.curr_index +=1
        else:
            self.curr_line = -1

    def read_file_content(self):  
        found_section = False
        while(self.curr_line) != -1:
            #if the len of the line is one it means we found a section header
            if len(self.curr_line) == 1:
                found_section = self.curr_line[0]
                self.get_next_line()
            
            #if the len of the line is two we found either the start or the end 
            elif len (self.curr_line) == 2:
                if "COMPILER" in self.curr_line:
                    self.compiler_name = self.curr_line[0]
                else:
                    pass
                self.get_next_line()
            # we are inside a section
            else:
                id = self.curr_line.pop(0)
                equals = self.curr_line.pop(0)
                i = 0
                value = ''
                while i < len(self.curr_line):
                    to_add = self.curr_line[i]
                    if to_add == "EXCEPT":
                        break
                    else:
                        if i + 1 < len(self.curr_line):
                            value += to_add + ' '
                        else:
                            value += to_add
                    i+= 1
                #removing the last position that is the dot
                if value[-1] == ".":
                    value = value[0:-1]
                # add (id, value) to corresponding dictionary 
                if found_section == "CHARACTERS":
                    self.character_definitions[id] = value
                elif found_section == "KEYWORDS":
                    self.keywords[id] = value
                elif found_section == "TOKENS":
                    self.tokens[id] = value
                else:
                    pass
                self.get_next_line()
    
    def clean_keywords_definitions(self):  
        for key in self.keywords.keys():         
            self.keywords[key] = add_parenthesis(self.keywords[key])

    def tokenize_chars(self):
        for key in self.character_definitions.keys():
            self.character_definitions_tokenized[key] = self.tokenizer.find_tokens(self.character_definitions[key])
    
    def tokenize_tokens(self):
        for key in self.tokens.keys():
            self.tokens_tokenized[key] = self.tokenizer.find_tokens(self.tokens[key])

    def apply_opperator(self, opp, x, y=0):
        if opp == "+":
            x = list(x)
            y = list(y)
            if len(x) == 1:
                x = x[0]
            if len(y) == 1:
                y = y[0]
            x = set(x)
            y = set(y)
            result = x.union(y)
            return result
        elif opp == "-":
            x = list(x)
            y = list(y)
            return set(x) - set(y)
        elif opp == "..":
            x = list(x)
            y = list(y)
            start = ord(x[0])
            end = ord(y[0])
            chars = ''
            for i in range(start, end+1):
                chars += chr(i)
            return set(chars)
        elif opp == "CHR":
            return set(chr(x))
        else:
            pass
    
    def build_characters(self):
        for key in self.character_definitions_tokenized.keys():
            result = []
            while len(self.character_definitions_tokenized[key]) != 0:
                definition = self.character_definitions_tokenized[key].pop(0)
                if definition.token_name == "opp":
                    if definition.value in ["+", "-", ".."]:
                        opperand1= result.pop()
                        opperand2 = self.character_definitions_tokenized[key].pop(0)
                        # if the second operand is an id replace it with its value in char definitions
                        if opperand2.token_name == "id":
                            opperand2 = self.character_definitions[opperand2.value]
                            result.append(self.apply_opperator(definition.value, opperand1, opperand2))
                        # if the second operand is CHR apply CHR to the next token and apply operators
                        elif opperand2.token_name == "char_opp":
                            opperand2 = self.apply_opperator("CHR",int(self.character_definitions_tokenized[key].pop(0).value))
                            result.append(self.apply_opperator(definition.value, opperand1, opperand2))
                        else:
                            result.append(self.apply_opperator(definition.value, opperand1, opperand2.value.replace('"', '')))
                elif definition.token_name == "char_opp":
                    opperand1 = self.character_definitions_tokenized[key].pop(0)
                    result.append(self.apply_opperator(definition.value, int(opperand1.value)))
                elif definition.token_name == "set" or definition.token_name == "string" :
                    result.append(set(definition.value.replace('"','')))
                elif definition.token_name == "char":
                    result.append(set(definition.value.replace("'",'')))
                elif definition.token_name == 'any':
                    result.append(set(any))
                elif definition.token_name == "id":
                    result.append(self.character_definitions[definition.value])
            self.character_definitions[key] = result[0]
    
    def char_definitions_to_regex(self):
        for key in self.character_definitions.keys():
            result = ['≤']
            char_list = list(self.character_definitions[key])
            i = 0
            while i < len(char_list):
                result.append(ord(char_list[i]))
                if i +1 < len(char_list):
                    result.append("∥")
                i +=1
            result.append('≥')
            self.character_definitions[key] = result

    
    def build_tokens_from_regex(self):
        for key in self.tokens_tokenized.keys():
            result = []
            while len(self.tokens_tokenized[key]) != 0:
                definition = self.tokens_tokenized[key].pop(0)
                if definition.token_name == "set" or definition.token_name == "string" or definition.token_name == "char":
                    if definition.token_name == "char":
                        for i in definition.value.replace("'",''):
                            result.append(ord(i))
                    else:
                        for i in definition.value.replace('"',''):
                            result.append(ord(i))
                elif definition.token_name == "id":
                    if definition.value in self.character_definitions.keys():
                        for i in self.character_definitions[definition.value]:
                            result.append(i)
                    else:
                        for i in self.tokens[definition.value]:
                            result.append(i)
                elif definition.token_name == "opp":
                    if definition.value == '|':
                        result.append('∥')
                    else:
                        result.append(definition.value)
            self.tokens[key] = result

    def build_tokens(self):
        found_tokens = []
        for i in self.keywords.keys():
            found_token = token(i, self.keywords[i])
            found_tokens.append(found_token)
        for i in self.tokens.keys():
            found_token = token(i, self.tokens[i])
            found_tokens.append(found_token)
        return found_tokens
if __name__ == '__main__':
    file_input = input("Archivo con las definiciones ->")
    scanner = Scanner(file_input)
    tokens = scanner.build_tokens()
    file_name = 'tokens'
    outfile = open(file_name, 'wb')
    pickle.dump(tokens,outfile)
    outfile.close()
    print(f'Las tokens se enceuntran en el archivo {file_name}')

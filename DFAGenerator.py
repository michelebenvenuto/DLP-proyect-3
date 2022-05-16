from Automata.direct_construction import Tree
from utils import token
import pickle
import sys

class DFAGenerator():
    def __init__(self, definitions):
        self.definitions = definitions
        self.build_regex()
        self.tree = Tree(self.regex)
        self.dfa = self.tree.generate_DFA()
        self.simple_regexes = dict((x,Tree(y).generate_DFA()) for x,y in definitions)
        self.ignore_set = set()    
        self.find_ignore_set()

    def build_regex(self):
        final_regex = []
        i = 0
        while i < len(self.definitions):
            if i +1 >=len(self.definitions):
                for j in self.definitions[i].value:
                    final_regex.append(j) 
            else:
                for j in self.definitions[i].value:
                    final_regex.append(j)
                final_regex.append('∥')
            i+=1
        self.regex = final_regex

    def find_ignore_set(self):
        for token in self.definitions:
            if token.token_name == "IGNORE":
                list = []
                for i in token.value:
                    if isinstance(i, int):
                        list.append(i)
                self.ignore_set = set(list)

    def identify_token(self,string):
        for key in self.simple_regexes:
            if self.simple_regexes[key].simulate(string)[0]:
                return key

    def find_tokens(self,string):
        buffer = ''       
        simulation_results = [] 
        Identified_tokens = []
        while string != '':
            position_of_last_true = -1
            #fill the simulation results array with the result of simulating the chars of the strings 
            i = 0
            while i < len(string):
                if ord(string[i]) in self.ignore_set:
                    string = string[0:i] + string[i+1:]

                buffer += string[i]
                result = self.dfa.simulate(buffer)
                simulation_results.append(result[0])
                i += 1
            #find the position of the last and first true
            j =0
            while j < len(simulation_results):
                if simulation_results[j]:
                    position_of_last_true = j
                j+=1
            # check if position_of_last_true is -1, if this is true remove the first char of the string
            if position_of_last_true == -1:
                string_list = list(string)
                char_error = string_list.pop(0)
                print('Error Lexico encontramos:', char_error)
                string = ''.join([str(item) for item in string_list])
            else:
                token_name = self.identify_token(string[0:position_of_last_true+1])
                Identified_tokens.append(token(token_name,string[0:position_of_last_true+1]))
                string = string[position_of_last_true+1:]
            buffer = ''
            simulation_results = []
        return Identified_tokens
if __name__ == '__main__':
    filename = input("Ingrese el archivo generado por el Scanner->")
    infile = open(filename, 'rb')
    tokens = pickle.load(infile)
    infile.close()  
    sys.setrecursionlimit(5000)       
    parser = DFAGenerator(tokens)
    out_file_name = 'dfa'
    outfile = open(out_file_name, 'wb')
    pickle.dump(parser, outfile)
    outfile.close()
    print(f'El dfa se encuentra en el archivo {out_file_name}')

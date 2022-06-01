from Scanner import Scanner
import pickle
from DFAGenerator import DFAGenerator

tokens_file = 'TempFiles/token_specifications.ATG'
scanner = Scanner(tokens_file)
tokens = scanner.build_tokens()
file_name = 'tokens'
outfile = open(file_name, 'wb')
pickle.dump(tokens,outfile)
outfile.close()
print(f'Las tokens se enceuntran en el archivo {file_name}')

productions_file = 'Productions.ATG'
productionsScanner = Scanner(productions_file)
productionsTokens = productionsScanner.build_tokens()
dfa = DFAGenerator(productionsTokens)
file = open("TempFiles/productions.ATG", 'r')
file_content = file.read()
file.close()
productionsTokens = dfa.find_tokens(file_content)
file_name = 'tokens_productions'
outfile = open(file_name, 'wb')
pickle.dump(productionsTokens,outfile)
outfile.close()
print(f'Las tokens para las producciones se enceuntran en el archivo {file_name}')
class codeGenerator():
    def __init__(self, path):
        self.path = path
        self.tab = '    '
        self.line_end = '\n'
        self.write_program()
    
    def write_program(self):
        file = open(self.path, 'w')
        file.write(
'''import sys
import pickle
from DFAGenerator import DFAGenerator

sys.setrecursionlimit(5000)  

if len(sys.argv) == 0:
    sys.exit("input file missing")
file_path = sys.argv[1]

file = open(file_path, 'r')
file_content = file.read()
file.close()

filename = input("Ingrese el archivo generado por el programa DFAGenerator->")
infile = open(filename, 'rb')
parser = pickle.load(infile)
infile.close()

identified_tokens = parser.find_tokens(file_content)
for i in identified_tokens:
    print(i)

out_file_name = 'tokens'
outfile = open(out_file_name, 'wb')
pickle.dump(identified_tokens, outfile)
outfile.close()

print(f'Las tokens identificadas se encuentra en el archivo {out_file_name}')
''')
        file.close()

code_generator = codeGenerator('generated_code.py')
print('Generated code available in file generated_code.py')


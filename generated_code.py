import sys
import pickle
from DFAGenerator import DFAGenerator

sys.setrecursionlimit(5000)  

if len(sys.argv) == 0:
    sys.exit("input file missing")
file_path = sys.argv[1]

file = open(file_path, 'r')
file_content = file.read()
file.close()

filename = "dfa"
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

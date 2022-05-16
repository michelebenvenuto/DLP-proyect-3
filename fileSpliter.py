#This class splits a definitions file into two files and generates the tokens for both files

class fileSpliter():
    def __init__(self,filePath):
        self.file_path = filePath
        self.extractFileContent()
        self.splitFile()

    def extractFileContent(self):
        file = open(self.file_path, 'r')
        self.file_content = file.read()
        file.close()

    #Splits a definition file into a Productions file and a file with the token Specifications
    def splitFile(self):
        productions_start = self.file_content.find("PRODUCTIONS")
        production_specifications = self.file_content[productions_start:]
        token_specifications = self.file_content[0:productions_start-1]
        file1 = open('TempFiles/productions.ATG','w')
        file1.write(production_specifications)
        file1.close()
        file2 = open('TempFiles/token_specifications.ATG','w')
        file2.write(token_specifications)
        file2.close()
if __name__ =='__main__':
    file = input("Archivo con las definiciones ->")
    spliter = fileSpliter(file)

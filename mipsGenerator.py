class MipsGenerator():
    def __init__(self, threeAddressCode):
        self.threeAddressCode = threeAddressCode
        self.code = []
        self.data = []
        self.text = []
        self.stack = []
        self.savedVariables = []
        self.currentSaved = 0
    
    def generateData(self):
        self.data.append(".data")
        string_counter = 0
        for three in self.threeAddressCode:
            for quadruple in three.code:
                if quadruple.op == 'PARAMETER':
                    if quadruple.result[0] == '"' and quadruple.result[-1] == '"':
                        self.data.append("const_" + str(string_counter) + ": .asciiz " + quadruple.result)
    
    def generateText(self):
        self.text.append(".text")
        self.text.append(".globl main")
        self.text.append("main: ")

    def detectTemporal(self, arg):
        if arg[0] == 't':
            return True
        else:
            return False

    def getSVariable(self):
        if (len(self.savedVariables) == 0):
            temporal  = "s" + str(self.currentSaved)
            self.currentSaved += 1
        else:
            temporal = self.savedVariables[0]
            self.savedVariables.remove(temporal)
        return temporal

    def makeSAvailable(self, value):
        if (value[0] == '$' and value[1] == 's'):
            self.savedVariables.append(value[1:])

    def generateDefault(self):
        self.code.append("out_string: li $v0, 4\n\tla $a0, const_0\n\tsyscall\n\tjr $ra")
        return

    def generateCode(self):
        result, arg1, arg2 = None, None, None
        for three in self.threeAddressCode:
            for quadruple in three.code:
                if quadruple.result != None and quadruple.op != 'CALL':
                    if quadruple.result[0] == 't':
                        result = '$'+quadruple.result
                    elif quadruple.result.startswith('global.') or quadruple.result.startswith('local.'):
                        # LOAD VALUE FROM TABLE
                        availableVar = '$' + self.getSVariable()
                        startAddress = quadruple.result.index('[')
                        endAddress = quadruple.result.index(']')
                        resultName = quadruple.result[startAddress + 1: endAddress] + '(' + quadruple.result[0:startAddress] + ')'
                        self.code.append("\tlw "+ availableVar + ", " + resultName)
                        result = availableVar
                    else:
                        result = quadruple.result
                if quadruple.arg1 != None and quadruple.op != 'CALL':
                    if quadruple.arg1[0] == 't':
                        arg1 = '$'+quadruple.arg1
                    elif quadruple.arg1.startswith('global.') or quadruple.arg1.startswith('local.'):
                        # LOAD VALUE FROM TABLE
                        availableVar = '$' + self.getSVariable()
                        startAddress = quadruple.arg1.index('[')
                        endAddress = quadruple.arg1.index(']')
                        arg1Name = quadruple.arg1[startAddress + 1: endAddress] + '(' + quadruple.arg1[0:startAddress] + ')'
                        self.code.append("\tlw "+ availableVar + ", " + arg1Name)
                        arg1 = availableVar
                    else:
                        arg1 = quadruple.arg1
                if quadruple.arg2 != None and quadruple.op != 'CALL':
                    if quadruple.arg2[0] == 't':
                        arg2 = '$'+quadruple.arg2
                    elif quadruple.arg2.startswith('global.') or quadruple.arg2.startswith('local.'):
                        # LOAD VALUE FROM TABLE
                        availableVar = '$' + self.getSVariable()
                        startAddress = quadruple.arg2.index('[')
                        endAddress = quadruple.arg2.index(']')
                        arg2Name = quadruple.arg2[startAddress + 1: endAddress] + '(' + quadruple.arg2[0:startAddress] + ')'
                        self.code.append("\tlw "+ availableVar + ", " + arg2Name)
                        arg2 = availableVar
                    else:
                        arg2 = quadruple.arg2
                if quadruple.op == '+':
                    self.code.append("\tadd " + result + ", " + arg1 + ", " + arg2)
                    self.makeSAvailable(result)
                    self.makeSAvailable(arg1)
                    self.makeSAvailable(arg2)
                elif quadruple.op == '-':
                    self.code.append("\tsub " + result + ", " + arg1 + ", " + arg2)
                    self.makeSAvailable(result)
                    self.makeSAvailable(arg1)
                    self.makeSAvailable(arg2)
                elif quadruple.op == '*':
                    self.code.append("\tmult " + arg1 + ", " + arg2)
                    self.code.append("\tmflo " + result)
                    self.makeSAvailable(result)
                    self.makeSAvailable(arg1)
                    self.makeSAvailable(arg2)
                elif quadruple.op == '/':
                    self.code.append("\tdiv " + arg1 + ", " + arg2)
                    self.code.append("\tmflo " + result)
                    self.makeSAvailable(result)
                    self.makeSAvailable(arg1)
                    self.makeSAvailable(arg2)
                elif quadruple.op == 'equal':
                    if quadruple.arg2 == None:
                        # self.code.append("\tsw " + result + ", " + arg1)
                        self.makeSAvailable(result)
                        self.makeSAvailable(arg1) 
                elif quadruple.op == 'CALL':
                    if quadruple.result == 'global.IO[0]':
                        self.code.append("\tjal out_string")
        self.code.append("\tjr $ra")

                    
    def generate(self):
        self.generateData()
        self.generateText()
        self.generateCode()
        self.generateDefault()

    
    def __str__(self):
        string = ""
        for line in self.data:
            string += line + "\n"
        for line in self.text:
            string += line + "\n"
        for line in self.code:
            string += line + "\n"
        return string

   
        

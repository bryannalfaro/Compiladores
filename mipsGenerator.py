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
    
    def generateText(self):
        self.text.append(".text")
        self.text.append(".globl main")

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

    def generateCode(self):
        result, arg1, arg2 = None, None, None
        for three in self.threeAddressCode:
            for quadruple in three.code:
                if quadruple.result != None:
                    if quadruple.result[0] == 't':
                        result = '$'+quadruple.result
                    elif quadruple.result.startswith('global.') or quadruple.result.startswith('local.'):
                        # LOAD VALUE FROM TABLE
                        availableVar = '$' + self.getSVariable()
                        self.code.append("lw "+ availableVar + ", " + quadruple.result)
                        result = availableVar
                    else:
                        result = quadruple.result
                if quadruple.arg1 != None:
                    if quadruple.arg1[0] == 't':
                        arg1 = '$'+quadruple.arg1
                    elif quadruple.arg1.startswith('global.') or quadruple.arg1.startswith('local.'):
                        # LOAD VALUE FROM TABLE
                        availableVar = '$' + self.getSVariable()
                        self.code.append("lw "+ availableVar + ", " + quadruple.arg1)
                        arg1 = availableVar
                    else:
                        arg1 = quadruple.arg1
                if quadruple.arg2 != None:
                    if quadruple.arg2[0] == 't':
                        arg2 = '$'+quadruple.arg2
                    elif quadruple.arg2.startswith('global.') or quadruple.arg2.startswith('local.'):
                        # LOAD VALUE FROM TABLE
                        availableVar = '$' + self.getSVariable()
                        self.code.append("lw "+ availableVar + ", " + quadruple.arg2)
                        arg2 = availableVar
                    else:
                        arg2 = quadruple.arg2
                if quadruple.op == '+':
                    self.code.append("add " + result + ", " + arg1 + ", " + arg2)
                    self.makeSAvailable(result)
                    self.makeSAvailable(arg1)
                    self.makeSAvailable(arg2)
                elif quadruple.op == '-':
                    self.code.append("sub " + result + ", " + arg1 + ", " + arg2)
                    self.makeSAvailable(result)
                    self.makeSAvailable(arg1)
                    self.makeSAvailable(arg2)
                elif quadruple.op == '*':
                    self.code.append("mult " + arg1 + ", " + arg2)
                    self.code.append("mflo " + result)
                    self.makeSAvailable(result)
                    self.makeSAvailable(arg1)
                    self.makeSAvailable(arg2)
                elif quadruple.op == '/':
                    self.code.append("div " + arg1 + ", " + arg2)
                    self.code.append("mflo " + result)
                    self.makeSAvailable(result)
                    self.makeSAvailable(arg1)
                    self.makeSAvailable(arg2)
                elif quadruple.op == 'equal':
                    if quadruple.arg2 == None:
                        self.code.append("sw " + result + ", " + arg1)
                        self.makeSAvailable(result)
                        self.makeSAvailable(arg1)

                    
    def generate(self):
        self.generateData()
        self.generateText()
        self.generateCode()

    
    def __str__(self):
        string = ""
        for line in self.data:
            string += line + "\n"
        for line in self.text:
            string += line + "\n"
        for line in self.code:
            string += line + "\n"
        return string

   
        

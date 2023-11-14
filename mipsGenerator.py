class MipsGenerator():
    def __init__(self, threeAddressCode):
        self.threeAddressCode = threeAddressCode
        self.code = []
        self.data = []
        self.text = []
        self.stack = []
        self.savedVariables = []
        self.currentSaved = 0
        self.strings = {}
        self.types = {}
        self.hasSubstr = False
    
    def generateData(self):
        self.data.append(".data")
        string_counter = 0
        type_counter = 0
        for three in self.threeAddressCode:
            for quadruple in three.code:
                if quadruple.op == 'PARAMETER':
                    if quadruple.result[0] == '"' and quadruple.result[-1] == '"':
                        self.data.append("const_" + str(string_counter) + ": .asciiz " + quadruple.result)
                        #add the const_counter and quadruple result
                        self.strings[string_counter] = quadruple.result
                        string_counter += 1
                if quadruple.op == 'CALLER':
                    self.data.append("type_"+ str(type_counter)+": .asciiz "+'"'+quadruple.result+'"') #agregar el texto
                    self.data.append("buffer_"+str(type_counter)+": .space "+str(len(quadruple.result)+1)) #reservar espacio para substring
                    self.types[type_counter] = '"' + quadruple.result + '"'
                    type_counter += 1

    
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
        self.code.append("out_string: li $v0, 4 \n\tsyscall\n\tjr $ra")
        return
    
    def generateSubstr(self):
        self.code.append("substr: add $a0, $a0, $a1\n\tmove $t0, $a0\n\tmove $t1, $a3\n\tli $t2, 0")         
        self.code.append("fill_buffer:lb $t3, 0($t0)\n\tsb $t3, 0($t1)\n\taddi $t0, $t0, 1\n\taddi $t1, $t1, 1\n\taddi $t2, $t2, 1\n\tbne $t2, $a2, fill_buffer")
        self.code.append("\n\tsb $zero, 0($t1)\n\tmove $v0, $a3\n\tjr $ra")
        
    def generateCode(self):
        result, arg1, arg2 = None, None, None
        counterArguments= 0
        actualCaller = None
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
                        counterArguments = 0
                        self.code.append("\tjal out_string")
                    if quadruple.result == 'global.String[2]':
                        self.hasSubstr = True
                        keyCount = None
                        for key, value in self.types.items():
                            if value == actualCaller:
                                self.code.append("\tla $a"+str(counterArguments%4)+", buffer_" + str(key))
                                counterArguments+=1
                                keyCount = str(key)
                        self.code.append("\tjal substr")
                        self.code.append("\t la $t1, buffer_"+keyCount)
                elif quadruple.op == 'CALLER':
                    for key, value in self.types.items():
                        if value == '"' + quadruple.result + '"':
                            self.code.append("\tla $t0, type_" + str(key))
                            self.code.append("\tmove $a"+str(counterArguments%4)+", $t0")
                            actualCaller = '"' + quadruple.result + '"'
                            counterArguments+=1
                elif quadruple.op == 'PARAMETER':
                    if quadruple.result[0] == '"' and quadruple.result[-1] == '"':
                        #search if value matches in object of string
                        for key, value in self.strings.items():
                            if value == quadruple.result:
                                self.code.append("\tla $a0, const_" + str(key))
                    else:
                        #check if result is int
                        try:
                            int(result)
                            self.code.append("\tli $a"+str(counterArguments%4)+", " + result)
                        except:
                            self.code.append("\tmove $a"+str(counterArguments%4)+", " + result)
                            
                        counterArguments +=1
        self.code.append("\tjr $ra")

                    
    def generate(self):
        self.generateData()
        self.generateText()
        self.generateCode()
        #terminate
        self.code.append("li $v0, 10")
        self.code.append("syscall")
        self.generateDefault()
        if self.hasSubstr:
            self.generateSubstr()
        


    
    def __str__(self):
        string = ""
        for line in self.data:
            string += line + "\n"
        for line in self.text:
            string += line + "\n"
        for line in self.code:
            string += line + "\n"
        return string

   
        

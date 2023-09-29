from quadrupleCode import *

class ThreeAddressCode():
    def __init__(self):
        self.code = []
        self.tempCounters = -1
        self.address = None
        self.typeValue = None
    
    def add(self, quadruple):
        if quadruple != []:
            if isinstance(quadruple, list):
                for q in quadruple:
                    self.code.append(q)
            else:
                self.code.append(quadruple)
        
    
    def addAddress(self, address):
        self.address = address

    
    def __str__(self):
        string = ""
        for quadruple in self.code:
            if quadruple != []:
                string += str(quadruple) + "\n"
            else:
                string += 'empty' + "\n"
        
        return string
    
class Generator():
    def __init__(self):
        self.tempCounters = 0
        self.counterIf = 0
        self.counterNext=0
        self.counterBegin = 0
    
    
    def getTemporal(self):
        temporal  = "t" + str(self.tempCounters)
        self.tempCounters += 1

        return temporal
    
    def getIfLabel(self):
        trueLabel , falseLabel = "true" + str(self.counterIf), "false" + str(self.counterIf)
        self.counterIf += 1
        return trueLabel, falseLabel
    
    def getNextLabel(self):
        nextLabel = "next" + str(self.counterNext)
        self.counterNext += 1
        return nextLabel    
    
    def getBeginLabel(self):
        beginLabel = "begin" + str(self.counterBegin)
        self.counterBegin += 1
        return beginLabel
    
    
    def __str__(self):
        string = ""
        for temporal in self.temporals:
            string += str(temporal) + "\n"
        
        return string
            


    
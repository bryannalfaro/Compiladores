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
    
class Temporals():
    def __init__(self):
        self.tempCounters = -1
    
    
    def getTemporal(self):
        self.tempCounters += 1
        return "t" + str(self.tempCounters)
    
    def __str__(self):
        string = ""
        for temporal in self.temporals:
            string += str(temporal) + "\n"
        
        return string
            


    
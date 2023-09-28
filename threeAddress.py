from quadrupleCode import *
class ThreeAddressCode():
    def __init__(self):
        self.code = []
        self.tempCounters = -1
        self.address = None
    
    def add(self, quadruple):
        self.code.append(quadruple)
    
    def addAddress(self, address):
        self.address = address
    
    def getTemporal(self):
        self.tempCounters += 1
        return "t" + str(self.tempCounters)
    
    def __str__(self):
        string = ""
        for quadruple in self.code:
            string += str(quadruple) + "\n"
        
        return string
            


    
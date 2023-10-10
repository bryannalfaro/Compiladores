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
        self.availableCounters = []
        self.stackIfNeeded = []
        self.counterIf = 0
        self.counterNext=0
        self.counterBegin = 0
        self.counterWhile = 0
        self.lowestTemporal = 0
    
    
    def getTemporal(self):
        if (len(self.availableCounters) == 0):
            temporal  = "t" + str(self.tempCounters)
            self.tempCounters += 1
        else:
            temporal = self.availableCounters[0]
            self.availableCounters.remove(temporal)
        return temporal

    def makeTemporalAvailable(self, temporal):
        self.availableCounters.append(temporal)

    def makeTemporalAvailableFirst(self, temporal):
        self.availableCounters.insert(0, temporal)
    
    def getIfLabel(self, amount, label=None):
        if amount == 1:
            trueLabel , falseLabel = "true" + str(self.counterIf), "false" + str(self.counterIf)
            self.counterIf += 1
        else:
            if label == 'true':
                trueLabel  = "true" + str(self.counterIf)
                self.counterIf += 1
                return trueLabel
            else:
                falseLabel  = "false" + str(self.counterIf)
                self.counterIf += 1
                return falseLabel

        return trueLabel, falseLabel
    
    def getWhileLabel(self,amount, label=None):
        if amount == 1:
            trueLabel , falseLabel = "trueWhile" + str(self.counterWhile), "falseWhile" + str(self.counterWhile)
            self.counterWhile += 1
        else:
            if label == 'true':
                trueLabel  = "trueWhile" + str(self.counterWhile)
                self.counterWhile += 1
                return trueLabel
            else:
                falseLabel  = "false" + str(self.counterWhile)
                self.counterWhile += 1
                return falseLabel

        return trueLabel, falseLabel
    
    def getNextLabel(self):
        nextLabel = "next" + str(self.counterNext)
        self.counterNext += 1
        return nextLabel    
    
    def getBeginLabel(self):
        beginLabel = "begin" + str(self.counterBegin)
        self.counterBegin += 1
        return beginLabel

    def resetTemporal(self):
        self.tempCounters = 0

    def setLowestTemporal(self, lowestTemporal):
        self.lowestTemporal = int(lowestTemporal[1:])
    
    def resetLowestTemporal(self):
        self.tempCounters = self.lowestTemporal
    
    
    
    def __str__(self):
        string = ""
        for temporal in self.temporals:
            string += str(temporal) + "\n"
        
        return string
            


    
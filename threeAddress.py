from tripletCode import *
class ThreeAddressCode():
    def __init__(self):
        self.triplets_list = []
        self.tempCounters = -1
    
    def add(self, triplet):
        self.triplets_list.append(triplet)
        return triplet
    
    def getTemporal(self):
        self.tempCounters += 1
        return "t" + str(self.tempCounters)


    
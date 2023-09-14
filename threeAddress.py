from tripletCode import *
class ThreeAddressCode():
    def __init__(self):
        self.triplets_list = []
    
    def add(self, triplet):
        self.triplets_list.append(triplet)
        return triplet
    
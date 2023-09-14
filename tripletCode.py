class Triplet(object):
    #None porque puede solo tener un argumento
    def __init__(self, op, arg1, arg2 = None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        

    def __str__(self):
        return str(self.op) + " " + str(self.arg1) + " " + str(self.arg2) 
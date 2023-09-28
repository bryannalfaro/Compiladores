class Quadruple(object):
    def __init__(self, op, arg1, arg2 = None, result=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
        

    def __str__(self):
        if self.op == 'identifier':
            return str(self.arg1)
        elif self.op == '=':
            return str(self.result) + str(self.op) + str(self.arg1)
        elif self.op == '*' or self.op == '/' or self.op == '+' or self.op == '-':
            return str(self.result) + " = " + str(self.arg1) + str(self.op) + str(self.arg2)
from CalculatorListener import CalculatorListener
class CalculatorListener(CalculatorListener):
    def __init__(self):
        self.stack = []

    def exitStart(self, ctx):
        print(self.stack.pop())

    def exitExpression(self, ctx):
        if ctx.getChildCount() == 3:  # Binary operation
            right = self.stack.pop()
            left = self.stack.pop()
            operator = ctx.getChild(1).getText()
            if operator == '+':
                result = left + right
            else:
                result = left - right
            self.stack.append(result)

    def exitTerm(self, ctx):
        if ctx.getChildCount() == 3:  # Binary operation
            right = self.stack.pop()
            left = self.stack.pop()
            operator = ctx.getChild(1).getText()
            if operator == '*':
                result = left * right
            else:
                result = left / right
            self.stack.append(result)

    def exitFactor(self, ctx):
        if ctx.NUMBER():
            self.stack.append(int(ctx.NUMBER().getText()))

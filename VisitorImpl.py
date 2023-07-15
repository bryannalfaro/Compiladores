from antlr4 import *
class HelloWorld(ParseTreeVisitor):
    def visitStart(self, ctx):
        return self.visit(ctx.expression())

    def visitExpression(self, ctx):
        left = self.visit(ctx.term(0))
        for i in range(1, len(ctx.term())):
            operator = ctx.getChild(2 * i - 1).getText()
            right = self.visit(ctx.term(i))
            if operator == '+':
                left += right
            else:
                left -= right
        return left

    def visitTerm(self, ctx):
        left = self.visit(ctx.factor(0))
        for i in range(1, len(ctx.factor())):
            operator = ctx.getChild(2 * i - 1).getText()
            right = self.visit(ctx.factor(i))
            if operator == '*':
                left *= right
            else:
                left /= right
        return left

    def visitFactor(self, ctx):
        if ctx.NUMBER():
            return int(ctx.NUMBER().getText())
        else:
            return self.visit(ctx.expression())
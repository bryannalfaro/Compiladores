# Generated from HelloWorld.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .HelloWorldParser import HelloWorldParser
else:
    from HelloWorldParser import HelloWorldParser

# This class defines a complete generic visitor for a parse tree produced by HelloWorldParser.

class HelloWorldVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by HelloWorldParser#start.
    def visitStart(self, ctx:HelloWorldParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HelloWorldParser#expression.
    def visitExpression(self, ctx:HelloWorldParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HelloWorldParser#term.
    def visitTerm(self, ctx:HelloWorldParser.TermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HelloWorldParser#factor.
    def visitFactor(self, ctx:HelloWorldParser.FactorContext):
        return self.visitChildren(ctx)



del HelloWorldParser
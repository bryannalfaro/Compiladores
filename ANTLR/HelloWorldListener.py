# Generated from HelloWorld.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .HelloWorldParser import HelloWorldParser
else:
    from HelloWorldParser import HelloWorldParser

# This class defines a complete listener for a parse tree produced by HelloWorldParser.
class HelloWorldListener(ParseTreeListener):

    # Enter a parse tree produced by HelloWorldParser#start.
    def enterStart(self, ctx:HelloWorldParser.StartContext):
        pass

    # Exit a parse tree produced by HelloWorldParser#start.
    def exitStart(self, ctx:HelloWorldParser.StartContext):
        pass


    # Enter a parse tree produced by HelloWorldParser#expression.
    def enterExpression(self, ctx:HelloWorldParser.ExpressionContext):
        pass

    # Exit a parse tree produced by HelloWorldParser#expression.
    def exitExpression(self, ctx:HelloWorldParser.ExpressionContext):
        pass


    # Enter a parse tree produced by HelloWorldParser#term.
    def enterTerm(self, ctx:HelloWorldParser.TermContext):
        pass

    # Exit a parse tree produced by HelloWorldParser#term.
    def exitTerm(self, ctx:HelloWorldParser.TermContext):
        pass


    # Enter a parse tree produced by HelloWorldParser#factor.
    def enterFactor(self, ctx:HelloWorldParser.FactorContext):
        pass

    # Exit a parse tree produced by HelloWorldParser#factor.
    def exitFactor(self, ctx:HelloWorldParser.FactorContext):
        pass



del HelloWorldParser
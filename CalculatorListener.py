# Generated from Calculator.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .CalculatorParser import CalculatorParser
else:
    from CalculatorParser import CalculatorParser

# This class defines a complete listener for a parse tree produced by CalculatorParser.
class CalculatorListener(ParseTreeListener):

    # Enter a parse tree produced by CalculatorParser#start.
    def enterStart(self, ctx:CalculatorParser.StartContext):
        pass

    # Exit a parse tree produced by CalculatorParser#start.
    def exitStart(self, ctx:CalculatorParser.StartContext):
        pass


    # Enter a parse tree produced by CalculatorParser#expression.
    def enterExpression(self, ctx:CalculatorParser.ExpressionContext):
        pass

    # Exit a parse tree produced by CalculatorParser#expression.
    def exitExpression(self, ctx:CalculatorParser.ExpressionContext):
        pass


    # Enter a parse tree produced by CalculatorParser#term.
    def enterTerm(self, ctx:CalculatorParser.TermContext):
        pass

    # Exit a parse tree produced by CalculatorParser#term.
    def exitTerm(self, ctx:CalculatorParser.TermContext):
        pass


    # Enter a parse tree produced by CalculatorParser#factor.
    def enterFactor(self, ctx:CalculatorParser.FactorContext):
        pass

    # Exit a parse tree produced by CalculatorParser#factor.
    def exitFactor(self, ctx:CalculatorParser.FactorContext):
        pass



del CalculatorParser
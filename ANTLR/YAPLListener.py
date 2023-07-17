# Generated from YAPL.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .YAPLParser import YAPLParser
else:
    from YAPLParser import YAPLParser

# This class defines a complete listener for a parse tree produced by YAPLParser.
class YAPLListener(ParseTreeListener):

    # Enter a parse tree produced by YAPLParser#program.
    def enterProgram(self, ctx:YAPLParser.ProgramContext):
        pass

    # Exit a parse tree produced by YAPLParser#program.
    def exitProgram(self, ctx:YAPLParser.ProgramContext):
        pass


    # Enter a parse tree produced by YAPLParser#class_grammar.
    def enterClass_grammar(self, ctx:YAPLParser.Class_grammarContext):
        pass

    # Exit a parse tree produced by YAPLParser#class_grammar.
    def exitClass_grammar(self, ctx:YAPLParser.Class_grammarContext):
        pass


    # Enter a parse tree produced by YAPLParser#feature.
    def enterFeature(self, ctx:YAPLParser.FeatureContext):
        pass

    # Exit a parse tree produced by YAPLParser#feature.
    def exitFeature(self, ctx:YAPLParser.FeatureContext):
        pass


    # Enter a parse tree produced by YAPLParser#formal.
    def enterFormal(self, ctx:YAPLParser.FormalContext):
        pass

    # Exit a parse tree produced by YAPLParser#formal.
    def exitFormal(self, ctx:YAPLParser.FormalContext):
        pass


    # Enter a parse tree produced by YAPLParser#plusminus.
    def enterPlusminus(self, ctx:YAPLParser.PlusminusContext):
        pass

    # Exit a parse tree produced by YAPLParser#plusminus.
    def exitPlusminus(self, ctx:YAPLParser.PlusminusContext):
        pass


    # Enter a parse tree produced by YAPLParser#negation.
    def enterNegation(self, ctx:YAPLParser.NegationContext):
        pass

    # Exit a parse tree produced by YAPLParser#negation.
    def exitNegation(self, ctx:YAPLParser.NegationContext):
        pass


    # Enter a parse tree produced by YAPLParser#curly.
    def enterCurly(self, ctx:YAPLParser.CurlyContext):
        pass

    # Exit a parse tree produced by YAPLParser#curly.
    def exitCurly(self, ctx:YAPLParser.CurlyContext):
        pass


    # Enter a parse tree produced by YAPLParser#string.
    def enterString(self, ctx:YAPLParser.StringContext):
        pass

    # Exit a parse tree produced by YAPLParser#string.
    def exitString(self, ctx:YAPLParser.StringContext):
        pass


    # Enter a parse tree produced by YAPLParser#isvoid.
    def enterIsvoid(self, ctx:YAPLParser.IsvoidContext):
        pass

    # Exit a parse tree produced by YAPLParser#isvoid.
    def exitIsvoid(self, ctx:YAPLParser.IsvoidContext):
        pass


    # Enter a parse tree produced by YAPLParser#false.
    def enterFalse(self, ctx:YAPLParser.FalseContext):
        pass

    # Exit a parse tree produced by YAPLParser#false.
    def exitFalse(self, ctx:YAPLParser.FalseContext):
        pass


    # Enter a parse tree produced by YAPLParser#less.
    def enterLess(self, ctx:YAPLParser.LessContext):
        pass

    # Exit a parse tree produced by YAPLParser#less.
    def exitLess(self, ctx:YAPLParser.LessContext):
        pass


    # Enter a parse tree produced by YAPLParser#while.
    def enterWhile(self, ctx:YAPLParser.WhileContext):
        pass

    # Exit a parse tree produced by YAPLParser#while.
    def exitWhile(self, ctx:YAPLParser.WhileContext):
        pass


    # Enter a parse tree produced by YAPLParser#int.
    def enterInt(self, ctx:YAPLParser.IntContext):
        pass

    # Exit a parse tree produced by YAPLParser#int.
    def exitInt(self, ctx:YAPLParser.IntContext):
        pass


    # Enter a parse tree produced by YAPLParser#call.
    def enterCall(self, ctx:YAPLParser.CallContext):
        pass

    # Exit a parse tree produced by YAPLParser#call.
    def exitCall(self, ctx:YAPLParser.CallContext):
        pass


    # Enter a parse tree produced by YAPLParser#newtype.
    def enterNewtype(self, ctx:YAPLParser.NewtypeContext):
        pass

    # Exit a parse tree produced by YAPLParser#newtype.
    def exitNewtype(self, ctx:YAPLParser.NewtypeContext):
        pass


    # Enter a parse tree produced by YAPLParser#timesdiv.
    def enterTimesdiv(self, ctx:YAPLParser.TimesdivContext):
        pass

    # Exit a parse tree produced by YAPLParser#timesdiv.
    def exitTimesdiv(self, ctx:YAPLParser.TimesdivContext):
        pass


    # Enter a parse tree produced by YAPLParser#equal.
    def enterEqual(self, ctx:YAPLParser.EqualContext):
        pass

    # Exit a parse tree produced by YAPLParser#equal.
    def exitEqual(self, ctx:YAPLParser.EqualContext):
        pass


    # Enter a parse tree produced by YAPLParser#not.
    def enterNot(self, ctx:YAPLParser.NotContext):
        pass

    # Exit a parse tree produced by YAPLParser#not.
    def exitNot(self, ctx:YAPLParser.NotContext):
        pass


    # Enter a parse tree produced by YAPLParser#paren.
    def enterParen(self, ctx:YAPLParser.ParenContext):
        pass

    # Exit a parse tree produced by YAPLParser#paren.
    def exitParen(self, ctx:YAPLParser.ParenContext):
        pass


    # Enter a parse tree produced by YAPLParser#lesseq.
    def enterLesseq(self, ctx:YAPLParser.LesseqContext):
        pass

    # Exit a parse tree produced by YAPLParser#lesseq.
    def exitLesseq(self, ctx:YAPLParser.LesseqContext):
        pass


    # Enter a parse tree produced by YAPLParser#true.
    def enterTrue(self, ctx:YAPLParser.TrueContext):
        pass

    # Exit a parse tree produced by YAPLParser#true.
    def exitTrue(self, ctx:YAPLParser.TrueContext):
        pass


    # Enter a parse tree produced by YAPLParser#let.
    def enterLet(self, ctx:YAPLParser.LetContext):
        pass

    # Exit a parse tree produced by YAPLParser#let.
    def exitLet(self, ctx:YAPLParser.LetContext):
        pass


    # Enter a parse tree produced by YAPLParser#id.
    def enterId(self, ctx:YAPLParser.IdContext):
        pass

    # Exit a parse tree produced by YAPLParser#id.
    def exitId(self, ctx:YAPLParser.IdContext):
        pass


    # Enter a parse tree produced by YAPLParser#if.
    def enterIf(self, ctx:YAPLParser.IfContext):
        pass

    # Exit a parse tree produced by YAPLParser#if.
    def exitIf(self, ctx:YAPLParser.IfContext):
        pass


    # Enter a parse tree produced by YAPLParser#assign.
    def enterAssign(self, ctx:YAPLParser.AssignContext):
        pass

    # Exit a parse tree produced by YAPLParser#assign.
    def exitAssign(self, ctx:YAPLParser.AssignContext):
        pass


    # Enter a parse tree produced by YAPLParser#bigexpr.
    def enterBigexpr(self, ctx:YAPLParser.BigexprContext):
        pass

    # Exit a parse tree produced by YAPLParser#bigexpr.
    def exitBigexpr(self, ctx:YAPLParser.BigexprContext):
        pass



del YAPLParser
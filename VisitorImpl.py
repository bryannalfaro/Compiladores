from antlr4 import *
from ANTLR.YAPLParser import YAPLParser
from listenerError import MyErrorVisitor
from termcolor import cprint    
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

class YAPL(ParseTreeVisitor):
    def __init__(self):
        super().__init__()
        self.errors_list = []
     # Visit a parse tree produced by YAPLParser#program.
    def visitProgram(self, ctx:YAPLParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#class_grammar.
    def visitClass_grammar(self, ctx:YAPLParser.Class_grammarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#feature.
    def visitFeature(self, ctx:YAPLParser.FeatureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#formal.
    def visitFormal(self, ctx:YAPLParser.FormalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#plusminus.
    def visitPlusminus(self, ctx:YAPLParser.PlusminusContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#negation.
    def visitNegation(self, ctx:YAPLParser.NegationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#curly.
    def visitCurly(self, ctx:YAPLParser.CurlyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#string.
    def visitString(self, ctx:YAPLParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#isvoid.
    def visitIsvoid(self, ctx:YAPLParser.IsvoidContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#false.
    def visitFalse(self, ctx:YAPLParser.FalseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#less.
    def visitLess(self, ctx:YAPLParser.LessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#while.
    def visitWhile(self, ctx:YAPLParser.WhileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#int.
    def visitInt(self, ctx:YAPLParser.IntContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#call.
    def visitCall(self, ctx:YAPLParser.CallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#newtype.
    def visitNewtype(self, ctx:YAPLParser.NewtypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#timesdiv.
    def visitTimesdiv(self, ctx:YAPLParser.TimesdivContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#equal.
    def visitEqual(self, ctx:YAPLParser.EqualContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#not.
    def visitNot(self, ctx:YAPLParser.NotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#paren.
    def visitParen(self, ctx:YAPLParser.ParenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#lesseq.
    def visitLesseq(self, ctx:YAPLParser.LesseqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#true.
    def visitTrue(self, ctx:YAPLParser.TrueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#let.
    def visitLet(self, ctx:YAPLParser.LetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#id.
    def visitId(self, ctx:YAPLParser.IdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#if.
    def visitIf(self, ctx:YAPLParser.IfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#assign.
    def visitAssign(self, ctx:YAPLParser.AssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#bigexpr.
    def visitBigexpr(self, ctx:YAPLParser.BigexprContext):
        return self.visitChildren(ctx)
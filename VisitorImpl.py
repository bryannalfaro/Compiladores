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
        classType = ctx.children[1].getText()
        classParent = ctx.children[3].getText() if str(ctx.children[2]).lower() == 'inherits' else None

        symbol = {
            'type': classType,
            'category': 'CLASS',
            'size': 0,
            'data': {
                'parent': classParent
            }
        }
        print('CLASS SYMBOL', symbol)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#function.
    def visitFunction(self, ctx:YAPLParser.FunctionContext):
        functionName = ctx.children[0].getText()
        # Attribute count takes 8 (no attributes) from the children length, and then it ignores commas
        attributeCount = 0 if len(ctx.children) == 8 else int(((len(ctx.children) - 8) / 2) + 0.5)
        functionType = ctx.children[-4].getText()
        attributes = []
        for i in range(2, 2 * attributeCount + 1, 2):
            # Visiting all attributes (Formal)
            attributes.append(self.visit(ctx.children[i]))

        symbol = {
            'type': functionType,
            'category': 'FUNCTION',
            'size': 0,
            'data': {
                'name': functionName,
                'attributeCount': attributeCount,
                'attributes': attributes
            }
        }
        print('FUNCTION SYMBOL', symbol)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#variable.
    def visitVariable(self, ctx:YAPLParser.VariableContext):
        variableName = ctx.children[0].getText()
        variableType = ctx.children[2].getText()
        variableValue = ctx.children[4].getText() if len(ctx.children) > 3 else None
        symbol = {
            'type': variableType,
            'category': 'VARIABLE',
            'size': 0,
            'data': {
                'name': variableName,
                'value': variableValue
            }
        }
        print('VARIABLE SYMBOL', symbol)
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#formal.
    def visitFormal(self, ctx:YAPLParser.FormalContext):
        attributeName = ctx.children[0].getText()
        attributeType = ctx.children[2].getText()
        attribute = {
            'name': attributeName,
            'type': attributeType
        }
        return attribute


    # Visit a parse tree produced by YAPLParser#plusminus.
    def visitPlusminus(self, ctx:YAPLParser.PlusminusContext):
        #get the type of the left and right side
        print('CONTEXT', ctx.getText())
        results = []
        for plus_node in ctx.expr():
            print('PLUS NODE', plus_node.getText()  )
            results.append(self.visit(plus_node))
        print('RESULTS', results)
        left = results[0]
        right = results[-1]
        #if the type of the left and right side are not the same, then add an error
        if left != right:
            typeErrorMsg ="Arithmetic on " + left + " " + right + " instead of Ints"
            self.errors_list.append(MyErrorVisitor(ctx, typeErrorMsg))
            return "ERROR"
        else:
            if left == "INTEGER":
                return "INTEGER"
            elif left == "BOOL":
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on Bool Bool instead of Ints"))
                return "ERROR"
            elif left == "STRING":
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on String String instead of Ints"))
                return "ERROR"
            else:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic type mismatch"))
                return "ERROR"

    # Visit a parse tree produced by YAPLParser#negation.
    def visitNegation(self, ctx:YAPLParser.NegationContext):
        print('CONTEXT', ctx.getText())
        result = self.visit(ctx.expr())
        #check if the type is an integer
        if result == "INTEGER":
            return "INTEGER"
        elif result == "BOOL":
            return "BOOL"
        elif result == "STRING":
            self.errors_list.append(MyErrorVisitor(ctx, "Negate applied to String instead of Int"))
            return "ERROR"
        else:
            self.errors_list.append(MyErrorVisitor(ctx, "Negate applied to invalid type"))
            return "ERROR"


    # Visit a parse tree produced by YAPLParser#curly.
    def visitCurly(self, ctx:YAPLParser.CurlyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#string.
    def visitString(self, ctx:YAPLParser.StringContext):
        return "STRING"


    # Visit a parse tree produced by YAPLParser#isvoid.
    def visitIsvoid(self, ctx:YAPLParser.IsvoidContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#false.
    def visitFalse(self, ctx:YAPLParser.FalseContext):
        return "BOOL"


    # Visit a parse tree produced by YAPLParser#while.
    def visitWhile(self, ctx:YAPLParser.WhileContext):
        compareExpression = self.visit(ctx.children[1])
        if compareExpression == "BOOL":
            return "BOOL"
        else:
            self.errors_list.append(MyErrorVisitor(ctx, "Predicate has type " + compareExpression + " instead of BOOL"))
            return "ERROR"


    # Visit a parse tree produced by YAPLParser#int.
    def visitInt(self, ctx:YAPLParser.IntContext):
        return "INTEGER"


    # Visit a parse tree produced by YAPLParser#call.
    def visitCall(self, ctx:YAPLParser.CallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#newtype.
    def visitNewtype(self, ctx:YAPLParser.NewtypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#timesdiv.
    def visitTimesdiv(self, ctx:YAPLParser.TimesdivContext):
        #get the type of the left and right side
        print('CONTEXT', ctx.getText())
        results = []
        for times_node in ctx.expr():
            print('PLUS NODE', times_node.getText()  )
            results.append(self.visit(times_node))
        print('RESULTS', results)
        left = results[0]
        right = results[-1]
        #if the type of the left and right side are not the same, then add an error
        if left != right:
            typeErrorMsg ="Arithmetic on " + left + " " + right + " instead of Ints"
            self.errors_list.append(MyErrorVisitor(ctx, typeErrorMsg))
            return "ERROR"
        else:
            if left == "INTEGER":
                return "INTEGER"
            elif left == "BOOL":
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on Bool Bool instead of Ints"))
                return "ERROR"
            elif left == "STRING":
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on String String instead of Ints"))
                return "ERROR"
            else:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic type mismatch"))
                return "ERROR"

    # Visit a parse tree produced by YAPLParser#compare.
    def visitCompare(self, ctx:YAPLParser.CompareContext):
        print('CONTEXT', ctx.getText())
        results = []
        for compare_node in ctx.expr():
            results.append(self.visit(compare_node))
        left = results[0]
        right = results[-1]
        #if the type of the left and right side are not the same, then add an error

        if left != right:
            typeErrorMsg ="Comparison between " + left + " and " + right
            self.errors_list.append(MyErrorVisitor(ctx, typeErrorMsg))
            return "ERROR"
        else:
            return "BOOL"


    # Visit a parse tree produced by YAPLParser#not.
    def visitNot(self, ctx:YAPLParser.NotContext):
        print('CONTEXT', ctx.getText())
        #get the type of the left and right side
        print('CONTEXT', ctx.getText())
        result = self.visit(ctx.expr())
        print('RESULTS', result)
        #if they are integers, then return an error
        if result == "INTEGER":
            self.errors_list.append(MyErrorVisitor(ctx, "Not applied to Int instead of Bool"))
            return "ERROR"
        elif result == "STRING":
            self.errors_list.append(MyErrorVisitor(ctx, "Not applied to String instead of Bool"))
            return "ERROR"
        else:
            return "BOOL"


    # Visit a parse tree produced by YAPLParser#paren.
    def visitParen(self, ctx:YAPLParser.ParenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#true.
    def visitTrue(self, ctx:YAPLParser.TrueContext):
        return "BOOL"


    # Visit a parse tree produced by YAPLParser#let.
    def visitLet(self, ctx:YAPLParser.LetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#id.
    def visitId(self, ctx:YAPLParser.IdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#if.
    def visitIf(self, ctx:YAPLParser.IfContext):
        compareExpression = self.visit(ctx.children[1])
        if compareExpression == "BOOL":
            return "BOOL"
        else:
            self.errors_list.append(MyErrorVisitor(ctx, "Conditional has type " + compareExpression + " instead of BOOL"))
            return "ERROR"


    # Visit a parse tree produced by YAPLParser#assign.
    def visitAssign(self, ctx:YAPLParser.AssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#bigexpr.
    def visitBigexpr(self, ctx:YAPLParser.BigexprContext):
        return self.visitChildren(ctx)
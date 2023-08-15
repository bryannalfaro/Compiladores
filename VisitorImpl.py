from antlr4 import *
from ANTLR.YAPLParser import YAPLParser
from listenerError import MyErrorVisitor
from termcolor import cprint    
from SymbolTable import *

class YAPL(ParseTreeVisitor):
    def __init__(self):
        super().__init__()
        self.symbol_table = SymbolTable()
        self.symbol_table.initialize()
        self.errors_list = []
        self.defaultValues = {
            IntType: 0,
            BoolType: False,
            StringType: ""
        }
        # Global variables to set Scope
        self.current_class = None
        self.current_function = None
        self.current_let = 0
     # Visit a parse tree produced by YAPLParser#program.
    def visitProgram(self, ctx:YAPLParser.ProgramContext):
        
        self.visitChildren(ctx)
        #search for the main class and it has to be just one
        counterMain = self.symbol_table.getNumberOfEntries("Main")
        if counterMain != 1:
            self.errors_list.append(MyErrorVisitor(ctx, "There must be one Main class"))
            
            cprint("Number of Main classes: " + str(counterMain),"red")
        


    # Visit a parse tree produced by YAPLParser#class_grammar.
    def visitClass_grammar(self, ctx:YAPLParser.Class_grammarContext): 
        
        classType = ctx.children[1].getText()
        self.current_class = classType

        classParent = ctx.children[3].getText() if str(ctx.children[2]).lower() == 'inherits' else None
        #Main class can not inherit from another class
        if classType == "Main" and classParent != None:
            self.errors_list.append(MyErrorVisitor(ctx, "Main class can not inherit from another class"))
            self.visitChildren(ctx)
            return ErrorType
        self.symbol_table.add(classType, 'class', 0, 0, {'parent': classParent})
        if self.symbol_table.getClassParent(classType) == classParent and classParent != None:
            typeErrorMsg = "Inheritance cycle: " + classType + " " + classParent
            self.errors_list.append(MyErrorVisitor(ctx, typeErrorMsg))
            return ErrorType

        self.visitChildren(ctx)

        #visit features of the class
        # resultFeatures= ctx.feature()
        # for feature in resultFeatures:
        #     if isinstance(feature, YAPLParser.VariableContext):
        #         self.featureScoping(feature.children[0].getText(), 'class.' + classType)
        #     elif isinstance(feature, YAPLParser.FunctionContext):
        #         self.featureScoping(feature.children[0].getText(), 'class.' + classType)

    # Set Scope for feature
    def featureScoping(self, name, scope = None):
        self.symbol_table.setScope(name, scope)

    # Visit a parse tree produced by YAPLParser#function.
    def visitFunction(self, ctx:YAPLParser.FunctionContext):
        functionName = ctx.children[0].getText()
        self.current_function = functionName
        # Attribute count takes 8 (no attributes) from the children length, and then it ignores commas
        attributeCount = 0 if len(ctx.children) == 8 else int(((len(ctx.children) - 8) / 2) + 0.5)
        functionType = ctx.children[-4].getText()
        attributes = []
        for i in range(2, 2 * attributeCount + 1, 2):
            # Visiting all attributes (Formal)
            attributes.append(self.visit(ctx.children[i]))

        # Inheritance errors:
            # class [name] redefines method [method] and changes number of formals
            # class [name] redefines method [method] and changes return type (from [original] to [new])
            # class [name] redefines method [method] and changes type of formal [formal]
        # Non errors:
            # Changing formal id

        self.symbol_table.add(functionType, 'function', 0, 0, {'name': functionName, 'attributeCount': attributeCount, 'attributes': attributes, 'scope': 'global.' + self.current_class})
        self.visitChildren(ctx)
        self.current_function = None
        return


    # Visit a parse tree produced by YAPLParser#variable.
    def visitVariable(self, ctx:YAPLParser.VariableContext):
        variableName = ctx.children[0].getText()
        variableType = ctx.children[2].getText()
        #evaluate the value to assign default values
        if len(ctx.children) > 3:
            variableValue = ctx.children[4].getText()
            valueType  = self.visit(ctx.children[4]) #Type of value to assign
            
            #check if the types are the same
            if variableType != valueType:
                self.errors_list.append(MyErrorVisitor(ctx, "Variable type mismatch"))
                return ErrorType
        elif variableType in self.defaultValues:
            variableValue = self.defaultValues[variableType]
        else:
            variableValue = None
        
        self.symbol_table.add(variableType, 'variable', 0, 0, {'name': variableName, 'value': variableValue, 'scope': 'global.' + self.current_class})
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#formal.
    def visitFormal(self, ctx:YAPLParser.FormalContext):
        attributeName = ctx.children[0].getText()
        attributeType = ctx.children[2].getText()
        if attributeType in self.defaultValues:
            attributeValue = self.defaultValues[attributeType]
        else:
            attributeValue = None
        attribute = {
            'name': attributeName,
            'type': attributeType,
            'value': attributeValue,
            'scope': 'local.' + self.current_class + '.' + self.current_function
        },
        return attribute


    # Visit a parse tree produced by YAPLParser#plusminus.
    def visitPlusminus(self, ctx:YAPLParser.PlusminusContext):
        #get the type of the left and right side
        results = []
        for plus_node in ctx.expr():
            results.append(self.visit(plus_node))
        left = results[0]
        right = results[-1]
        #if the type of the left and right side are not the same, then add an error
        if left != right:
            #make implicit casting of bool to int
            if left == BoolType and right == IntType:
                return IntType
            elif left == IntType and right == BoolType:
                return IntType
            else:
                typeErrorMsg ="Arithmetic on " + left + " " + right + " instead of Ints"
                self.errors_list.append(MyErrorVisitor(ctx, typeErrorMsg))
                return ErrorType
        else:
            if left == IntType:
                return IntType
            elif left == BoolType:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on Bool Bool instead of Ints"))
                return ErrorType
            elif left == StringType:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on String String instead of Ints"))
                return ErrorType
            else:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic type mismatch"))
                return ErrorType

    # Visit a parse tree produced by YAPLParser#negation.
    def visitNegation(self, ctx:YAPLParser.NegationContext):
        result = self.visit(ctx.expr())
        #check if the type is an integer
        if result == IntType:
            return IntType
        elif result == BoolType:
            return BoolType
        elif result == StringType:
            self.errors_list.append(MyErrorVisitor(ctx, "Negate applied to String instead of Int"))
            return ErrorType
        else:
            self.errors_list.append(MyErrorVisitor(ctx, "Negate applied to invalid type"))
            return ErrorType


    # Visit a parse tree produced by YAPLParser#curly.
    def visitCurly(self, ctx:YAPLParser.CurlyContext):
        self.visitChildren(ctx)
        # Return last expr type
        return self.visit(ctx.children[-3])


    # Visit a parse tree produced by YAPLParser#string.
    def visitString(self, ctx:YAPLParser.StringContext):
        return StringType


    # Visit a parse tree produced by YAPLParser#isvoid.
    def visitIsvoid(self, ctx:YAPLParser.IsvoidContext):
        self.visitChildren(ctx)
        # Return bool evaluates to true if expr is void 
        # and evaluates to false if expr is not void.
        return BoolType


    # Visit a parse tree produced by YAPLParser#false.
    def visitFalse(self, ctx:YAPLParser.FalseContext):
        return BoolType


    # Visit a parse tree produced by YAPLParser#while.
    def visitWhile(self, ctx:YAPLParser.WhileContext):
        compareExpression = self.visit(ctx.children[1])
        if compareExpression == BoolType:
            return ObjectType
        else:
            self.errors_list.append(MyErrorVisitor(ctx, "Predicate has type " + compareExpression + " instead of BOOL"))
            return ErrorType


    # Visit a parse tree produced by YAPLParser#int.
    def visitInt(self, ctx:YAPLParser.IntContext):
        return IntType


    # Visit a parse tree produced by YAPLParser#call.
    def visitCall(self, ctx:YAPLParser.CallContext):
        self.visitChildren(ctx)
        # Return ID type
        callType = self.symbol_table.getCategory(ctx.children[0].getText())
        return callType


    # Visit a parse tree produced by YAPLParser#newtype.
    def visitNewtype(self, ctx:YAPLParser.NewtypeContext):
        self.visitChildren(ctx)
        # Return Type
        return self.visit(ctx.children[1])


    # Visit a parse tree produced by YAPLParser#timesdiv.
    def visitTimesdiv(self, ctx:YAPLParser.TimesdivContext):
        #get the type of the left and right side
        #print('CONTEXT', ctx.getText())
        results = []
        for times_node in ctx.expr():
            results.append(self.visit(times_node))
        left = results[0]
        right = results[-1]
        #if the type of the left and right side are not the same, then add an error
        if left != right:
            #make implicit casting of bool to int
            if left == BoolType and right == IntType:
                return IntType
            elif left == IntType and right == BoolType:
                return IntType
            else:
                typeErrorMsg ="Arithmetic on " + left + " " + right + " instead of Ints"
                self.errors_list.append(MyErrorVisitor(ctx, typeErrorMsg))
                return ErrorType
        else:
            if left == IntType:
                return IntType
            elif left == BoolType:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on Bool Bool instead of Ints"))
                return ErrorType
            elif left == StringType:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on String String instead of Ints"))
                return ErrorType
            else:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic type mismatch"))
                return ErrorType

    # Visit a parse tree produced by YAPLParser#compare.
    def visitCompare(self, ctx:YAPLParser.CompareContext):
        results = []
        for compare_node in ctx.expr():
            results.append(self.visit(compare_node))
        left = results[0]
        right = results[-1]
        #if the type of the left and right side are not the same, then add an error

        if left != right:
            typeErrorMsg ="Comparison between " + left + " and " + right
            self.errors_list.append(MyErrorVisitor(ctx, typeErrorMsg))
            return ErrorType
        else:
            return BoolType


    # Visit a parse tree produced by YAPLParser#not.
    def visitNot(self, ctx:YAPLParser.NotContext):
        #get the type of the left and right side
        result = self.visit(ctx.expr())
        #if they are integers, then return an error
        if result == IntType:
            self.errors_list.append(MyErrorVisitor(ctx, "Not applied to Int instead of Bool"))
            return ErrorType
        elif result == StringType:
            self.errors_list.append(MyErrorVisitor(ctx, "Not applied to String instead of Bool"))
            return ErrorType
        else:
            return BoolType


    # Visit a parse tree produced by YAPLParser#paren.
    def visitParen(self, ctx:YAPLParser.ParenContext):
        self.visitChildren(ctx)
        # Return expr type
        return self.visit(ctx.children[1])


    # Visit a parse tree produced by YAPLParser#true.
    def visitTrue(self, ctx:YAPLParser.TrueContext):
        return BoolType


    # Visit a parse tree produced by YAPLParser#let.
    def visitLet(self, ctx:YAPLParser.LetContext):
        # Return Value of expr here: [IN expr]
        variableName = ctx.children[1].getText()
        variableType = ctx.children[2].getText()
        #evaluate the value to assign default values
        if len(ctx.children) > 3:
            variableValue = ctx.children[5].getText()
        elif variableType in self.defaultValues:
            variableValue = self.defaultValues[variableType]
        else:
            variableValue = None
    

        self.symbol_table.add(variableType, 'variable', 0, 0, {'name': variableName, 'value': variableValue, 'scope': 'local.' + self.current_class + '.' + self.current_function + '.let' + str(self.current_let)})
        self.visitChildren(ctx)
        self.current_let += 1
        return self.visit(ctx.children[-1])


    # Visit a parse tree produced by YAPLParser#id.
    def visitId(self, ctx:YAPLParser.IdContext):

        #search for the variable in the symbol table 
        #@TODO verificar scope al tenerlo 
        variable = self.symbol_table.getVariable(ctx.getText())

        if variable == None:
            self.errors_list.append(MyErrorVisitor(ctx, "Variable " + ctx.getText() + " not declared"))
            return ErrorType
        else:
            return variable.getCategory()


    # Visit a parse tree produced by YAPLParser#if.
    def visitIf(self, ctx:YAPLParser.IfContext):
        compareExpression = self.visit(ctx.children[1])
        thenType = self.visit(ctx.children[3])
        elseType = self.visit(ctx.children[5])

        # Defining ifType. Highest common class
        ifType = ObjectType
        if thenType == elseType:
            ifType = thenType
        else:
            # Cycle through class parents
            thenTempType = thenType
            elseTempType = elseType
            while thenTempType != None:
                while elseTempType != None:
                    elseTempType = self.symbol_table.getClassParent(elseTempType)
                    if elseTempType == thenTempType:
                        ifType = elseTempType
                        break
                elseTempType = elseType
                thenTempType = self.symbol_table.getClassParent(thenTempType)

        if compareExpression == BoolType:
            return ifType
        else:
            self.errors_list.append(MyErrorVisitor(ctx, "Conditional has type " + compareExpression + " instead of BOOL"))
            return ErrorType


    # Visit a parse tree produced by YAPLParser#assign.
    def visitAssign(self, ctx:YAPLParser.AssignContext):
        #get id of the assignment
        idValue = ctx.children[0].getText()
        #get the expression of the assignment
        exprValue = ctx.children[2].getText()

        #assing in symbol table value
        self.symbol_table.setVariableValue(idValue, exprValue)
        cprint("ASSIGN: "+"ID:"+idValue+" EXPR>"+exprValue,"green")
        self.visitChildren(ctx)
        return self.visitChildren(ctx.children[2])


    # Visit a parse tree produced by YAPLParser#bigexpr.
    def visitBigexpr(self, ctx:YAPLParser.BigexprContext):
        self.visitChildren(ctx)

        # Return ID type
        idIndex = 4 if ctx.children[1].getText() == '@' else 2
        bigExprType = self.symbol_table.getCategory(ctx.children[idIndex].getText())
        return bigExprType
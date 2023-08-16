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
        existenceMainMethod = self.symbol_table.getMethodExistence("main","global.Main")
        if counterMain != 1:
            self.errors_list.append(MyErrorVisitor(ctx, "There must be one Main class"))
            
            cprint("Number of Main classes: " + str(counterMain),"red")
        #validate existence of main method in scope global.Main
        if existenceMainMethod == False:
            self.errors_list.append(MyErrorVisitor(ctx, "Main class must have a main method"))
            cprint("Main class must have a main method","red")

        #Validate no params on main method
        paramsMainMethod = self.symbol_table.getMethodParams("main","global.Main")
        if len(paramsMainMethod) != 0:
            self.errors_list.append(MyErrorVisitor(ctx, "Main method must have no params"))
            cprint("Main method must have no params","red")
        


    # Visit a parse tree produced by YAPLParser#class_grammar.
    def visitClass_grammar(self, ctx:YAPLParser.Class_grammarContext): 
        
        classType = ctx.children[1].getText()
        self.current_class = classType

        classParent = ctx.children[3].getText() if str(ctx.children[2]).lower() == 'inherits' else None
        
        self.symbol_table.add(classType, 'class', 0, 0, {'parent': classParent})
        if self.symbol_table.getClassParent(classParent) == classType and classParent != None:
            # If the parent of the parent is the same as the classType, Inheritance
            typeErrorMsg = "Inheritance cycle: " + classType + " " + classParent
            self.errors_list.append(MyErrorVisitor(ctx, typeErrorMsg))
            self.visitChildren(ctx)
            return ErrorType
        if classParent == 'Int' or classParent == 'Bool' or classParent == 'String':
            typeErrorMsg = 'Type-check: class ' + classType + ' inherits from ' + classParent
            self.errors_list.append(MyErrorVisitor(ctx, typeErrorMsg))
            self.visitChildren(ctx)
            return ErrorType

        self.visitChildren(ctx)
        return

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

        parentClass = self.symbol_table.getClassParent(self.current_class)
        if parentClass != None:
            parentFunction = self.symbol_table.getFunctionByScope(functionName, 'global.' + parentClass)
            if parentFunction != None:
                # Check number of formals
                if attributeCount != parentFunction.data["attributeCount"]:
                    errorMsg = 'Class ' + self.current_class + ' redefines method ' + functionName + ' and changes number of formals.'
                    self.errors_list.append(MyErrorVisitor(ctx, errorMsg))
                    self.visitChildren(ctx)
                    return ErrorType
                # Check return type
                if functionType != parentFunction.category:
                    errorMsg = 'Class ' + self.current_class + ' redefines method ' + functionName + ' and changes return type (from ' + parentFunction.category + ' to ' + functionType + ')'
                    self.errors_list.append(MyErrorVisitor(ctx, errorMsg))
                    self.visitChildren(ctx)
                    return ErrorType
                # Check formal types
                for i in range(attributeCount):
                    if attributes[i][0]["type"] != parentFunction.data["attributes"][i][0]["type"]:
                        errorMsg = 'Class ' + self.current_class + ' redefines method ' + functionName + ' and changes type of formal ' + attributes[i][0]["name"]
                        self.errors_list.append(MyErrorVisitor(ctx, errorMsg))
                        self.visitChildren(ctx)
                        return ErrorType

        # Check return type matches
        exprType = self.visit(ctx.children[-2])
        originalExprType = exprType
        hasMatch = False
        if exprType != functionType:
            while exprType != None:
                exprType = self.symbol_table.getClassParent(exprType)
                if exprType == functionType:
                    hasMatch = True
            if not hasMatch:
                # Return type of function body nor its parents match expected type
                errorMsg = 'Type-Check: ' + str(originalExprType) + ' does not conform to ' + functionType + ' in method ' + functionName
                self.errors_list.append(MyErrorVisitor(ctx, errorMsg))
                self.visitChildren(ctx)
                return ErrorType

        self.symbol_table.add(functionType, 'function', 0, 0, {'name': functionName, 'attributeCount': attributeCount, 'attributes': attributes, 'scope': 'global.' + self.current_class})
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
                self.visitChildren(ctx)
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
                self.visitChildren(ctx)
                return ErrorType
        else:
            if left == IntType:
                return IntType
            elif left == BoolType:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on Bool Bool instead of Ints"))
                self.visitChildren(ctx)
                return ErrorType
            elif left == StringType:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on String String instead of Ints"))
                self.visitChildren(ctx)
                return ErrorType
            else:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic type mismatch"))
                self.visitChildren(ctx)
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
            self.visitChildren(ctx)
            return ErrorType
        else:
            self.errors_list.append(MyErrorVisitor(ctx, "Negate applied to invalid type"))
            self.visitChildren(ctx)
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
            self.visitChildren(ctx)
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
                self.visitChildren(ctx)
                return ErrorType
        else:
            if left == IntType:
                return IntType
            elif left == BoolType:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on Bool Bool instead of Ints"))
                self.visitChildren(ctx)
                return ErrorType
            elif left == StringType:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic on String String instead of Ints"))
                self.visitChildren(ctx)
                return ErrorType
            else:
                self.errors_list.append(MyErrorVisitor(ctx, "Arithmetic type mismatch"))
                self.visitChildren(ctx)
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
            #make implicit casting of bool to int
            if left == BoolType and right == IntType:
                return BoolType
            elif left == IntType and right == BoolType:
                return BoolType
            else:
                typeErrorMsg ="Comparison between " + left + " and " + right
                self.errors_list.append(MyErrorVisitor(ctx, typeErrorMsg))
                self.visitChildren(ctx)
                return ErrorType
        else:
            if left == IntType:
                return BoolType
            elif left == BoolType:
                return BoolType
            elif left == StringType:
                self.errors_list.append(MyErrorVisitor(ctx, "Comparison on String String instead of Ints"))
                self.visitChildren(ctx)
                return ErrorType
            else:
                self.errors_list.append(MyErrorVisitor(ctx, "Compare type mismatch"))
                self.visitChildren(ctx)
                return ErrorType
           


    # Visit a parse tree produced by YAPLParser#not.
    def visitNot(self, ctx:YAPLParser.NotContext):
        #get the type of the left and right side
        result = self.visit(ctx.expr())
        #if they are integers, then return an error
        if result == IntType:
            self.errors_list.append(MyErrorVisitor(ctx, "Not applied to Int instead of Bool"))
            self.visitChildren(ctx)
            return ErrorType
        elif result == StringType:
            self.errors_list.append(MyErrorVisitor(ctx, "Not applied to String instead of Bool"))
            self.visitChildren(ctx)
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
            self.visitChildren(ctx)
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
            self.visitChildren(ctx)
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
        return self.visit(ctx.children[2])


    # Visit a parse tree produced by YAPLParser#bigexpr.
    def visitBigexpr(self, ctx:YAPLParser.BigexprContext):
        self.visitChildren(ctx)

        # Return ID type
        idIndex = 4 if ctx.children[1].getText() == '@' else 2
        bigExprType = self.symbol_table.getCategory(ctx.children[idIndex].getText())
        return bigExprType
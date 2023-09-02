from antlr4 import *
from ANTLR.YAPLParser import YAPLParser
from listenerError import MyErrorVisitor
from termcolor import cprint    
from SymbolTable import *
import sys
class YAPL(ParseTreeVisitor):
    def __init__(self):
        super().__init__()
        self.symbol_table = SymbolTable()
        self.function_table = SymbolTable()
        self.symbol_table.initialize()
        self.function_table.initialize()
        self.errors_list = []
        self.defaultValues = {
            IntType: { 'value': 0, 'size': 8 },
            BoolType: { 'value': False, 'size': 1 },
            StringType: { 'value': '', 'size': 1 }
        }
        # Global variables to set Scope
        self.current_class = None
        self.current_function = None
        self.current_let = 0
        self.current_function_type = None
        self.offset_acc = 0
     # Visit a parse tree produced by YAPLParser#program.
    def visitProgram(self, ctx:YAPLParser.ProgramContext):
        for child in ctx.children:
            if isinstance(child, YAPLParser.Class_grammarContext):
                self.visitDefineClasses(child)
        self.visitChildren(ctx)
        #search for the main class and it has to be just one
        counterMain = self.symbol_table.getNumberOfEntries("Main")
        existenceMainMethod = self.symbol_table.getMethodExistence("main","global.Main")
        if counterMain != 1:
            self.errors_list.append(MyErrorVisitor(ctx, "There must be one Main class"))
            
            # cprint("Number of Main classes: " + str(counterMain),"red")
        #validate existence of main method in scope global.Main
        if existenceMainMethod == False:
            self.errors_list.append(MyErrorVisitor(ctx, "Main class must have a main method"))
            # cprint("Main class must have a main method","red")

        #Validate no params on main method
        paramsMainMethod = self.symbol_table.getMethodParams("main","global.Main")
        if len(paramsMainMethod) != 0:
            self.errors_list.append(MyErrorVisitor(ctx, "Main method must have no params"))
            # cprint("Main method must have no params","red")
        

    # Visit a parse tree produced by YAPLParser#class_grammar.
    def visitDefineClasses(self, ctx:YAPLParser.Class_grammarContext): 
        #cprint("IM HERE DEFINING","red")
        classType = ctx.children[1].getText()
        for child in ctx.children:
            if isinstance(child, YAPLParser.FunctionContext):
                self.visitDefineFunction(child, classType)

        classParent = ctx.children[3].getText() if str(ctx.children[2]).lower() == 'inherits' else ObjectType
        #cprint(classType+classParent,"blue")
        #print(ctx.children[1].getText())
        self.symbol_table.add(classType, 'class', None, 0, {'parent': classParent})
        return
    
    # Visit a parse tree produced by YAPLParser#class_grammar.
    def visitClass_grammar(self, ctx:YAPLParser.Class_grammarContext): 
        
        classType = ctx.children[1].getText()
        self.current_class = classType
        self.offset_acc = 0

        classParent = ctx.children[3].getText() if str(ctx.children[2]).lower() == 'inherits' else ObjectType
        
        #self.symbol_table.add(classType, 'class', 0, 0, {'parent': classParent})
        if self.symbol_table.getClassParent(classParent) == classType and classParent != None:
            # If the parent of the parent is the same as the classType, Inheritance cycle
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

    def visitDefineFunction(self, ctx:YAPLParser.FunctionContext, className):
        functionName = ctx.children[0].getText()
        # Attribute count takes 8 (no attributes) from the children length, and then it ignores commas
        attributeCount = 0 if len(ctx.children) == 8 else int(((len(ctx.children) - 8) / 2) + 0.5)
        functionType = ctx.children[-4].getText()
        #Evaluation of SELF_TYPE
        if functionType == SELF_TYPE:
            functionType = self.current_class

        self.function_table.add(functionType, 'function', 0, 0, {'name': functionName, 'attributeCount': attributeCount, 'scope': 'global.' + className})

        return

    # Visit a parse tree produced by YAPLParser#function.
    def visitFunction(self, ctx:YAPLParser.FunctionContext):
        functionName = ctx.children[0].getText()
        self.current_function = functionName
        # Attribute count takes 8 (no attributes) from the children length, and then it ignores commas
        attributeCount = 0 if len(ctx.children) == 8 else int(((len(ctx.children) - 8) / 2) + 0.5)
        functionType = ctx.children[-4].getText()
        self.current_function_type = functionType
        #Evaluation of SELF_TYPE
        if functionType == SELF_TYPE:
            functionType = self.current_class

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
        #cprint("PARENT CLASS: "+str(parentClass),"red")
        if parentClass != None:
            parentFunction = self.symbol_table.getFunctionByScope(functionName, 'global.' + parentClass)
            #cprint("PARENT FUNCTION: "+str(parentFunction),"red")
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
        #print("EXPR TYPE",exprType, "functionType", functionType)
        #cprint(str(exprType)+str(functionType),"green")
        
        #Evaluation of SELF_TYPE
        if exprType == SELF_TYPE:
            exprType = self.current_class

        originalExprType = exprType
        hasMatch = False
        if exprType != functionType:
            while exprType != None:
                exprType = self.symbol_table.getClassParent(exprType)
                if exprType == functionType:
                    hasMatch = True
            if not hasMatch:
                #print('FUNC', self.symbol_table.getClassIndex(functionType), functionType)
                #print('EXPR', self.symbol_table.getClassIndex(originalExprType), originalExprType)
                if originalExprType != ErrorType and self.symbol_table.getClassIndex(functionType) < self.symbol_table.getClassIndex(originalExprType):
                    # Return type of function body nor its parents match expected type
                    errorMsg = 'Type-Check: ' + str(originalExprType) + ' does not conform to ' + functionType + ' in method ' + functionName
                    self.errors_list.append(MyErrorVisitor(ctx, errorMsg))
                    self.visitChildren(ctx)
                    return ErrorType
                if originalExprType == ObjectType:
                    # Return type of function body nor its parents match expected type
                    errorMsg = 'Type-Check: ' + str(originalExprType) + ' does not conform to ' + functionType + ' in method ' + functionName
                    self.errors_list.append(MyErrorVisitor(ctx, errorMsg))
                    self.visitChildren(ctx)
                    return ErrorType

        # Check in symbol table if function exists in scope
        if self.symbol_table.getFunctionByScope(functionName, 'global.' + self.current_class) != None or self.symbol_table.getFunctionByScope(functionName, 'global.' + "IO") != None:
            errorMsg = 'Type-Check: class ' + self.current_class + ' redefines method ' + functionName
            self.errors_list.append(MyErrorVisitor(ctx, errorMsg))
            self.visitChildren(ctx)
            return ErrorType

        # Check if formals of function are repeated
        for i in range(0, len(attributes)):
            for j in range(i+1, len(attributes)):
                if attributes[i][0]["name"] == attributes[j][0]["name"]:
                    errorMsg = 'Type-Check: class ' + self.current_class + ' has method ' + functionName + ' with duplicate formal parameter named ' + attributes[i][0]["name"]
                    self.errors_list.append(MyErrorVisitor(ctx, errorMsg))
                    self.visitChildren(ctx)
                    return ErrorType

        self.current_function = None
        # #print("Saliendo de function")
        #Check of type is primitive to add size
        # if functionType == IntType or functionType == BoolType:
        #     self.symbol_table.add(functionType, 'function',self.defaultValues[functionType]['size'], self.offset_acc, {'name': functionName, 'attributeCount': attributeCount, 'attributes': attributes, 'scope': 'global.' + self.current_class})
        #     self.offset_acc += self.defaultValues[functionType]['size']
        # elif functionType == StringType:
        #     #size of ctx.children[-2]
        #     #print(len(ctx.children[-2].getText()))
        #     #-1 because of the quotes but the end of string
        #     size = (self.defaultValues[functionType]['size'] * len(ctx.children[-2].getText()))-1 
        #     self.symbol_table.add(functionType, 'function', size, self.offset_acc, {'name': functionName, 'attributeCount': attributeCount, 'attributes': attributes, 'scope': 'global.' + self.current_class})
        #     self.offset_acc += size
        # else:
        self.symbol_table.add(functionType, 'function', None, self.offset_acc, {'name': functionName, 'attributeCount': attributeCount, 'attributes': attributes, 'scope': 'global.' + self.current_class})

        return


    # Visit a parse tree produced by YAPLParser#variable.
    def visitVariable(self, ctx:YAPLParser.VariableContext):
        variableName = ctx.children[0].getText()
        variableType = ctx.children[2].getText()
        #evaluate the value to assign default values
        if len(ctx.children) > 3:
            variableValue = ctx.children[4].getText()
            #print('VARIABLE VALUE', variableValue)
            valueType  = self.visit(ctx.children[4]) #Type of value to assign
            
            #check if the types are the same
            if variableType != valueType:
                self.errors_list.append(MyErrorVisitor(ctx, "Variable type mismatch"))
                #self.visitChildren(ctx)
                return ErrorType
        elif variableType in self.defaultValues:
            variableValue = self.defaultValues[variableType]['value']
        else:
            variableValue = None

        # Check in symbol table if variable exists in scope
        if self.symbol_table.getIdByScope(variableName, 'global.' + self.current_class) != None:
            errorMsg = 'Type-Check: class ' + self.current_class + ' redefines attribute ' + variableName
            self.errors_list.append(MyErrorVisitor(ctx, errorMsg))
            self.visitChildren(ctx)
            return ErrorType
            
        
        # check for size 
        if variableType in self.defaultValues and variableType != StringType:
            self.symbol_table.add(variableType, 'variable', self.defaultValues[variableType]['size'], self.offset_acc, {'name': variableName, 'value': variableValue, 'scope': 'global.' + self.current_class})
            self.offset_acc += self.defaultValues[variableType]['size']
        elif variableType == StringType:
            #size of string * length of variable
            #-1 because of the quotes but the end of string
            size = (self.defaultValues[variableType]['size'] * len(variableValue))-1
            self.symbol_table.add(variableType, 'variable', size, self.offset_acc, {'name': variableName, 'value': variableValue, 'scope': 'global.' + self.current_class})
            self.offset_acc += size
        else:
            self.symbol_table.add(variableType, 'variable', None, 0, {'name': variableName, 'value': variableValue, 'scope': 'global.' + self.current_class})
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YAPLParser#formal.
    def visitFormal(self, ctx:YAPLParser.FormalContext):
        attributeName = ctx.children[0].getText()
        attributeType = ctx.children[2].getText()
        if attributeType in self.defaultValues:
            attributeValue = self.defaultValues[attributeType]['value']
        else:
            attributeValue = None
        attribute = {
            'name': attributeName,
            'type': attributeType,
            'value': attributeValue,
            'scope': 'local.' + self.current_class + '.' + self.current_function
        },
        
        #Check size
        if attributeType in self.defaultValues and attributeType != StringType:
            self.symbol_table.add(attributeType, 'variable', self.defaultValues[attributeType]['size'], self.offset_acc, {'name': attributeName, 'value':attributeValue, 'scope': 'local.' + self.current_class + '.' + self.current_function})
            self.offset_acc += self.defaultValues[attributeType]['size']
        elif attributeType == StringType:
            #size of string * length of variable
            #-1 because of the quotes but the end of string
            size = (self.defaultValues[attributeType]['size'] * len(attributeValue))-1
            self.symbol_table.add(attributeType, 'variable', size, self.offset_acc, {'name': attributeName, 'value':attributeValue, 'scope': 'local.' + self.current_class + '.' + self.current_function})
            self.offset_acc += size
        else:
            self.symbol_table.add(attributeType, 'variable', None, 0, {'name': attributeName, 'value':attributeValue, 'scope': 'local.' + self.current_class + '.' + self.current_function})
        return attribute


    # Visit a parse tree produced by YAPLParser#plusminus.
    def visitPlusminus(self, ctx:YAPLParser.PlusminusContext):
        #cprint("PLUSMINUS"+ctx.children[0].getText(), "blue")
        #get the type of the left and right side
        results = []
        for plus_node in ctx.expr():
            #print("plus node",plus_node.getText())
            results.append(self.visit(plus_node))
        left = results[0]
        right = results[-1]
        #print("LEFT: "+left+" RIGHT: "+right)
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
        self.visit(ctx.children[0])
        result = self.visit(ctx.children[1])
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
        # Visit all children, but return type of last <expr>
        for index, child in enumerate(ctx.children):
            if index != len(ctx.children) - 3:
                self.visit(child)
            else:
                #print(ctx.children[-2].getText())

                self.visit(ctx.children[-2])
                #print(ctx.children[-1].getText())
                self.visit(ctx.children[-1])
                last = self.visit(child)
                #print(child.getText())
                #cprint("LAST: "+str(last),"blue")
                return last


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
    #@TODO check only type or change the value of 0 to false
    def visitWhile(self, ctx:YAPLParser.WhileContext):
        compareExpression = self.visit(ctx.children[1])
        if compareExpression == BoolType:
            self.visit(ctx.children[3])
            return ObjectType
        elif compareExpression == IntType:
            #make casting int to bool
            self.visit(ctx.children[3])
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
        #print("CALL")
        self.visitChildren(ctx)
        # Return ID type
        #print("CHILDREN 0 CALL",ctx.children[0].getText())
        callParameterCount = 0 if len(ctx.children) == 3 else int(((len(ctx.children) - 3) / 2) + 0.5)
        existenceMethod = self.symbol_table.getCallMethodExistence(ctx.children[0].getText(), 'global.' + self.current_class, self.current_function)
        inFunctionTableExistence = self.function_table.getCallMethodExistence(ctx.children[0].getText(), 'global.' + self.current_class, self.current_function)
        parentCheck = self.current_class
        funcParentCheck = self.current_class

        while existenceMethod == False and parentCheck != ObjectType and parentCheck!= None:
            parentCheck = self.symbol_table.getClassParent(parentCheck)
            if parentCheck != None:
                existenceMethod = self.symbol_table.getCallMethodExistence(ctx.children[0].getText(), 'global.' + parentCheck, self.current_function)
                if not inFunctionTableExistence:
                    funcParentCheck = parentCheck
                    inFunctionTableExistence = self.function_table.getCallMethodExistence(ctx.children[0].getText(), 'global.' + parentCheck, self.current_function)
        
        if existenceMethod == False:
            #print("IM HERE CALL METHOD")
            if ctx.children[0].getText() == self.current_function:
                if (callParameterCount == self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + self.current_class)):
                    return self.current_function_type
                else:
                    self.errors_list.append(MyErrorVisitor(ctx, "Wrong number of actual arguments (" + callParameterCount + " vs. " + str(self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + self.current_class)) + ")"))
                    return ErrorType
            if inFunctionTableExistence:
                # Function defined in non visited class/method
                callType = self.function_table.getCategoryScope(ctx.children[0].getText(), 'global.' + funcParentCheck)
                #print("CALL TYPE CALL",callType)
                if (callParameterCount == self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + funcParentCheck)):
                    if callType == None:
                        return self.current_function_type
                    return callType
                else:
                    localCurrentClass = 'global.' + self.current_class
                    self.errors_list.append(MyErrorVisitor(ctx, "Wrong number of actual arguments (" + str(callParameterCount) + " vs. " + str(self.function_table.getFunctionAttrCount(ctx.children[0].getText(), localCurrentClass)) + ")"))
                    return ErrorType
            #TODO change this when class definition error is fixed
            #self.errors_list.append(MyErrorVisitor(ctx, "Type-Check: unkonwn method "+ctx.children[0].getText()+" in dispatch on " + self.visit(ctx.children[0])))
            self.errors_list.append(MyErrorVisitor(ctx, "Type-Check: unkonwn method "+ctx.children[0].getText()+" in dispatch on " +self.current_class))
            return ErrorType
        else:

            #print("PARENT HERE", parentCheck)
            #print("FUNCTION NAME", ctx.children[0].getText())
            callType = self.symbol_table.getCategoryScope(ctx.children[0].getText(), 'global.' + parentCheck)
            ioCallType = self.symbol_table.getCategoryScope(ctx.children[0].getText(), 'global.IO')
            #print("CALL TYPE CALL",callType)
            if ioCallType != None:
                return ioCallType
            if callType == None:
                #print("SEARCHING FUNCTION TABLE")
                callType = self.function_table.getCategoryScope(ctx.children[0].getText(), 'global.' + parentCheck)
                if callType == None:
                    if (callParameterCount == self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + funcParentCheck)):
                        return self.current_function_type
                    else:
                        self.errors_list.append(MyErrorVisitor(ctx, "Wrong number of actual arguments (" + str(callParameterCount) + " vs. " + str(self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + self.current_class)) + ")"))
                        return ErrorType
                else:
                    if (callParameterCount == self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + funcParentCheck)):
                        return callType
                    else:
                        self.errors_list.append(MyErrorVisitor(ctx, "Wrong number of actual arguments (" + str(callParameterCount) + " vs. " + str(self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + self.current_class)) + ")"))
                        return ErrorType
            return callType


    # Visit a parse tree produced by YAPLParser#newtype.
    def visitNewtype(self, ctx:YAPLParser.NewtypeContext):
        self.visit(ctx.children[0])
        # Return Type
        return ctx.children[1].getText() if ctx.children[1].getText() != SELF_TYPE else self.current_class


    # Visit a parse tree produced by YAPLParser#timesdiv.
    def visitTimesdiv(self, ctx:YAPLParser.TimesdivContext):
        #get the type of the left and right side
        #print('CONTEXT', ctx.getText())
        results = []
        for times_node in ctx.expr():
            #print("TIMES TEXT",times_node.getText())
            results.append(self.visit(times_node))
        left = results[0]
        right = results[-1]
        #print("TIMES LEFT RIGHT",left,right)
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
                return BoolType
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
        self.visit(ctx.children[0])
        self.visit(ctx.children[2])
        # Return expr type
        return self.visit(ctx.children[1])


    # Visit a parse tree produced by YAPLParser#true.
    def visitTrue(self, ctx:YAPLParser.TrueContext):
        return BoolType


    # Visit a parse tree produced by YAPLParser#let.
    def visitLet(self, ctx:YAPLParser.LetContext):
        # # Return Value of expr here: [IN expr]
        # variableName = ctx.children[1].getText()
        # variableType = ctx.children[2].getText()
        # #evaluate the value to assign default values
        # if len(ctx.children) > 3:
        #     variableValue = ctx.children[5].getText()
        # elif variableType in self.defaultValues:
        #     variableValue = self.defaultValues[variableType]
        # else:
        #     variableValue = None
    

        # self.symbol_table.add(variableType, 'variable', 0, 0, {'name': variableName, 'value': variableValue, 'scope': 'local.' + self.current_class + '.' + self.current_function + '.let' + str(self.current_let)})
        # self.visitChildren(ctx)
        # self.current_let += 1
        # # Visit all children, and return last visit
        # for index, child in enumerate(ctx.children):
        #     if index != len(ctx.children) - 1:
        #         self.visit(child)
        #     else:
        #         return self.visit(child)
        variableName = None
        variableType = None
        variableValue = None
        #print("ENTERING LET")
        for index, child in enumerate(ctx.children):
            #print("INSIDE FOR")
            if child.getText() == ',' or child.getText() == 'IN' or child.getText() == 'in':
                if variableType in self.defaultValues:
                    variableValue = self.defaultValues[variableType]['value']
                else:
                    variableValue = None
                
                #print("SI ENTRO")
                #sizes
                if variableType in self.defaultValues and variableType != StringType:
                    self.symbol_table.add(variableType, 'variable', self.defaultValues[variableType]['size'], self.offset_acc, {'name': variableName, 'value': variableValue, 'scope': 'local.' + self.current_class + '.' + self.current_function + '.let' + str(self.current_let)})
                    self.offset_acc += self.defaultValues[variableType]['size']
                elif variableType == StringType:
                    #size of string * length of variable
                    #-1 because of the quotes but the end of string
                    size = (self.defaultValues[variableType]['size'] * len(variableValue))-1
                    self.symbol_table.add(variableType, 'variable', size, self.offset_acc, {'name': variableName, 'value': variableValue, 'scope': 'local.' + self.current_class + '.' + self.current_function + '.let' + str(self.current_let)})
                    self.offset_acc += size
                else:
                    self.symbol_table.add(variableType, 'variable', None, 0, {'name': variableName, 'value': variableValue, 'scope': 'local.' + self.current_class + '.' + self.current_function + '.let' + str(self.current_let)})
                variableName = None
                variableType = None
                variableValue = None
            elif child.getText() == ':':

                variableName = ctx.children[index -1].getText()
                variableType = ctx.children[index + 1].getText() if ctx.children[index + 1].getText() != SELF_TYPE else self.current_class
                #print("VARIABLE NAME",variableName)
                #print("VARIABLE TYPE",variableType)
                continue
            elif isinstance(child, TerminalNode):
                #print("TERMINAL NODE",child.getText())
                continue
            else:
                if index != len(ctx.children) - 1:
                    variableValue = self.visit(child)
                else:
                    self.current_let += 1
                    return self.visit(child)

    # Visit a parse tree produced by YAPLParser#id.
    def visitId(self, ctx:YAPLParser.IdContext):
        #print("FUNCTION TYPE ID",self.current_function_type,self.current_function)
        #search for the variable in the symbol table 
        #print(self.symbol_table.printTable())
        if ctx.getText() == 'self': #si es self
            return SELF_TYPE
        #@TODO verificar scope al tenerlo 
        else:
            #print("IM HERE IN ID ELSE AAAAAA")
            #print(ctx.getText())
            classScope = 'global.' + str(self.current_class)
            functionScope = 'global.' + str(self.current_class) + '.' + str(self.current_function)
            letScope = 'local.' + str(self.current_class) + '.' + str(self.current_function) + '.let' + str(self.current_let-1)
            paramScope = 'local.' + str(self.current_class) + '.' + str(self.current_function)

            variable = self.symbol_table.getVariableCategory(ctx.getText(), letScope)
            
            if variable == None:
                variable = self.symbol_table.getVariableCategory(ctx.getText(), paramScope)

                if variable == None:
                    variable = self.symbol_table.getVariableCategory(ctx.getText(), functionScope)
                    if variable == None:
                     variable= self.symbol_table.getVariableCategory(ctx.getText(), classScope)
           

            if variable == None:
                if ctx.getText() == self.current_function:
                    #print("IM HERE IN ID")
                    return self.current_function_type
                else:
                    self.errors_list.append(MyErrorVisitor(ctx, "Variable " + ctx.getText() + " not declared"))
                    self.visitChildren(ctx)
                    return ErrorType
            else:
                return variable

    
    # Visit a parse tree produced by YAPLParser#if.
    #@TODO check and return the if type or not, for casting.
    def visitIf(self, ctx:YAPLParser.IfContext):
        #print("COMPARE TYPE", self.visit(ctx.children[1]))
        compareExpression = self.visit(ctx.children[1])
        thenType = self.visit(ctx.children[3])
        #print("THEN TYPE",thenType)
        elseType = self.visit(ctx.children[5])
        #print("else",elseType)

        # Defining ifType. Highest common class
        if thenType == elseType:
            if compareExpression == BoolType or compareExpression == IntType:
                #print("IN THE IF")
                return thenType
        else:
            #print("IN THE ELSE")
            # Cycle through class parents
            #print("HERE")
            thenTempType = thenType
            elseTempType = elseType
            while thenTempType != None:
                while elseTempType != None:
                    elseTempType = self.symbol_table.getClassParent(elseTempType)
                    #print("ELSE TEMP TYPE",elseTempType, "THEN TEMP TYPE",thenTempType)
                    if elseTempType == thenTempType:
                        #print("Compare expression",compareExpression == BoolType)
                        if compareExpression == BoolType or compareExpression == IntType:
                            #print("THEN TEMP TYPE",thenTempType)   
                            return thenTempType
                elseTempType = elseType
                if thenTempType == SELF_TYPE and self.function_table.getClassParent(thenTempType) == None:
                    if compareExpression == BoolType or compareExpression == IntType:
                        thenTempType = self.function_table.getCategory(self.current_function)
                        return thenTempType
                else:
                    if compareExpression == BoolType or compareExpression == IntType:
                        #print("ELSE THEN TEMP TYPE",thenTempType)
                        thenTempType = self.symbol_table.getClassParent(thenTempType)
                        return thenTempType

            
        self.errors_list.append(MyErrorVisitor(ctx, "Conditional has type " + compareExpression + " instead of BOOL"))
        self.visitChildren(ctx)
        return ErrorType

    #@TODO error expr not complete
    # Visit a parse tree produced by YAPLParser#assign.
    def visitAssign(self, ctx:YAPLParser.AssignContext):
        #print the text of all children
        #print("FULL TEXT",ctx.getText(),ctx.children[2])
        #for to iterate children 2
        #get id of the assignment
        idValue = ctx.children[0].getText()
        #get the expression of the assignment
        exprValue = ctx.children[2].getText()
        #print("HAHA",ctx.expr())

        #print("ASSIGN: "+idValue+" EXPR> "+exprValue)
        
        #get type of the expression
        exprType = self.visit(ctx.children[2])

        #print("EXPRTYPE",exprType)
        #search ID in symbol table with scopes to find the type
        classScope = 'global.' + str(self.current_class)
        functionScope = 'global.' + str(self.current_class) + '.' + str(self.current_function)
        letScope = 'local.' + str(self.current_class) + '.' + str(self.current_function) + '.let' + str(self.current_let-1)
        paramScope = 'local.' + str(self.current_class) + '.' + str(self.current_function)
        #print("ASSIGN SCOPE",letScope,idValue)
        idType = self.symbol_table.getVariableCategory(idValue, letScope)
        
        if idType == None:
            idType = self.symbol_table.getVariableCategory(idValue, paramScope)
            if idType == None:
                idType = self.symbol_table.getVariableCategory(idValue, functionScope)
                if idType == None:
                    idType = self.symbol_table.getVariableCategory(idValue, classScope)
                    if idType == None:
                        self.errors_list.append(MyErrorVisitor(ctx, "Variable " + idValue + " not declared"))
                        self.visitChildren(ctx)
                        return ErrorType
            
            #cprint("ID TYPE: "+idType,"red")

        #search type of expr if type it is not primitive or function call
        hasMatch = False
        if exprType != idType:
            while exprType != None:
                #cprint("EXPR TYPE busqueda: "+exprType,"yellow")
                exprType = self.symbol_table.getClassParent(exprType)
                if exprType == idType:
                    hasMatch = True
                    break
            if not hasMatch:
                # Return type of function body nor its parents match expected type
                errorMsg = 'Type-Check: ' + str(exprType) + ' does not conform to ' + idType + ' in variable ' + idValue
                self.errors_list.append(MyErrorVisitor(ctx, errorMsg))
                #@TODO este se vuelve a visitar
                #self.visitChildren(ctx)
                return ErrorType
            
        # cprint("TYPES MATCH "+idType+exprType,"blue")


        #assing in symbol table value
        if self.symbol_table.setVariableValue(idValue, exprValue, letScope ):
            return exprType
        if self.symbol_table.setVariableValue(idValue, exprValue, paramScope):
            return exprType
        if self.symbol_table.setVariableValue(idValue, exprValue, functionScope):
            return exprType
        if self.symbol_table.setVariableValue(idValue, exprValue, classScope):
            return exprType
        # cprint("ASSIGN: "+"ID:"+idValue+" EXPR> "+exprValue,"green")
        return exprType


    # Visit a parse tree produced by YAPLParser#bigexpr.
    def visitBigexpr(self, ctx:YAPLParser.BigexprContext):
        # Return ID type
        callerType = self.visit(ctx.children[0])
        for i in range(1, len(ctx.children)):
            self.visit(ctx.children[i])
        #print("BIG EXPR TYPE",callerType)
        idIndex = 4 if ctx.children[1].getText() == '@' else 2
        #print('CHECKING', callerType, ctx.children[idIndex].getText())
        existenceMethod = self.symbol_table.getCallMethodExistence(ctx.children[idIndex].getText(), 'global.' + callerType, self.current_function)
        inFunctionTableExistence = self.function_table.getCallMethodExistence(ctx.children[idIndex].getText(), 'global.' + callerType, self.current_function)
        parentCheck = callerType
        funcParentCheck = callerType

        while existenceMethod == False and parentCheck != ObjectType and parentCheck!= None:
            parentCheck = self.symbol_table.getClassParent(parentCheck)
            if parentCheck != None:
                existenceMethod = self.symbol_table.getCallMethodExistence(ctx.children[idIndex].getText(), 'global.' + parentCheck, self.current_function)
                if not inFunctionTableExistence:
                    funcParentCheck = parentCheck
                    inFunctionTableExistence = self.function_table.getCallMethodExistence(ctx.children[idIndex].getText(), 'global.' + parentCheck, self.current_function)

        if existenceMethod == False:
            #print("IM HERE CALL BIG EXPR METHOD")
            if ctx.children[idIndex].getText() == self.current_function:
                return self.current_function_type
            if inFunctionTableExistence:
                # Function defined in non visited class/method
                bigExprType = self.function_table.getCategoryScope(ctx.children[idIndex].getText(), 'global.' + funcParentCheck)
                if bigExprType == None:
                    return self.current_function_type
                return bigExprType
            #TODO change this when class definition error is fixed
            #self.errors_list.append(MyErrorVisitor(ctx, "Type-Check: unkonwn method "+ctx.children[idIndex].getText()+" in dispatch on " + self.visit(ctx.children[idIndex])))
            self.errors_list.append(MyErrorVisitor(ctx, "Type-Check: unkonwn method "+ctx.children[idIndex].getText()+" in dispatch on " +self.current_class))
            #self.visitChildren(ctx)
            return ErrorType
        else:
            bigExprType = self.symbol_table.getCategoryScope(ctx.children[idIndex].getText(), 'global.' + parentCheck)
            if bigExprType == None:
                return self.current_function_type
            return bigExprType
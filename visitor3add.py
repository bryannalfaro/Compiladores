from antlr4 import *
from ANTLR.YAPLParser import YAPLParser
from listenerError import MyErrorVisitor
from termcolor import cprint    
from SymbolTable import *
from threeAddress import *
from quadrupleCode import *
import copy

class IntermediateCode(ParseTreeVisitor):
    def __init__(self, symbolTable):
        super().__init__()
        self.symbol_table = symbolTable
        self.function_table = symbolTable
        self.threeCode = ThreeAddressCode()
        self.generate = Generator()
        self.errors_list = []
        self.fatherTrueLabel = False
        self.fatherFalseLabel = False
        self.nextFatherLabel = False
        self.beginLabel = False

        self.defaultValues = {
            IntType: { 'value': 0, 'size': 4 },
            BoolType: { 'value': False, 'size': 1 },
            StringType: { 'value': '', 'size': 1 }
        }
        # Global variables to set Scope
        self.current_class = None
        self.current_function = None
        self.current_let = 0
        self.current_function_type = None
        self.global_offset = 0
        self.local_offset = 0

     # Visit a parse tree produced by YAPLParser#program.
    def visitProgram(self, ctx:YAPLParser.ProgramContext):
        children = []
        for child in ctx.children:
            children.append(self.visit(child))
        
        #return all that are not None
        return [child for child in children if child is not None]
    
    # Visit a parse tree produced by YAPLParser#class_grammar.
    def visitClass_grammar(self, ctx:YAPLParser.Class_grammarContext): 
        classType = ctx.children[1].getText()
        self.current_class = classType
        self.global_offset = 0

        #create quadruple 
        quadruple_class = Quadruple('identifier', 'class_'+classType, None, None)
        threeCode = ThreeAddressCode()
        threeCode.add(quadruple_class)
        #visit the children
        for child in ctx.children:
            res = self.visit(child)
            if res != None:
                threeCode.add(res.code)
        return threeCode

    # Visit a parse tree produced by YAPLParser#function.
    def visitFunction(self, ctx:YAPLParser.FunctionContext):
        functionName = ctx.children[0].getText()
        self.current_function = functionName
        self.local_offset = self.global_offset
        # Attribute count takes 8 (no attributes) from the children length, and then it ignores commas
        attributeCount = 0 if len(ctx.children) == 8 else int(((len(ctx.children) - 8) / 2) + 0.5)
        functionType = ctx.children[-4].getText()
        self.current_function_type = functionType

        #@TODO add logic when parameters in 3 add code
        if attributeCount > 0: 
            attributes = []
            for i in range(2, 2 * attributeCount + 1, 2):
                # Visiting all attributes (Formal)
                attributes.append(self.visit(ctx.children[i]))


    
        functionName = ctx.children[0].getText()
        threeCode = ThreeAddressCode()

        self.current_function = functionName

        self.local_offset = self.global_offset
        
        #Create the quadruple
        funct_expr = self.visit(ctx.children[-2])
        threeCode.add(Quadruple('identifier', 'function_'+functionName+"_"+self.current_class+f"[{functionType}]", None, None))
        threeCode.add(funct_expr.code) #añadir el codigo de la expresion
        
        #Si hay una label definida
        if self.nextFatherLabel != False:
            threeCode.add(Quadruple('label', None, None, self.nextFatherLabel))
            self.nextFatherLabel = False
        threeCode.add(Quadruple('return', 'function_'+functionName+"_"+self.current_class+f"[{functionType}]", None, None))
        return threeCode


    # Visit a parse tree produced by YAPLParser#variable.
    def visitVariable(self, ctx:YAPLParser.VariableContext):
        variableName = ctx.children[0].getText()
        threeCode = ThreeAddressCode()
        if len(ctx.children) > 3:
            #visit the children
            childCode = self.visitChildren(ctx)
            threeCode.add(childCode.code)
            threeCode.add(Quadruple('equal',childCode.address, None, variableName))
        else:
            #search default values
            variableType = ctx.children[2].getText()
            if variableType in self.defaultValues:
                variableValue = self.defaultValues[variableType]['value']
            else:
                variableValue = None
            #quadruple
            quadruple_variable = Quadruple('equal', variableValue, None, variableName)
            threeCode.add(quadruple_variable)
        
        return threeCode


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
            self.symbol_table.add(attributeType, 'variable', self.defaultValues[attributeType]['size'], self.local_offset, {'name': attributeName, 'value':attributeValue, 'scope': 'local.' + self.current_class + '.' + self.current_function})
            self.local_offset += self.defaultValues[attributeType]['size']
        elif attributeType == StringType:
            #size of string * length of variable
            #-1 because of the quotes but the end of string
            size = (self.defaultValues[attributeType]['size'] * len(attributeValue))+10
            self.symbol_table.add(attributeType, 'variable', size, self.local_offset, {'name': attributeName, 'value':attributeValue, 'scope': 'local.' + self.current_class + '.' + self.current_function})
            self.local_offset += size
        else:
            self.symbol_table.add(attributeType, 'variable', None, 0, {'name': attributeName, 'value':attributeValue, 'scope': 'local.' + self.current_class + '.' + self.current_function})
        return attribute


    # Visit a parse tree produced by YAPLParser#plusminus.
    def visitPlusminus(self, ctx:YAPLParser.PlusminusContext):
        results = []
        for times_node in ctx.expr():
            results.append(self.visit(times_node))
        left = results[0]
        right = results[-1]
        threeCode = ThreeAddressCode()
        threeCode.addAddress(self.generate.getTemporal())
        threeCode.add(left.code)
        threeCode.add(right.code)
        threeCode.add(Quadruple(ctx.children[1].getText(), left.address, right.address, threeCode.address))

        return threeCode

    # Visit a parse tree produced by YAPLParser#negation.
    def visitNegation(self, ctx:YAPLParser.NegationContext):
        result = self.visit(ctx.expr())
        threeCode = ThreeAddressCode()
        threeCode.addAddress(self.generate.getTemporal())
        threeCode.add(result.code)
        
        threeCode.add(Quadruple('negation', result.address, None, threeCode.address))
        return threeCode
        
    # Visit a parse tree produced by YAPLParser#curly.
    def visitCurly(self, ctx:YAPLParser.CurlyContext):
        print('im here ')
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
        threeCode  = ThreeAddressCode()
        threeCode.typeValue = StringType
        threeCode.addAddress(ctx.getText())
        return threeCode

    # Visit a parse tree produced by YAPLParser#isvoid.
    def visitIsvoid(self, ctx:YAPLParser.IsvoidContext):
        print('im here ')
        self.visitChildren(ctx)
        # Return bool evaluates to true if expr is void 
        # and evaluates to false if expr is not void.
        return BoolType


    # Visit a parse tree produced by YAPLParser#false.
    def visitFalse(self, ctx:YAPLParser.FalseContext):
        threeCode  = ThreeAddressCode()
        threeCode.typeValue = BoolType
        threeCode.addAddress(ctx.getText())
        return threeCode


    # Visit a parse tree produced by YAPLParser#while.
    def visitWhile(self, ctx:YAPLParser.WhileContext):

        self.nextFatherLabel = self.generate.getNextLabel()
        self.fatherFalseLabel = copy.deepcopy(self.nextFatherLabel) #hago copia B.false = S.siguiente
        self.fatherTrueLabel = self.generate.getWhileLabel(0, 'true') 
        compareExpression = self.visit(ctx.children[1])
        whileType = self.visit(ctx.children[3])
        
        
        self.nextFatherLabel = self.beginLabel #cambio nextFather S1.siguiente = inicio


        threeCode = ThreeAddressCode()
        self.beginLabel  = self.generate.getBeginLabel()
        threeCode.add(Quadruple('label', None, None, self.beginLabel))
        threeCode.add(compareExpression.code)
        threeCode.add(Quadruple('label', None, None, self.fatherTrueLabel))
        threeCode.add(whileType.code)
        threeCode.add(Quadruple('goto', None, None, self.beginLabel))
        threeCode.add(Quadruple('label', None, None, self.fatherFalseLabel))

        return threeCode


    # Visit a parse tree produced by YAPLParser#int.
    def visitInt(self, ctx:YAPLParser.IntContext):
        threeCode  = ThreeAddressCode()
        threeCode.typeValue = IntType
        threeCode.addAddress(ctx.getText())
        return threeCode

    # Visit a parse tree produced by YAPLParser#call.
    def visitCall(self, ctx:YAPLParser.CallContext):
        print('im here ')
        #print("CALL")
        self.visitChildren(ctx)
        # Return ID type
        #print("CHILDREN 0 CALL",ctx.children[0].getText())
        callParameterCount = 0 if len(ctx.children) == 3 else int(((len(ctx.children) - 3) / 2) + 0.5)
        existenceMethod = self.symbol_table.getCallMethodExistence(ctx.children[0].getText(), 'global.' + self.current_class, self.current_function)
        inFunctionTableExistence = self.function_table.getCallMethodExistence(ctx.children[0].getText(), 'global.' + self.current_class, self.current_function)
        parentCheck = self.current_class
        funcParentCheck = self.current_class

        threeCode = ThreeAddressCode()
        threeCode.addAddress('R')
        '''
        threeCode.add(Quadruple('PARAMETER', None, None, ctx.children[5]))
        PARAMETER a
        PARAMETER b
        CALL function_name
        threeCode.add(Quadruple('CALL', None, None, ctx.children[6]))
        '''
        for i in range(callParameterCount):
            threeCode.add(Quadruple('PARAMETER', None, None, ctx.children[2*i+2].getText()))

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
                    functionName = 'function_'+ctx.children[0].getText()+'_'+self.current_class+'['+self.current_function_type+']'
                    threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionName))
                    return threeCode
                else:
                    self.errors_list.append(MyErrorVisitor(ctx, "Wrong number of actual arguments (" + callParameterCount + " vs. " + str(self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + self.current_class)) + ")"))
                    return ErrorType
            if inFunctionTableExistence:
                # Function defined in non visited class/method
                callType = self.function_table.getCategoryScope(ctx.children[0].getText(), 'global.' + funcParentCheck)
                #print("CALL TYPE CALL",callType)
                if (callParameterCount == self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + funcParentCheck)):
                    if callType == None:
                        functionName = 'function_'+ctx.children[0].getText()+'_'+self.current_class+'['+self.current_function_type+']'
                        threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionName))
                        return threeCode
                    functionName = 'function_'+ctx.children[0].getText()+'_'+self.current_class+'['+callType+']'
                    threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionName))
                    return threeCode
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
                functionName = 'function_'+ctx.children[0].getText()+'_'+self.current_class+'['+ioCallType+']'
                threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionName))
                return threeCode
            if callType == None:
                #print("SEARCHING FUNCTION TABLE")
                callType = self.function_table.getCategoryScope(ctx.children[0].getText(), 'global.' + parentCheck)
                if callType == None:
                    if (callParameterCount == self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + funcParentCheck)):
                        functionName = 'function_'+ctx.children[0].getText()+'_'+self.current_class+'['+self.current_function_type+']'
                        threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionName))
                        return threeCode
                    else:
                        self.errors_list.append(MyErrorVisitor(ctx, "Wrong number of actual arguments (" + str(callParameterCount) + " vs. " + str(self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + self.current_class)) + ")"))
                        return ErrorType
                else:
                    if (callParameterCount == self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + funcParentCheck)):
                        functionName = 'function_'+ctx.children[0].getText()+'_'+self.current_class+'['+callType+']'
                        threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionName))
                        return threeCode
                    else:
                        self.errors_list.append(MyErrorVisitor(ctx, "Wrong number of actual arguments (" + str(callParameterCount) + " vs. " + str(self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + self.current_class)) + ")"))
                        return ErrorType
            functionName = 'function_'+ctx.children[0].getText()+'_'+self.current_class+'['+callType+']'
            threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionName))
            return threeCode


    # Visit a parse tree produced by YAPLParser#newtype.
    def visitNewtype(self, ctx:YAPLParser.NewtypeContext):
        self.visit(ctx.children[0])
        # Return Type
        return ctx.children[1].getText() if ctx.children[1].getText() != SELF_TYPE else self.current_class


    # Visit a parse tree produced by YAPLParser#timesdiv.
    def visitTimesdiv(self, ctx:YAPLParser.TimesdivContext):
        results = []
        for times_node in ctx.expr():
            results.append(self.visit(times_node))
        left = results[0]
        right = results[-1]
        threeCode = ThreeAddressCode()
        threeCode.addAddress(self.generate.getTemporal())
        threeCode.add(left.code)
        threeCode.add(right.code)
        threeCode.add(Quadruple(ctx.children[1].getText(), left.address, right.address, threeCode.address))

        return threeCode
         
    # Visit a parse tree produced by YAPLParser#compare.
    def visitCompare(self, ctx:YAPLParser.CompareContext):
        results = []
        for compare_node in ctx.expr():
            results.append(self.visit(compare_node))
        left = results[0]
        right = results[-1]

        threeCode = ThreeAddressCode()
        threeCode.add(left.code)
        threeCode.add(right.code)
        threeCode.add(Quadruple(ctx.children[1].getText(), left.address, right.address, self.fatherTrueLabel))
        threeCode.add(Quadruple('goto', None, None, self.fatherFalseLabel))
        return threeCode
           

    # Visit a parse tree produced by YAPLParser#not.
    def visitNot(self, ctx:YAPLParser.NotContext):
        result = self.visit(ctx.expr())
        threeCode = ThreeAddressCode()
        threeCode.addAddress(self.generate.getTemporal())
        threeCode.add(result.code)

        threeCode.add(Quadruple('not', result.address, None, threeCode.address))
        return threeCode


    # Visit a parse tree produced by YAPLParser#paren.
    def visitParen(self, ctx:YAPLParser.ParenContext):
        threeCode = ThreeAddressCode()
        expr = self.visit(ctx.children[1])
        threeCode.addAddress(expr.address)
        threeCode.add(expr.code)

        return threeCode


    # Visit a parse tree produced by YAPLParser#true.
    def visitTrue(self, ctx:YAPLParser.TrueContext):
        threeCode  = ThreeAddressCode()
        threeCode.typeValue = BoolType
        threeCode.addAddress(ctx.getText())
        return threeCode


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
                    self.symbol_table.add(variableType, 'variable', self.defaultValues[variableType]['size'], self.local_offset, {'name': variableName, 'value': variableValue, 'scope': 'local.' + self.current_class + '.' + self.current_function + '.let' + str(self.current_let)})
                    self.local_offset += self.defaultValues[variableType]['size']
                elif variableType == StringType:
                    #size of string * length of variable
                    #-1 because of the quotes but the end of string
                    size = (self.defaultValues[variableType]['size'] * len(variableValue))+10
                    self.symbol_table.add(variableType, 'variable', size, self.local_offset, {'name': variableName, 'value': variableValue, 'scope': 'local.' + self.current_class + '.' + self.current_function + '.let' + str(self.current_let)})
                    self.local_offset += size
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
        threeCode = ThreeAddressCode()
        if ctx.getText() == 'self': #si es self
            return threeCode.addAddress('self')
        else:
            #@TODO agregar el caso en 3add code cuando entre aca
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
                threeCode.addAddress(ctx.getText())
                return  threeCode

    
    # Visit a parse tree produced by YAPLParser#if.
    def visitIf(self, ctx:YAPLParser.IfContext):
        self.fatherTrueLabel, self.fatherFalseLabel = self.generate.getIfLabel(1)
        self.nextFatherLabel = self.generate.getNextLabel()
        
        compareExpression = self.visit(ctx.children[1])
        thenType = self.visit(ctx.children[3])
        elseType = self.visit(ctx.children[5])

        threeCode = ThreeAddressCode()
        threeCode.add(compareExpression.code)
        threeCode.add(Quadruple('label', None, None, self.fatherTrueLabel))
        threeCode.add(thenType.code)
        threeCode.add(Quadruple('goto', None, None, self.nextFatherLabel))
        threeCode.add(Quadruple('label', None, None, self.fatherFalseLabel))
        threeCode.add(elseType.code)

        return threeCode

    # Visit a parse tree produced by YAPLParser#assign.
    def visitAssign(self, ctx:YAPLParser.AssignContext):

        idValue = ctx.children[0].getText()
        exprType = self.visit(ctx.children[2])

        threeCode = ThreeAddressCode()
        threeCode.add(exprType.code)
        threeCode.add(Quadruple('equal', exprType.address, None, idValue))

        return threeCode

    # Visit a parse tree produced by YAPLParser#bigexpr.
    def visitBigexpr(self, ctx:YAPLParser.BigexprContext):
        print('im here ')
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
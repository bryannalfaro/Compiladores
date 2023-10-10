from antlr4 import *
from ANTLR.YAPLParser import YAPLParser
from listenerError import MyErrorVisitor
from VisitorImpl import YAPL as originalVisitor
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
        self.inheritsWhile1 = []
        
        

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
        self.generate.resetTemporal()
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
        self.current_function = None
        return threeCode


    # Visit a parse tree produced by YAPLParser#variable.
    def visitVariable(self, ctx:YAPLParser.VariableContext):
        variableName = ctx.children[0].getText()
        threeCode = ThreeAddressCode()
        variableOffset, variableScope = self.symbol_table.getVariableOffset(variableName, self.current_class)
        variableAddress = variableScope + '[' + str(variableOffset) + ']'
        if len(ctx.children) > 3:
            #visit the children
            childCode = self.visitChildren(ctx)
            threeCode.add(childCode.code)
            threeCode.add(Quadruple('equal',childCode.address, None, variableAddress))
            isTemporal = True
            if childCode.address[0] == 't':
                for i in range(1, len(childCode.address)):
                    if not childCode.address[i].isdigit():
                        isTemporal = False
                        break
            else:
                isTemporal = False
            if isTemporal:
                self.generate.makeTemporalAvailable(childCode.address)

        else:
            #search default values
            variableType = ctx.children[2].getText()
            if variableType in self.defaultValues:
                variableValue = self.defaultValues[variableType]['value']
            else:
                variableValue = None
            #quadruple
            quadruple_variable = Quadruple('equal', variableValue, None, variableAddress)
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
            print('TIMESNODE', type(times_node))
            results.append(self.visit(times_node))
        left = results[0]
        right = results[-1]
        threeCode = ThreeAddressCode()
        generate  = self.generate.getTemporal()
        threeCode.addAddress(generate)
        threeCode.add(left.code)
        threeCode.add(right.code)
        print('LEFTRIGHT', type(left), type(right), left.address, right.address, threeCode.address)
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
        print('im here curly')

        '''
        threeCode = ThreeAddressCode()
        expr = self.visit(ctx.children[1])
        threeCode.addAddress(expr.address)
        threeCode.add(expr.code)

        return threeCode
        '''
        #print parent ctx
        threeCode = ThreeAddressCode()

        # Visit all children, but return type of last <expr>
        for index, child in enumerate(ctx.children):
            if index == 0:
                continue
            elif index != len(ctx.children) - 3:
                print('CHILD: ', child.getText())
                a = self.visit(child)
                if a is not None:
                    #expr = self.visit(child)
                   
                    threeCode.add(a.code)
                    print('a')
            else:
                print('LAST CHILD: ', child.getText(), type(child))
                last = self.visit(child)
                cprint(last,'green')
                threeCode.add(last.code)
                threeCode.addAddress(last.address)
                return threeCode


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
        try:
            fatherFalseLabel = ctx.parentCtx.falseLabel
            if fatherFalseLabel != '':
                threeCode.add(Quadruple('goto',None, None, fatherFalseLabel))
            else:
                threeCode.add(Quadruple('boolean',None, None, ctx.getText()))
        except:
            return threeCode
        return threeCode


    # Visit a parse tree produced by YAPLParser#while.
    def visitWhile(self, ctx:YAPLParser.WhileContext):
        threeCode = ThreeAddressCode()
        
        
        try:
            fatherTrueLabel = ctx.parentCtx.trueLabel
            fatherBeginLabel = ctx.parentCtx.beginLabel
            fatherFalseLabel = ctx.parentCtx.nextLabel
        except:
            fatherBeginLabel  = self.generate.getBeginLabel()
            fatherTrueLabel = self.generate.getWhileLabel(0, 'true') 
            fatherFalseLabel = self.generate.getNextLabel() 
            
            ctx.trueLabel = fatherTrueLabel
            ctx.beginLabel = fatherBeginLabel
            ctx.falseLabel = fatherFalseLabel
            

        print('false' , fatherFalseLabel)
        nextLabel = fatherBeginLabel
        ctx.nextLabel = nextLabel
        
        compareExpression = self.visit(ctx.children[1])
        threeCode.add(Quadruple('label', None, None, fatherBeginLabel))
        threeCode.add(compareExpression.code)
        threeCode.add(Quadruple('label', None, None, fatherTrueLabel))
        whileType = self.visit(ctx.children[3])
        threeCode.add(whileType.code)
        threeCode.add(Quadruple('goto', None, None, fatherBeginLabel))
        print(self.fatherFalseLabel)
        threeCode.add(Quadruple('label', None, None, fatherFalseLabel))
       
        return threeCode


    # Visit a parse tree produced by YAPLParser#int.
    def visitInt(self, ctx:YAPLParser.IntContext):
        threeCode  = ThreeAddressCode()
        threeCode.typeValue = IntType
        threeCode.addAddress(ctx.getText())
        return threeCode

    # Visit a parse tree produced by YAPLParser#call.
    def visitCall(self, ctx:YAPLParser.CallContext):
        # print('im here ')
        print("CALL")
        #Se ve si proviene de un if para agregar un texto distinto
        try:
            fatherTrueLabel = ctx.parentCtx.trueLabel
            fatherFalseLabel = ctx.parentCtx.falseLabel
            fatherNextLabel = ctx.parentCtx.nextLabel
        except:
            fatherTrueLabel = ''
            fatherFalseLabel = ''
            fatherNextLabel = ''
        # Return ID type
        #print("CHILDREN 0 CALL",ctx.children[0].getText())
        callParameterCount = 0 if len(ctx.children) == 3 else int(((len(ctx.children) - 3) / 2) + 0.5)
        existenceMethod = self.symbol_table.getCallMethodExistence(ctx.children[0].getText(), 'global.' + self.current_class, self.current_function)
        inFunctionTableExistence = self.function_table.getCallMethodExistence(ctx.children[0].getText(), 'global.' + self.current_class, self.current_function)
        parentCheck = self.current_class
        funcParentCheck = self.current_class

        threeCode = ThreeAddressCode()
        #threeCode.addAddress(self.generate.getTemporal())
        '''
        threeCode.add(Quadruple('PARAMETER', None, None, ctx.children[5]))
        PARAMETER a
        PARAMETER b
        CALL function_name
        threeCode.add(Quadruple('CALL', None, None, ctx.children[6]))
        '''
        for i in range(callParameterCount):
            element = self.visit(ctx.children[2*i+2])
            threeCode.add(element.code)
            threeCode.add(Quadruple('PARAMETER', None, None, element.address))
            if element.address[0] == 't' and element.address[1:].isnumeric():
                self.generate.makeTemporalAvailable(element.address)

        while existenceMethod == False and parentCheck != ObjectType and parentCheck!= None:
            parentCheck = self.symbol_table.getClassParent(parentCheck)
            if parentCheck != None:
                existenceMethod = self.symbol_table.getCallMethodExistence(ctx.children[0].getText(), 'global.' + parentCheck, self.current_function)
                if not inFunctionTableExistence:
                    funcParentCheck = parentCheck
                    inFunctionTableExistence = self.function_table.getCallMethodExistence(ctx.children[0].getText(), 'global.' + parentCheck, self.current_function)
        functionOffset, functionCategory = self.symbol_table.getSizeOffsetFunction(ctx.children[0].getText(), self.current_class)
        functionCall = functionCategory + '[' + str(functionOffset) + ']'
        if existenceMethod == False:
            #print("IM HERE CALL METHOD")
            if ctx.children[0].getText() == self.current_function:
                if (callParameterCount == self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + self.current_class)):
                    threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionCall))
                    responseTemporal = self.generate.getTemporal()
                    threeCode.addAddress(responseTemporal)
                    threeCode.add(Quadruple('equal', 'R', None, responseTemporal))
                    if fatherTrueLabel != '':

                         threeCode.add(Quadruple('big', responseTemporal, None, fatherTrueLabel))
                    if fatherFalseLabel != '':
                        threeCode.add(Quadruple('goto', None, None, fatherFalseLabel))
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
                        threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionCall))
                        responseTemporal = self.generate.getTemporal()
                        threeCode.add(Quadruple('equal', responseTemporal, None, 'R'))
                        if fatherTrueLabel != '':
                         threeCode.add(Quadruple('big', responseTemporal, None, fatherTrueLabel))
                        if fatherFalseLabel != '':
                          threeCode.add(Quadruple('goto', None, None, fatherFalseLabel))
                        return threeCode
                    threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionCall))
                    responseTemporal = self.generate.getTemporal()
                    threeCode.addAddress(responseTemporal)
                    threeCode.add(Quadruple('equal', 'R', None, responseTemporal))
                    if fatherTrueLabel != '':
                         threeCode.add(Quadruple('big', responseTemporal, None, fatherTrueLabel))
                    if fatherFalseLabel != '':
                        threeCode.add(Quadruple('goto', None, None, fatherFalseLabel))
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
                threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionCall))
                responseTemporal = self.generate.getTemporal()
                threeCode.addAddress(responseTemporal)
                threeCode.add(Quadruple('equal', 'R', None, responseTemporal))
                if fatherTrueLabel != '':
                         threeCode.add(Quadruple('big', responseTemporal, None, fatherTrueLabel))
                if fatherFalseLabel != '':
                        threeCode.add(Quadruple('goto', None, None, fatherFalseLabel))
                return threeCode
            if callType == None:
                #print("SEARCHING FUNCTION TABLE")
                callType = self.function_table.getCategoryScope(ctx.children[0].getText(), 'global.' + parentCheck)
                if callType == None:
                    if (callParameterCount == self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + funcParentCheck)):
                        threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionCall))
                        responseTemporal = self.generate.getTemporal()
                        threeCode.addAddress(responseTemporal)
                        threeCode.add(Quadruple('equal', 'R', None, responseTemporal))
                        if fatherTrueLabel != '':
                         threeCode.add(Quadruple('big', responseTemporal, None, fatherTrueLabel))
                        if fatherFalseLabel != '':
                          threeCode.add(Quadruple('goto', None, None, fatherFalseLabel))
                        return threeCode
                    else:
                        self.errors_list.append(MyErrorVisitor(ctx, "Wrong number of actual arguments (" + str(callParameterCount) + " vs. " + str(self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + self.current_class)) + ")"))
                        return ErrorType
                else:
                    if (callParameterCount == self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + funcParentCheck)):
                        threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionCall))
                        responseTemporal = self.generate.getTemporal()
                        threeCode.addAddress(responseTemporal)
                        threeCode.add(Quadruple('equal', 'R', None, responseTemporal))
                        if fatherTrueLabel != '':
                         threeCode.add(Quadruple('big', responseTemporal, None, fatherTrueLabel))
                        if fatherFalseLabel != '':
                          threeCode.add(Quadruple('goto', None, None, fatherFalseLabel))
                        return threeCode
                    else:
                        self.errors_list.append(MyErrorVisitor(ctx, "Wrong number of actual arguments (" + str(callParameterCount) + " vs. " + str(self.function_table.getFunctionAttrCount(ctx.children[0].getText(), 'global.' + self.current_class)) + ")"))
                        return ErrorType
            threeCode.add(Quadruple('CALL', str(callParameterCount), None, functionCall))
            responseTemporal = self.generate.getTemporal()
            threeCode.addAddress(responseTemporal)
            threeCode.add(Quadruple('equal', 'R', None, responseTemporal))
            if fatherTrueLabel != '':
                         threeCode.add(Quadruple('big', responseTemporal, None, fatherTrueLabel))
            if fatherFalseLabel != '':
                        threeCode.add(Quadruple('goto', None, None, fatherFalseLabel))
            return threeCode


    # Visit a parse tree produced by YAPLParser#newtype.
    def visitNewtype(self, ctx:YAPLParser.NewtypeContext):
        threeCode = ThreeAddressCode()
        className = ctx.children[1].getText() if ctx.children[1].getText() != SELF_TYPE else self.current_class
        threeCode.addAddress('class_' + className)
        threeCode.add(Quadruple('new', None, None, className))
        self.visit(ctx.children[0])
        # Return Type
        return threeCode

    def getNewtype(self, new):
        indexOfNew = new.index('new')
        newType = ''
        i = indexOfNew + 3
        new = new[i:]
        i = 0
        while i<len(new) and new[i] != ' ' and new[i] != ')' :
            newType += new[i]
            i += 1
        return newType


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

        trueLabel  = ctx.parentCtx.trueLabel
        falseLabel = ctx.parentCtx.falseLabel

        threeCode = ThreeAddressCode()
        threeCode.add(left.code)
        threeCode.add(right.code)
        threeCode.add(Quadruple(ctx.children[1].getText(), left.address, right.address, trueLabel))
        threeCode.add(Quadruple('goto', None, None, falseLabel))
        #self.inheritsWhile1 = []
        
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
        try:
            fatherTrueLabel = ctx.parentCtx.trueLabel
            if fatherTrueLabel != '':
                threeCode.add(Quadruple('goto',None, None, fatherTrueLabel))
            else:
                threeCode.add(Quadruple('boolean',None, None, ctx.getText()))
        except:
            return threeCode
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
        threeCode = ThreeAddressCode()
        for index, child in enumerate(ctx.children):
            #print("INSIDE FOR")
            if child.getText() == ',' or child.getText() == 'IN' or child.getText() == 'in':
                if variableType in self.defaultValues:
                    variableValue = self.defaultValues[variableType]['value']
                else:
                    variableValue = None
                
                #print("SI ENTRO")
                #sizes
                variableOffset = self.symbol_table.getLetParamOffset(variableName, self.current_function, self.current_let)
                print('VARIABLE OFFSET', variableOffset)
                variableName  = "global." + self.current_class + '[' + str(variableOffset) + ']'
                if variableType in self.defaultValues and variableType != StringType:
                    threeCode.add(Quadruple('equal',variableValue, None, variableName))
                elif variableType == StringType:
                    threeCode.add(Quadruple('equal',variableValue, None, variableName))
                else:
                    threeCode.add(Quadruple('equal',variableValue, None, variableName))
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
                print('AAAAAAAAAAAAAAAH', child.getText())
                if index != len(ctx.children) - 1:
                    variableValue = self.visit(child).address
                    #print('VARIABLE VALUE', variableValue.address)
                else:
                    self.current_let += 1
                    cprint("CURRENT LET", 'red')
                    threeCode.add(self.visit(child).code)
        return threeCode
    # Visit a parse tree produced by YAPLParser#id.
    def visitId(self, ctx:YAPLParser.IdContext):
        threeCode = ThreeAddressCode()
        cprint(ctx.getText(),'blue')
        if ctx.getText() == 'self': #si es self
            threeCode.add(Quadruple('equal', 'self', None, 'self'))
            threeCode.addAddress('self')
            return threeCode
        
        else:
            #@TODO agregar el caso en 3add code cuando entre aca
            classScope = 'global.' + str(self.current_class)
            functionScope = 'global.' + str(self.current_class) + '.' + str(self.current_function)
            paramScope = 'local.' + str(self.current_class) + '.' + str(self.current_function)
            
            #Se busca en todos los let
            variable = None
            counter = self.current_let
            while counter >= 0 and variable == None:
                letScope = 'local.' + str(self.current_class) + '.' + str(self.current_function) + '.let' + str(counter)
                variable = self.symbol_table.getIdByScope(ctx.getText(), letScope)
                counter -= 1
            # generatedTemp = self.generate.getTemporal()
            if variable == None:
                variable = self.symbol_table.getIdByScope(ctx.getText(), paramScope)

                if variable == None:
                    variable = self.symbol_table.getIdByScope(ctx.getText(), functionScope)
                    if variable == None:
                        variable= self.symbol_table.getIdByScope(ctx.getText(), classScope)
           

            if variable == None:
                if ctx.getText() == self.current_function:
                    #print("IM HERE IN ID")
                    return self.current_function_type
                else:
                    self.errors_list.append(MyErrorVisitor(ctx, "Variable " + ctx.getText() + " not declared"))
                    self.visitChildren(ctx)
                    return ErrorType
            else:
                variableScope = variable.data['scope']
                if 'local' in variable.data['scope']:
                 scopeSplit = variable.data['scope'].split('.')
                 variableScope = 'global.' + scopeSplit[1]

                variableAddress = variableScope + '[' + str(variable.offset) + ']'
                threeCode.add(Quadruple('equal',variable.data['value'], None,  variableAddress))
                threeCode.addAddress(variableAddress)
                return  threeCode

    
    # Visit a parse tree produced by YAPLParser#if.
    def visitIf(self, ctx:YAPLParser.IfContext):
        threeCode = ThreeAddressCode()
        fatherTrueLabel, fatherFalseLabel = self.generate.getIfLabel(1)
        
            
        fatherNextLabel = self.generate.getNextLabel()
       
            
        
        ctx.trueLabel = fatherTrueLabel
        ctx.falseLabel = fatherFalseLabel
        ctx.nextLabel = fatherNextLabel
        
        
        compareExpression = self.visit(ctx.children[1])
        # if len(compareExpression.code) > 2:
        #     #get last 2
        #     threeCode.add(compareExpression.code)
        #     compareExpression.code = compareExpression.code[-2:]
        threeCode.add(compareExpression.code)
        threeCode.add(Quadruple('label', None, None, fatherTrueLabel))
        ctx.trueLabel = ''
        ctx.falseLabel = ''
        thenType = self.visit(ctx.children[3])
        threeCode.add(thenType.code)
        
        threeCode.add(Quadruple('goto', None, None, fatherNextLabel))
        threeCode.add(Quadruple('label', None, None, fatherFalseLabel))
        ctx.trueLabel = ''
        ctx.falseLabel = ''
        elseType = self.visit(ctx.children[5])
        threeCode.add(elseType.code)
        threeCode.add(Quadruple('label', None, None, fatherNextLabel))

        return threeCode

    # Visit a parse tree produced by YAPLParser#assign.
    def visitAssign(self, ctx:YAPLParser.AssignContext):

        idValue = ctx.children[0].getText()
        exprType = self.visit(ctx.children[2])
        print('TYPE CHILDREn', type(ctx.children[2]), exprType.address)
        variableOffset, variableScope = self.symbol_table.getVariableOffset(idValue, self.current_class, self.current_function)
        print('ID: ', idValue)
        print('HEEEEEEEEEEEERE', variableOffset, variableScope)

        if 'local' in variableScope:
            scopeSplit = variableScope.split('.')
            variableScope = 'global.' + scopeSplit[1]

        idAddress = variableScope + '[' + str(variableOffset) + ']'

        threeCode = ThreeAddressCode()
        threeCode.add(exprType.code)
        threeCode.add(Quadruple('equal', exprType.address, None, idAddress))
        
        for i in threeCode.code:
            print(i)

        if exprType.address[0] == 't' and exprType.address[1:].isnumeric():
            self.generate.makeTemporalAvailable(exprType.address)
        

        return threeCode

    # Visit a parse tree produced by YAPLParser#bigexpr.
    def visitBigexpr(self, ctx:YAPLParser.BigexprContext):
        print('im here bigexpr', ctx.getText())
        threeCode = ThreeAddressCode()
        #threeCode.addAddress(self.generate.getTemporal())
        #Evaluar si el padre tiene etiqueta (caso de if)
        try:
            trueLabel  = ctx.parentCtx.trueLabel
            falseLabel = ctx.parentCtx.falseLabel
        except:
            trueLabel = ''
            falseLabel = ''

        if trueLabel != '' and falseLabel != '':
             threeCode.add(Quadruple('big', ctx.getText(), None, trueLabel))
             threeCode.add(Quadruple('goto', None, None, falseLabel))
             return threeCode

        idIndex = 4 if ctx.children[1].getText() == '@' else 2
        if idIndex == 4:
            callerType = ctx.children[2].getText()
        else:
            firstExpr = ctx.children[0].getText()
            print('FIRST EXPR', firstExpr, type(firstExpr), type(ctx.children[0]))
            if isinstance(ctx.children[0], YAPLParser.StringContext):
                callerType = StringType
            elif isinstance(ctx.children[0], YAPLParser.IntContext) or isinstance(ctx.children[0], YAPLParser.PlusminusContext) or isinstance(ctx.children[0], YAPLParser.TimesdivContext):
                callerType = IntType
            elif isinstance(ctx.children[0], YAPLParser.TrueContext) or isinstance(ctx.children[0], YAPLParser.FalseContext) or isinstance(ctx.children[0], YAPLParser.CompareContext or isinstance(ctx.children[0], YAPLParser.IsvoidContext) or isinstance(ctx.children[0], YAPLParser.NotContext)):
                callerType = BoolType
            elif isinstance(ctx.children[0], YAPLParser.BigexprContext):
                localid = 4 if ctx.children[0].children[1] == '@' else 2
                b = self.visit(ctx.children[0])
                threeCode.add(b.code)
                callerType = self.symbol_table.getFunctionType(ctx.children[0].children[idIndex].getText())
            elif 'new' in firstExpr:
                callerType = self.getNewtype(firstExpr)
            elif 'isvoid' in firstExpr:
                callerType = BoolType

            # elif isinstance(ctx.children[0], YAPLParser.NewtypeContext):
            #     print('entering new', firstExpr)
            #     callerType = self.getNewtype(firstExpr)
            # elif isinstance(ctx.children[0], YAPLParser.ParenContext):
            #     print('entering paren', firstExpr)
            #     if 'new' in firstExpr:
            #      callerType = self.getNewtype(firstExpr)
            #     else:
            #         self.visit(ctx.children[1])
            
            else:
                classScope = 'global.' + str(self.current_class)
                functionScope = 'global.' + str(self.current_class) + '.' + str(self.current_function)
                paramScope = 'local.' + str(self.current_class) + '.' + str(self.current_function)
                #Se busca en todos los let
                variable = None
                counter = self.current_let
                while counter >= 0 and variable == None:
                    letScope = 'local.' + str(self.current_class) + '.' + str(self.current_function) + '.let' + str(counter)
                    variable = self.symbol_table.getIdByScope(firstExpr, letScope)
                    counter -= 1
                if variable == None:
                    print('searchign')
                    variable = self.symbol_table.getIdByScope(firstExpr, paramScope)
                    print(variable)
                    if variable == None:
                        variable = self.symbol_table.getIdByScope(firstExpr, functionScope)
                    if variable == None:
                        variable= self.symbol_table.getIdByScope(firstExpr, classScope)
                    
                callerType = variable.getCategory()

        cprint('CALLER TYPE' + callerType, 'red')
        cprint('CALLER' + ctx.children[idIndex].getText(), 'red')

        bigexprChildCount = int((len(ctx.children) - idIndex - 3) / 2 + 0.5)
        ## Add parameters
        for i in range(idIndex + 2, len(ctx.children) - 1, 2):
            element = self.visit(ctx.children[i])
            threeCode.add(element.code)
            threeCode.add(Quadruple('PARAMETER', None, None, element.address))
            if element.address[0] == 't' and element.address[1:].isnumeric():
                self.generate.makeTemporalAvailable(element.address)
        # Return ID type
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
        functionOffset, functionCategory = self.symbol_table.getSizeOffsetFunction(ctx.children[idIndex].getText(), callerType)
        functionCall = functionCategory + '[' + str(functionOffset) + ']'
        if existenceMethod == False:
            #print("IM HERE CALL BIG EXPR METHOD")
            if ctx.children[idIndex].getText() == self.current_function:
                
                return self.current_function_type
            if inFunctionTableExistence:
                # Function defined in non visited class/method
                bigExprType = self.function_table.getCategoryScope(ctx.children[idIndex].getText(), 'global.' + funcParentCheck)
                if bigExprType == None:
                    threeCode.add(Quadruple('CALL', str(bigexprChildCount), None, functionCall))
                    responseTemporal = self.generate.getTemporal()
                    threeCode.addAddress(responseTemporal)
                    threeCode.add(Quadruple('equal', 'R', None, responseTemporal))
                    return threeCode
                threeCode.add(Quadruple('CALL', str(bigexprChildCount), None, functionCall))
                responseTemporal = self.generate.getTemporal()
                threeCode.addAddress(responseTemporal)
                threeCode.add(Quadruple('equal', 'R', None, responseTemporal))
                return threeCode
            #TODO change this when class definition error is fixed
            #self.errors_list.append(MyErrorVisitor(ctx, "Type-Check: unkonwn method "+ctx.children[idIndex].getText()+" in dispatch on " + self.visit(ctx.children[idIndex])))
            self.errors_list.append(MyErrorVisitor(ctx, "Type-Check: unkonwn method "+ctx.children[idIndex].getText()+" in dispatch on " +self.current_class))
            #self.visitChildren(ctx)
            print('soy yo')
            return ErrorType
        else:
            bigExprType = self.symbol_table.getCategoryScope(ctx.children[idIndex].getText(), 'global.' + parentCheck)
            if bigExprType == None:
                threeCode.add(Quadruple('CALL', str(bigexprChildCount), None, functionCall))
                responseTemporal = self.generate.getTemporal()
                threeCode.addAddress(responseTemporal)
                threeCode.add(Quadruple('equal', 'R', None, responseTemporal))
                return threeCode
            threeCode.add(Quadruple('CALL', str(bigexprChildCount), None, functionCall))
            responseTemporal = self.generate.getTemporal()
            threeCode.addAddress(responseTemporal)
            threeCode.add(Quadruple('equal', 'R', None, responseTemporal))
            return threeCode
StringType = "String"
IntType = "Int"
BoolType = "Bool"
ObjectType = "Object"
IOType = "IO"
SELF_TYPE = "SELF_TYPE"
ErrorType = "Error"





class TableEntry():
    def __init__(self, category, type, width, offset, data):
        self.category = category
        self.type = type
        self.width = width
        self.offset = offset
        self.data = data # dictionary of data

    def getCategory(self):
        return self.category

class SymbolTable():
    def __init__(self):
        self.table = []

    def initialize(self):
        # Initialize the symbol table with the predefined functions
        self.table.append(TableEntry(SELF_TYPE,"function", 0,0, {"name":"out_string","parent": IOType, "params": [StringType], "attributeCount":1,"return_type": SELF_TYPE, "scope": "global.IO"}))
        self.table.append(TableEntry(SELF_TYPE,"function", 0,0, {"name":"out_int","parent": IOType, "params": [IntType], "attributeCount":1,"return_type": SELF_TYPE, "scope": "global.IO"}))
        self.table.append(TableEntry(StringType,"function", 0,0, {"name":"in_string","parent": IOType, "params": [], "return_type": StringType, "scope": "global.IO"}))
        self.table.append(TableEntry(IntType,"function", 0,0, {"name":"in_int","parent": IOType, "params": [], "return_type": IntType, "scope": "global.IO"}))
        self.table.append(TableEntry(IntType,"function", 0,0, {"name":"length","parent": StringType, "params": [], "return_type": IntType, "scope": "global.String"}))
        self.table.append(TableEntry(StringType,"function", 0,0, {"name":"concat","parent": StringType, "params": [StringType], "attributeCount":1,"return_type": StringType, "scope": "global.String"}))
        self.table.append(TableEntry(StringType,"function", 0,0, {"name":"substr","parent": StringType, "params": [IntType, IntType], "attributeCount":2,"return_type": StringType, "scope": "global.String"}))
        self.table.append(TableEntry(StringType,"function", 0,0, {"name":"type_name","parent": ObjectType, "params": [], "return_type": StringType, "scope": "global.Object"}))
        self.table.append(TableEntry(SELF_TYPE,"function", 0,0, {"name":"copy","parent": ObjectType, "params": [], "return_type": SELF_TYPE, "scope": "global.Object"}))
        self.table.append(TableEntry(SELF_TYPE,"function", 0,0, {"name":"abort","parent": ObjectType, "params": [], "return_type": ObjectType, "scope": "global.Object"}))

        #Add Object class
        self.table.append(TableEntry(ObjectType,"class", 0,0, {"parent": None}))
        #Add IO class
        self.table.append(TableEntry(IOType,"class", 0,0, {"parent": ObjectType}))
        #Add Int class
        self.table.append(TableEntry(IntType,"class", 4,0, {"parent": ObjectType}))
        #Add Bool class
        self.table.append(TableEntry(BoolType,"class", 1,0, {"parent": ObjectType}))
        #Add String class
        self.table.append(TableEntry(StringType,"class", 0,0, {"parent": ObjectType}))



    def add(self,category=None, type=None, width=None, offset=None, data=None):
        self.table.append(TableEntry(category, type, width, offset, data))

    def get(self, name):
        for entry in self.table:
            if entry.category == name:
                return entry
        return None
    
    def getVariable(self, name):
        for entry in self.table:
            if entry.type == "variable":
                if entry.data["name"] == name:
                    return entry
                
    def setVariableValue(self, name, value, scope):
        for entry in self.table:
            if entry.type == "variable":
                if entry.data["name"] == name and entry.data["scope"] == scope:
                    entry.data["value"] = value
                    return True
        return False

    def getNumberOfEntries(self,name):
        count = 0
        for entry in self.table:
            if entry.category == name and entry.type == "class":
                count += 1
        return count

    def getClassIndex(self,name):
        for index, entry in enumerate(self.table):
            if entry.category == name:
                return index
        return None
    def getMethodExistence(self,name,scope):
        count = 0
        for entry in self.table:
            if entry.type == "function":
                if entry.data["name"]==name and entry.data["scope"] == scope:
                    return True
        return False

    def getMethodParams(self,name,scope):
        for entry in self.table:
            if entry.type == "function":
                if entry.data["name"]==name and entry.data["scope"] == scope:
                    return entry.data["attributes"]
        return []

    def getClassParent(self, name):
        for entry in self.table:
            if entry.category == name and entry.type == 'class':
                return entry.data["parent"]

    def setScope(self, name, scope):
        for entry in self.table:
            if entry.type == 'function' or entry.type == 'variable':
                if entry.data["name"] == name:
                    entry.data["scope"] = scope
                    return

    def getCategory(self, name):
        for entry in self.table:
            if entry.type == 'function':
                if entry.data["name"] == name:
                    return entry.category
        return None
                
    def getCategoryScope(self, name, scope):
        for entry in self.table:
            if entry.type == 'function':
                if entry.data["name"] == name and entry.data["scope"] == scope:
                    return entry.category
        return None

    def getFunctionAttrCount(self, name, scope):
        for entry in self.table:
            if entry.type == 'function':
                if entry.data["name"] == name and entry.data["scope"] == scope:
                    return entry.data["attributeCount"]
    
    def getCallMethodExistence(self,name,  scope,current=None):
        for entry in self.table:
            if entry.type == "function":
                if entry.data["name"]==name and (entry.data["scope"] == scope or entry.data["scope"] == "global.IO") or name == current: 
                    return True
        return False
    
    def getVariableCategory(self, name, scope=None):
        for entry in self.table:
            if entry.type == "variable":
                if entry.data["name"] == name and entry.data["scope"] == scope:
                    return entry.category
                if entry.data["name"] == name and "let" in scope:
                    letIndex = scope.index("let") + 3
                    newScope = scope[0:letIndex]
                    if entry.data["scope"].startswith(newScope):
                        return entry.category
        return None

    def getFunctionByScope(self, name, scope):
        for entry in self.table:
            if entry.type == 'function':
                if entry.data["name"] == name and entry.data["scope"] == scope:
                    return entry
        return None

    def getIdByScope(self, name, scope):
        for entry in self.table:
            if entry.type == 'variable':
                if entry.data["name"] == name and entry.data["scope"] == scope:
                    return entry
        return None

    def classHasUnsized(self, className):
        for entry in self.table:
            if entry.type == 'function' or entry.type == 'variable':
                if entry.data["scope"].startswith('local.' + className) and entry.width == None:
                    return True
        return False

    def functionHasUnsized(self, functionName, className):
        initScope = 'local.' + className + '.' + functionName
        for entry in self.table:
            if entry.type == 'variable':
                if entry.data["scope"].startswith(initScope):
                    if entry.width == None:
                        return True
        return False

    def getFunctionSize(self, functionName, className):
        initScope = 'local.' + className + '.' + functionName
        size_acc = 0
        for entry in self.table:
            if entry.type == 'variable':
                if entry.data["scope"].startswith(initScope):
                    if entry.width == None:
                        return None
                    size_acc += entry.width
        return size_acc

    def getVariableSize(self, classType):
        for entry in self.table:
            if entry.type == 'class':
                if entry.category == classType:
                    return entry.width
        return None

    def getClassSize(self, className):
        size_acc = 0
        for entry in self.table:
            if entry.type == 'function' or entry.type == 'variable':
                if entry.data["scope"].startswith('global.' + className):
                    if entry.width == None:
                        return None
                    size_acc += entry.width
        return size_acc

    def getAllUnsized(self):
        unsized_elements = []
        for entry in self.table:
            if entry.width == None:
                unsized_elements.append(entry)
        return unsized_elements

    def setSize(self, originalEntry, size):
        for entry in self.table:
            if entry == originalEntry:
                entry.width = size
                return

    def setOffset(self, originalEntry, offset):
        for entry in self.table:
            if entry == originalEntry:
                entry.offset = offset
                return

    def reviewOffsets(self):
        classes = []
        # Get all defined classes
        for entry in self.table:
            if entry.type == 'class':
                if entry.category != ObjectType and entry.category != IOType and entry.category != IntType and entry.category != BoolType and entry.category != StringType:
                    classes.append(entry)
        # For each class, get variables and functions
        for tableClass in classes:
            global_offset = 0
            features = []
            for entry in self.table:
                if (entry.type == 'variable' or entry.type == 'function') and entry.data["scope"] == ('global.' + tableClass.category):
                    features.append(entry)
            
            for feat in features:
                self.setOffset(feat, global_offset)
                if feat.type == 'function':
                    function_vars = []
                    for entry in self.table:
                        if entry.type == 'variable' and entry.data["scope"].startswith('local.' + tableClass.category + '.' + feat.data["name"]):
                            function_vars.append(entry)
                    local_offset = global_offset
                    for local_var in function_vars:
                        self.setOffset(local_var, local_offset)
                        local_offset += local_var.width
                global_offset += feat.width

    def getAllFunctionsWithName(self, name):
        variables = []
        for entry in self.table:
            if entry.type == 'function':
                if entry.data["name"] == name:
                    variables.append(entry)
        return variables


    def set(self, name, value):
        self.table[name] = value

    def __str__(self):
        return str(self.table)
    
    def printTable(self):
        for entry in self.table:
            print("Category: " + str(entry.category))
            print("Type: " + str(entry.type))
            print("Width: " + str(entry.width))
            print("Offset: " + str(entry.offset))
            print("Data: " + str(entry.data))
            print("--------------------------------------------------\n")

        print()
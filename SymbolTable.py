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
        self.table.append(TableEntry(SELF_TYPE,"function", 0,0, {"name":"out_string","parent": IOType, "params": [StringType], "return_type": SELF_TYPE, "scope": "global.IO"}))
        self.table.append(TableEntry(SELF_TYPE,"function", 0,0, {"name":"out_int","parent": IOType, "params": [IntType], "return_type": SELF_TYPE, "scope": "global.IO"}))
        self.table.append(TableEntry(SELF_TYPE,"function", 0,0, {"name":"in_string","parent": IOType, "params": [], "return_type": StringType, "scope": "global.IO"}))
        self.table.append(TableEntry(SELF_TYPE,"function", 0,0, {"name":"in_int","parent": IOType, "params": [], "return_type": IntType, "scope": "global.IO"}))
        self.table.append(TableEntry(SELF_TYPE,"function", 0,0, {"name":"length","parent": StringType, "params": [], "return_type": IntType, "scope": "global.String"}))
        self.table.append(TableEntry(SELF_TYPE,"function", 0,0, {"name":"concat","parent": StringType, "params": [StringType], "return_type": StringType, "scope": "global.String"}))
        self.table.append(TableEntry(SELF_TYPE,"function", 0,0, {"name":"substr","parent": StringType, "params": [IntType, IntType], "return_type": StringType, "scope": "global.String"}))
        

        #Add Object class
        self.table.append(TableEntry(ObjectType,"class", 0,0, {"parent": None}))
        #Add IO class
        self.table.append(TableEntry(IOType,"class", 0,0, {"parent": ObjectType}))
        #Add Int class
        self.table.append(TableEntry(IntType,"class", 0,0, {"parent": ObjectType}))
        #Add Bool class
        self.table.append(TableEntry(BoolType,"class", 0,0, {"parent": ObjectType}))
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
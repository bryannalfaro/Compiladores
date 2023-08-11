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
        self.table.append(TableEntry("out_string",SELF_TYPE, 0,0, {"parent": IOType, "params": [StringType], "return_type": SELF_TYPE, "scope": "global"}))
        self.table.append(TableEntry("out_int",SELF_TYPE, 0,0, {"parent": IOType, "params": ["Int"], "return_type": SELF_TYPE, "scope": "global"}))
        self.table.append(TableEntry("in_string",StringType, 0,0, {"parent": IOType, "params": [], "return_type": StringType, "scope": "global"}))
        self.table.append(TableEntry("in_int",IntType, 0,0, {"parent": IOType, "params": [], "return_type": IntType, "scope": "global"}))
        self.table.append(TableEntry("length",IntType, 0,0, {"parent": StringType, "params": [], "return_type": IntType, "scope": "global"}))
        self.table.append(TableEntry("concat",StringType, 0,0, {"parent": StringType, "params": [StringType], "return_type": StringType, "scope": "global"}))
        self.table.append(TableEntry("substr",StringType, 0,0, {"parent": StringType, "params": [IntType, IntType], "return_type": StringType, "scope": "global"}))

        #Add Object class
        self.table.append(TableEntry(ObjectType,"class", 0,0, {"parent": "no_parent", "params": [], "return_type": ObjectType, "scope": "global"}))
        #Add IO class
        self.table.append(TableEntry(IOType,"class", 0,0, {"parent": ObjectType, "params": [], "return_type": IOType, "scope": "global"}))
        #Add Int class
        self.table.append(TableEntry(IntType,"class", 0,0, {"parent": ObjectType, "params": [], "return_type": IntType, "scope": "global"}))
        #Add Bool class
        self.table.append(TableEntry(BoolType,"class", 0,0, {"parent": ObjectType, "params": [], "return_type": BoolType, "scope": "global"}))
        #Add String class
        self.table.append(TableEntry(StringType,"class", 0,0, {"parent": ObjectType, "params": [], "return_type": StringType, "scope": "global"}))



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

    def getNumberOfEntries(self,name):
        count = 0
        for entry in self.table:
            if entry.category == name:
                count += 1
        return count


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
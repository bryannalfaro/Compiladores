class TableEntry():
    def __init__(self, category, type, width, offset, data):
        self.category = category
        self.type = type
        self.width = width
        self.offset = offset
        self.data = data # dictionary of data

    def __str__(self):
        return str(self.name) + " " + str(self.type) + " " + str(self.value)

class SymbolTable():
    def __init__(self):
        self.table = []

    def initialize(self):
        # Initialize the symbol table with the predefined functions
        self.table.append(TableEntry("out_string","SELF_TYPE", 0,0, {"parent": "IO", "params": ["String"], "return_type": "SELF_TYPE", "scope": "global"}))
        self.table.append(TableEntry("out_int","SELF_TYPE", 0,0, {"parent": "IO", "params": ["Int"], "return_type": "SELF_TYPE", "scope": "global"}))
        self.table.append(TableEntry("in_string","String", 0,0, {"parent": "IO", "params": [], "return_type": "String", "scope": "global"}))
        self.table.append(TableEntry("in_int","Int", 0,0, {"parent": "IO", "params": [], "return_type": "Int", "scope": "global"}))
        self.table.append(TableEntry("length","Int", 0,0, {"parent": "String", "params": [], "return_type": "Int", "scope": "global"}))
        self.table.append(TableEntry("concat","String", 0,0, {"parent": "String", "params": ["String"], "return_type": "String", "scope": "global"}))
        self.table.append(TableEntry("substr","String", 0,0, {"parent": "String", "params": ["Int", "Int"], "return_type": "String", "scope": "global"}))

        #Add Object class
        self.table.append(TableEntry("Object","class", 0,0, {"parent": "no_parent", "params": [], "return_type": "Object", "scope": "global"}))
        #Add IO class
        self.table.append(TableEntry("IO","class", 0,0, {"parent": "Object", "params": [], "return_type": "IO", "scope": "global"}))
        #Add Int class
        self.table.append(TableEntry("Int","class", 0,0, {"parent": "Object", "params": [], "return_type": "Int", "scope": "global"}))
        #Add Bool class
        self.table.append(TableEntry("Bool","class", 0,0, {"parent": "Object", "params": [], "return_type": "Bool", "scope": "global"}))
        #Add String class
        self.table.append(TableEntry("String","class", 0,0, {"parent": "Object", "params": [], "return_type": "String", "scope": "global"}))



    def add(self,category=None, type=None, width=None, offset=None, data=None):
        self.table.append(TableEntry(category, type, width, offset, data))

    def get(self, name):
        return self.table[name]

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
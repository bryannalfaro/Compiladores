from antlr4 import *
from ANTLR.HelloWorldLexer import HelloWorldLexer
from ANTLR.HelloWorldParser import HelloWorldParser
from ANTLR.HelloWorldVisitor import HelloWorldVisitor
from VisitorImpl import HelloWorld
import os
from antlr4.tree.Trees import Trees



def evaluate_expression(input_str):
    input_stream = InputStream(input_str)
    lexer = HelloWorldLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = HelloWorldParser(token_stream)
    tree = parser.start()

    print(Trees.toStringTree(tree, None, parser))

    #print tokens 
    for token in token_stream.tokens:
        print(token.text,token.line)
    
    #command to show tree
    command = f"antlr4-parse HelloWorld.g4 start -gui"
    process = os.popen(command, 'w')
    process.write(input_string)
    process.close()

    visitor = HelloWorld()
    return visitor.visit(tree)

# Example usage
input_string = "2 + (3 * 4)"
result = evaluate_expression(input_string)
print(result)  # Output: 14


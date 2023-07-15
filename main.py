from antlr4 import *
from CalculatorLexer import CalculatorLexer
from CalculatorParser import CalculatorParser
from CalculatorListenerImpl import CalculatorListener
from antlr4.tree.Trees import Trees
import os


def evaluate_expression(input_str):
    input_stream = InputStream(input_str)
    lexer = CalculatorLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = CalculatorParser(token_stream)
    tree = parser.start()

    print(Trees.toStringTree(tree, None, parser))

    #print tokens 
    for token in token_stream.tokens:
        print(token)
    
    #command to show tree
    command = f"antlr4-parse Calculator.g4 start -gui"
    process = os.popen(command, 'w')
    process.write(input_string)
    process.close()

    listener = CalculatorListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)

# Example usage
input_string = "2 + (3 * 4)"
evaluate_expression(input_string)

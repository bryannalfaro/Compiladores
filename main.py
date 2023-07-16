from antlr4 import *
from ANTLR.YAPLLexer import YAPLLexer
from ANTLR.YAPLParser import YAPLParser
from ANTLR.YAPLVisitor import YAPLVisitor
from VisitorImpl import YAPL
import os
from antlr4.tree.Trees import Trees
from ErrorListener import MyErrorListener
from termcolor import cprint



def evaluate_expression(input_str):
    input_stream = InputStream(input_str)
    lexer = YAPLLexer(input_stream)

    listener = MyErrorListener()

    #errors
    lexer.removeErrorListeners()
    lexer.addErrorListener(listener)
    token_stream = CommonTokenStream(lexer)


    token_stream.fill()  # Ensure all tokens are loaded
    for token in token_stream.getTokens(0, len(token_stream.tokens) - 1):
        if token.type == YAPLLexer.ERROR:
            cprint(f"Error token: {token.text} at line {token.line}, column {token.column}","red")
        else:
            cprint(f"Token {token.text} found on line {token.line}","green")  # Or perform any other desired action with the token

    parser = YAPLParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(listener)
    
    tree = parser.program()

    #print(Trees.toStringTree(tree, None, parser))

    visitor = YAPL()
    

    if len(listener.get_errors()) > 0:
        print('errors found')
        return None
    else:
      #command to show tree
      command = f"antlr4-parse YAPL.g4 program -gui"
      process = os.popen(command, 'w')
      process.write(input_string)
      process.close()
      return visitor.visit(tree)

    
    

# Example usage
input_string = FileStream(input('name file : ')).strdata
result = evaluate_expression(input_string)
print(result)  # Output: 14


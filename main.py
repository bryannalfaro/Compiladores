from antlr4 import *
from ANTLR.YAPLLexer import YAPLLexer
from ANTLR.YAPLParser import YAPLParser
from ANTLR.YAPLVisitor import YAPLVisitor
from VisitorImpl import YAPL
import os
from antlr4.tree.Trees import Trees



def evaluate_expression(input_str):
    input_stream = InputStream(input_str)
    lexer = YAPLLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = YAPLParser(token_stream)
    tree = parser.program()

    print(Trees.toStringTree(tree, None, parser))

    #print tokens 
    for token in token_stream.tokens:
        print(token.text,token.line)
    
    #command to show tree
    command = f"antlr4-parse YAPL.g4 program -gui"
    process = os.popen(command, 'w')
    process.write(input_string)
    process.close()

    visitor = YAPL()
    return visitor.visit(tree)

# Example usage
input_string = """
(* hello-world.cl *) 
class Main inherits IO { 
  a: Int <- 5;
  b: Int <- 6;
  c: Int <- 8;
  d: Int <- c * a - b;
    main() : Object { 
      out_int("HELLO WORLD   ")
    } ; 
} ; 
"""
result = evaluate_expression(input_string)
print(result)  # Output: 14


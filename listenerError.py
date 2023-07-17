from antlr4.error.ErrorListener import ErrorListener
from ANTLR.YAPLLexer import YAPLLexer
from antlr4 import *
from termcolor import cprint

class MyErrorVisitor(Exception):
    pass

class MyErrorListener(ErrorListener):

    def __init__(self):
        super().__init__()
        self.syntax_errors = []
    
    def get_errors(self):
        return self.syntax_errors
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        cprint(f"Syntax Error at line {line}, column {column}: {msg}", 'red')
        self.syntax_errors.append(f"Syntax Error at line {line}, column {column}: {msg}")

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        cprint(f"Ambiguity at line {startIndex}, column {stopIndex}", 'red')
        

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        cprint(f"Attempting full context at line {startIndex}, column {stopIndex}", 'red')
        

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        cprint(f"Context sensitivity at line {startIndex}, column {stopIndex}", 'red')
       
from ANTLR.YAPLLexer import YAPLLexer
from antlr4 import *
from termcolor import cprint
class CustomLexer(YAPLLexer):
    def emit(self, token=None):
        if token is None:
            token = super().emit()

        if token.type == YAPLLexer.STRING:
            # Modify the token type if the string length exceeds the limit
            if len(token.text) - 2 > 30:  # Excluding the surrounding double quotes
                token.type = YAPLLexer.ERROR
            string_text = token.text[1:-1]
            if ('\n' in string_text and string_text[-1] != '\\n') or (string_text[-1] == '\\n'):
                token.type = YAPLLexer.ERROR

        return token
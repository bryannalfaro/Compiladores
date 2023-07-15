grammar Calculator;

start: expression EOF;

expression: term (('+' | '-') term)* ;

term: factor (('*' | '/') factor)*;

factor: NUMBER | '(' expression ')';

NUMBER: [0-9]+ { print("hola") };
WS: [ \t\r\n]+ -> skip;
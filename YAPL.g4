grammar YAPL;

program: class_grammar ';' program;
class_grammar: CLASS TYPE (INHERITS TYPE)? '{' (feature ';')* '}';
feature: ID '(' (formal (',' formal)*)')' ':' TYPE '{' expr '}'
| ID ':' TYPE (ASSIGN_OP expr);
formal: ID ':' TYPE;
expr: ID ASSIGN_OP expr
| expr('@'TYPE)'.'ID '(' (expr (',' expr)*) ')'
| ID '(' (expr (',' expr)*) ')'
| IF expr THEN expr ELSE expr FI
| WHILE expr LOOP expr POOL
| '{' (expr ';')+ '}'
| LET ID ':' TYPE (ASSIGN_OP expr)? (',' ID ':' TYPE (ASSIGN_OP expr)?)* IN expr
| NEW TYPE
| ISVOID expr
| expr PLUS expr
| expr MINUS expr
| expr MULT expr
| expr DIV expr
| '~' expr
| expr LESS_THAN expr
| expr LESS_EQUAL expr
| expr EQUAL expr
| NOT expr
| '(' expr ')'
| ID
| INT
| STRING
| TRUE
| FALSE; 





//reserved keywords case insensitive
CLASS: [Cc][Ll][Aa][Ss][Ss];
INHERITS: [Ii][Nn][Hh][Ee][Rr][Ii][Tt][Ss];
ELSE: [Ee][Ll][Ss][Ee];
IF: [Ii][Ff];
THEN: [Tt ][Hh][Ee][Nn];
FI: [Ff][Ii];
LOOP: [Ll][Oo][Oo][Pp];
POOL: [Pp][Oo][Oo][Ll];
IN: [Ii][Nn];
ISVOID: [Ii][Ss][Vv][Oo][Ii][Dd];
WHILE: [Ww][Hh][Ii][Ll][Ee];
NEW: [Nn][Ee][Ww];
NOT: [Nn][Oo][Tt];
TRUE: 'true';
FALSE: 'false';
LET: [Ll][Ee][Tt];
STRING: '"'  .*?  '"' ;

//Other types
ASSIGN_OP: '<-';
ID: [a-z][_a-zA-Z0-9]*; //start with minuscule letter
TYPE: [A-Z][_a-zA-Z0-9]*; //start with mayus letter
INT: [0-9]+;
START_COMMENT: '(*';
END_COMMENT: '*)';
COMMENT: START_COMMENT .*? END_COMMENT -> skip;
WS: [ \t\r\n]+ -> skip;
PLUS: '+';
MINUS: '-';
MULT: '*';
DIV: '/';
EQUAL: '=';
LESS_THAN: '<';
LESS_EQUAL: '<=';




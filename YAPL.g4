grammar YAPL;

program: (class_grammar ';')+;
class_grammar: CLASS TYPE (INHERITS TYPE)? '{' (feature ';')* '}';
feature: ID '(' (formal (',' formal)*)?')' ':' TYPE '{' expr '}'
| ID ':' TYPE (ASSIGN_OP expr)?;
formal: ID ':' TYPE;
expr: ID ASSIGN_OP expr # assign
| expr('@'TYPE)?'.'ID '(' (expr (',' expr)*)? ')' # bigexpr
| ID '(' (expr (',' expr)*)? ')' # call
| IF expr THEN expr ELSE expr FI # if
| WHILE expr LOOP expr POOL # while
| '{' (expr ';')+ '}' # curly
| LET ID ':' TYPE (ASSIGN_OP expr)? (',' ID ':' TYPE (ASSIGN_OP expr)?)* IN expr # let
| NEW TYPE # newtype
| '~' expr # negation
| ISVOID expr # isvoid
| expr (MULT | DIV) expr # timesdiv
| expr (PLUS | MINUS) expr # plusminus
| expr (LESS_THAN | LESS_EQUAL | EQUAL) expr # compare
| NOT expr # not
| '(' expr ')' # paren
| ID # id
| INT # int
| STRING # string
| TRUE # true
| FALSE # false; 





//reserved keywords case insensitive
CLASS: [Cc][Ll][Aa][Ss][Ss];
INHERITS: [Ii][Nn][Hh][Ee][Rr][Ii][Tt][Ss];
ELSE: [Ee][Ll][Ss][Ee];
IF: [Ii][Ff];
THEN: [Tt][Hh][Ee][Nn];
FI: [Ff][Ii];
LOOP: [Ll][Oo][Oo][Pp];
POOL: [Pp][Oo][Oo][Ll];
IN: [Ii][Nn];
ISVOID: [Ii][Ss][Vv][Oo][Ii][Dd];
WHILE: [Ww][Hh][Ii][Ll][Ee];
NEW: [Nn][Ee][Ww];
NOT: [Nn][Oo][Tt];
LET: [Ll][Ee][Tt];
//reserved keywords case sensitive
TRUE: 'true';
FALSE: 'false';

STRING: '"'  .*?  '"' ;

//Other types
ASSIGN_OP: '<-';
ID: [a-z][_a-zA-Z0-9]*; //start with minuscule letter
TYPE: [A-Z][_a-zA-Z0-9]*; //start with mayus letter
INT: [0-9]+;
START_COMMENT: '(*';
END_COMMENT: '*)';
COMMENT: START_COMMENT .*? END_COMMENT -> skip;
LINE_COMMENT: '--' .*? '\n' -> skip;
WS: [ \t\r\n\f]+ -> skip;
PLUS: '+';
MINUS: '-';
MULT: '*';
DIV: '/';
EQUAL: '=';
LESS_THAN: '<';
LESS_EQUAL: '<=';
ERROR: . ; //cath errors




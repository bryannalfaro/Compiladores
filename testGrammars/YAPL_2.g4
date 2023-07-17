grammar YAPL;

program: (class_grammar ';')+;
class_grammar: CLASS TYPE (INHERITS TYPE)? '{' (feature ';')* '}';
feature: ID '(' (formal (',' formal)*)?')' ':' TYPE '{' expr '}'
       | ID ':' TYPE (ASSIGN_OP expr)?;
formal: ID ':' TYPE;
expr: assignment_expr # assignment
    | expr ('@' TYPE)? '.' ID '(' (expr (',' expr)*)? ')' #bigexpr
    | call_expr #call
    | if_expr #if
    | while_expr #while
    | block_expr #block
    | let_expr #let
    | new_expr #new
    | '~' expr # negation
    | isvoid_expr #isvoid
    | expr timesdiv_expr #timesdiv
    | expr plusminus_expr #plusminus
    | expr comparison_expr #comparison
    | not_expr #not
    | paren_expr #paren
    | ID # id
    | INT # int
    | STRING # string
    | TRUE # true
    | FALSE # false
    ;

assignment_expr: ID ASSIGN_OP expr;
call_expr: ID '(' (expr (',' expr)*)? ')';
if_expr: IF expr THEN expr ELSE expr FI;
while_expr: WHILE expr LOOP expr POOL;
block_expr: '{' (expr ';')+ '}';
let_expr: LET ID ':' TYPE (ASSIGN_OP expr)? (',' ID ':' TYPE (ASSIGN_OP expr)?)* IN expr;
new_expr: NEW TYPE;
isvoid_expr: ISVOID expr;
timesdiv_expr: (MULT | DIV) expr;
plusminus_expr: (PLUS | MINUS) expr;
comparison_expr: (LESS_THAN | LESS_EQUAL | EQUAL) expr;
not_expr: NOT expr;
paren_expr: '(' expr ')';





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




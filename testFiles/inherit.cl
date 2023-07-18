(* program of ThanhVu (Vu) Nguyen *)
class Foo inherits IO {

     h : Int <- 1;

     i : Object <- printh();

     printh() : Int { { out_int(h); 0; } };

     doh() : Int { (let i: Int <- h in { h <- h + 1; i; } ) };
};

(* scary . . . *)
class Main inherits IO {
  a : Foo <- new Foo;
  main(): String { { out_string("\n") ; "nada" ; } };

};
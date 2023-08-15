class Main { 
  a: Int <- 5;
  b: Int <- 4;

  main() : Object { 
    sum(a, 8)
  } ; 

  sum (a: Int, b: Int): Int {
    {
      let c: Int <- a*b in {
        out_string("c");
        c;
      };
      
      let d: Int <- a*b in {
        out_string("d");
        d;
      };
    }
  };
} ; 

class DB {
  a: Int;
};
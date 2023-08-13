class SuperInt inherits MegaInt {};

class MegaInt inherits SuperInt {};

class Main { 
  a: Int <- 5;
  b: Int <- 6;

    main() : Object { 
      out_int(a)
    } ; 
} ; 
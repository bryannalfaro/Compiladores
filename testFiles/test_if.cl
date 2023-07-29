class Main inherits IO { 
  a: Int <- 5;
  b: Int <- 6;

    main() : Object { 
      if false
      then out_int(b)
      else out_int(a)
      fi
    } ; 
} ; 
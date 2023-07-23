class Main inherits IO { 
  a: Int <- 5;
  b: Int <- 6;
  c: Int <- NOT 5;
  d: Int <- 5 + "4";
  e: Bool <- true + true;
  f: Bool <- true - false;
  g: Bool <- false * true;
  h: Bool <- false / false;
  i: Bool <- "Hi" < true;
  j: Bool <- 2 <= false;
  k: Bool <- 5 = "Bye";
    main() : Object { 
      out_int("HELLO")
    } ; 
} ; 
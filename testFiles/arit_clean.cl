class Main inherits IO { 
  a: Int <- 5;
  b: Int <- 6;
  c: Int <- 5 + 4;
  d: Int <- 5 - 4;
  e: Int <- 5 * 4;
  f: Int <- 5 / 4;
  g: Int <- d + c;
  (*g: Int <- 5 < 4;
  h: Bool <- true < false;
  i: Bool <- true <= false;
  j: Bool <- true = false;
  k: Bool <- not true;
  l: Bool <- ~ false;
  m: Bool <- "Hi" < "Hello";
  m: Bool <- "Hi" <= "Hello";
  n: Bool <- "Hi" = "Hello";*)

    main() : Object { 
      out_int("HELLO")
    } ; 
} ; 
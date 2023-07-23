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
  m: Bool <- "Hi" + "Hello";
  m: Bool <- "Hi" - "Hello";
  n: Bool <- "Hi" * "Hello";
  o: Bool <- "Hi" / "Hello";
  p: String <- not "Bye";
  q: String <- ~ "Goodbye";
    main() : Object { 
      out_int("HELLO")
    } ; 
} ; 
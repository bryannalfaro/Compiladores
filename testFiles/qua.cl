class Main inherits IO {
  out: Int <-2;
  
  testee : Int <- out;	-- testee is a number to be tested for primeness.   
  divisor : Int;	-- divisor is a number which may factor testee.
  stop : Int <- 500;	-- stop is an arbitrary value limiting testee. 	
  a: Int <- 0;

  main() : Object {	-- main() is an atrophied method so we can parse. 
     
     if testee < divisor * divisor 
            then false	
	  else if testee - divisor*(testee/divisor) = 0 
            then false	
            else true
          fi fi 
  };
};
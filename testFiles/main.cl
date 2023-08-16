class Main inherits Trial{ 

  a: Int <- 2;
  c: Int <- 5 + a*4;

  main(a:Int) : Object { 
      {
       if a=1 then c<-1 else c<-3 fi;
      }
    } ; 

} ; 

class Trial {
    
	sum(a:Int, b:Int, c:Int) : Int {
  		1+2
  	};
};
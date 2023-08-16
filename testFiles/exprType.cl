class Trial {
	sum(a:Int, b:Int, c:Int) : Int {
  		1+2
  	};
};

class Trial2 inherits Trial {
	sum(a:Int, b:Int, c:Int) : Int {
  		1+2
  	};
};

class Trial3 inherits Trial2 {
	sum(a:Int, b:Int, c:Int) : Int {
  		1+2
  	};
};

class Main{ 
  a: Int;
  b: Trial3;
  c: Int <- 5;
  d: Int <- 5;
  e: Trial;
  
  sum(a:Int, b:Int, c:Int) : Int {
  		1+2
  	};

    main() : Object { 
      {
       if c=1 then a<-sum(1,3,4) else e<-b fi;
      }
    } ; 

} ; 


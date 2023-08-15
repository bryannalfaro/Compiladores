class SuperInt inherits IO {
	sum(a: Int) : Int {
  		a
  	};
};

class GoodInt inherits SuperInt {
	sum(a: Int) : Int {
  		{
          a;
      	}
  	};
};

class BadAttrCount inherits SuperInt {
	sum(a: Int, b: Int) : Int {
  		b
  	};
};

class BadReturnType inherits SuperInt {
	sum(b: Int) : String {
  		b
  	};
};

class BadAttrType inherits SuperInt {
	sum(b: String) : Int {
  		b
  	};
};

class Main { 
  a: Int <- 5;
  b: Int <- 6;

    main() : Object { 
      out_int(a)
    } ; 
} ; 
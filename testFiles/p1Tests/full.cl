class Main inherits IO {
    a: Int;
    b: Int <- sum(); -- No error expected
    sumResult: Int <- sum(5); -- Wrong error returned

    main(): Object {
      out_string("Hello Worlld")
    };

    sum(a: Int): Int {
        5
    };

    c: String <- if "fail" then "fail" else "works" fi; -- Predicate error expected
    d: Object <- while "fail" loop "FAIL" pool; -- No variable type mismatch expected

    e: Int <- true + 2;
    f: Int <- false * 2;
    g: Int <- true / 2 + 12 - false;
    
    
    cu: UltraInt;
    ci: ChildInt;

    trial(): SuperInt {
  		if false
        then "fail"
        else cu
        fi
  	};

    trial2(): SuperInt {
      if true
      then cu
      else ci
      fi
    };
};

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

class MegaInt inherits SuperInt {};

class UltraInt inherits MegaInt{};

class ChildInt inherits SuperInt{};

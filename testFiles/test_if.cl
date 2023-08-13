class SuperInt {};

class MegaInt inherits SuperInt {};

class UltraInt inherits MegaInt{};

class ChildInt inherits SuperInt{};

class Main { 
  a: Int <- 5;
  b: Int <- 6;
  c: UltraInt;
  d: ChildInt;

    main() : Object { 
      trial()
    } ; 
  
  	trial(): SuperInt {
  		if false
        then c
        else d
        fi
  	};
} ; 
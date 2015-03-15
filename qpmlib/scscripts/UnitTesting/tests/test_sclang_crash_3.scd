{
	|test|
	~f = {|i|
		if (i == 0) {
			Exception("test").throw
		} {
			~f.(i-1)
		};
	};

	try {
		~f.(100000)
	} {

	};

	test.assert(true, "Didn't crash.");
}
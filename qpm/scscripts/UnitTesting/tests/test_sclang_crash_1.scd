{
	|test|
	x = { 1+1 }.def;
	x.instVarSize.do { |i|
		i.debug("index");
		x.instVarAt(i).postln
	};
	test.assert(true, "Didn't crash.");
}
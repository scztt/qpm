{
	|test|
	{ 1+1 }.def.instVarAt(1);
	test.assert(true, "Didn't crash.");
}
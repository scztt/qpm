{
	|test|
	b = { nil.deprecated };
	b.();
	test.assert(true, "Didn't crash.")
}
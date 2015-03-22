{
	|test|
	var result, x = \foo;
	result = switch(x,
		\foo, { 1 },
		\bar, { 2 },
		\foo, { 3 },
	);
	test.assertEquals(result, 1);
}
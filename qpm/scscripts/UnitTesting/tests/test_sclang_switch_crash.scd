{
	|test|
	var result, x = \foo;
	result = switch(x,
		\foo, { 1 },
		\bar, { 2 },
		\foo, { 1 },
	);
	test.assertEquals(result, 1);
}
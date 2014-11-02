UnitTest.findTestClasses;
JSON.stringify(
	UnitTestScript.allTestClasses.collect({
		|value, key|
		if (key != "...All...") {
			(value.keys.select(_ != " run all in this class").asArray.collect({
				|key|
				key.asString;
			}, List))
		} {
			nil;
		}
	})
);
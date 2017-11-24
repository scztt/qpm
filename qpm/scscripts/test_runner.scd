//~testRecord = "/Users/fsc/Desktop/tests.json";

~writeResult = {
	|results, path|
	var resultsString = JSON.stringify(results);
	var file = File(path, "w");
	try {
		"writing to file: %\n".postf(path);
		//results.postln;
		file.putString(resultsString);
	} {
		"Error writing to file: %".format(path).error;
	};
	file.close();
};

~testrun = {
	| file |
	var test_record, test_record_string;
	try {
		test_record_string = File(file, "r").readAllString();
	} { |err|
		Error("testrun: Could not read input file %: %".format(file, err.what)).throw;
	};

	try {
		var tests, skipped, settings, toExpand, toExclude, starStarTests;
		test_record = test_record_string.parseYAML();

		UnitTest.findTestClasses();

		if (test_record["tests"].isEmpty) {
			Error("No tests defined").throw;
		};

		starStarTests = test_record["tests"].select({
			|item|
			item["suite"] == "*"
		});
		test_record["tests"].removeAll(starStarTests);

		if (starStarTests.notEmpty) {
			var all = UnitTest.allTestClasses.keys.select({ |t| t != "...All..." }).asArray.collect({
				|classSym|
				Dictionary.newFrom(("suite": classSym.asSymbol.asClass.asString, "test": "*"))
			});
			test_record["tests"] = all ++ test_record["tests"]
		};

		test_record["tests"] = List.newFrom(test_record["tests"].collect(Dictionary.newFrom(_)));

		tests = test_record["tests"];
		settings = test_record["settings"];
		~tests = tests;

		// Expand *'s
		toExpand = tests.select({ |t| (t["test"] == "*") && (t["completed"] != true) });
		"Expanding %\n".postf(toExpand);
		toExpand.do {
			| wildcardTest |
			var allTests, newTest, class;

			class = wildcardTest["suite"].asSymbol.asClass;

			if (class.respondsTo(\findTestMethods).not && class.notNil) {
				class = ("Test" ++ class.name.asString).asSymbol.asClass;
			};

			if (class.isNil) {
				wildcardTest["error"] = "Class % not found".format(class);
				wildcardTest["completed"] = true;
				~writeResult.(test_record, file);
			} {
				class.tryPerform(\findTestMethods).do {
					| test |
					newTest = Dictionary.newFrom((
						"suite": class.name.asString,
						"test": test.name,
						"skip": wildcardTest["skip"],
						"skipReason": wildcardTest["skipReason"],
					));

					tests.add(newTest);
				};
				tests.remove(wildcardTest);
				~writeResult.(test_record, file);
			}
		};

		// Ensure excluded tests are not run
		toExclude = tests.select({
			|t|
			if (t["skip"].notNil) {
				t["skip"] = (t["skip"].asString.toLower == "true")
			};

			t["skip"] == true
		});

		"Excluding: %".format(toExclude.join(", ")).postln;
		tests = tests.reject({
			|t|
			(toExclude.detect({
				|excluded|
				(t["suite"].asString == excluded["suite"].asString)
				&& (t["test"].asString == excluded["test"].asString)
				&& (t !== excluded)
			}).size > 0)
		});
		test_record["tests"] = tests;
		~writeResult.(test_record, file);
		"After exclude: ".post;
		tests.do(_.postln);

		// Okay, time to run the tests
		tests.do {
			| test |
			var class, testname, script, result,
			oldFailures, oldPasses, newPasses, newFailures,
			startTime, endTime;
			"\tTest: %\n".postf(test["test"]);

			try {
				if (test["completed"].isNil) {
					if (test["skip"] == true) {
						test["completed"] = true;
						test["attemptsRemaining"] = nil;
						~writeResult.(test_record, file);
					} {
						test["completed"] = false;
						class = test["suite"].asSymbol.asClass;
						testname = test["test"].asSymbol;
						if (class.isNil) {
							test["error"] = "Class % not found".format(class);
							test["completed"] = true;
							~writeResult.(test_record, file);
						} {
							class.findTestMethods();

							script = class.findTestMethods().detect({ |m| m.name == testname });
							if (script.notNil) {
								// This is a bad way to get the results, but there's no other for now.
								// One this is working end-to-end, then UnitTest can be improved incrementally.
								oldPasses = IdentitySet.newFrom(class.passes);
								oldFailures = IdentitySet.newFrom(class.failures);

								// RUN THE TEST ///////////////
								~writeResult.(test_record, file);
								startTime = Date.localtime();

								result = class.new.runTestMethod(script);
								endTime = Date.localtime();
								test["completed"] = true;
								test["attemptsRemaining"] = nil;
								test["duration"] = endTime.rawSeconds - startTime.rawSeconds;
								///////////////////////////////

								newPasses = IdentitySet.newFrom(class.passes).difference(oldPasses);
								newFailures = IdentitySet.newFrom(class.failures).difference(oldFailures);
								test["results"] = List();
								newPasses.do {
									|pass|
									test["results"].add((
										"test": ("" ++ pass.message)[0..1000],
										"pass": true,
									))
								};
								newFailures.do {
									|fail|
									test["results"].add((
										"pass": false,
										"test": ("" ++ fail.message.split($\n)[0])[0..1000],
										"reason": (fail.message.split($\n)[1..])[0..1000]
									))
								};

								~writeResult.(test_record, file);
							} {
								test["error"] = "Test not found.";
								test["completed"] = true;
								~writeResult.(test_record, file);
							}
						}
					}
				}

			} {
				|err|
				err.reportError;
				test["error"] = err.errorString;
				~writeResult.(test_record, file);
			}
		}
	} {
		|err|
		err.reportError;
	}
};


{
	try {
		~testrun.(~testRecord);
	} { |err|
		err.what.error;
	};
	"******** DONE ********".postln;
	0.exit;
}.forkIfNeeded(AppClock);

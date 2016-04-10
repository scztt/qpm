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
	test_record_string = File(file, "r").readAllString();
	try {
		var tests, settings, toExpand;
		test_record = test_record_string.parseYAML();
		test_record["tests"] = List.newFrom(test_record["tests"].collect(Dictionary.newFrom(_)));
		tests = test_record["tests"];
		settings = test_record["settings"];
		~tests = tests;
		"Tests: %\n".postf(tests);

		UnitTest.findTestClasses();

		// Expand *'s
		toExpand = tests.select({ |t| (t["test"] == "*") && (t["completed"] != true) });
		toExpand.do {
			| wildcardTest |
			var allTests, newTest, class;
			class = wildcardTest["suite"].asSymbol.asClass;
			if (class.isNil) {
				wildcardTest["error"] = "Class % not found".format(class);
				wildcardTest["completed"] = true;
				~writeResult.(test_record, file);
			} {
				class.findTestMethods().postln.do {
					| test |
					newTest = Dictionary.newFrom((
						"suite": class.name.asString,
						"test": test.name
					));
					tests.add(newTest);
				};
				tests.remove(wildcardTest);
				~writeResult.(test_record, file);
			}
		};

		tests.do {
			| test |
			var class, testname, script, result,
			oldFailures, oldPasses, newPasses, newFailures,
			startTime, endTime;
			"\tTest: %\n".postf(test["test"]);

			try {
				if (test["completed"].isNil) {
					test["completed"] = false;
					~writeResult.(test_record, file);

					class = test["suite"].asSymbol.asClass;
					testname = test["test"].asSymbol;
					if (class.isNil) {
						test["error"] = "Class % not found".format(class);
						test["completed"] = true;
						~writeResult.(test_record, file);
					} {
						class.findTestMethods().postln;

						script = class.findTestMethods().detect({ |m| m.name.postln == testname.postln });
						if (script.notNil) {
							// This is a bad way to get the results, but there's no other for now.
							// One this is working end-to-end, then UnitTest can be improved incrementally.
							oldPasses = IdentitySet.newFrom(class.passes);
							oldFailures = IdentitySet.newFrom(class.failures);

							// RUN THE TEST ///////////////
							startTime = Date.localtime();

							result = class.new.runTestMethod(script);
							endTime = Date.localtime();
							test["completed"] = true;
							test["attemptsRemaining"] = nil;
							test["duration"] = endTime.rawSeconds - startTime.rawSeconds;
							~writeResult.(test_record, file);
							///////////////////////////////

							oldPasses.asArray.collect(_.identityHash).join(", ");
							IdentitySet.newFrom(class.passes).asArray.collect(_.identityHash).join(", ");

							oldFailures.asArray.collect(_.identityHash).join(", ");
							IdentitySet.newFrom(class.failures).asArray.collect(_.identityHash).join(", ");

							newPasses = IdentitySet.newFrom(class.passes).difference(oldPasses);
							newFailures = IdentitySet.newFrom(class.failures).difference(oldFailures);
							test["results"] = List();
							newPasses.do {
								|pass|
								test["results"].add((
									"test": "" ++ pass.message,
									"pass": true,
								))
							};
							newFailures.do {
								|fail|
								test["results"].add((
									"pass": false,
									"test": "" ++ fail.message.split($\n)[0],
									"reason": fail.message.split($\n)[1..]
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
			} {
				|err|
				err.reportError;
				test["error"] = err.errorString;
				~writeResult.(test_record, file);
			}
		}
	}
};

{
	~testrun.(~testRecord);
	"******** DONE ********".postln;
	0.exit;
}.forkIfNeeded(AppClock);

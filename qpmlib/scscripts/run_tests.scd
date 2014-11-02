UnitTest.findTestClasses;
~className = "%(test_class)s".asSymbol;
~testNames = [ "%(test_name)s" ];
~testNames = ~testNames.collect(_.asSymbol);
~class = ~className.asClass;
~script = ~class.findTestMethods.select({ |t| ~testNames.includes(t.name) });

~result = ();
~result[~className] = ();

if (~script.isEmpty.not) {
	~script.do(_.runScript());
    ~class.passes.do {
        |pass|
		pass.message.postln;
        ~result[~className][pass.testMethod.name] = (
            "completed": true,
            "passed": true,
            "reason": pass.message
        );
    };

    ~class.failures.do {
        |fail|
		fail.message.postln;
        ~result[~className][fail.testMethod.name] = (
            "completed": true,
            "passed": false,
            "reason": fail.message
        );
    };
} {
	~result = (
		"completed": false,
		"error": "Test not found."
	)
};

JSON.stringify(~result);

json
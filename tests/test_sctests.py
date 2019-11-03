__author__ = 'fsc'

from nose.tools import *
import qpm.sclang_testing as testing
from qpm.sclang_testing import SCTestRun

sclang_path = "/Users/fsc/Downloads/SuperCollider-5/SuperCollider.app/Contents/MacOS/sclang"

def test_list_tests():
	found = testing.find_tests(sclang_path)
	eq_(len(found), 23)

def test_run_tests():
	test_plan = {
		'tests': []
	}
	suite = 'TestUnitTest'
	tests = [
		'test_assert',
		'test_bootServer',
		'test_findTestMethods',
		'test_findTestedClass',
		'test_setUp',
		#'test_setUp2',
		#'test_toreDown',
		#'missing'
	]

	for test in tests:
		test_plan['tests'].append({
			'suite': suite,
			'test': test,
		})

	test_run = SCTestRun(sclang_path, test_plan)
	result = test_run.run()

	print result

	eq_(len(test_plan['tests']), len(result['tests']))
	for test in result['tests']:
		if test['test'] != 'missing':
			ok_(test['completed'])
			ok_(test.get('results'))
			ok_(len(test['results']) > 0)
			passed = True
			for subtest in test['results']:
				passed = passed and subtest['pass']
			ok_(passed)
			ok_(test['duration'] < 5.0)
		else:
			ok_(not(test['completed']))

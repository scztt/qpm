from cement.core import controller
import os.path
import qpm.sclang_process as process
import qpm.sclang_testing as testing

from base import *

class SCLang_Execute(SCLang_AbstractBase):
	class Meta:
		label = 'execute'
		description = 'Execute a command in sclang'
		arguments = [
			(['--timeout', '-t'], {
				'help': 'Execution timeout.',
				'action': 'store'
			}),
			(['code'], {
				'help': 'sclang code to interpret',
				'action': 'store',
				'nargs': '*'
			})
		]

	@controller.expose(help="Execute some code in sclang.", hide=True)
	def default(self):
		sclang = process.find_sclang_executable(self.app.pargs.path)
		code = self.app.pargs.code[0]

		output, error = process.do_execute(sclang, code, self.app.pargs.print_output)

		if output:
			self.app.render({ "result": output })
		else:
			self.app.render(error, 'error')


class SCLang_ListTests(SCLang_AbstractBase):
	class Meta:
		label = 'test.list'
		description = 'List unit tests available in sclang.'

	@controller.expose(help="List unit tests available in sclang.")
	def default(self):
		sclang = process.find_sclang_executable(self.app.pargs.path)
		try:
			result = testing.find_tests(sclang, self.app.pargs.print_output)
			self.app.render(result, 'test_list')
		except Exception, e:
			self.app.render(e, 'error')

class SCLang_RunTest(SCLang_AbstractBase):
	class Meta:
		label = 'test.run'
		description = 'Run a test.'
		arguments = [
			(['test'], {
				'help': 'test to run',
				'action': 'store',
				'nargs': '*'
			})
		]

	@controller.expose(help="Run a unit test. Specify one or multiple using the form 'Class:test', or 'Class:*' for all tests.")
	def default(self):
		sclang = process.find_sclang_executable(self.app.pargs.path)

		if sclang:
			test_plan = {
				'tests': []
			}

			for test_specifier in self.app.pargs.test:
				specifiers = test_specifier.split(':')
				test_suite = specifiers[0]
				if len(specifiers) > 1:
					test_name = specifiers[1]
				else:
					test_name = "*"

				test_plan['tests'].append({
					'suite': test_suite, 'test': test_name
				})

			try:
				test_run = testing.SCTestRun(sclang, test_plan, includes=self.app.pargs.include)
				test_run.print_stdout = self.app.pargs.print_output
				result = test_run.run()
				summary = generate_summary(result, test_run.duration)

				for test in result['tests']:
					self.app.render(test, 'test_result')
				self.app.render(summary, 'test_summary')

				if summary['failed_tests'] > 0:
					self.app.close(1)

			except Exception, e:
				self.app.render(e, 'error')

def generate_summary(test_plan, duration):
	total = 0
	failed = 0
	for test in test_plan.get('tests', []):
		if not(test.get('results')):
			if not(test.get('error')):
				test['results'] = [{'test': 'completed without error', 'pass': 'true'}]
			else:
				test['results'] = [{'test': 'completed without error', 'pass': 'false'}]

		for subtest in test.get('results', []):
			total += 1
			if not(subtest.get('pass')) or subtest.get('pass') == 'false':
				failed += 1

	return {
		'total_tests': total,
		'failed_tests': failed,
		'duration': duration
	}








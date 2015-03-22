from cement.core import foundation, controller, output, handler
import os.path
import numbers
import colorama
colorama.init()

class QPMBaseController(controller.CementBaseController):
	class Meta:
		label = 'base'
		description = 'Do things with SuperCollider'

		arguments = [
            (['-p', '--path'], dict(default=os.getcwd(), help='Path to supercollider installation or config.yaml')),
		]

class QPMApp(foundation.CementApp):
	class Meta:
		label = 'qpm'
		base_controller = QPMBaseController
		output_handler = 'qpmoutput'
		bootstrap = 'qpmcli.bootstrap'


# RENDERING
# @TODO - Should be moved to plugin (for sc specific) / separate file
def unescape(string):
	return string.replace('\\n', '  ').replace('\\t', '\t')

headingF = lambda s: (colorama.Style.BRIGHT + s + colorama.Style.RESET_ALL)
passF = lambda s: (colorama.Fore.GREEN + s + colorama.Fore.RESET)
failF = lambda s: (colorama.Fore.RED + s + colorama.Fore.RESET)

class QPMOutput(output.CementOutputHandler):
	class Meta:
		label = 'qpmoutput'

	def render(self, data, template):
		for key, val in data.iteritems():
			if key == 'test_result':
				self.render_test_result(val)
			elif key == 'test_summary':
				self.render_test_summary(val)
			else:
				print "%s: %s" % (key, val)

	def render_test_summary(self, summary):
		summary_str = '\n   '

		if summary['total_tests'] > 0:
			if summary['failed_tests'] == 0:
				summary_str += passF(' %s TESTS PASSED' % summary['total_tests'])
			else:
				summary_str += failF(' %s TESTS FAILED' % summary['failed_tests'])
				summary_str += (', out of %s' % summary['total_tests'])

			summary_str += (' (total duration: {0:.1f}s)'.format(summary['duration']))
		else:
			summary_str += failF("NO TESTS RUN")

		print summary_str

	def render_test_result(self, test_result):
		duration = test_result.get('duration', '-')
		if isinstance(duration, numbers.Number): duration = "{0:.1f}".format(duration)

		template = '%s '.rjust(7) + headingF('%s:%s (%ss)') % (test_result['suite'], test_result['test'], duration)
		completed = (test_result.get('completed') == True)
		if completed:
			if test_result.get('results'):
				total = len(test_result['results'])
				passing = len(filter(lambda p: p.get('pass', False), test_result['results']))
				format = passF if (total == passing) else failF
				print template % format('[%d/%d]' % (passing, total))
				for subtest in test_result.get('results', []):
					if subtest.get('pass', False):
						print passF('*'.rjust(12)) + ' %s' % unescape(subtest.get('test')).strip()
					else:
						print failF('!'.rjust(12)) + ' %s' % (unescape(subtest.get('test'))).strip()
						if subtest.get('reason'):
							print (' ' * 14) + '%s' % unescape(" ".join(subtest['reason']).strip())
			else:
				if test_result.get('error'):
					print template % failF('[!]  No results: ') + test_result.get('error')
				else:
					print template % passF('     (completed)')
		else:
			print template % failF('[!]  ') + test_result.get('error')
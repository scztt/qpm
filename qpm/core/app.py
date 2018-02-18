import os.path
import numbers
import json

from cement.core import foundation, controller, output, handler

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
		bootstrap = 'qpm.cli.bootstrap'
		exit_on_close = True


# RENDERING
# @TODO - Should be moved to plugin (for sc specific) / separate file
def unescape(string):
	return string.replace('\\n', '  ').replace('\\t', '\t')

headingF = lambda s: (colorama.Style.BRIGHT + s + colorama.Style.RESET_ALL)
passF = lambda s: (colorama.Fore.GREEN + s + colorama.Fore.RESET)
failF = lambda s: (colorama.Fore.RED + s + colorama.Fore.RESET)
skipF = lambda s: (colorama.Fore.YELLOW + s + colorama.Fore.RESET)
ind = lambda n: ' ' * n

class QPMOutput(output.CementOutputHandler):
	class Meta:
		label = 'qpmoutput'

	def render(self, data, template):
		template = 'default' if not(template) else template
		render_method = getattr(self, 'render_' + template)
		if render_method:
			render_method(data)
		return ""

	def render_default(self, data):
		print data

	def render_error(self, error):
		print failF("ERROR:\n" + str(error))

	def render_quark_list(self, quarks):
		print self.column_list(quarks, 3, 30)

	def render_quark_checkout(self, quarks):
		print '\nResult:'
		for name, result in quarks.iteritems():
			name = name.rjust(20)
			print '  %s ===> %s' % (name, result)
		print ''

	def render_test_list(self, tests):
		print self.column_list(tests, 2, 50)

	def column_list(self, list, columns=4, width=35, indent=''):
		groups = zip(*(iter(list),) * columns)
		str = ""
		for row in groups:
			str += indent
			for item in row:
				spaces = max(width - len(item), 1)
				str += item + (" " * spaces)
			str += "\n"
		return str

	def render_quark_versions(self, list):

		for name, versions in list.iteritems():
			name = name.rjust(20)
			print '%s:  %s' % (headingF(name), passF('  '.join(['HEAD'] + versions)))

	def render_test_summary(self, summary):
		summary_str = '\n   '

		if summary['total_tests'] > 0:
			if summary['failed_tests'] == 0:
				summary_str += passF(' %s TESTS PASSED' % summary['total_tests'])
			else:
				summary_str += failF(' %s TESTS FAILED' % summary['failed_tests'])
				if summary['skipped_tests'] > 0:
					summary_str += ', ' + skipF('%s skipped' % summary['skipped_tests'])
				summary_str += (', out of %s' % summary['total_tests'])

			summary_str += (' (total duration: {0:.1f}s)'.format(int(summary.get('duration', 0))))
		else:
			summary_str += failF("NO TESTS RUN")

		print summary_str
		if summary['failed_tests'] > 0:
			print 'Search for ? or ! to find failed tests.'

	def render_quark_info(self, summary):
		for quark_name in summary:
			print headingF(quark_name)
			for version in sorted(summary[quark_name].keys()):
				if version == 'HEAD' and summary[quark_name][version].get('version'):
					print '    %s (v%s)' %(version, summary[quark_name][version]['version'])
				else:
					print '    ' + version

				for key, val in summary[quark_name][version].iteritems():
					if key == 'error':
						print (' ' * 4) + (failF('(%s)' % val.decode('utf-8', 'ignore'))).ljust(6)
					else:
						if not isinstance(val, basestring): val = ", ".join(val)
						print (' ' * 4) + ('%s: ' % key).rjust(15) + val

	def render_test_result(self, test_result):
		duration = float(test_result.get('duration', 0))
		if isinstance(duration, numbers.Number): duration = "{0:.1f}".format(duration)

		template = '%s '.rjust(7) + headingF('%s:%s (%ss)') % (test_result['suite'], test_result['test'], duration)
		completed = (test_result.get('completed') == True)
		if completed:
			if test_result.get('skip'):
				print template % skipF('[-]  ') + (' Skipped (reason: %s)' % test_result.get('skipReason')).rjust(12)
			elif test_result.get('results'):
				total = len(test_result['results'])
				passing = len(filter(lambda p: p.get('pass', False), test_result['results']))

				format = passF if (total == passing and not test_result.get('error')) else failF
				print template % format('[%d/%d]' % (passing, total))

				if test_result.get('error'):
					total += 1
					print failF('!'.rjust(12)) + ' %s' % ('Encountered error: %s' % test_result.get('error')).strip()

				for subtest in test_result.get('results', []):
					if subtest.get('pass', False):
						print passF('*'.rjust(12)) + ' %s' % unescape(subtest.get('test')).strip()
					else:
						print failF('!'.rjust(12)) + ' %s' % (unescape(subtest.get('test'))).strip()
						if subtest.get('reason'):
							print (' ' * 14) + '%s' % unescape(" ".join(subtest['reason']).strip())
			else:
				if test_result.get('error'):
					print template % failF('[!]') +  ' (No results found)'
					print failF('!'.rjust(12)) + ' %s' % ('Error: "%s"' % test_result.get('error')).strip()
				else:
					print template % passF('     (completed)')
		else:
			print template % failF('[!]') + ' (Did not complete.)'
			print failF('!'.rjust(12)) + ' %s' % ('Error: "%s"' % test_result.get('error')).strip()

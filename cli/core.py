from cement.core import backend, foundation, controller, handler, output
import os.path
import qpmlib.sclang_process as process

class QPMTestBaseController(controller.CementBaseController):
	class Meta:
		label = 'base'
		description = 'manage supercollider unit and functional tests'

		arguments = [
            (['-p', '--path'], dict(default=os.getcwd(), help='Path to supercollider installation or config.yaml')),
		]

	@controller.expose(help="List available tests.")
	def list(self):
		self.app.log.info("PATH=%s" % self.app.pargs.path)

	@controller.expose(help="Execute command in SuperCollider and get result.")
	def launch_test(self):
		test_result = {
			"complete": False,
			"pass": False
		}

		sclang = process.find_sclang_executable(self.app.pargs.path)
		if not(sclang) or not(os.path.exists(sclang)):
			raise Exception("No sclang binary found in path %s" % self.app.pargs.path)

		self.app.render({ "message": "Launching sclang at %s" % sclang })
		proc = process.ScLangProcess(sclang)

		if not(proc.launch()):
			raise Exception("SuperCollider failed to launch.\nOutput: %s\nError: %s" % (proc.output, proc.error))

		proc.execute('    "Hello world".postln;    ')
		output = proc.wait_for("Hello world")
		test_result["complete"] = True

		if not(output):
			raise Exception("Hello world not properly executed.\nOutput: %s" % proc.output)
		else:
			self.app.render({ "message": "Launched successfully" })
			test_result["pass"] = True

		self.app.render({ "test_result": test_result })


class QPMApp(foundation.CementApp):
	class Meta:
		label = 'qpm'
		base_controller = QPMTestBaseController
		output_handler = 'qpmoutput'

class QPMOutput(output.CementOutputHandler):
	class Meta:
		label = 'qpmoutput'

	def render(self, data, template):
		for key, val in data.iteritems():
			print "%s: %s" % (key, val)

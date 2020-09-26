import sys
import os.path
import subprocess
import time
import tempfile
import yaml
import json
import re
import datetime
from qpm.cli.main import global_app
import appdirs

from qpm.set_non_block import set_fd_non_block

SC_OUTPUT_PATTERN = "\x1B{10}(.*?)\x1B{10}"
SC_LAUNCHED_STRING = r"Welcome to SuperCollider"
SCLANG_NAME = "sclang" if sys.platform != "win32" else "sclang.exe"
CLASSLIB_NAME = "SCClassLibrary"

def find_sclang_executable(root):
	result = False
	if os.path.split(root)[1] == SCLANG_NAME:
		result = root
	else:
		for dirpath, dirnames, filenames in os.walk(root):
			if SCLANG_NAME in filenames:
				result = os.path.join(dirpath, SCLANG_NAME)

	return result

def find_classlibrary(root):
	result = False
	if os.path.split(root)[1] == CLASSLIB_NAME:
		result = root
	else:
		for dirpath, dirnames, filenames in os.walk(root):
			if CLASSLIB_NAME in dirnames:
				result = os.path.join(dirpath, CLASSLIB_NAME)

	return result

def load_script(name):
	script_path = os.path.join(os.path.split(__file__)[0], 'scscripts', name + '.scd')
	with open(script_path, 'r') as f:
		script = f.read()
		return script

def do_execute(sclang_path, code, includes=[], excludes=[], print_output=False):
	if not(sclang_path) or not(os.path.exists(sclang_path)):
		raise Exception("No sclang binary found in path %s" % sclang_path)

	#app.render({ "message": "Launching sclang at %s" % sclang_path })
	proc = ScLangProcess(sclang_path, print_output=print_output)
	for i in includes: proc.include(i)
	for e in excludes: proc.exclude(e)
	if not(proc.launch()):
		raise Exception("SuperCollider failed to launch.\nOutput: %s\nError: %s" % (proc.output, proc.error))

	begin_token = "********EXECUTE********"
	end_token = "********/EXECUTE********"

	exec_string = '{ var result; result = {%s}.value(); "%s".postln; result.postln; "%s".postln; }.fork(AppClock);' % (code, begin_token, end_token)

	line_end = "\n" if sys.platform != 'win32' else "\r\n"
	regex_string = '%s%s(.*)%s%s' % (re.escape(begin_token), line_end, line_end,
									re.escape(end_token))

	proc.execute(exec_string)
	output, error = proc.wait_for(regex_string)

	if output:
		return output.group(1), error
	else:
		print error
		return "", error

def set_non_block(output):
	fd = output.fileno()
	set_fd_non_block(fd)

def safe_read(output):
	fd = output.fileno()
	set_fd_non_block(fd)
	try:
		return output.read()
	except Exception, e:
		time.sleep(0.2)
		return ""

# @TODO - This is not the best way to find the extensions folder, but it works for unit testing for now
def user_extensions():
	return os.path.join(appdirs.user_data_dir('SuperCollider'), 'Extensions')

def system_extensions():
	return os.path.join(appdirs.site_data_dir('SuperCollider'), 'Extensions')


class ScLangProcess:
	def __init__(self, path, classlib=None, headless=True, print_output=False):
		assert(os.path.exists(path))
		self.print_output = print_output
		self.path = path
		self.launched = False
		self.ready = False
		self.headless = headless
		self.proc = None
		self.start_time = None
		self.buffer = ""
		self.output = ""
		self.error = ""
		self.includes = set()
		self.excludes = set()
		self.classlib = classlib if (classlib != None) else find_classlibrary(os.path.dirname(os.path.dirname(path)))
		if not(self.classlib):
			raise Exception("Could not find classlib.")
		else:
			self.includes.add(self.classlib)

	def include(self, path):
		self.includes.add(path)

	def exclude(self, path):
		self.excludes.add(path)

	def exclude_extensions(self):
		self.exclude(user_extensions())
		self.exclude(system_extensions())

	def create_sclang_conf(self):
		conf = {
			"includePaths": list(self.includes),
			"excludePaths": list(self.excludes)
		}
		conf_string = yaml.dump(conf)
		fd, self.sclang_conf_path = tempfile.mkstemp('.yaml', 'sclang_conf')
		with open(self.sclang_conf_path, 'w') as f:
			f.write(conf_string)

	def launch(self):
		if not(self.launched):
			env = dict(os.environ)

			if sys.platform == 'linux2' and self.headless:
				global_app.log.debug('Initializing offscreen display.')
				env['QT_PLATFORM_PLUGIN'] = 'offscreen'
				env['DISPLAY'] = ':99.0'
				subprocess.Popen('sh -e /etc/init.d/xvfb start', shell=True, env=env)
				subprocess.Popen("/sbin/start-stop-daemon --start --quiet --pidfile /tmp/custom_xvfb_99.pid --make-pidfile --background --exec /usr/bin/Xvfb -- :99 -ac -screen 0 1280x1024x16", shell=True, env=env)

			cmd = [self.path, '-i' 'python', '-a']
			if self.includes or self.excludes:
				self.create_sclang_conf()
				cmd = cmd + ['-l', '%s' % self.sclang_conf_path]

			if self.print_output:
				#app.render({ "message": "Running: %s" % ' '.join(cmd) })
				print "Running: %s" % ' '.join(cmd)

			global_app.log.debug('Launching with command: %s' % (' '.join(cmd)))
			self.proc = subprocess.Popen(cmd,
				stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
				env=env, close_fds=sys.platform!='win32')
			global_app.log.debug('Launch result: %s' % self.proc)

			self.start_time = time.time()
			self.launched = True

		if not(self.ready):
			output, error = self.wait_for(SC_LAUNCHED_STRING, 3 * 60)
			if not(error):
				self.ready = True
				return True
			else:
				self.error = error
				return False
		else:
			return self.ready

	def wait_for(self, regex, timeout=30, kill_on_error=True, filter_allowed_errors=True):
		output = ""
		error = ""
		start_time = time.time()
		re_match = None

		# Set of errors which can be safely ignored. On macOS, running sclang on Travis and from within a
		# bundle sometimes produces spurious warnings and errors. These can be safely ignored, as they will
		# not affect standard usage.
		allowed_error_regexes = [
			'The available OpenGL surface format was either not version 3.2 or higher or not a Core Profile.',
			'Chromium on macOS will fall back to software rendering in this case.',
			'Hardware acceleration and features such as WebGL will not be available.',
			r'\[\d*/\d*\.\d*:WARNING:resource_bundle_qt.cpp\(\d*\)\] locale_file_path.empty\(\) for locale',
			]

		set_non_block(self.proc.stdin)
		set_non_block(self.proc.stdout)

		global_app.log.debug('Beginning wait for: %s' % regex)

		while self.running() and not(re_match) and time.time() < (start_time + timeout):
			read = safe_read(self.proc.stdout)
			if self.print_output and read: print read
			output += read
			error += safe_read(self.proc.stderr)
			re_match = re.search(regex, output, re.DOTALL)

			if filter_allowed_errors:
				for allowed_error_regex in allowed_error_regexes:
					prev_error = error
					error = re.sub(allowed_error_regex, '', error)
					if error != prev_error:
						global_app.log.debug('Filtered stderr using regex \'%s\'' % allowed_error_regex)
				error = error.strip()

			if error and kill_on_error:
				global_app.log.debug('Killing because of error')
				self.kill()
				break

			time.sleep(0.5)

		self.output += output
		self.error += error

		if (error):
			global_app.log.debug('Wait resulted in error: %s' % error)
			return (None, error)
		else:
			global_app.log.debug('Wait result: %s' % re_match)
			return (re_match, None)

	def running(self):
		if self.proc:
			return (self.proc.returncode == None)
		else:
			return False

	def kill(self):
		if self.launched:
			tries = 3
			self.return_code = None
			while tries and self.return_code == None:
				tries -= 1
				self.proc.kill()
				time.sleep(0.1)
				self.return_code = self.proc.returncode
			self.launched = False

	def execute(self, command):
		global_app.log.debug('Executing in sclang: %s' % command)
		if not(self.launched):
			global_app.log.debug('sclang was not launched.')
			global_app.log.debug('output:\n%s' % self.output)
			global_app.log.debug('error:\n%s' % self.error)
			raise Exception("Process not running")
		if not(self.ready):
			global_app.log.debug('sclang launched but not ready.')
			global_app.log.debug('output:\n%s' % self.output)
			global_app.log.debug('error:\n%s' % self.error)
			raise Exception("Process not ready - may not have launched correctly")
		self.proc.stdin.write("%s %s" % (command, chr(0x1b)))



def runFile(sclang_path, file_path, timeout=30):
	os.path.abspath(os.path.expanduser(sclang_path))
	os.path.abspath(os.path.expanduser(file_path))

	proc = subprocess.Popen([sclang_path, file_path], stdout=subprocess.PIPE)
	start_time = time.time()

	buffer = ""
	while (time.time() - start_time) < timeout:
		buffer += proc.stdout.read()
		if proc.poll() == None:
			time.sleep(0.1)
		else:
			break
	resultStrings = re.findall(SC_OUTPUT_PATTERN, buffer, re.DOTALL)
	results = []
	for str in resultStrings:
		try:
			results.append(json.loads(str))
		except Exception, e:
			results.append(e)
	return results

def convert_quark_infos(sclang_path, quark_infos):
	infos_string = json.dumps(quark_infos)

	date = datetime.date.today()
	fd, infos_file = tempfile.mkstemp('.json', 'quark_infos' + "_".join([str(date.day), str(date.month), str(date.year)]))
	with file(infos_file, 'w') as f: f.write(infos_string)

	sc_script = r'''
		~result = ();
		~special_conversions = (
			\isCompatible: {
				| val |
				if (val.isKindOf(Function)) {
					var verString = ">=";
					var verArray = [3, 0, 0];
					var src = val.def.sourceCode;

					var atMost, atLeast, foundVersion;
					atLeast = src.findRegexp("Main.versionAtLeast\\(([\\s\\d]+),?([\\s\\d]+)?\\)");
					atMost = src.findRegexp("Main.versionAtMost\\(([\\s\\d]+),?([\\s\\d]+)?\\)");
					if (atLeast.size() > 1) {
						foundVersion = atLeast;
						verString = ">=";
					};
					if (atMost.size() > 1) {
						foundVersion = atMost;
						verString = "<=";
					};

					if (foundVersion.notNil) {
						verArray[0] = foundVersion[1][1].asInteger;
						if (foundVersion.size() > 2) {
							verArray[1] = foundVersion[2][1].asInteger;
						};
					};
					verString = verString ++ (verArray.join("."));
				} {
					val.asString();
				}
			}
		);
		~quark_infos = "%s".parseYAMLFile;
		~quark_infos.postln;
		~quark_infos.keysValuesDo {
			|quark, infos|
			~result[quark] = ();
			infos.keysValuesDo {
				|version, string|
				try {
					~result[quark][version] = string.interpret;
					~result[quark][version].keysValuesDo {
						|key, val|
						if (~special_conversions[key].notNil) {
							~result[quark][version][key] = ~special_conversions[key].value(val);
						} {
							~result[quark][version][key] = val.asString;
						}
					}
				} {
					|e|
					~result[quark][version] = ("error": e.errorString );
				}
			}
		};
		JSON.stringify(~result);
	''' % (infos_file)

	result_string = do_execute(sclang_path, sc_script, True)[0]
	print type(result_string)
	result_string = result_string.decode('utf8')
	print result_string
	result = json.loads(result_string)

	return result

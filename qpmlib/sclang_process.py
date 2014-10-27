import sys
import fcntl
import os.path
import subprocess
import time
import re
import json
import re

SC_OUTPUT_PATTERN = "\x1B{10}(.*?)\x1B{10}"
SC_LAUNCHED_STRING = r"Welcome to SuperCollider"
SCLANG_NAME = "sclang"

def find_sclang_executable(root):
	result = False
	if os.path.split(root)[1] == SCLANG_NAME:
		result = root
	else:
		for dirpath, dirnames, filenames in os.walk(root):
			if SCLANG_NAME in filenames:
				result = os.path.join(dirpath, "sclang")

	return result


def non_block_read(output):
	fd = output.fileno()
	fl = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
	try:
		return output.readline()
	except:
		return ""


class ScLangProcess:
	def __init__(self, path, headless=False):
		assert(os.path.exists(path))
		self.path = path
		self.launched = False
		self.ready = False
		self.headless = headless
		self.proc = None
		self.start_time = None
		self.buffer = ""
		self.output = ""
		self.error = ""

	def launch(self):
		if not(self.launched):
			env = dict(os.environ)

			if sys.platform == 'linux2' and self.headless:
				env['QT_PLATFORM_PLUGIN'] = 'offscreen'
				env['DISPLAY'] = ':99.0'
				subprocess.Popen('sh -e /etc/init.d/xvfb start', shell=True, env=env)
				subprocess.Popen("/sbin/start-stop-daemon --start --quiet --pidfile /tmp/custom_xvfb_99.pid --make-pidfile --background --exec /usr/bin/Xvfb -- :99 -ac -screen 0 1280x1024x16", shell=True, env=env)

			self.proc = subprocess.Popen([self.path, '-i' 'python'],
				stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
				env=env)

			self.start_time = time.time()
			self.launched = True

		if not(self.ready):
			if self.wait_for(SC_LAUNCHED_STRING, 3 * 60) != False:
				self.ready = True
				return True
			else:
				return False

	def wait_for(self, regex, timeout=30):
		output = ""
		error = ""
		start_time = time.time()
		re_match = None

		while not(re_match) and time.time() < (start_time + timeout):
			output += non_block_read(self.proc.stdout)
			error += non_block_read(self.proc.stderr)
			re_match = re.search(regex, output)

			if error:
				self.kill()
				break
			elif output:
				pass
				#print "\t\t" + output

			time.sleep(0.1)

		self.output += output
		self.error += error

		if (error):
			return False
		else:
			return re_match

	def kill(self):
		if self.launched:
			tries = 3
			self.return_code = None
			while tries or self.return_code == None:
				self.proc.kill()
				time.sleep(0.1)
				self.return_code = self.proc.returncode
			self.launched = False

	def execute(self, command):
		if not(self.launched): raise Exception("Process not running")
		if not(self.ready): raise Exception("Process not ready - may not have launched correctly")
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


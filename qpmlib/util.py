def is_mac():
	return True

def is_win():
	return False

def is_lin():
	return False

def safe_name(package_name):
	return package_name

def git_is_installed():
	import git
	version = git.cmd.Git("/").version()
	if version:
		return True

def init_git(interactive=False):
	import git
	r = git.Repo()
	config = r.config_writer('global')
	name = config.get('user', 'name')
	email = config.get('user', 'email')
	return

def ask(question, validator=None):
	result = None
	while not(result):
		result = raw_input(question + '\n')
		if validator:
			result = validator(result)
	return result


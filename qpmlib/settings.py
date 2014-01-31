import json, os.path, sys

settings_loaded = False
gitignore_loaded = False
defaults = {}
user_settings = {}
settings = {}

def load_settings():
	global settings_loaded, settings, defaults
	if not(settings_loaded):
		settings_loaded = True
		options_file = os.path.expanduser('~/.qpm')

		if os.path.exists(options_file):
			with open(options_file, 'r') as f:
				try:
					settings = json.loads(f.read())
					defaults = settings.get('defaults', {})
				except Exception:
					print 'Failed to load ~/.qpm'

def save_settings():
	global settings
	options_file = os.path.expanduser('~/.qpm')
	with open(options_file, 'w') as f:
		f.write(json.dumps(settings, indent=4))

def get(*args):
	global settings
	settings_dict = settings
	for arg in args[:-1]:
		if settings_dict.has_key(arg):
			settings_dict = settings_dict[arg]
		else:
			return None

	if settings_dict.has_key(args[-1]):
		return settings_dict[args[-1]]
	else:
		return None

def set(*args):
	global settings
	settings_dict = settings
	value = args[-1]
	args = args[:-1]

	for arg in args[:-1]:
		if settings_dict.has_key(arg):
			settings_dict = settings_dict[arg]
		else:
			settings_dict[arg] = dict()
			settings_dict = settings_dict[arg]

	settings_dict[args[-1]] = value
	save_settings()

def get_qpm_data_dir():
	app_name = 'qpm'
	if sys.platform == 'darwin':
		from AppKit import NSSearchPathForDirectoriesInDomains
		# http://developer.apple.com/DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous/Foundation_Functions/Reference/reference.html#//apple_ref/c/func/NSSearchPathForDirectoriesInDomains
		# NSApplicationSupportDirectory = 14
		# NSUserDomainMask = 1
		# True for expanding the tilde into a fully qualified path
		appdata = os.path.expanduser(os.path.join('~', 'Library', 'Application Support', 'SuperCollider', app_name))
	elif sys.platform == 'win32':
		appdata = os.path.join(os.environ['APPDATA'], 'SuperCollider', app_name)
	else:
		appdata = os.path.expanduser(os.path.join("~", "." + app_name))

def get_quark_map_file():
	path = os.path.join(get_app_data_dir(), 'quarks.map')
	return path

def load_user_defaults(keys, options_dict={}, defaults_dict={}):
	global defaults

	overrides_root = defaults
	final_dict = dict(defaults_dict)

	for key in keys:
		if overrides_root.has_key(key):
			overrides_root = overrides_root[key]
		else:
			overrides_root = None
			break
	
	if overrides_root:
		dict_add_recursive(overrides_root, final_dict)

	dict_add_recursive(options_dict, final_dict)

	return final_dict

def dict_add_recursive(source, target):
	for key in source:
		if source[key].__class__ == dict:
			if not(target.has_key(key)): target[key] = dict()
			dict_add_recursive(source[key], target[key])
		else:
			target[key] = source[key]
	return target

def user_gitignore():
	global gitignore_loaded
	if not(gitignore_loaded):
		gitignore_loaded = True
		gitignore_file = os.path.expanduser('~/.qpmignore')
		if os.path.exists(gitignore_file):
			with open(gitignore_file, 'r') as f:
				return f.read()
		else:
			return None



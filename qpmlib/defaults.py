import json, os.path, sys
import containers

overrides_loaded = False
default_overrides = {}

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
	global overrides_loaded
	global default_overrides

	if not(overrides_loaded):
		overrides_loaded = True
		defaults_file = os.path.expanduser('~/.qpm-defaults')

		if os.path.exists(defaults_file):
			with open(defaults_file, 'r') as f:
				try:
					default_overrides = json.loads(defaults_file.read())
				except Exception:
					print 'Failed to load ~/.qpm-defaults'					

	overrides_root = default_overrides
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
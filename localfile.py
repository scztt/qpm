import os.path, time, json
import defaults

class LocalDataFile:
	default_options = {
		'reload_timeout': 1000 * 1000,
		'create': True,
		'default_data': [],
		'write_on_delete': True
	}

	def __init__(self, path, options={}):
		options = defaults.dict_add_recursive(options, dict(self.default_options))
		print options
		defaults.load_user_defaults('LocalDataFile', options)
		self.options = options
		self.path = path
		self.data = None
		self.last_loaded = -1
		self.data_changed = False

	def __del__(self):
		if self.options['write_on_delete']:
			self.write()

	def get(self, force_reload=False):
		if force_reload or not(self.data) or (time.time() - self.last_loaded) > self.options['reload_timeout']:
			self.load_data(force_reload)
		return self.data

	def set(self, data, write_immediately=False):
		self.data = data
		self.data_changed = True
		if write_immediately: 
			self.write_data()

	def write_data(self):
		raw_data = json.dumps(self.data)
		with open(self.path, 'w') as f:
			f.write(raw_data)

	def load_data(self, force_reload=False):
		if self.data_changed and not(force_reload):
			raise Exception('Data has changed and will be overwritten by get_data (%s)' % self.path)
		else:
			if os.path.exists(self.path):
				with open(self.path, 'r') as f:
					raw_data = f.read()
					self.data = json.loads(raw_data)
					self.last_loaded = time.time()
					self.data_changed = False
			else:
				if self.options['create']:
					self.set(self.options['default_data'], True)
				else:
					raise Exception('File does not exist: %s' % self.path)
				





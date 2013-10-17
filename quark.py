import qpm
import os, os.path, json, collections

quark_file_name = "quark.json"

def get_quarkfile_path(base_path):
	return os.path.join(base_path, quark_file_name)

def get_existing_quark(pathname):
	quark_file = get_quarkfile_path(pathname)
	if os.path.exists(quark_file):
		return Quark(pathname)
	else:
		return None

class Quark:
	def __init__(self, path):
		self.path = path
		self.quarkfile_path = os.path.join(path, quark_file_name)
		self.checkout_quarkfile()

	def checkout_quarkfile(self):
		if not(os.path.exists(self.quarkfile_path)):
			f = open(self.quarkfile_path, 'w')
			f.write('{}')
			f.close()

		self.load()

	def checkin_quarkfile(self):
		self.save()

	def load(self):
		with open(self.quarkfile_path, 'r') as f:
			settings = json.loads(f.read(), object_pairs_hook=collections.OrderedDict)
			if not(settings): settings = collections.OrderedDict()

			self.name = settings.get('name')
			self.version = settings.get('version')
			self.sc_version = settings.get('sc_version')
			self.ide = settings.get('ide')
			self.dependencies = settings.get('dependencies', collections.OrderedDict())

	def save(self):
		with open(self.quarkfile_path, 'w') as f:
			settings = collections.OrderedDict()

			settings['name'] = self.name
			settings['version'] = self.version
			settings['sc_version'] = self.sc_version
			settings['ide'] = self.ide
			settings['dependencies'] = self.dependencies

			f.write(json.dumps(settings, indent=2))

	def add_dependency(self, name, version):
		self.dependencies[name] = version








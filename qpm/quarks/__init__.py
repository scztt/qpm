import requests
from github_http import GitHubEndpoint

endpoints = [GitHubEndpoint]

def get_endpoint(name, url):
	matches = filter(lambda endpoint: endpoint.url_matches(url), endpoints)
	if matches:
		endpoint_class = matches[0]
		return endpoint_class(name, url)
	else:
		raise Exception("Could not find appropriate endpoint for url: %s" % url)

class QuarkEndpoint():
	def name(self):
		raise NotImplementedError()
	def versions(self):
		raise NotImplementedError()
	def version_info(self, version='HEAD'):
		raise NotImplementedError()
	def update(self):
		raise NotImplementedError()
	def pull(self, destination, version='HEAD'):
		raise NotImplementedError()

class QuarksDirectory:
	def __init__(self, url = "https://raw.githubusercontent.com/supercollider-quarks/quarks/master/directory.txt"):
		self.url = url
		self.directory = None
		self.endpoints = dict()

	def update(self):
		self.directory = dict()

		req = requests.get(self.url)
		if req.ok:
			directory_str = req.text
			for line in directory_str.split("\n"):
				split_line = line.split("=")
				if len(split_line) == 2:
					self.directory[split_line[0]] = split_line[1]
		else:
			raise Exception("Failed to get quarks directory: %s" % self.url)

	def quarks(self):
		if not(self.directory): self.update()
		return self.directory.keys()

	def quark(self, name):
		if not(self.directory): self.update()

		url = self.directory.get(name)
		if not(url):
			raise Exception("No quark found: %s" % name)
		else:
			endpoint = get_endpoint(name, url)
			quark = Quark(endpoint)
			return quark



class Quark:
	def __init__(self, endpoint):
		self._endpoint = endpoint
		self._url = endpoint.url

	def name(self):
		return self._endpoint.name()

	def versions(self):
		return self._endpoint.versions()

	def dependencies(self, version):
		version_info = self._endpoint.version_info(version)
		return version_info['dependencies']

	def url(self):
		return self._url

	def checkout(self, version, destination):
		self._endpoint.install(version, destination)



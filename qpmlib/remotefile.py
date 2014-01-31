import os.path, time, json, tempfile, os
import settings
from localfile import LocalDataFile
from .endpoints.url import UrlEndpoint

class RemoteDataFile:
	default_options = {
		'cache_timeout': 60 * 60 * 24 * 1,
	}

	def __init__(self, url, local_path, options={}):	
		self.options = settings.load_user_defaults('RemoteDataFile', options, self.default_options)

		self.url = url
		if local_path:
			self.local_cache = LocalDataFile(local_path)
		else:
			self.local_cache_file = tempfile.NamedTemporaryFile('r')
			self.local_cache = LocalDataFile(self.local_cache_file.name)
		
		self.data = None
		if os.path.exists(self.local_cache.path):
			stat = os.stat(self.local_cache.path)
			self.last_fetched = stat.st_mtime
		else:
			self.last_fetched = -1

	def get(self, force_reload=False):
		if force_reload or (time.time() - self.last_fetched) > self.options['cache_timeout']:
			self.fetch_data()
		return self.local_cache.get()

	def fetch_data(self):
		endpoint = UrlEndpoint(self.url)
		endpoint.get_to_file(self.local_cache.path)
		self.local_cache.get(force_reload=True)


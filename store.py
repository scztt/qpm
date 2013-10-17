import os, os.path, json

store_location = os.path.expanduser('~/Library/Application Support/SuperCollider/qpm')

base_repo_list = {
	'test': 'http://none'
	}

class QuarkStore:
	@classmethod
	def create_dir(dir):
		if not(os.path.exists(dir)):
			os.makedirs(dirs)

	def __init__(self, root):
		self.repo_list_file = os.path.join(store_location, 'QPM Repositories.json')
		self.repo_cache_dir = os.path.join(store_location, 'Repository Cache')
		self.store_dir = os.path.join(store_location, 'Store')

		self.create_dir(self.repo_cache_dir)
		self.create_dir(self.store_dir)

		if not(os.path.exists(self.repo_list_file)):
			parent = os.path.split(self.repo_list_file)[0]
			self.create_dir(parent)
			with open(self.repo_list_file, 'w') as f:
				f.write(json.dumps(base_repo_list))


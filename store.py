import os, os.path, json, stat, time, collections, re
from .endpoints.url import UrlEndpoint
from localfile import LocalDataFile
from remotefile import RemoteDataFile


store_location = os.path.expanduser('~/Library/Application Support/SuperCollider/qpm')

base_repo_list = [
	'https://github.com/scztt/qpm/raw/master/sample_repo.json'
]

repo_name_pattern = '[:/_\.]+'

class QuarkStore:
	@classmethod
	def create_dir(cls, dir):
		if not(os.path.exists(dir)):
			os.makedirs(dir)

	def __init__(self):
		global store_location
		self.repo_list_file = LocalDataFile(os.path.join(store_location, 'QPM Repositories.json'), options={
			'default_data': base_repo_list
		})

		self.repo_files = []
		self.repo_cache_dir = os.path.join(store_location, 'Repository Cache')
		self.store_dir = os.path.join(store_location, 'Store')

		self.create_dir(self.repo_cache_dir)
		self.create_dir(self.store_dir)

		self.cache_days = 1
		self.repo_list = None

	def repo_to_filename(self, repo):
		return re.sub(repo_name_pattern, '-', repo)

	def repo_to_path(self, repo):
		local_file_name = self.repo_to_filename(repo)
		filename = os.path.join(self.repo_cache_dir, local_file_name)
		return filename		

	def update_repos(self):
		repo_list = self.repo_list_file.get()
		self.repo_files = []
		for repo in repo_list:
			repo_file = RemoteDataFile(repo, self.repo_to_path(repo))
			self.repo_files.append(repo_file)

	def get_package(self, package_name):
		if not(self.repo_files): self.update_repos()
		for repo in self.repo_files:
			repo_data = repo.get()
			if repo_data.has_key(package_name):
				package = repo_data[package_name]
				return package

q = QuarkStore()
print q.get_package('test_quark')


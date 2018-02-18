__author__ = 'fsc'

import requests
import re
import os
import zipfile
import shutil
import base64

GITHUB_GIT_URL_REGEXP = r"git://github\.com/([^!]+?)/([^@/]*)"
GITHUB_HTTP_URL_REGEXP = r"http.://github\.com/([^!]+?)/([^@/]*)"
GITHUB_QUARKFILE_PATTERN = r"[^/]+.quark"
GITHUB_OAUTH = os.getenv('GITHUB_OAUTH', 'e76bd60dd1878be9db79d468dc9917f1961443d0')

NUMERIC_VERSION = r"[vV]?[0-9](\.[0-9]+)+\w*"

minicache = dict()

def github_download(url, destination, ensure_dirs=True):
	base_url = 'https://api.github.com/'
	headers = {}
	if not(url.startswith("http")):
		url = base_url + url
		# only use auth tokens with an api.github.com header
		headers = {'Authorization': 'token %s' % GITHUB_OAUTH}

	base_path = os.path.split(destination)[0]
	if not(os.path.exists(base_path)):
		os.makedirs(base_path)

	size = 0
	with open(destination, 'w') as f:
		req = requests.get(url, headers=headers, stream=True)
		if not(req.ok):
			raise Exception('Failed to access url: %s (%s)' % (url, req.status_code))

		for block in req.iter_content(1024):
			size += len(block)
			if not block: break
			f.write(block)

	return size

def github_request(url, json=True):
	base_url = 'https://api.github.com/'
	if not(url.startswith('http')):
		url = base_url + url

	cached = minicache.get(url)
	if cached: return cached

	req = requests.get(url, headers={'Authorization': 'token %s' % GITHUB_OAUTH})
	if req.ok:
		if json:
			minicache[url] = result = req.json()
		else:
			minicache[url] = result = req.content

		return result
	else:
		raise Exception('Failed to access url: %s (%s)' % (url, req.status_code))

class GitHubEndpoint:
	@classmethod
	def url_match(cls, url):
		patterns = [
			GITHUB_GIT_URL_REGEXP,
			GITHUB_HTTP_URL_REGEXP
		];
		matches = filter(lambda p: re.match(p, url), patterns)
		return len(matches) > 0

	def __init__(self, name, url):
		self.url = url
		self._name = name
		self._versions = []
		self._head_hash = None

		if url[0:6] == 'git://':
			pattern = GITHUB_GIT_URL_REGEXP
		elif url[:8] == 'https://' or url[0:7] == 'http://':
			pattern = GITHUB_HTTP_URL_REGEXP
		else:
			raise Exception("Invalid github url: %s" % url)

		match = re.match(GITHUB_GIT_URL_REGEXP, url)
		if not(match): match = re.match(GITHUB_HTTP_URL_REGEXP, url)
		if not(match): raise Exception("Failure parsing github url: %s (%s)" % (url, pattern))

		self.user = match.group(1)
		self.repo = match.group(2)

	def tags_url(self): return 'repos/%s/%s/tags' % (self.user, self.repo)
	def branches_url(self): return 'repos/%s/%s/branches' % (self.user, self.repo)
	def tree_url(self, commit_hash): return 'repos/%s/%s/git/trees/%s' % (self.user, self.repo, commit_hash)
	def raw_content_url(self, commit, path):
		return 'https://raw.githubusercontent.com/%s/%s/%s/%s' % (self.user, self.repo, commit, path)
	def zip_url(self, commit):
		return 'https://github.com/%s/%s/archive/%s.zip' % (self.user, self.repo, commit)

	def head_hash(self):
		if not(self._head_hash):
			# find commit has for "HEAD"
			branches = github_request(self.branches_url())
			master = filter(lambda b: b['name'] == 'master', branches)
			if master:
				self._head_hash = master[0]['commit']['sha']
		return self._head_hash

	def update_versions(self):
		if not(self._versions):
			refs = github_request(self.tags_url())
			versions = []
			for ref in refs:
				versions.append(ref)
			self._versions = versions

		return self._versions

	def versions(self, numerical_only=True):
		versions =  map(lambda v: v['name'], self.update_versions())
		if numerical_only:
			return filter(lambda v: re.match(NUMERIC_VERSION, v), versions)
		else:
			return versions

	def checkout(self, version, quark_store):
		commit_hash = self.commit_hash_for_version(version)
		version_name = commit_hash if (version == 'HEAD') else version
		quark_destination = os.path.expanduser(os.path.join(quark_store, self._name, version_name))
		zip_destination = os.path.expanduser(os.path.join(quark_destination, '_tmp', 'download.zip'))

		size = github_download(self.zip_url(commit_hash), zip_destination)
		if size:
			zip = zipfile.ZipFile(zip_destination)
			zip.extractall(quark_destination)
			shutil.rmtree(os.path.split(zip_destination)[0])
			folders = [ f for f in os.listdir(quark_destination) if os.path.isdir(os.path.join(quark_destination, f)) ]
			if len(folders) == 1:
				quark_destination_tmp = quark_destination + "_tmp"
				shutil.move(quark_destination, quark_destination_tmp)
				shutil.move(os.path.join(quark_destination_tmp, folders[0]), quark_destination)
				shutil.rmtree(quark_destination_tmp)
		else:req.content
			raise Exception('Problem with file download: $s (size %s)' % (zip_destination, size))

		return quark_destination

	def commit_hash_for_version(self, version):
		commit_hash = None
		if version == 'HEAD':
			commit_hash = self.head_hash()
		else:
			versions = filter(lambda v: v.get('name') == version, self.update_versions())
			if not(versions): raise Exception("Requested version '%s' doesn't exist!" % version)
			version_info = versions[0]
			commit = github_request(version_info['commit']['url'])
			commit_hash = commit['commit']['tree']['sha']

		return commit_hash

	def version_info(self, version):
		commit_hash = self.commit_hash_for_version(version)
		tree = github_request(self.tree_url(commit_hash))
		quark_files = filter(lambda path: path['path'].lower().endswith('.quark'), tree['tree'])
		if quark_files:
			quark_file = quark_files[0]
			return github_request(quark_file['url'], json=False)

	def info(self, version):
		commit_hash = self.commit_hash_for_version(version)
		tree = github_request(self.tree_url(commit_hash))
		quark_files = filter(lambda path: path['path'].lower().endswith('.quark'), tree['tree'])
		if quark_files:
			quark_file = quark_files[0]
			blob = github_request(quark_file['url'], json=True)
			content = blob['content']
			info = base64.b64decode(content)
			return info

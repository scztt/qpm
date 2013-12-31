import subprocess, os, re
from base import EndpointBase

check_repo_cmd = ['git', 'ls-remote', '--exit-code']
git_get_cmd = ['git', 'clone']

class GitEndpoint(EndpointBase):
	types = ['http://', 'https://', 'ssh://', 'git://', 'ftp://', 'rsync://', 'file://']
	pattern = 'git+(?P<url>(?P<type>\w+://)?[^#]*)(#(?P<commit>.*))?'

	@classmethod
	def validate(cls, target):
		match = re.search(cls.pattern, target)
		match_groups = match.groupdict()
		if match_groups['type'] in cls.types:
			return True
		else:
			return os.path.exists(target)

	def __init__(self, validated_target):
		match = re.search(self.pattern, validated_target)
		match_groups = match.groupdict()
		if match_groups:
			self.target = match_groups['url']
			self.commit = match_groups['commit']

			if match_groups['type']:
				self.type = match_groups['type']
			else:
				self.type = 'file://'
				self.target = self.type + self.target

		else:
			raise Exception('incorrect url: ' + validated_url)

	def verify(self):
		cmd = check_repo_cmd + [self.target]
		try:
			result = subprocess.check_output(cmd)
			return True
		except Exception:
			return False

	def get_to(self, local_dir):
		if self.commit:
			cmd = git_get_cmd + ['-b', self.commit, self.target, local_dir]
		else:
			cmd = git_get_cmd + [self.target, local_dir]

		try:
			print cmd
			result = subprocess.check_output(cmd)
			print result
			return True
		except Exception:
			return False


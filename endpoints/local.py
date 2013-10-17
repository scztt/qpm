import sys, os, os.path, shutil
from base import EndpointBase
import qpm

class LocalEndpoint(EndpointBase):

	@classmethod
	def validate(cls, target):
		return os.path.exists(target)

	def verify(self):
		return False

	def get_to(self, local_dir, link = False):
		if qpm.is_mac() or qpm.is_lin():
			if link:
				os.symlink(self.target, local_dir)
			else:
				shutil.copytree(self.target, local_dir)
			return True

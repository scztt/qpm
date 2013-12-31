import re
from .base import EndpointBase

valid_quark_name_pattern = '[\w\-]+'

class QuarknameEndpoint(EndpointBase):
	@classmethod
	def validate(cls, target):

		if not(re.match(valid_quark_name_pattern, target)):
			return False

		quark_registry = os.path.abspath('')

import quark
from generic_action import GenericAction

class FetchAction(GenericAction):
	name = 'fetch'
	default_options = {}

	def __init__(self, options):
		super(options)
		self.target = quark.validate_target(self.options['target'])

	def validate_target(self):
		target = self.options.target['target']

		if re.match(valid_quark_name_pattern, target):
			validated = self.validate_target_as_quark(target)
			if not(validated):
				validated = self.validate_target_as_path(target)

		target_as_path = qpm.validate_path(target)
		

action = FetchAction
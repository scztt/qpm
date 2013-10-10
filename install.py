class QPM_Install_Action:

	@classmethod
	def Create_Action(klass, config, command_line):
		action = klass(config)
		parse_ok = action.parse_command_line(command_line)
		if parse_ok:
			return action

	def __init__(self, config):
		self.config = config

	def parse_command_line(self, command_line):
		print command_line




import argparse
import defaults, qpm, containers

class GenericAction:
	default_options = {}
	name = 'none'

	@classmethod 
	def get_default_options(cls):
		options = dict(cls.default_options)
		defaults.load_user_defaults([cls.name], options)
		return options

	@classmethod
	def cmd_line_to_options(cls, cmd_line):
		parser = cls.get_arg_parser()
		parsed = parser.parse_args(cmd_line);

		options = cls.get_default_options()
		defaults.dict_add_recursive(vars(parsed), options)
	 
	 	return options

	@classmethod
	def get_arg_parser(cls):
	 	return argparse.ArgumentParser()

	@classmethod
	def do(cls, options):
	 	action = cls(options)
	 	result = action.do()
	 	return result

	def __init__(self, options):
		self.options = options
		self.do_validation()

		self.result = containers.tree()
		self.result['completed'] = False
		self.result['success'] = False
		self.result['reason'] = None
		self.result['messages'] = list()	

	def do(self):
		pass	

	def do_validation(self):
		self.options['quark_path'] = qpm.validate_path(self.options['quark_path'])
		return True

	def report(self, message):
		self.result['messages'].append(message)

	def get_result(self):
		return self.result

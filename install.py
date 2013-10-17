import qpm, quark, containers, ide, defaults, fetch
import argparse, sys, os, os.path
from collections import OrderedDict
from generic_action import GenericAction
from fetch import action as Fetch

class InstallAction(GenericAction):
	name = 'install'
	default_options = {
		'target': None,
		'global': False,
		'copy': False,
		'add': False,
		'version': '>=0.0.1',
		'dependencies_dir': 'dependencies'
	}

	@classmethod
	def get_arg_parser(cls):
		default_options = cls.get_default_options()

		parser = argparse.ArgumentParser()

		parser.add_argument('target', nargs='?', default=default_options['target'],
			help='path / package to install')	
		parser.add_argument('--global', '-g', action='store_true', default=default_options['global'],
			help='Install in global location.')
		parser.add_argument('--copy', '-c', action='store_true', default=default_options['copy'],
			help='Make copy to local folder (instead of a link).')
		parser.add_argument('--add', '-a', action='store_true', default=default_options['add'],
			help='Add installed package to quarkfile.')
		parser.add_argument('--version', '-v', nargs='?', default=default_options['version'],
			help='Requested package version.')

	 	return parser	

	def do_validate(self):
		deps_dir = os.path.join(options['quark_path'], options['dependencies_dir'])
		if not(os.path.exists(deps_dir)): os.mkdir(deps_dir)
		options['dependencies_dir'] = deps_dir
		
		return super.do_validate() and True


	def do(self):
		fetch_options = Fetch.get_default_options()
		fetch_options['target'] = self.options['target']
		fetch_options['version'] = self.options['version']
		fetch_options['quark_path'] = self.options['quark_path']

		fetch = Fetch(fetch_options)
		fetch.do()
		fetch_result = fetch.get_result()

		if fetch_result['success']:
			location = fetch_result['location']
			local_target = self.options['dependencies_dir']


action = InstallAction

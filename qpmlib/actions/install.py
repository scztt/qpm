	from ..generic_action import GenericAction
from .fetch import FetchAction
from ..store import QuarkStore
from ..quark import Quark

import argparse, sys, os, os.path
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
		options = self.options
		self.quark = Quark(options['quark_path'])

		# With no target, just install all dependencies
		if options['target'] == None:
			self.do_install_all_deps()
		else:
			self.do_install_dep(options['target'])

	def do_install_dep(self, package_name):
		options = self.options

		store = QuarkStore()

		package_location = store.find_package_local(package_name, options['version'])
		if not(package_location):
			package_location = store.fetch_package(package_name, options['version'])

		if package_location:
			if options['global']:
				install_result = self.do_install(package_location)
			else:
				install_result = self.do_global_install(package_location)
		else:
			# fail
			print 'Failed to find / fetch package "%s"' % package_name

	def do_install_all_deps(self):
		to_parse = set()
		self_dependencies = self.quark.get_dependencies()
		to_parse.add()


	def do_fetch_dep(self):
		options = self.options

		fetch_options = Fetch.get_default_options()
		fetch_options['target'] = options['target']
		fetch_options['version'] = options['version']
		fetch_options['quark_path'] = options['quark_path']

		fetch = FetchAction(fetch_options)
		fetch.do()
		return fetch.get_result()

	def do_install(self, package_location, copy=False):
		location = package_location
		local_target = self.options['dependencies_dir']

	def do_global_install(self, package_location, copy=False):
		location = package_location
		local_target = self.options['dependencies_dir']


action = InstallAction

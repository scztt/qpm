from .. import quark
from ..generic_action import GenericAction
from ..store import QuarkStore

import argparse, os

class ListAction(GenericAction):
	name = 'list'
	default_options = {
		'local': False,
		'global': False,
		'remote': True
	}

	@classmethod
	def get_arg_parser(cls):
		default_options = cls.get_default_options()

		parser = argparse.ArgumentParser()

		parser.add_argument('path', nargs='?', help='path to initialize', default=os.getcwd())
		parser.add_argument('--global', '-g', action='store_true', default=default_options['global'],
			help='List globally installed packages.')
		parser.add_argument('--local', '-l', action='store_true', default=default_options['local'],
			help='List installed packages local to this quark.')
		parser.add_argument('--remote', '-r', action='store_true', default=default_options['remote'],
			help='List all remote packages.')

		return parser

	def do(self):
		if self.options['global']:
			result_list = self.list_global()
		elif self.options['local']:
			result_list =  self.list_local()
		elif self.options['remote']:
			result_list =  self.list_remote()

		for package, versions in result_list.iteritems():
			self.msg('%s:\t\t[%s]' % (package, ', '.join(versions)))

		self.result['packages'] = result_list
		self.result['completed'] = self.result['success'] = True
		self.result['result']

	def list_remote(self):
		store = QuarkStore()
		return store.collect_packages()

	def list_global(self):
		store = QuarkStore()
		return store.collect_packages()

	def list_local(self):
		store = QuarkStore()
		return store.find_all_global()

action = ListAction
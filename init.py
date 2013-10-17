import qpm, quark, containers, ide, defaults
import argparse, sys, os
from collections import OrderedDict
from generic_action import GenericAction

class InitAction(GenericAction):
	name = 'init'
	default_options = {
		'git': False,
		'reinit': False,
		'show': False,
		'name': '-',
		'version': '0.0.1',
		'sc': '3.6.5',
	}

	@classmethod
	def get_arg_parser(cls):
		default_options = cls.get_default_options()

		parser = argparse.ArgumentParser()

		parser.add_argument('path', nargs='?', help='path to initialize', default=os.getcwd())
		parser.add_argument('--git', '-g', action='store_true', help='initialize git repo for quark', default=default_options['git'])
		parser.add_argument('--reinit', '-r', action='store_true', help='Reinitialize (danger - will destroy old quarks.json!)', default=default_options['reinit'])
		parser.add_argument('--show', '-p', action='store_true', help='Print quark.json after changes.', default=default_options['show'])
		parser.add_argument('--name', '-n', nargs='?', help='name of quark', default=default_options['name'])
		parser.add_argument('--version', '-v', nargs='?', help='quark version', default=default_options['version'])
		parser.add_argument('--sc', '-s', nargs='?', help='supercollider version', default=default_options['sc'])
	 
	 	return parser

	def do(self):
		options = self.options

		if options['reinit']: 
			self.report('WARNING: Deleted an existing quarkfile.')
			if os.path.exists(quark.get_quarkfile_path(options['path'])):
				os.remove(quark.get_quarkfile_path(options['path']))

		if options['name'] == '-':
			options['name'] = os.path.basename(options['path'])

		if quark.get_existing_quark(options['path']):
			self.result['reason'] = 'Quark already exists at this location.'
			self.result['success'] = False
		else:
			self.create_quark()

		self.result['completed'] = True

	def create_quark(self):
		options = self.options

		new_quark = quark.Quark(options['path'])
		new_quark.checkout_quarkfile()

		new_quark.name = options['name']
		new_quark.version = options['version']
		new_quark.sc_version = options['sc']
		new_quark.add_dependency('core', options['sc'])
		new_quark.ide = {
			'path': ide.find_ide(options['sc'], interactive=True),
			'name': 'sc-ide',
		}
		self.report('Using ide at: %s' % new_quark.ide['path'])

		new_quark.checkin_quarkfile()

		if options['show']:
			with open(quark.get_quarkfile_path(options['path']), 'r') as f: 
				self.report(f.read())

		self.result['reason'] = 'Quark successfully created at %s' % options['path']
		self.result['success'] = True


action = InitAction



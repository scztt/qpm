from .. import quark, containers, ide, util, settings
from ..settings import user_settings
from ..generic_action import GenericAction

import argparse, sys, os, getpass, socket
from pydispatch import dispatcher

class InitAction(GenericAction):
    name = 'init'
    default_options = {
        'git': False,
        'reinit': False,
        'show': False,
        'name': '-',
        'version': '0.0.1',
        'sc': '3.6.5',
        'interactive': True,
        'author': None,
        'email': None
    }

    @classmethod
    def get_arg_parser(cls):
        default_options = cls.get_default_options()

        parser = argparse.ArgumentParser()

        parser.add_argument('path', nargs='?', help='path to initialize', default=os.getcwd())
        #parser.add_argument('--git', '-g', action='store_true', help='initialize git repo for quark', default=default_options['git'])
        parser.add_argument('--reinit', '-r', action='store_true', help='Reinitialize (danger - will destroy old quarks.json!)', default=default_options['reinit'])
        parser.add_argument('--show', '-p', action='store_true', help='Print quark.json after changes.', default=default_options['show'])
        parser.add_argument('--name', '-n', nargs='?', help='name of quark', default=default_options['name'])
        parser.add_argument('--author', '-a', nargs='?', help='quark author (you)', default=None)
        parser.add_argument('--email', '-e', nargs='?', help='quark author email (yours)', default=None)
        parser.add_argument('--version', '-v', nargs='?', help='quark version', default=default_options['version'])
        parser.add_argument('--sc', '-s', nargs='?', help='supercollider version', default=default_options['sc'])

        dispatcher.send(signal='qpm.init:arg_parser', sender=cls, parser)

        return parser

    def do(self):
        options = self.options
        dispatcher.send('qpm.init:options', self, options)

        if options['reinit']: 
            self.msg('Deleted an existing quarkfile.', 'warning')
            if os.path.exists(quark.get_quarkfile_path(options['path'])):
                os.remove(quark.get_quarkfile_path(options['path']))

        if options['name'] == '-':
            options['name'] = os.path.basename(options['path'])

        if not(options['author']):
            author = settings.get('defaults', 'author')
            if author == None:
                if options['interactive']:
                     author = util.ask('No author name is set. What name should I use? (This can be changed later in your quark, or in your .qpm file)')
                else:
                    author = getpass.getuser()
                self.msg('Default user name has been set to "%s" - this can be changed in your .qpm file.' % options['author'])
                settings.set('defaults', 'author', options['author'])
            options['author'] = author

        if not(options['email']):
            email = settings.get('defaults', 'email')
            if email == None:
                if options['interactive']:
                    email = util.ask('No email is set. Which email address should I use? (This can be changed later in your quark, or in your .qpm file)')
                else:
                    email = getpass.getuser() + '@' + socket.gethostname()
                self.msg('Default email has been set to "%s" - this can be changed in your .qpm file.' % options['email'])
                settings.set('defaults', 'email', options['email'])
            options['email'] = email

        if quark.get_existing_quark(options['path']):
            self.result['reason'] = 'Quark already exists at this location.'
            self.result['success'] = False
        else:
            new_quark = self.create_quark()
            dispatcher.send('qpm.init:created_quark', self, new_quark)

        if options['git']:
            self.init_git()

        self.result['completed'] = True

    def create_quark(self):
        options = self.options

        new_quark = quark.Quark(options['path'])
        new_quark.checkout_quarkfile()

        new_quark.name = options['name']
        new_quark.version = options['version']
        new_quark.sc_version = options['sc']
        new_quark.author = options['author']
        new_quark.email = options['email']

        new_quark.add_dependency('core', options['sc'])
        new_quark.ide = {
            'path': ide.find_ide(options['sc'], interactive=options['interactive']),
            'name': 'sc-ide',
        }
        self.msg('Using ide at: %s' % new_quark.ide['path'])

        dispatcher.send('qpm.init:creating_quark', self, new_quark)

        new_quark.checkin_quarkfile()

        self.init_paths()

        if options['show']:
            with open(quark.get_quarkfile_path(options['path']), 'r') as f: 
                self.report(f.read())

        self.result['reason'] = 'Quark successfully created at %s' % options['path']
        self.result['success'] = True

        return new_quark

    def init_paths(self):
        paths = [
#            os.path.join(self.options['path'], 'media'),
            os.path.join(self.options['path'], 'dependencies'),
#            os.path.join(self.options['path'], 'recordings')
        ]

        for p in paths:
            if not(os.path.exists(p)):
                os.makedirs(p)

action = InitAction



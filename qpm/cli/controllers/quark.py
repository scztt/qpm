import os.path
from multiprocessing.pool import ThreadPool

import qpm.quarks

from cement.core import controller
from qpm.quarks import *
from cement.core.controller import CementBaseController, expose

quark_list_m = '''
    Available quarks from {{repo-count}} repos.
    {{#quarks}}
      - {{quark}}
    {{/quarks}}
'''

class Quark_Base(CementBaseController):
    class Meta:
        label = 'quark'
        description = 'Quark installation and test tool'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = 'do things with quarks'

class Quark_List(CementBaseController):
    class Meta:
        label = 'list'
        stacked_on = 'quark'
        stacked_type = 'nested'
        description = 'List available quarks.'
        arguments = []

    @controller.expose(help="List available quarks.", hide=True)
    def default(self):
        directory = QuarksDirectory()
        url = directory.url
        quarks = sorted(directory.quarks())
        self.app.render(quarks, 'quark_list')


class Quark_Checkout(CementBaseController):
    class Meta:
        label = 'checkout'
        stacked_on = 'quark'
        stacked_type = 'nested'
        description = 'Download quark to local store.'
        arguments = [
            (['quarks'], {
				'action': 'store',
				'nargs': '+'
			}),
            (['-l', '--location'], {
                'default': os.path.expanduser('~/Library/Application Support/SuperCollider/quark_versions'),
                'nargs': '?',
                'help': 'Quark store location'
            })
        ]

    @controller.expose(help="Download quark to local store.", hide=True)
    def default(self):
        directory = QuarksDirectory()
        specs = self.app.pargs.quarks
        destination = self.app.pargs.location
        results = {}

        pool = ThreadPool(processes=20)

        def checkout(spec):
            split_spec = spec.split('@')
            if len(split_spec) < 2:
                split_spec.append('HEAD')
            quark = directory.quark(split_spec[0])
            self.app.render('Checking out %s [%s]' % (split_spec[0], split_spec[1]))
            return [split_spec[0], quark.checkout(split_spec[1], destination)]

        results = dict(pool.map(checkout, specs))

        self.app.render(results, 'quark_checkout')

class Quark_Versions(CementBaseController):
    class Meta:
        label = 'versions'
        stacked_on = 'quark'
        stacked_type = 'nested'
        description = 'List quarks versions available.'
        arguments = [
            (['quarks'], {
				'action': 'store',
				'nargs': '+'
			})
        ]
    @controller.expose(help="Show quark versions.", hide=True)
    def default(self):
        directory = QuarksDirectory()
        names = self.app.pargs.quarks
        result = dict()

        for name in names:
            result[name] = directory.quark(name).versions()

        self.app.render(result, 'quark_versions')

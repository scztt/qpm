import os.path
import itertools
from multiprocessing.pool import ThreadPool

import qpm.quarks
import qpm.sclang_process as process

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

class Quark_Info(CementBaseController):
    class Meta:
        label = 'info'
        stacked_on = 'quark'
        stacked_type = 'nested'
        description = 'Show info about a quark.'
        arguments = [
            (['-p', '--path'], dict(default=os.getcwd(), help='Path to supercollider installation or config.yaml')),
            (['quarks'], {
                'default': ['*'],
				'action': 'store',
				'nargs': '+'
			})
        ]
    @controller.expose(help="Show info about a quark.", hide=True)
    def default(self):
        pool = ThreadPool(processes=4)
        directory = QuarksDirectory()
        sclang = process.find_sclang_executable(self.app.pargs.path)

        quark_specs = self.app.pargs.quarks
        if '*' in quark_specs:
            quark_specs = directory.quarks()

        def do_request_version(request):
            quark_name = request[0]
            version = request[1]
            return (quark_name, version, directory.quark(quark_name).info(version))

        def do_request_specs(quark_spec):
            split_spec = quark_spec.split('@')
            requests = list()
            if len(split_spec) < 2:
                split_spec.append('*')
            if split_spec[1] == '*':
                quark = directory.quark(split_spec[0])
                versions = quark.versions()
                versions.append('HEAD')
                for version in versions:
                    requests.append((split_spec[0], version))
            else:
                requests.append(split_spec)

            return requests

        requests = list(itertools.chain(*pool.map(do_request_specs, quark_specs)))
        if len(requests) > 20:
            print 'Requesting info on %s quark version - this may take some time...' % len(requests)

        results_list = pool.map(do_request_version, requests)

        results_dict = dict()
        for result in results_list:
            (name, version, content) = result
            quark = results_dict.get(name, dict())
            if content:
                quark[version] = content.decode('utf-8', 'replace')
            results_dict[name] = quark

        results = process.convert_quark_infos(sclang, results_dict)

        self.app.render(results, 'quark_info')

#!/usr/bin/env python
import gevent.greenlet
import argparse, sys, os, os.path, importlib, json

actions_list = ['init', 'config', 'install', 'archive', 'publish', 'develop', 'run', 'test', 'list']

parser = argparse.ArgumentParser()
parser.add_argument('action', help='action to perform', choices=actions_list)
parser.add_argument('--path', help='root path of quark', nargs='?', default=os.getcwd())
parser.add_argument('-j', '--json', help='show json result output', action='store_true')
parser.add_argument('-n', '--noninteractive', help='Do not ask for user input. Command may fail if options are missing.', action='store_true')

def validate_path(pathname, must_exist=True):
    pathname = os.path.expandvars(os.path.expanduser(pathname))

    # @TODO make win safe
    if not(pathname[0] == '/'):
        pathname = os.path.join(os.getcwd(), pathname)

    if must_exist and not(os.path.exists(pathname)):
        raise IOError('Path doesn\'t exist. (%s)' % pathname)
    else:
        return pathname

def get_action_class(name):
    action_module = importlib.import_module('.' + name, 'qpmlib.actions')
    action = action_module.action
    return action

def exec_action(parameters):
    quark_path = parameters['path']
    TheAction = get_action_class(parameters['action'])
    if TheAction:
        options = parameters
        options['quark_path'] = validate_path(quark_path)
        options['json'] = True
        options['interactive'] = False

        action = TheAction(options)
        gl = gevent.Greenlet(action.do)
        gl.start()
        gl.join()

        return action.get_result()

if __name__ == '__main__':
    cmd_line = sys.argv[1:]
    parameters, unknown = parser.parse_known_args(cmd_line)

    quark_path = parameters.path

    TheAction = get_action_class(parameters.action)
    if TheAction:
        options = TheAction.cmd_line_to_options(unknown)
        options['quark_path'] = validate_path(quark_path)
        options['interactive'] = not(parameters.noninteractive)

        action = TheAction(options)
        gl = gevent.Greenlet(action.do)
        gl.start()
        gl.join()
        result = action.get_result()

    if parameters.json:
        if result:
            print json.dumps(result)
        else:
            print '{}'
    else:
        if not(result['completed']):
            print '%s was not completed!\nReason: %s' % (action, result['reason'])
            for m in result['messages']: print m.message
        elif not(result['success']):
            print '%s was not successful.\nReason: %s' % (action, result['reason'])
            for m in result['messages']: print m.message
        else:
            for m in result['messages']: print m.message
            if result['reason']:
                print '%s' % result['reason']

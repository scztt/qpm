#!/usr/bin/env python
import argparse, sys, os, os.path

actions_list = ['init', 'config', 'install', 'archive', 'publish', 'develop', 'run', 'test']

parser = argparse.ArgumentParser()
parser.add_argument('action', help='action to perform', choices=actions_list)
parser.add_argument('--path', help='root path of quark', nargs='?', default=os.getcwd())

def is_mac():
	return True

def is_win():
	return False

def is_lin():
	return False


def validate_path(pathname, must_exist=True):
	pathname = os.path.expandvars(os.path.expanduser(pathname))

	# @TODO make win safe
	if not(pathname[0] == '/'):
		pathname = os.path.join(os.getcwd(), pathname)

	if must_exist and not(os.path.exists(pathname)):
		raise IOError('Path doesn\'t exist. (%)' % pathname)
	else:
		return pathname

def get_action_class(name):
	action_module = __import__(name)
	action = action_module.action
	return action

if __name__ == '__main__':
	cmd_line = sys.argv[1:]
	parameters, unknown = parser.parse_known_args(cmd_line)

	quark_path = parameters.path

	TheAction = get_action_class(parameters.action)
	if TheAction:
		options = TheAction.cmd_line_to_options(unknown)
		options['quark_path'] = validate_path(quark_path)

		action = TheAction(options)
		action.do()
		result = action.get_result()

	if not(result['completed']):
		print '%s was not completed!\nReason: %s' % (action, result['reason'])
		for msg in result['messages']: print msg
	elif not(result['success']):
		print '%s was not successful.\nReason: %s' % (action, result['reason'])
		for msg in result['messages']: print msg
	else:
		for msg in result['messages']: print msg
		print '%s' % result['reason']


#!/usr/bin/env python
import argparse, sys

actions_list = ['init', 'config', 'install', 'archive', 'publish', 'develop', 'run', 'test']

parser = argparse.ArgumentParser()
parser.add_argument("action", help="action to perform", choices=actions_list, )

if __name__ == "__main__":
	cmd_line = sys.argv[1:]
	parameters = parser.parse_args(cmd_line)
	action = parameters.action

	action_module = __import__(action)
	options = action_module.cmd_line_to_options(cmd_line[2:])
	action_modile.do(options)
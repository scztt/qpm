__author__ = 'fsc'

import os.path
import qpm, tests

quark_name = 'unit-test-quark'

def test_basic_init():
	result = qpm.exec_action({
		'action': 'init',
		'path': tests.test_dir,
		'name': quark_name,
		'version': '1.2.3'
	})

	assert result['completed']
	assert result['success']
	assert ('Quark successfully created at %s' % tests.test_dir) in result['reason']

	assert os.path.exists(tests.test_dir)
	assert not(os.path.exists(os.path.join(tests.test_dir, '.git')))

	quark_file = os.path.join(tests.test_dir, 'quark.json')
	assert os.path.exists(quark_file)

	with file(quark_file) as f:
		contents = f.read()
		assert '"name": "unit-test-quark"' in contents
		assert '"version": "1.2.3"' in contents

def test_reinit_fail():
	# test for proper failure when trying to re-initialize an existing quark folder
	result = qpm.exec_action({
		'action': 'init',
		'path': tests.test_dir,
		'name': quark_name,
		'version': '1.2.3'
	})

	assert result['completed']
	assert not(result['success'])

def test_reinit_pass():
	# test for pass when using the reinit param with an existing quark folder
	result = qpm.exec_action({
		'action': 'init',
		'path': tests.test_dir,
		'name': quark_name,
		'version': '1.2.4',
		'reinit': True
	})

	assert result['completed']
	assert result['success']

	quark_file = os.path.join(tests.test_dir, 'quark.json')
	with file(quark_file) as f:
		contents = f.read()
		assert '"version": "1.2.4"' in contents

def test_git():
	result = qpm.exec_action({
		'action': 'init',
		'path': tests.test_dir,
		'name': quark_name,
		'version': '1.2.4',
		'reinit': True,
		'git': True
	})

	git_folder = os.path.join(tests.test_dir, '.git')
	assert os.path.exists(git_folder)

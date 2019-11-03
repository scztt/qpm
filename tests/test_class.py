__author__ = 'fsc'

import os.path, shutil
import qpmcli.core

class QPMAppTest(qpmcli.core.QPMApp):
	class Meta:
		argv = []
		config_files = []

"""
def test_basic_init():
    global test_dir
    test_dir = '/c/qpm/tests/test_dir'
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir, True)
    os.makedirs(test_dir)

    result = qpm.exec_action({
        'action': 'init',
        'path': test_dir,
        'name': quark_name,
        'version': '1.2.3'
    })

    assert result['completed']
    assert result['success']
    assert ('Quark successfully created at %s' % test_dir) in result['reason']

    quark_file = os.path.join(test_dir, 'quark.json')
    assert os.path.exists(test_dir)
    assert os.path.exists(quark_file)

    assert os.path.exists(os.path.join(test_dir, 'dependencies'))
    assert os.path.exists(os.path.join(test_dir, 'media'))
    assert os.path.exists(os.path.join(test_dir, 'recordings'))
    assert not(os.path.exists(os.path.join(test_dir, '.git')))

    with file(quark_file) as f:
        contents = f.read()
        assert '"name": "unit-test-quark"' in contents
        assert '"version": "1.2.3"' in contents

def test_reinit_fail():
    global test_dir
    # test for proper failure when trying to re-initialize an existing quark folder
    result = qpm.exec_action({
        'action': 'init',
        'path': test_dir,
        'name': quark_name,
        'version': '1.2.3'
    })

    assert result['completed']
    assert not(result['success'])

def test_reinit_pass():
    global test_dir
    # test for pass when using the reinit param with an existing quark folder
    result = qpm.exec_action({
        'action': 'init',
        'path': test_dir,
        'name': quark_name,
        'version': '1.2.4',
        'reinit': True
    })

    assert result['completed']
    assert result['success']

    quark_file = os.path.join(test_dir, 'quark.json')
    with file(quark_file) as f:
        contents = f.read()
        assert '"version": "1.2.4"' in contents

def test_git():
    global test_dir

    f = open(os.path.join(test_dir, 'test.txt'), 'w')
    f.write('...')
    f.close()

    result = qpm.exec_action({
        'action': 'init',
        'path': test_dir,
        'name': quark_name,
        'version': '1.2.4',
        'reinit': True,
        'git': True
    })


    git_folder = os.path.join(test_dir, '.git')
    assert os.path.exists(git_folder)
    commits = list(Repo(test_dir).iter_commits())
    assert len(commits) == 3
"""

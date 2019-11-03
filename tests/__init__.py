from nose import with_setup
import os, errno, shutil

test_dir = '/c/qpm-test-dir'

def setup():
    try:
        print 'Creating ' + test_dir
        os.makedirs(test_dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(test_dir):
            pass
        else: raise

def teardown():
    shutil.rmtree(test_dir, True)
    return

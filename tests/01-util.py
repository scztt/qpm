__author__ = 'fsc'

import qpmlib.util as util
from nose.tools import *

def test_build_sorting():
    versions = ['0', '0.1', '0.0.1', '0.1.0', '3.0.1', '3.0', '3']
    sorted_versions = util.sort_versions(versions)
    eq_(sorted_versions, ['0', '0.0.1', '0.1.0', '3', '3.0.1'])

def test_select_version():
    versions = ['0', '0.1', '0.0.1', '0.1.0', '3.0.1', '3.0', '3']
    eq_(util.select_versions('>0.5.0', versions), '3.0.1')
    eq_(util.select_versions('<0.5.0', versions), '0.1.0')
    eq_(util.select_versions('~3.0.0', versions), '3.0.1')
    eq_(util.select_versions('3.0.0', versions), '3')

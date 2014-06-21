__author__ = 'fsc'

import json
from qpmlib.package import Package
from nose.tools import *

mock_data = '''
{
    "name": "UGenPatterns",
    "description": "patterns acting as ugens",
    "maintainer": "redFrik",
    "maintainer-email": "",
    "authors": ["redFrik"],
    "created": "Wed Mar  5 10:15:00 2014",

    "versions": {
        "1.0.1": {
            "date": "Wed Mar  5 10:15:00 2014",
            "release": "svn://svn.code.sf.net/p/quarks/code/UGenPatterns",
            "scversion": ">=3.3.0",
            "dependencies": {
                "Other": ">1",
                "SomeOther": "~1"
            }
        },
        "0.0.1": {
            "date": "Wed Mar  5 10:15:00 2014",
            "release": "svn://svn.code.sf.net/p/quarks/code/UGenPatterns",
            "scversion": ">=3.3.0",
            "dependencies": {
                "Other": ">0"
            }
        }
    }
}
'''

def test_versions():
    global mock_data
    package = Package(json.loads(mock_data))

    assert('0.0.1' in package.versions())
    assert('1.0.1' in package.versions())

def test_latest():
    global mock_data
    package = Package(json.loads(mock_data))
    assert(package.latest_version() == '1.0.1')

def test_dependencies():
    global mock_data
    package = Package(json.loads(mock_data))
    eq_(package.dependencies()['Other'], '>1')
    eq_(package.dependencies('1.0.1')['SomeOther'], '~1')
    eq_(package.dependencies('0.0.1')['Other'], '>0')
qpm
===

Quarks package manager and test runner for SuperCollider (https://supercollider.github.io).
Written in Python.

Author: Scott Carver (https://github.com/scztt)

Supported versions: 
- Python 2.7

Features and Usage
------------------

To see available options, use:

    qpm -h

Installing
----------

qpm is available via pip:

    pip install qpm

For developing, install via either:

    pip install -e . # install from this directory

or:

    pip install -r requirements.txt

Requirements
------------

- semantic-version==2.2.0
- wsgiref==0.1.2
- nose==1.3.0
- gitpython==0.3.1-beta2
- gevent==1.0.1
- PyDispatcher==2.0.3
- cement
- colorama
- appdirs
- pyyaml

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "qpmlib",
    version = "0.0.1",
    author = "Scott Carver",
    author_email = "scott@artificia.org",
    description = ("Command line utilities for SuperCollider"),
    license = "BSD",
    url = "https://github.com/scztt/qpm/tree/qpm-unit",
    packages=['qpmlib', 'cli'],
)
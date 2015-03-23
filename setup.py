
from setuptools import setup, find_packages
from pip.req import parse_requirements
import sys, os

install_reqs = parse_requirements("requirements.txt")

setup(name='qpm',
    version='0.0.1',
    description="SuperCollider test and installation tool",
    long_description="SuperCollider test and installation tool",
    classifiers=[], 
    keywords='',
    author='scztt',
    author_email='scott@artificia.org',
    url='',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        'semantic-version',
        'wsgiref',
        'nose',
        'gitpython',
        'PyDispatcher',
        'cement',
        'colorama',
        'appdirs',
        'cement',
        'pyyaml'
    ],
    setup_requires=[],
    entry_points="""
        [console_scripts]
        qpm = qpm.cli.main:main
    """,
    namespace_packages=[],
)
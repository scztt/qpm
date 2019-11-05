
from setuptools import setup, find_packages
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
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
        'semantic-version==2.2.0',
        'wsgiref==0.1.2',
        'nose==1.3.0',
        'gitpython==0.3.2',
        'PyDispatcher==2.0.3',
        'cement==2.10.2',
        'colorama',
        'appdirs',
        'pyyaml',
        'requests==2.5.3'
    ],
    setup_requires=[],
    entry_points="""
        [console_scripts]
        qpm = qpm.cli.main:main
    """,
    namespace_packages=[],
)

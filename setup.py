from setuptools import setup, find_packages

with open("requirements.txt") as reqs_file:
    reqs = reqs_file.readlines()

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
    install_requires=reqs,
    setup_requires=[],
    entry_points="""
        [console_scripts]
        qpm = qpm.cli.main:main
    """,
    namespace_packages=[],
)

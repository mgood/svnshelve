try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='svnshelve',
    author='Matthew Good',
    version='0.1',
    scripts=['scripts/svn-shelve'],
    packages=['svnshelve'],
)

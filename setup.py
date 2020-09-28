from setuptools import setup, find_packages
from os import walk
from os.path import abspath, dirname, join, splitext
import re

__distname__ = 'MyFunctions'
__packagename__ = 'MyFunctions'
CURDIR = dirname(abspath(__file__))

# https://pypi.org/classifiers/
CLASSIFIERS = '''
Development Status :: 3 - Alpha
License :: Other/Proprietary License
Operating System :: Windows
Programming Language :: Python
Programming Language :: Python :: 3
'''.strip().splitlines()

with open(join(CURDIR, 'src', __packagename__, '__init__.py')) as f:
    VERSION = re.search("\n__version__ = '(.*)'", f.read()).group(1)
with open(join(CURDIR, 'requirements.txt')) as f:
    REQUIREMENTS = f.read().splitlines()
EXTS = [
    '.ico',
    '.jpg',
    '.png',
    '.xml',
    '.ini',
    '.txt',
    '.py',
    '.lnk',
    '.bat',
    '.md']


def package_files(directory):
    paths = []
    for (path, _directories, filenames) in walk(directory):
        for filename in filenames:
            if (splitext(filename)[1]) in EXTS:
                paths.append(join('..', path, filename))
    return paths


setup(
    name=__distname__,
    version=VERSION,
    description='Collection of Functions',
    author='Zach Robida',
    author_email='robidaz@gmail.com',
    platforms='any',
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    package_data={__packagename__: package_files(join(CURDIR, 'src'))})

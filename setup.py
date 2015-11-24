from setuptools import setup
from codecs import open
from os import path
from omnivore.version import VERSION

# Get the long description from the README.md file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='omnivore',
    version=VERSION,
    description='Omnivore.io python library',
    long_description=long_description,
    license='MIT',
    author='Alex Grover',
    author_email='alex.grover@doordash.com',
    url='https://github.com/doordash/omnivore',
    packages=['omnivore', 'omnivore.test'],
    install_requires=['requests == 2.8.1'],
    test_suite='pytest',  # 'omnivore.test.all?'
    tests_require=['pytest'],  # TODO: stripe uses unittest2 and mock?
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)

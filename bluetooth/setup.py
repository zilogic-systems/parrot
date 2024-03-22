from setuptools import setup
from setuptools import find_namespace_packages
from setuptools import find_packages
from os import path

setup(
    name='parrot-bluetoothcontroller',
    version='1.0.0',
    license="Apache License 2.0",
    url="https://github.com/zilogic-systems/parrot",
    author='Zilogic Systems',
    author_email='code@zilogic.com',
    packages=find_namespace_packages(),
    package_dir={'parrot':'.'},
    py_modules=['parrot.BluetoothController'],
    install_requires=["robotframework", "beautifulsoup4", "parrot-adbcontroller"],
)

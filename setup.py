from distutils.core import setup

from setuptools import find_packages

setup(
    name='dmonroy.web',
    version='0.1.0',
    namespace_packages=['dmonroy'],
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/dmonroy/dmonroy.web',
    author='Darwin Monroy',
    author_email='contact@darwinmonroy.com',
    description='A micro framework!',
    install_requires=[
        'aiohttp>=0.16.6',
    ]
)

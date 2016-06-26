from distutils.core import setup

from setuptools import find_packages

setup(
    name='chilero',
    use_scm_version=True,
    namespace_packages=['chilero'],
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/dmonroy/chilero',
    author='Darwin Monroy',
    author_email='contact@darwinmonroy.com',
    description='A micro framework... A la Tortrix!',
    install_requires=[
        'aiohttp>=0.21',
    ],
    setup_requires=[
        'setuptools_scm',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)

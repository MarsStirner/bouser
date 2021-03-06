# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

__author__ = 'viruzzz-kun'
__version__ = '0.2.1'


if __name__ == '__main__':
    setup(
        name="bouser",
        version=__version__,
        description="Bouser application server for Twisted",
        long_description='',
        author=__author__,
        author_email="viruzzz.soft@gmail.com",
        license='ISC',
        url="http://bitbucket.org/hitsl/bouser",
        packages=find_packages() + ["twisted.plugins"],
        zip_safe=False,
        package_data={
            'bouser.web': [
                'static/bootstrap/css/*',
                'static/bootstrap/fonts/*',
                'static/bootstrap/img/*',
                'static/bootstrap/js/*',
                'static/css/*',
                'static/js/*',
                'templates/*'
            ],
            'twisted': ['plugins/bouser_plugin.py'],
        },
        install_requires=[
            'twisted',  # Core
            'blinker',  # For signals
            'msgpack-python',  # Serialization
            'jinja2',  # Web
            'six',  # Compatibility
        ],
        extras_require={
            'YAML': 'PyYAML',
        },
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: No Input/Output (Daemon)",
            "Programming Language :: Python",
        ])

    try:
        from twisted.plugin import IPlugin, getPlugins
        list(getPlugins(IPlugin))
    except ImportError:
        print("Twisted not found.  Make sure you have installed the Twisted core package.")
        print("Twisted Plugins won't be refreshed")

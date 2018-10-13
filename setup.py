# generated by pylib shelly plugin version 1.7.3
        
from setuptools import setup, find_packages

# Version info -- read without importing
_locals = {}
with open('spatial_distribution_tourist_perception/_version.py') as fp:
    exec(fp.read(), None, _locals)
__version__ = _locals['__version__']

setup(name='spatial_distribution_tourist_perception',
      version=__version__,
      packages=find_packages(include='spatial_distribution_tourist_perception.*'),
      include_package_data=True,
      install_requires=[
          'pymongo',
      ],
      tests_require=[
          'pytest',
          'PyHamcrest',
      ],
      dependency_links=[
      ])
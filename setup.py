from setuptools import setup, find_packages
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.rst')).read()


version = '0.1.1'

install_requires = [
    'python-dateutil',
]

setup(name='srules',
      version=version,
      description="schedule rules",
      long_description=README + '\n\n' + NEWS,
      classifiers=[],
      keywords='',
      author='LCS',
      author_email='tchiroux@linkcareservices.com',
      url='http://linkcareservices.com',
      license='GPLv3',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires, )


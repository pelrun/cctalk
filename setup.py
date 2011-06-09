# Setup file to distribute cctalk package using distutils.
#
# The python-cctalk package allows one to send ccTalk messages and decode replies from a coin validator. 
license_text = "(C) 2011 David Schryer GNU GPLv3 or later."
__copyright__ = license_text

import os
from distutils.core import setup

package_name = 'cctalk'

setup(name=package_name,
      version='0.1',
      license=license,
      package_dir={package_name:package_name},
      packages=[package_name],
      long_description=open('README.txt').read(),
      )

# Setup file to distribute cctalk package using distutils.
#
# The python-cctalk package allows one to send ccTalk messages and decode replies from a coin validator. 
license_text = "(C) 2011 David Schryer GNU GPLv3 or later."
__copyright__ = license_text

import os
import glob
from distutils.core import setup

pn = 'cctalk'
pn_scripts = glob.glob('scripts/{0}.*'.format(pn))

setup(name=pn,
      version='0.1',
      license=license,
      package_dir={pn:pn},
      packages=[pn],
      scripts=pn_scripts,
      long_description=open('README.txt').read(),
      )

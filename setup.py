# Setup file to distribute cctalk package using distutils.
import os
from distutils.core import setup

package_name = 'cctalk'

setup(name=package_name,
      version='1.0',
      package_dir={package_name:package_name},
      packages=[package_name],
      )

# Setup file to distribute mytools package using distutils.
import os
from distutils.core import setup

script_dir = 'scripts'
package_name = 'mytools'
script_names = ['lm', 'qu', 'make_cpp_menu_files', 'temperature_profile', 'ft', 'kev']

scripts = []
for item in script_names:
    scripts.append(os.path.join(script_dir, item))

setup(name=package_name,
      version='1.0',
      package_dir={package_name:package_name},
      packages=[package_name],
      scripts=scripts
      )

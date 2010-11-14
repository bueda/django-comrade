from distutils.core import setup
import os

execfile('comrade/version.py')

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('comrade'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[8:] # Strip "comrade/" or "comrade\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(name='django-comrade',
      version = __version__,
      description='Bueda specific commonware',
      author='Christopher Peplin',
      author_email='peplin@bueda.com',
      url='http://github.com/bueda/django-comrade',
      package_dir={'comrade': 'comrade'},
      packages=packages,
      package_data={'comrade': data_files},
      classifiers=['Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Utilities'],
      )

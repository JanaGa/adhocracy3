"""Adhocracy backend customization package."""
import os
import version

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = ['adhocracy_core',
            ]

test_requires = ['adhocracy_core[test]',
                 ]

debug_requires = ['adhocracy_core[debug]',
                  ]

setup(name='adhocracy_meinberlin',
      version=version.get_git_version(),
      description='Adhocracy backend customization package',
      long_description=README + '\n\n' + CHANGES,
      classifiers=["Programming Language :: Python",
                   "Framework :: Pylons",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
                   ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons adhocracy',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      extras_require={'test': test_requires,
                      'debug': debug_requires,
                      },
      entry_points="""\
      [paste.app_factory]
      main = adhocracy_meinberlin:main
      [console_scripts]
      ad_meinberlin_import_bezirksregions=\
          adhocracy_meinberlin.scripts.ad_import_geodata:main
      ad_meinberlin_import_bezirke =\
          adhocracy_meinberlin.scripts.ad_import_geodata:main
      ad_meinberlin_create_process_for_region =\
          adhocracy_meinberlin.scripts.ad_create_process_for_region:main
      ad_meinberlin_change_german_salutation =\
          adhocracy_meinberlin.scripts.ad_translations:main
      """,
      )

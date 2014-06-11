Coding style guideline
======================

Testing
-------

* 100% test coverage (must)
* Test driven development with acceptance/functional, integration und unit test (should)

  * testing guideline: http://pyramid.readthedocs.org/en/latest/narr/testing.html
  * unit test examples substanced code, http://www.diveintopython.net/unit_testing/
  * testdriven concept: http://www.c2.com/cgi/wiki?TestDrivenDevelopment)

Python
------

Code formatting
+++++++++++++++

* 4 spaces instead of tabs (must)
* no trailing white space (must)

* `pep8 <http://legacy.python.org/dev/peps/pep-0008/>`_ (must)
* pyflakes (must)
* pylint (should)
* mcabe (should)

* Advances String Formatting `pep3101 <http://legacy.python.org/dev/peps/pep-3101/>`_ (must)

* Single Quotes for strings except for docstrings (must)

Docstring formatting
++++++++++++++++++++

* pep257 (must, bei tests und zope.Interface classes should)
* python 3 type annotation (must) according to
  https://pypi.python.org/pypi/sphinx_typesafe
* javadoc-style parameter descriptions, see
  http://sphinx-doc.org/domains.html#info-field-lists (should)
* example::

    def methodx(self, a: dict, flag=False) -> str:
        """Do something.

        :param a: description for a
        :param flag: description for flag

        """


Imports
+++++++

* one import per line
* don't use * to import everything from a module
* don't use relative import paths
* dont catch ``ImportError`` to detect wheter a package is available or not, as
  it might hide circular import errors. Instead use
  ``pkgresources.getdistribution`` and catch ``DistributionNotFound``.
  (http://do3.cc/blog/2010/08/20/do-not-catch-import-errors,-use-pkg_resources/)

Javascript
----------

* 4 spaces instead of tabs (must)
* no trailing white space (must)
* jshint formatting rules (should)
* `tslint <https://github.com/palantir/tslint>`_ (must)

CSS/Compass
-----------

See :doc:`CSS_Guidelines`.

Restructured text
+++++++++++++++++

* 4 spaces instead of tabs (must)
* no trailing white space (must)
* Headline hierarchy: ===== ----- +++++ ~~~~~~~ ****** (must)

Translation
===========

Markup translatable strings
---------------------------

For translations in the frontend we use `angular-translate`_.  It
offers several ways of marking a string as translatable, but we
mainly use the ``translate`` filter in templates::

   <a href="#">{{ "TR__LOGIN" | translate }}</a>
   <a href="#">{{ "TR__USERS_PROPOSALS" | translate:{name: adhUser.name} }}</a>

In few cases it is not possible to do translation in the template.
In these cases you can also use the ``$translate`` service. Note that
this service returns a promise::

   $translate("TR__LOGIN").then((translated) => {
       ...
   });

In our code we do not use actual human language. Instead, we use
technical strings (uppercase, with underscores, prefixed with ``TR__``).


String extraction
-----------------

angular-translate does not provide a script to extract translatable
strings.  So we hacked our own:

-  ``adhocracy_frontend/scripts/extract_messages.sh`` will output
   a list of all translatable strings in the current git subtree.

   .. NOTE: It relies on the ``TR__`` prefix to find translatable
      strings in TypeScript code.

-  You can pipe the output into
   ``adhocracy_frontend/scripts/merge_messages.py`` to update the
   JSON files.  It takes two parameters: The package name and a filename
   prefix, e.g.::

      adhocracy_frontend/scripts/merge_messages.py adhocracy_frontend core

So in order to update the translation files in the "foo" package, you
can use the following command::

   cd src/foo/
   ../adhocracy_frontend/adhocracy_frontend/scripts/extract_messages.sh | python3 ../adhocracy_frontend/adhocracy_frontend/scripts/merge_messages.py foo foo

.. NOTE:: Both scripts are not of good quality and may not cover all
   edge-cases.


Translation
-----------

Translators can use `transifex`_ for translation. Note that changes in
transifex are not instantly reflected in neither the code nor any
running platform. In order to pull changes from transifex into the code,
the transifex-client can be used::

   $ cd src/adhocracy_frontend/
   $ tx pull -a

.. NOTE:: The configuration for transifex-client is stored in
   ``src/{package_name}/.tx/config``.

.. WARNING:: Transifex requires us to specify a "source language"
   (currently English). This has the benefit that translators do not
   need to handle technical strings. But it also has several
   disadvantages:

   -  The source language can not be translated on transifex.

   -  All translations will be lost when the string in the source
      language is changed.

   -  Downloaded translation files will contain all keys. Any key
      that does not have a translation will have the translation from
      the source language as a value.

   An alternative could be to have a fake source language that simply
   has the technical strings themselves as translations and an exotic
   locale.


German Du/Sie
-------------

Adhocracy is currently used mostly in Germany, i.e. in German language.
Unfortunately, there are two variants of German, a formal (Sie) and an
informal (Du) one.

All translations should use the informal variant.  The script
``bin/change_german_salutation`` can be used to convert informal
translations to formal ones.  Note that you will need to extend that
script whenever the translation changes. The common workflow for this
is: Iteratively run the script, check the output and add new rules until
everything is fine.


.. _angular-translate: https://angular-translate.github.io
.. _transifex: https://www.transifex.com/liqd/adhocracy3/

"""Script to import/create resources into the system."""
import argparse
import inspect
import logging
import sys
import transaction

from pyramid.paster import bootstrap

from . import import_resources


resources_epilog = """The JSON file contains the interface name of the resource
type to create and a serialization of the sheets data.

Strings having the form 'user_by_login: <username>' are resolved
to the user's path.

Example::

[
 {"path": "/organisation",
  "creator": "god",
  "content_type": "adhocracy_core.resources.organisation.IOrganisation",
  "data": {"adhocracy_core.sheets.name.IName": {"name": "alt-treptow"}},
 },
]
"""


def main():  # pragma: no cover
    """Import resources from a JSON file."""
    docstring = inspect.getdoc(main)
    parser = argparse.ArgumentParser(description=docstring,
                                     epilog=resources_epilog)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('filename',
                        type=str,
                        help='file containing the resources descriptions')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    import_resources(env['root'], env['registry'], args.filename)
    transaction.commit()
    env['closer']()

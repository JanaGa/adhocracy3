"""Export proposals and count 'lost' rates of older versions.

This is registered as console script 'export_mercator_lost_rates' in setup.py.

"""

import argparse
import csv
import inspect
from pyramid.paster import bootstrap
from pyramid.registry import Registry

from adhocracy_core.interfaces import IResource
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.rate import IRate
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.sheets.pool import IPool
from adhocracy_core.resources.principal import IUser
from adhocracy_core.utils import create_filename
from adhocracy_mercator.scripts.export_users import get_most_rated_proposals
from adhocracy_mercator.scripts.export_users import get_titles


def export_lost_rates():
    """Export all proposals and count 'lost' rates of older versions.

    usage::

        bin/export_mercator_lost_rates etc/development.ini  10
    """
    docstring = inspect.getdoc(export_lost_rates)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('min_rate',
                        type=int,
                        help='minimal rate to restrict listed proposals')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    filename = create_filename(directory='./var/export/',
                               prefix='adhocracy-lost-rates',
                               suffix='.csv')
    _export_lost_rates(env['root'], filename, env['registry'],
                       min_rate=args.min_rate)
    env['closer']()


def _export_lost_rates(root: IResource, filename: str, registry: Registry,
                       min_rate=0):
    proposals = get_most_rated_proposals(root, min_rate)
    proposals_titles = get_titles(proposals)
    column_names = proposals_titles
    with open(filename, 'w', newline='') as result_file:
        wr = csv.writer(result_file, delimiter=';', quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
        wr.writerow(column_names)
        row = []
        for pos, proposal in enumerate(proposals):
            users = _get_rate_users(proposal)
            lost_users = _get_lost_rate_users(proposal, users, registry)
            count = 'all: {0} lost: {1}'.format(len(users), len(lost_users))
            row.append(count)
            print('exported proposal {0} of {1}'.format(pos, len(proposals)))
        wr.writerow(row)
    print('Proposals exported to {0}'.format(filename))


def _get_lost_rate_users(rateable: IRateable,
                         rate_users: set(IUser),
                         registry: Registry,
                         ) -> set(IUser):
    lost_rate_users = set()
    old_versions = _get_old_versions(rateable, registry)
    for old in old_versions:
        old_rate_users = _get_rate_users(old, registry)
        old_lost = old_rate_users.difference(rate_users)
        lost_rate_users.update(old_lost)
    return lost_rate_users


def _get_old_versions(version: IVersionable,
                      registry: Registry) -> [IVersionable]:
    follows = registry.content.get_sheet_field(version,
                                               IVersionable,
                                               'follows')
    versions = []
    while follows:
        old_version = follows[0]
        versions.append(old_version)
        follows = registry.content.get_sheet_field(old_version,
                                                   IVersionable,
                                                   'follows')
    return versions


def _get_rate_users(rateable: IRateable, registry: Registry) -> set(IUser):
    params = {'depth': 3,
              'interfaces': IRate,
              'indexes': {'tag': 'LAST',
                          'rate': 1},
              'resolve': 'True',
              'references': [(None, IRate, 'object', rateable)]
              }
    pool = registry.content.get_sheet(rateable.__parent__, IPool)
    rates = pool.get(params)['elements']
    get_sheet_field = registry.content.get_sheet_field
    users = [get_sheet_field(x, IRate, 'subject') for x in rates]
    return set(users)

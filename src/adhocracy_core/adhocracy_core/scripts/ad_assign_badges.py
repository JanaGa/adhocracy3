"""Assign badges to proposals.

The functions of that script are registered as console script in
setup.py.

"""

import inspect
import logging

import argparse
import transaction
from pyramid.paster import bootstrap
from pyramid.traversal import find_resource
from pyramid.registry import Registry
from substanced.util import find_service

from adhocracy_core.resources.principal import IUser
from adhocracy_core.resources.badge import IBadge
from adhocracy_core.resources.badge import IBadgeAssignment
from adhocracy_core import sheets
from adhocracy_core.interfaces import IResource
from adhocracy_core.utils import load_json


logger = logging.getLogger(__name__)


def main():  # pragma: no cover
    """Assign badges to proposals.

    usage::
      bin/assign_badges <config> <jsonfile>
    """
    args = _parse_args()
    env = bootstrap(args.ini_file)
    root = env['root']
    registry = env['registry']
    import_assignments(root, registry, args.jsonfile)
    transaction.commit()
    env['closer']()


def _parse_args():  # pragma: no cover
    docstring = inspect.getdoc(main)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('jsonfile',
                        type=str,
                        help='path to jsonfile')

    return parser.parse_args()


def import_assignments(root: IResource, registry: Registry, filename: str):
    """Import badge assignments."""
    entries = load_json(filename)
    for entry in entries:
        user, badge, badgeable = _find_resources(root, entry)
        description = entry['description']
        create_badge_assignment(user, badge, badgeable, description, registry)


def _find_resources(root,
                    entry: dict) -> (IUser, IBadge, sheets.badge.IBadgeable):
    userpath = entry.get('user')
    user = find_resource(root, userpath)
    badgepath = entry.get('badge')
    badge = find_resource(root, badgepath)
    badgeablepath = entry.get('badgeable')
    badgeable = find_resource(root, badgeablepath)
    return user, badge, badgeable


def create_badge_assignment(user: IUser,
                            badge: IBadge,
                            badgeable: sheets.badge.IBadgeable,
                            description: str,
                            registry: Registry) -> IBadgeAssignment:
    """Create badge assignment."""
    assignment_appstruct = {'subject': user,
                            'badge': badge,
                            'object': badgeable}
    appstructs = {sheets.badge.IBadgeAssignment.__identifier__:
                  assignment_appstruct}
    if description != '':  # pragma: no branch
        appstructs[sheets.description.IDescription.__identifier__] =\
            {'description': description}
    assignments = find_service(badgeable, 'badge_assignments')
    if _assignment_exists(assignment_appstruct, assignments, registry):
        logger.warn('Assignment already exists, skipping. {}'
                    .format(assignment_appstruct))
        return None
    assignment = registry.content.create(IBadgeAssignment.__identifier__,
                                         parent=assignments,
                                         appstructs=appstructs)
    return assignment


def _assignment_exists(assignment_appstruct: dict, assignments: IResource,
                       registry: Registry):
    for assignment in assignments.values():
        if assignment_appstruct == \
           registry.content.get_sheet(assignment,
                                      sheets.badge.IBadgeAssignment).get():
            return True
    return False

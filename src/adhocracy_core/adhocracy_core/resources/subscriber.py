"""Autoupdate resources."""
from base64 import b64encode
from collections import Sequence
from logging import getLogger
from os import urandom

from pyramid.registry import Registry
from pyramid.request import Request
from pyramid.settings import asbool
from pyramid.i18n import TranslationStringFactory
from substanced.util import find_service

from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import ISimple
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import ISheetReferenceNewVersion
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.resources.principal import IGroup
from adhocracy_core.resources.principal import IUser
from adhocracy_core.resources.principal import IPasswordReset
from adhocracy_core.resources.asset import add_metadata
from adhocracy_core.resources.asset import IAsset
from adhocracy_core.resources.image import add_image_size_downloads
from adhocracy_core.resources.image import IImage
from adhocracy_core.sheets.principal import IPermissions
from adhocracy_core.exceptions import AutoUpdateNoForkAllowedError
from adhocracy_core.utils import find_graph
from adhocracy_core.utils import get_following_new_version
from adhocracy_core.utils import get_last_new_version_in_transaction
from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import get_sheet_field
from adhocracy_core.utils import get_iresource
from adhocracy_core.utils import get_last_version
from adhocracy_core.utils import get_modification_date
from adhocracy_core.utils import get_user
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.asset import IAssetData


logger = getLogger(__name__)

_ = TranslationStringFactory('adhocracy')


def update_modification_date_modified_by(event):
    """Update the IMetadata fields `modified_by` and `modification_date`."""
    sheet = get_sheet(event.object, IMetadata, registry=event.registry)
    request = event.request
    appstruct = {}
    appstruct['modification_date'] = get_modification_date(event.registry)
    if request is not None:
        appstruct['modified_by'] = get_user(request)
    sheet.set(appstruct,
              send_event=False,
              request=request,
              omit_readonly=False,
              )


def add_default_group_to_user(event):
    """Add default group to user if no group is set."""
    group = _get_default_group(event.object)
    if group is None:
        return
    user_groups = _get_user_groups(event.object, event.registry)
    if user_groups:
        return None
    _add_user_to_group(event.object, group, event.registry)


def _get_default_group(context) -> IGroup:
    groups = find_service(context, 'principals', 'groups')
    default_group = groups.get('authenticated', None)
    return default_group


def _get_user_groups(user: IUser, registry: Registry):
    from pyramid.traversal import resource_path
    from adhocracy_core.interfaces import IRolesUserLocator
    request = Request.blank('/')
    request.registry = registry
    locator = registry.getMultiAdapter((user, request), IRolesUserLocator)
    user_id = resource_path(user)
    groups = locator.get_groups(user_id)
    return groups


def _add_user_to_group(user: IUser, group: IGroup, registry: Registry):
    sheet = get_sheet(user, IPermissions)
    groups = sheet.get()['groups']
    groups = groups + [group]
    sheet.set({'groups': groups})


def autoupdate_versionable_has_new_version(event):
    """Auto updated versionable resource if a reference has new version.

    :raises AutoUpdateNoForkAllowedError: if a fork is created but not allowed
    """
    if not _is_in_root_version_subtree(event):
        return
    sheet = get_sheet(event.object, event.isheet, event.registry)
    if not sheet.meta.editable:
        return
    appstruct = _get_updated_appstruct(event, sheet)
    new_version = _get_last_version_created_in_transaction(event)
    if new_version is None:
        if _new_version_needed_and_not_forking(event):
            _create_new_version(event, appstruct)
    else:
        new_version_sheet = get_sheet(new_version, event.isheet,
                                      event.registry)
        new_version_sheet.set(appstruct)


def _is_in_root_version_subtree(event: ISheetReferenceNewVersion) -> bool:
    if event.root_versions == []:
        return True
    graph = find_graph(event.object)
    return graph.is_in_subtree(event.object, event.root_versions)


def _get_updated_appstruct(event: ISheetReferenceNewVersion,
                           sheet: ISheet) -> dict:
    appstruct = sheet.get()
    field = appstruct[event.isheet_field]
    if isinstance(field, Sequence):
        old_version_index = field.index(event.old_version)
        field.pop(old_version_index)
        field.insert(old_version_index, event.new_version)
    else:
        appstruct[event.isheet_field] = event.new_version
    return appstruct


def _get_last_version_created_in_transaction(event: ISheetReferenceNewVersion)\
        -> IItemVersion:
    if event.is_batchmode:
        new_version = get_last_new_version_in_transaction(event.registry,
                                                          event.object)
    else:
        new_version = get_following_new_version(event.registry, event.object)
    return new_version


def _new_version_needed_and_not_forking(event: ISheetReferenceNewVersion)\
        -> bool:
    """Check whether to autoupdate if resource is non-forkable.

    If the given resource is the last version or there's no last version yet,
    do autoupdate.

    If it's not the last version, but references the same object (namely the
    one which caused the autoupdate), don't update.

    If it's not the last version, but references a different object,
    throw an AutoUpdateNoForkAllowedError. This should only happen in batch
    requests.
    """
    last = get_last_version(event.object, event.registry)
    if last is None or last is event.object:
        return True
    value = get_sheet_field(event.object, event.isheet, event.isheet_field,
                            event.registry)
    last_value = get_sheet_field(last, event.isheet, event.isheet_field,
                                 event.registry)
    if last_value == value:
        return False
    else:
        raise AutoUpdateNoForkAllowedError(event.object, event)


def _create_new_version(event, appstruct) -> IResource:
    appstructs = _get_writable_appstructs(event.object, event.registry)
    appstructs[IVersionable.__identifier__]['follows'] = [event.object]
    appstructs[event.isheet.__identifier__] = appstruct
    registry = event.registry
    iresource = get_iresource(event.object)
    new_version = registry.content.create(iresource.__identifier__,
                                          parent=event.object.__parent__,
                                          appstructs=appstructs,
                                          creator=event.creator,
                                          registry=event.registry,
                                          root_versions=event.root_versions,
                                          is_batchmode=event.is_batchmode,
                                          )
    return new_version


def _get_writable_appstructs(resource, registry) -> dict:
    appstructs = {}
    sheets = registry.content.get_sheets_all(resource)
    for sheet in sheets:
        editable = sheet.meta.editable
        creatable = sheet.meta.creatable
        if editable or creatable:  # pragma: no branch
            appstructs[sheet.meta.isheet.__identifier__] = sheet.get()
    return appstructs


def autoupdate_non_versionable_has_new_version(event):
    """Auto update non versionable resources if a reference has new version."""
    if not _is_in_root_version_subtree(event):
        return
    sheet = get_sheet(event.object, event.isheet, event.registry)
    if not sheet.meta.editable:
        return
    appstruct = _get_updated_appstruct(event, sheet)
    sheet.set(appstruct)


def send_password_reset_mail(event):
    """Send mail with reset password link if a reset resource is created."""
    user = get_sheet_field(event.object, IMetadata, 'creator')
    password_reset = event.object
    event.registry.messenger.send_password_reset_mail(user, password_reset)


def send_activation_mail_or_activate_user(event):
    """Send mail with activation link if a user is created.

    If the setting "adhocracy.skip_registration_mail" is true, no mail is send
    but the user is activated directly.
    """
    settings = event.registry.settings
    user = event.object
    skip_mail = asbool(settings.get('adhocracy.skip_registration_mail', False))
    if skip_mail:
        user.activate()
        return
    activation_path = _generate_activation_path()
    user.activation_path = activation_path
    messenger = getattr(event.registry, 'messenger', None)
    if messenger is not None:  # ease testing
        messenger.send_registration_mail(user, activation_path)


def _generate_activation_path() -> str:
    random_bytes = urandom(18)
    # TODO: not DRY, .resources.generate_name does almost the same
    # We use '+_' as altchars since both are reliably recognized in URLs,
    # even if they occur at the end. Conversely, '-' at the end of URLs is
    # not recognized as part of the URL by some programs such as Thunderbird,
    # and '/' might cause problems as well, especially if it occurs multiple
    # times in a row.
    return '/activate/' + b64encode(random_bytes, altchars=b'+_').decode()


def update_asset_download(event):
    """Update asset download."""
    add_metadata(event.object, event.registry)


def update_image_downloads(event):
    """Update image downloads."""
    add_image_size_downloads(event.object, event.registry)


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(autoupdate_versionable_has_new_version,
                          ISheetReferenceNewVersion,
                          object_iface=IItemVersion,
                          event_isheet=ISheetReferenceAutoUpdateMarker)
    config.add_subscriber(autoupdate_non_versionable_has_new_version,
                          ISheetReferenceNewVersion,
                          object_iface=IPool,
                          event_isheet=ISheetReferenceAutoUpdateMarker)
    config.add_subscriber(autoupdate_non_versionable_has_new_version,
                          ISheetReferenceNewVersion,
                          object_iface=ISimple,
                          event_isheet=ISheetReferenceAutoUpdateMarker)
    config.add_subscriber(add_default_group_to_user,
                          IResourceCreatedAndAdded,
                          object_iface=IUser)
    config.add_subscriber(send_activation_mail_or_activate_user,
                          IResourceCreatedAndAdded,
                          object_iface=IUser)
    config.add_subscriber(update_modification_date_modified_by,
                          IResourceSheetModified,
                          object_iface=IMetadata)
    config.add_subscriber(send_password_reset_mail,
                          IResourceCreatedAndAdded,
                          object_iface=IPasswordReset)
    config.add_subscriber(update_asset_download,
                          IResourceSheetModified,
                          object_iface=IAsset,
                          event_isheet=IAssetData)
    config.add_subscriber(update_image_downloads,
                          IResourceSheetModified,
                          object_iface=IImage,
                          event_isheet=IAssetData)

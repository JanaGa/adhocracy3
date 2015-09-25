"""Tests for the principal package."""
import unittest
from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import mark
from pytest import fixture


@fixture
def integration(integration):
    integration.include('pyramid_mailer.testing')
    integration.include('pyramid_mako')
    integration.include('adhocracy_core.changelog')
    integration.include('adhocracy_core.messaging')
    return integration


@fixture
def mock_is_older(monkeypatch):
    from adhocracy_core.sheets.metadata import is_older_than
    from . import principal
    mock = Mock(spec=is_older_than)
    monkeypatch.setattr(principal, 'is_older_than', mock)
    return mock


@fixture
def principals(pool_with_catalogs, registry):
    from adhocracy_core.resources.principal import IPrincipalsService
    inst = registry.content.create(IPrincipalsService.__identifier__,
                                   parent=pool_with_catalogs)
    return inst


class TestPrincipalsService:

    @fixture
    def meta(self):
        from .principal import principals_meta
        return principals_meta

    def test_meta(self, meta, context):
        from adhocracy_core import sheets
        from . import badge
        from . import principal
        assert meta.iresource is principal.IPrincipalsService
        assert meta.permission_create == 'create_service'
        assert meta.content_name == 'principals'
        assert meta.extended_sheets == \
            (sheets.badge.IHasBadgesPool,)
        assert badge.add_badges_service in meta.after_creation

    @mark.usefixtures('integration')
    def test_create(self, meta, registry, pool):
        resource = registry.content.create(meta.iresource.__identifier__,
                                           parent=pool)
        assert meta.iresource.providedBy(resource)

    @mark.usefixtures('integration')
    def test_register_services(self, meta, registry, pool):
        from substanced.util import find_service
        registry.content.create(meta.iresource.__identifier__, parent=pool)
        assert find_service(pool, 'principals', 'users')
        assert find_service(pool, 'principals', 'groups')
        assert find_service(pool, 'principals', 'resets')


class TestUsers:

    @fixture
    def meta(self):
        from .principal import users_meta
        return users_meta

    def test_meta(self, meta):
        from . import badge
        from . import principal
        assert meta.iresource is principal.IUsersService
        assert meta.permission_create == 'create_service'
        assert meta.content_name == 'users'
        assert badge.add_badge_assignments_service in meta.after_creation

    @mark.usefixtures('integration')
    def test_create(self, meta, registry):
        resource = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(resource)


class TestUser:

    @fixture
    def meta(self):
        from .principal import user_meta
        return user_meta

    def test_meta(self, meta):
        from . import principal
        import adhocracy_core.sheets
        assert meta.iresource is principal.IUser
        assert meta.content_class == principal.User  # TODO do we really need this class?
        assert meta.permission_create == 'create_user'
        assert meta.is_implicit_addable is False
        assert meta.basic_sheets == (adhocracy_core.sheets.principal.IUserBasic,
                                     adhocracy_core.sheets.principal.IUserExtended,
                                     adhocracy_core.sheets.principal.IPermissions,
                                     adhocracy_core.sheets.metadata.IMetadata,
                                     adhocracy_core.sheets.pool.IPool,
                                     )
        assert meta.extended_sheets == \
            (adhocracy_core.sheets.principal.IPasswordAuthentication,
                adhocracy_core.sheets.rate.ICanRate,
                adhocracy_core.sheets.badge.ICanBadge,
                adhocracy_core.sheets.badge.IBadgeable,
            )
        assert meta.element_types == ()
        assert meta.use_autonaming is True

    @mark.usefixtures('integration')
    def test_create(self, meta, registry, principals):
        from zope.interface.verify import verifyObject
        from adhocracy_core import sheets
        appstructs = {
            sheets.principal.IUserBasic.__identifier__ : {
                'name': 'Anna Müller',
            },
            sheets.principal.IPasswordAuthentication.__identifier__ : {
                'password': 'fodThyd2'
            },
        }
        user = registry.content.create(meta.iresource.__identifier__,
                                       parent=principals['users'],
                                       appstructs=appstructs)
        assert principals['users']['0000000'] is user
        assert meta.iresource.providedBy(user)
        assert verifyObject(meta.iresource, user)
        assert user.email == ''
        assert user.password.startswith('$2')
        assert user.tzname == 'UTC'
        assert user.roles == []


class TestGroups:

    @fixture
    def meta(self):
        from .principal import groups_meta
        return groups_meta

    def test_meta(self, meta):
        from . import principal
        assert meta.iresource is principal.IGroupsService
        assert meta.permission_create == 'create_service'
        assert meta.content_name == 'groups'

    @mark.usefixtures('integration')
    def test_create(self, meta, registry):
        resource = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(resource)


class TestGroup:

    @fixture
    def meta(self):
        from .principal import group_meta
        return group_meta

    def test_meta(self, meta):
        from . import principal
        assert meta.iresource is principal.IGroup
        assert meta.content_class == principal.Group
        assert meta.permission_create == 'create_group'
        assert meta.is_implicit_addable is False
        assert meta.element_types == ()

    @mark.usefixtures('integration')
    def test_create(self, meta, registry):
        from zope.interface.verify import verifyObject
        resource = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(resource)
        assert verifyObject(meta.iresource, resource)
        assert resource.roles == []

    @mark.usefixtures('integration')
    def test_create_and_add_group(self, registry, principals):
        from . import principal
        from adhocracy_core.utils import get_sheet
        from adhocracy_core import sheets
        appstructs = {sheets.name.IName.__identifier__: {'name': 'Group1'},
                      sheets.principal.IGroup.__identifier__:
                           {'roles': ['reader']}}
        group = registry.content.create(principal.IGroup.__identifier__,
                                        parent=principals['groups'],
                                        appstructs=appstructs)
        appstructs = {sheets.principal.IPermissions.__identifier__:
                          {'groups': [group]}}
        user = registry.content.create(principal.IUser.__identifier__,
                                       parent=principals['users'],
                                       appstructs=appstructs)
        user.activate()
        group_sheet = get_sheet(group, sheets.principal.IGroup)
        assert principals['groups']['Group1'] is group
        assert group_sheet.get()['users'] == [user]
        assert group_sheet.get()['roles'] == ['reader']


class TestPasswordResets:

    @fixture
    def meta(self):
        from .principal import passwordresets_meta
        return passwordresets_meta

    def test_meta(self, meta):
        from . import principal
        assert meta.iresource is principal.IPasswordResetsService
        assert meta.permission_create == 'create_service'
        assert meta.content_name == 'resets'

    @mark.usefixtures('integration')
    def test_create(self, meta, registry):
        resource = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(resource)

    @mark.usefixtures('integration')
    def test_remove_view_permission(self, meta, registry):
        from adhocracy_core.authorization import get_acl
        resource = registry.content.create(meta.iresource.__identifier__)
        acl = get_acl(resource)
        assert acl == [('deny', 'system.Everyone', 'view')]

    @mark.usefixtures('integration')
    def test_hide(self, meta, registry):
        """Even if view permission is not checked, we don't want to expose
        password resets to the client. So in addition we hide them."""
        resource = registry.content.create(meta.iresource.__identifier__)
        assert resource.hidden


class TestPasswordReset:

    @fixture
    def meta(self):
        from .principal import passwordreset_meta
        return passwordreset_meta

    def test_meta(self, meta):
        from . import principal
        import adhocracy_core.sheets
        assert meta.iresource is principal.IPasswordReset
        assert meta.permission_create == 'create_password_reset'
        assert meta.use_autonaming_random
        assert meta.basic_sheets == (adhocracy_core.sheets.metadata.IMetadata,)

    @mark.usefixtures('integration')
    def test_create(self, meta, registry, pool):
        from zope.interface.verify import verifyObject
        from .principal import IPasswordReset
        resource = registry.content.create(meta.iresource.__identifier__)
        assert IPasswordReset.providedBy(resource)
        assert verifyObject(IPasswordReset, resource)

    @mark.usefixtures('integration')
    def test_reset_password(self, registry, principals):
        from . import principal
        user = registry.content.create(principal.IUser.__identifier__,
                                       parent=principals['users'],
                                       appstructs={})
        reset = registry.content.create(principal.IPasswordReset.__identifier__,
                                        parent=principals['resets'],
                                        creator=user)
        old_password = user.password
        reset.reset_password('new_password')
        new_password = user.password
        assert old_password != new_password

    @mark.usefixtures('integration')
    def test_suicide_after_reset_password(self, registry, principals):
        from . import principal
        user = registry.content.create(principal.IUser.__identifier__,
                                       parent=principals['users'],
                                       appstructs={})
        reset = registry.content.create(principal.IPasswordReset.__identifier__,
                                        parent=principals['resets'],
                                        creator=user)
        reset.reset_password('new_password')
        assert reset.__parent__ is None

    @mark.usefixtures('integration')
    def test_activate_after_reset_password(self, registry, principals):
        from . import principal
        user = registry.content.create(principal.IUser.__identifier__,
                                       parent=principals['users'],
                                       appstructs={})
        reset = registry.content.create(principal.IPasswordReset.__identifier__,
                                        parent=principals['resets'],
                                        creator=user)
        reset.reset_password('new_password')
        assert user.active

    @mark.usefixtures('integration')
    def test_hide(self, meta, registry):
        """Even if view permission is not checked, we don't want to expose
        password resets to the client. So in addition we hide them."""
        resource = registry.content.create(meta.iresource.__identifier__)
        assert resource.hidden


class TestUserLocatorAdapter:

    @fixture
    def context(self, pool, service):
        from copy import deepcopy
        pool['principals'] = service
        pool['principals']['users'] = deepcopy(service)
        return pool

    @fixture
    def request(self, context, registry_with_content):
        request = testing.DummyRequest(context=context)
        request.registry = registry_with_content
        return request

    @fixture
    def inst(self, context, request):
        from .principal import UserLocatorAdapter
        return UserLocatorAdapter(context, request)

    def test_create(self, inst):
        from adhocracy_core.interfaces import IRolesUserLocator
        from zope.interface.verify import verifyObject
        assert IRolesUserLocator.providedBy(inst)
        assert verifyObject(IRolesUserLocator, inst)

    def test_get_user_by_email_user_exists(self, context, request, inst):
        from .principal import IUser
        user = testing.DummyResource(email='test@test.de', __provides__=IUser)
        context['principals']['users']['User1'] = user
        assert inst.get_user_by_email('test@test.de') is user

    def test_get_user_by_email_user_not_exists(self, context, request, inst):
        from .principal import IUser
        user = testing.DummyResource(email='', __provides__=IUser)
        context['principals']['users']['User1'] = user
        assert inst.get_user_by_email('wrong@test.de') is None

    def test_get_user_by_login_user_exists(self, context, request, inst):
        from .principal import IUser
        user = testing.DummyResource(name='login name', __provides__=IUser)
        context['principals']['users']['User1'] = user
        other = testing.DummyResource()
        context['principals']['users']['other'] = other
        assert inst.get_user_by_login('login name') is user

    def test_get_user_by_login_user_not_exists(self, context, request, inst,
                                               mock_catalogs, search_result):
        mock_catalogs.search.return_value = search_result
        assert inst.get_user_by_login('wrong login name') is None

    def test_get_user_by_activation_path_user_exists(self, context, request, inst):
        from .principal import IUser
        user = testing.DummyResource(activation_path='/activate/foo',
                                     __provides__=IUser)
        context['principals']['users']['User1'] = user
        other = testing.DummyResource()
        context['principals']['users']['other'] = other
        assert inst.get_user_by_activation_path('/activate/foo') is user
        
    def test_get_user_by_activation_path_user_not_exists(self, context, request, inst):
        user = testing.DummyResource(activation_path=None)
        context['principals']['users']['User1'] = user
        assert inst.get_user_by_activation_path('/activate/no_such_link') is None

    def test_get_user_by_userid_user_exists(self, context, request, inst):
        user = testing.DummyResource()
        context['principals']['users']['User1'] = user
        assert inst.get_user_by_userid('/principals/users/User1') is user

    def test_get_user_by_userid_user_not_exists(self, context, request, inst):
        assert inst.get_user_by_userid('/principals/users/User1') is None

    def test_get_groupids_user_exists(self, context, mock_sheet, request, inst):
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.testing import register_sheet
        group = testing.DummyResource(__name__='group1')
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        mock_sheet.get.return_value = {'groups': [group]}
        user = testing.DummyResource()
        register_sheet(user, mock_sheet, request.registry)
        context['principals']['users']['User1'] = user
        assert inst.get_groupids('/principals/users/User1') == ['group:group1']

    def test_get_groupids_user_not_exists(self, context, request, inst):
        assert inst.get_groupids('/principals/users/User1') is None

    def test_get_role_and_group_role_ids_user_exists(self, context, request, inst):
        inst.get_user_by_userid = Mock()
        inst.get_user_by_userid.return_value = context
        inst.get_roleids = Mock()
        inst.get_roleids.return_value = ['role:admin']
        inst.get_group_roleids = Mock()
        inst.get_group_roleids.return_value = ['role:reader']
        assert inst.get_role_and_group_roleids('/principals/users/User1') ==\
               ['role:admin', 'role:reader']

    def test_get_role_and_group_roleids_user_not_exists(self, context, request, inst):
        assert inst.get_role_and_group_roleids('/principals/users/User1') is None

    def test_get_group_roleids_user_exists(self, inst, context, mock_sheet, request,
                                          ):
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.testing import register_sheet
        group = testing.DummyResource(__name__='group1', roles=[])
        user = testing.DummyResource()
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        mock_sheet.get.return_value = {'groups': [group]}
        register_sheet(user, mock_sheet, request.registry)
        group.roles = ['role1']
        context['principals']['users']['User1'] = user
        assert inst.get_group_roleids('/principals/users/User1') == ['role:role1']

    def test_get_group_roleids_user_not_exists(self, context, request, inst):
        assert inst.get_group_roleids('/principals/users/User1') is None

    def test_get_roleids_user_exists(self, context, mock_sheet, request, inst):
        from adhocracy_core.testing import register_sheet
        user = testing.DummyResource(roles=['role1'])
        register_sheet(user, mock_sheet, request.registry)
        context['principals']['users']['User1'] = user
        assert inst.get_roleids('/principals/users/User1') == ['role:role1']

    def test_get_roleids_user_not_exists(self, context, request, inst):
        assert inst.get_roleids('/principals/users/User1') is None


class UserLocatorAdapterIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy_core.content')
        self.config.include('adhocracy_core.resources.principal')
        self.context = testing.DummyResource()
        self.registry = self.config.registry

    def tearDown(self):
        testing.tearDown()

    def test_create(self):
        from adhocracy_core.interfaces import IRolesUserLocator
        assert self.registry.getMultiAdapter(
            (self.context,  testing.DummyRequest), IRolesUserLocator)


class TestGroupsAndRolesFinder:

    @fixture
    def request(self, context, registry):
        request = testing.DummyRequest(context=context)
        request.registry = registry
        return request

    def call_fut(self, userid, request):
        from adhocracy_core.resources.principal import groups_and_roles_finder
        return groups_and_roles_finder(userid, request)

    def test_userid_wrong(self, request,  mock_user_locator):
        assert self.call_fut('WRONG', request) == []
        assert mock_user_locator.get_groupids.call_args[0] == ('WRONG',)
        assert mock_user_locator.get_role_and_group_roleids.call_args[0] == ('WRONG',)

    def test_userid_with_roles(self, request, mock_user_locator):
        mock_user_locator.get_role_and_group_roleids.return_value = ['role:reader']
        assert self.call_fut('userid', request) == ['role:reader']

    def test_userid_with_groups_and_group_roles(self, request, mock_user_locator):
        mock_user_locator.get_role_and_group_roleids.return_value = ['group:Readers']
        assert self.call_fut('userid', request) == ['group:Readers']


class TestDeleteNotActiveUsers:

    @fixture
    def request_(self, context, registry):
        request = testing.DummyRequest(context=context)
        request.registry = registry
        return request

    @fixture
    def user(self):
        user = testing.DummyResource(active=False, email='', name='')
        return user

    @fixture
    def users(self, context, user):
        context['user'] = user
        return context

    def call_fut(self, *args):
        from .principal import delete_not_activated_users
        return delete_not_activated_users(*args)

    def test_delete_not_active_users_older_then_days(
            self, users, user, request_, mock_is_older, mock_user_locator):
        mock_is_older.return_value = True
        mock_user_locator.get_users.return_value = [user]
        self.call_fut(request_, 7)
        mock_is_older.assert_called_with(user, 7)
        assert 'user' not in users

    def test_ignore_not_active_user_younger_then_days(
            self, users, user, request_, mock_is_older, mock_user_locator):
        mock_is_older.return_value = False
        mock_user_locator.get_users.return_value = [user]
        self.call_fut(request_, 7)
        assert 'user' in users

    def test_ignore_active_user(
            self, users, user, request_, mock_user_locator):
        user.active = True
        mock_user_locator.get_users.return_value = [user]
        self.call_fut(request_, 7)
        assert 'user' in users


class TestDeletePasswordResets:

    @fixture
    def reset(self):
        reset = testing.DummyResource()
        return reset

    @fixture
    def resets(self, reset, monkeypatch):
        from . import principal
        mock = testing.DummyResource()
        mock['reset'] = reset
        monkeypatch.setattr(principal, 'find_service', lambda x, y, z: mock)
        return mock

    def call_fut(self, *args):
        from .principal import delete_password_resets
        return delete_password_resets(*args)

    def test_delete_resets_older_then_days(
            self, resets, reset, request_, mock_is_older):
        mock_is_older.return_value = True
        self.call_fut(request_, 7)
        mock_is_older.assert_called_with(reset, 7)
        assert 'reset' not in resets

    def test_ignore_resets_younger_then_days(
            self, resets, reset, request_, mock_is_older):
        mock_is_older.return_value = False
        self.call_fut(request_, 7)
        assert 'reset' in resets

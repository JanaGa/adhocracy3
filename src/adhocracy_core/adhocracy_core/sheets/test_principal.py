import colander
from pyramid import testing
from pytest import raises
from pytest import fixture
from pytest import mark


class TestPasswordSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.principal import password_meta
        return password_meta

    @fixture
    def inst(self, meta, context, registry):
        inst = meta.sheet_class(meta, context, registry)
        return inst

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.principal import IPasswordAuthentication
        from adhocracy_core.sheets.principal import PasswordAuthenticationSheet
        from adhocracy_core.sheets.principal import PasswordAuthenticationSchema
        inst = meta.sheet_class(meta, context, None)
        assert isinstance(inst, PasswordAuthenticationSheet)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IPasswordAuthentication
        assert inst.meta.schema_class == PasswordAuthenticationSchema
        assert inst.meta.permission_create == 'create_user'

    def test_set_password(self, inst):
        inst.set({'password': 'test'})
        assert len(inst.context.password) == 60

    def test_reset_password(self, inst):
        inst.set({'password': 'test'})
        password_old = inst.context.password
        inst.set({'password': 'test'})
        password_new = inst.context.password
        assert password_new != password_old

    def test_set_empty_password(self, inst):
        inst.set({'password': ''})
        assert not hasattr(inst.context, 'password')

    def test_get_password(self, inst):
        inst.context.password = 'test'
        assert inst.get()['password'] == 'test'

    def test_get_empty_password(self, inst):
        assert inst.get()['password'] == ''

    def test_check_password_valid(self, inst):
        inst.set({'password': 'test'})
        assert inst.check_plaintext_password('test')

    def test_check_password_not_valid(self, inst):
        inst.set({'password': 'test'})
        assert not inst.check_plaintext_password('wrong')

    def test_check_password_is_too_long(self, inst):
        password = 'x' * 40026
        with raises(ValueError):
            inst.check_plaintext_password(password)


@mark.usefixtures('integration')
def test_includeme_register_password_sheet(registry):
    from adhocracy_core.sheets.principal import IPasswordAuthentication
    context = testing.DummyResource(__provides__=IPasswordAuthentication)
    assert registry.content.get_sheet(context, IPasswordAuthentication)


class TestUserBasicSchema:

    def make_one(self):
        from adhocracy_core.sheets.principal import UserBasicSchema
        return UserBasicSchema()

    def test_deserialize_all(self):
        inst = self.make_one()
        cstruct = {'name': 'login'}
        assert inst.deserialize(cstruct) == cstruct

    def test_deserialize_name_missing(self):
        inst = self.make_one()
        with raises(colander.Invalid):
            inst.deserialize({})

    def test_deserialize_name_empty(self):
        inst = self.make_one()
        with raises(colander.Invalid):
            inst.deserialize({'name': ''})

    def test_deserialize_name(self):
        inst = self.make_one()
        assert inst.deserialize({'name': 'login'}) == {'name': 'login'}

    def test_name_has_deferred_validator(self):
        inst = self.make_one()
        assert isinstance(inst['name'].validator, colander.deferred)


class TestUserExtendedSchema:

    def make_one(self):
        from adhocracy_core.sheets.principal import UserExtendedSchema
        return UserExtendedSchema()

    def test_deserialize_all(self):
        inst = self.make_one()
        cstruct = {'email': 'test@test.de',
                   'tzname': 'Europe/Berlin'}
        assert inst.deserialize(cstruct) == cstruct

    def test_deserialize_email(self):
        inst = self.make_one()
        assert inst.deserialize(
            {'email': 'test@test.de'}) == {'email': 'test@test.de'}

    def test_deserialize_email_upper_case(self):
        inst = self.make_one()
        assert inst.deserialize(
            {'email': 'teST@test.de'}) == {'email': 'test@test.de'}

    def test_email_has_deferred_validator(self):
        inst = self.make_one()
        assert isinstance(inst['email'].validator, colander.deferred)


class TestCaptchaSchema:

    @fixture
    def mock_response(self, mocker):
        return mocker.Mock()

    @fixture
    def mock_post(self, mocker, mock_response):
        mock_post = mocker.patch('requests.post', autospec=True)
        mock_post.return_value = mock_response
        return mock_post

    def make_one(self, request):
        from adhocracy_core.sheets.principal import CaptchaSchema
        return CaptchaSchema().bind(request=request)

    def test_deserialize_and_validate_captcha(self, mock_response,
                                              mock_post, request_):
        inst = self.make_one(request_)
        mock_response.json.return_value = {'data': True}
        cstruct = {'id': 'captcha-id', 'solution': 'some test'}
        assert inst.deserialize(cstruct) == cstruct
        mock_post.assert_called_with('http://localhost:6542/solve_captcha',
                                     json={'solution': 'some test',
                                           'id': 'captcha-id'})

    def test_deserialize_raise_if_captcha_invalid(self, mock_response,
                                                   mock_post, request_):
        inst = self.make_one(request_)
        mock_response.json.return_value = {'data': False}
        cstruct = {'id': 'captcha-id', 'solution': 'some test'}
        with raises(colander.Invalid):
            inst.deserialize(cstruct) == cstruct

    def test_deserialize_raise_if_id_missing(self, request_):
        inst = self.make_one(request_)
        with raises(colander.Invalid):
            inst.deserialize({'solution': 'some test'})

    def test_deserialize_raise_if_solution_missing(self, request_):
        inst = self.make_one(request_)
        with raises(colander.Invalid):
            inst.deserialize({'id': 'captcha-id'})


class TestDeferredValidateUserName:

    def call_fut(self, node, kw):
        from adhocracy_core.sheets.principal import deferred_validate_user_name
        return deferred_validate_user_name(node, kw)

    def test_name_is_empty(self, node, kw, mock_user_locator):
        mock_user_locator.get_user_by_login.return_value = None
        validator = self.call_fut(node, kw)
        assert validator(node, '') is None

    def test_name_is_unique(self, node, kw, mock_user_locator):
        mock_user_locator.get_user_by_login.return_value = None
        validator = self.call_fut(node, kw)
        assert validator(node, 'unique') is None

    def test_name_is_not_unique(self, node, kw, mock_user_locator):
        mock_user_locator.get_user_by_login.return_value = object()
        validator = self.call_fut(node, kw)
        with raises(colander.Invalid):
            validator(node, 'not unique')


class TestDeferredValidateUserEmail:

    def call_fut(self, node, kw):
        from adhocracy_core.sheets.principal import deferred_validate_user_email
        return deferred_validate_user_email(node, kw)

    def test_email_is_empty(self, node, kw, mock_user_locator):
        mock_user_locator.get_user_by_email.return_value = None
        validator = self.call_fut(node, kw)
        with raises(colander.Invalid):
            validator(node, '') is None

    def test_email_is_wrong(self, node, kw, mock_user_locator):
        validator = self.call_fut(node, kw)
        with raises(colander.Invalid):
             validator(node, 'wrong_email') is None

    def test_email_is_unique(self, node, kw, mock_user_locator):
        mock_user_locator.get_user_by_email.return_value = None
        validator = self.call_fut(node, kw)
        assert validator(node, 'test@test.de') is None

    def test_email_is_not_unique(self, node, kw, mock_user_locator):
        mock_user_locator.get_user_by_email.return_value = object()
        validator = self.call_fut(node, kw)
        with raises(colander.Invalid):
            validator(node, 'not unique')


class TestUserBasicSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.principal import userbasic_meta
        return userbasic_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.principal import IUserBasic
        from adhocracy_core.sheets.principal import UserBasicSchema
        from adhocracy_core.sheets import AttributeResourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert isinstance(inst, AttributeResourceSheet)
        assert inst.meta.isheet == IUserBasic
        assert inst.meta.schema_class == UserBasicSchema
        assert inst.meta.permission_create == 'create_user'

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'name': ''}


class TestUserExtendedSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.principal import userextended_meta
        return userextended_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.principal import IUserExtended
        from adhocracy_core.sheets.principal import UserExtendedSchema
        from adhocracy_core.sheets import AttributeResourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert isinstance(inst, AttributeResourceSheet)
        assert inst.meta.isheet == IUserExtended
        assert inst.meta.schema_class == UserExtendedSchema
        assert inst.meta.permission_create == 'create_user'
        assert inst.meta.permission_view == 'view_userextended'
        assert inst.meta.permission_edit == 'edit_userextended'

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'email': '', 'tzname': 'UTC'}


class TestCaptchaSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.principal import captcha_meta
        return captcha_meta

    @fixture
    def inst(self, meta, context, registry):
        inst = meta.sheet_class(meta, context, registry)
        return inst

    def test_meta(self, meta):
        from . import principal
        assert meta.sheet_class == principal.CaptchaSheet
        assert meta.isheet == principal.ICaptcha
        assert meta.schema_class == principal.CaptchaSchema
        assert meta.permission_create == 'create_user'
        assert meta.readable is False
        assert meta.editable is False
        assert meta.creatable is False
        assert meta.create_mandatory is False

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_returns_default_values(self, inst):
        assert inst.get() == {'id': '', 'solution': ''}

    def test_set_does_not_store_data(self, inst):
        inst.set({'id': '1', 'solution': '1'})
        assert inst.get() == {'id': '', 'solution': ''}

    @mark.usefixtures('integration')
    def test_includeme_register(self, registry, meta):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)

    def test_includeme_set_create_mandatory_if_captcha_enabled(self, config,
                                                               meta):
        config.registry.settings['adhocracy.thentos_captcha.enabled'] = 'true'
        config.include('adhocracy_core.content')
        config.include('adhocracy_core.sheets.principal')
        meta_included = config.registry.content.sheets_meta[meta.isheet]
        assert meta_included.creatable
        assert meta_included.create_mandatory


class TestPermissionsSchema:

    @fixture
    def context(self, context):
        context.roles = []
        return context

    @fixture
    def group(self, context):
        group = testing.DummyResource()
        group.roles = []
        context['group'] = group
        return group

    @fixture
    def permissions_sheet(self, context, registry, mock_sheet):
        import copy
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.testing import register_sheet
        mock_sheet = copy.deepcopy(mock_sheet)
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IPermissions)
        register_sheet(context, mock_sheet, registry)
        return mock_sheet

    def make_one(self):
        from adhocracy_core.sheets.principal import PermissionsSchema
        return PermissionsSchema()

    def test_create(self):
        from .principal import get_group_choices
        inst = self.make_one()
        assert inst
        assert inst['groups'].choices_getter == get_group_choices

    def test_deserialize_empty(self):
        inst = self.make_one()
        assert inst.deserialize({}) == {'groups': []}

    def test_serialize_empty(self, context, request_):
        inst = self.make_one().bind(context=context, request=request_)
        assert inst.serialize({}) == {'groups': [],
                                      'roles': [],
                                      }

    def test_serialize_with_groups_and_roles(self, context, group, request_):
        context.roles = ['view']
        context.group_ids = ['/group']
        group.roles = ['admin']
        appstruct = {'groups': [group], 'roles': ['view']}
        inst = self.make_one().bind(context=context, request=request_)
        assert inst.serialize(appstruct) == \
            {'groups': [request_.application_url + '/group/'],
             'roles': ['view'],
             }


class TestGetGroupChoices:

    def call_fut(self, *args):
        from .principal import get_group_choices
        return get_group_choices(*args)

    def test_return_empty_list_if_no_assets_service(self, pool):
        assert self.call_fut(pool, None) == []

    def test_return_empty_list_if_empty_assets_service(self, pool, service):
        pool['principals'] = service
        pool['principals']['groups'] = service.clone()
        assert self.call_fut(pool, None) == []

    def test_get_asset_choices_from_assets_service(self, pool, request_,
                                                   service):
        from .principal import IGroup
        pool['principals'] = service
        pool['principals']['groups'] = service.clone()
        pool['principals']['groups']['group'] = \
            testing.DummyResource(__provides__=IGroup)
        pool['principals']['groups']['no_group'] = testing.DummyResource()
        choices = self.call_fut(pool, request_)
        assert choices == [('http://example.com/principals/groups/group/',
                            'group')]


class TestPermissionsSheet:

    @fixture
    def context(self, context):
        context.roles = []
        context.group_ids = []
        return context

    @fixture
    def inst(self, meta, context, registry):
        return meta.sheet_class(meta, context, registry)

    @fixture
    def meta(self):
        from adhocracy_core.sheets.principal import permissions_meta
        return permissions_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.principal import IPermissions
        from adhocracy_core.sheets.principal import PermissionsSchema
        from adhocracy_core.sheets.principal import \
            PermissionsAttributeResourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert isinstance(inst, PermissionsAttributeResourceSheet)
        assert inst.meta.isheet == IPermissions
        assert inst.meta.schema_class == PermissionsSchema
        assert inst.meta.permission_create == 'create_edit_sheet_permissions'
        assert inst.meta.permission_edit == 'create_edit_sheet_permissions'
        assert inst.meta.permission_view == 'view_userextended'

    def test_get_empty(self, inst):
        assert inst.get() == {'groups': [],
                              'roles': [],
                              }

    def test_set_groups(self, inst, context):
        group = testing.DummyResource()
        context['group'] = group
        inst.set({'groups': [group]})
        assert context.group_ids == ['/group']

    @mark.usefixtures('integration')
    def test_includeme_register_permissions_sheet(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)


class TestGroupSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.principal import group_meta
        return group_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.principal import IGroup
        from adhocracy_core.sheets.principal import GroupSchema
        from adhocracy_core.sheets import AttributeResourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert isinstance(inst, AttributeResourceSheet)
        assert inst.meta.isheet == IGroup
        assert inst.meta.schema_class == GroupSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'users': [],
                              'roles': [],
                              }

    @mark.usefixtures('integration')
    def test_includeme_register_sheet(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)

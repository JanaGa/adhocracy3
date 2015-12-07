import colander
from pyramid import testing
from pytest import fixture
from pytest import raises


class TestValidateLinearHistoryNoMerge:

    @fixture
    def last_version(self):
        return testing.DummyResource()

    @fixture
    def node(self):
        return testing.DummyResource()

    def call_fut(self, node, value):
        from .versions import validate_linear_history_no_merge
        return validate_linear_history_no_merge(node, value)

    def test_value_length_lt_1(self, node):
        with raises(colander.Invalid) as err:
            self.call_fut(node, [])
        assert err.value.msg.startswith('No merge allowed')

    def test_value_length_gt_1(self, node, last_version):
        with raises(colander.Invalid) as err:
            self.call_fut(node, [last_version, last_version])
        assert err.value.msg.startswith('No merge allowed')

    def test_value_length_eq_1(self, node, last_version):
        assert self.call_fut(node, [last_version]) is None


class TestValidateLinearHistoryNoFork:

    @fixture
    def node(self, context, request_):
        node = testing.DummyResource(bindings={})
        node.bindings['context'] = context
        node.bindings['request'] = request_
        return node

    @fixture
    def mock_sheet(self, mock_sheet, registry_with_content):
        registry_with_content.content.get_sheet.return_value = mock_sheet
        return mock_sheet

    @fixture
    def last(self, context):
        last = testing.DummyResource()
        context['last_version'] = last
        return last

    @fixture
    def other(self, context):
        other = testing.DummyResource()
        context['other_version'] = other
        return other

    def call_fut(self, node, value):
        from .versions import validate_linear_history_no_fork
        return validate_linear_history_no_fork(node, value)

    def test_ignore_if_value_is_last_version(
            self, node, last, mock_sheet):
        mock_sheet.get.return_value = {'LAST': last}
        assert self.call_fut(node, [last]) is None

    def test_raise_if_value_is_not_last_last_version(
            self, node, last, other, mock_sheet):
        mock_sheet.get.return_value = {'LAST': last}
        with raises(colander.Invalid) as err:
            self.call_fut(node, [other])
        assert err.value.msg == 'No fork allowed - valid follows resources '\
                                'are: /last_version'

    def test_batchmode_ignore_if_value_is_last(
            self, node, last, other, mock_sheet, changelog, request_):
        from adhocracy_core.utils import set_batchmode
        request_.registry.changelog = changelog
        set_batchmode(request_)
        mock_sheet.get.return_value = {'LAST': last}
        assert self.call_fut(node, [last]) is None

    def test_batchmode_raise_if_value_is_not_last_last_version(
            self, node, last, other, mock_sheet, changelog, request_):
        from adhocracy_core.utils import set_batchmode
        request_.registry.changelog = changelog
        set_batchmode(request_)
        mock_sheet.get.return_value = {'LAST': last}
        with raises(colander.Invalid) as err:
            self.call_fut(node, [other])
        assert err.value.msg == 'No fork allowed - valid follows resources '\
                                'are: /last_version'

    def test_batchmode_ingnore_if_last_new_new_version_in_transaction(
            self, node, last, other, mock_sheet, changelog, request_):
        from adhocracy_core.utils import set_batchmode
        request_.registry.changelog = changelog
        set_batchmode(request_)
        mock_sheet.get.return_value = {'LAST': last}
        request_.registry.changelog['/'] = changelog['/']._replace(
            last_version=other)
        assert self.call_fut(node, [other]) is None


class TestVersionsSchema:

    @fixture
    def inst(self):
        from adhocracy_core.sheets.versions import VersionableSchema
        return VersionableSchema()

    def test_follows_validators(self, inst):
        from .versions import validate_linear_history_no_merge
        from .versions import validate_linear_history_no_fork
        field = inst['follows']
        validators = field.validator(object(), {}).validators
        assert validators == (validate_linear_history_no_merge,
                              validate_linear_history_no_fork,
                              )


class TestVersionsSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.versions import versions_meta
        return versions_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.versions import IVersions
        from adhocracy_core.sheets.versions import VersionsSchema
        from adhocracy_core.sheets.pool import PoolSheet
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, PoolSheet)
        assert inst.meta.isheet == IVersions
        assert inst.meta.schema_class == VersionsSchema
        assert inst.meta.editable is False
        assert inst.meta.creatable is False

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': []}

    def test_get_not_empty(self, meta, context):
        context['child'] = testing.DummyResource()
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': []}


def test_includeme_register_version_sheet(config):
    from adhocracy_core.utils import get_sheet
    from adhocracy_core.sheets.versions import IVersions
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.versions')
    context = testing.DummyResource(__provides__=IVersions)
    assert get_sheet(context, IVersions)


class TestVersionableSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.versions import versionable_meta
        return versionable_meta

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.versions import IVersionable
        from adhocracy_core.sheets.versions import VersionableSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IVersionable
        assert inst.meta.schema_class == VersionableSchema

    def test_get_empty(self, meta, context, sheet_catalogs):
        inst = meta.sheet_class(meta, context)
        data = inst.get()
        assert list(data['follows']) == []
        assert list(data['followed_by']) == []

    def test_set_with_followed_by(self, meta, context):
        inst = meta.sheet_class(meta, context)
        inst.set({'followed_by': iter([])})
        appstruct = getattr(context, inst._annotation_key)
        assert not 'followed_by' in appstruct


def test_includeme_register_versionable_sheet(config):
    from adhocracy_core.utils import get_sheet
    from adhocracy_core.sheets.versions import IVersionable
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.versions')
    context = testing.DummyResource(__provides__=IVersionable)
    assert get_sheet(context, IVersionable)

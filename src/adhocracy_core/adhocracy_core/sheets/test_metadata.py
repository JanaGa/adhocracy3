from pyramid import testing
from pytest import fixture
from pytest import mark


def register_and_add_sheet(context, registry, mock_sheet):
    from zope.interface import alsoProvides
    from adhocracy_core.interfaces import IResourceSheet
    isheet = mock_sheet.meta.isheet
    alsoProvides(context, isheet)
    registry.registerAdapter(lambda x: mock_sheet, (isheet,),
                             IResourceSheet,
                             isheet.__identifier__)


class TestResourceModifiedMetadataSubscriber:

    def _call_fut(self, event):
        from adhocracy_core.sheets.metadata import resource_modified_metadata_subscriber
        return resource_modified_metadata_subscriber(event)

    def test_with_metadata_isheet(self, context, registry, mock_sheet,
                                  cornice_request):
        from datetime import datetime
        from adhocracy_core.sheets.metadata import IMetadata
        event = testing.DummyResource(object=context,
                                      registry=registry,
                                      request=cornice_request)
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IMetadata)
        register_and_add_sheet(context, registry, mock_sheet)

        self._call_fut(event)

        set_modification_date = mock_sheet.set.call_args[0][0]['modification_date']
        assert set_modification_date.date() == datetime.now().date()


class TestIMetadataSchema:

    def _make_one(self, **kwargs):
        from adhocracy_core.sheets.metadata import MetadataSchema
        return MetadataSchema(**kwargs)

    def test_deserialize_empty(self):
        inst = self._make_one()
        result = inst.deserialize({})
        assert result == {'deleted': False, 'hidden': False}

    def test_serialize_empty(self):
        from colander import null
        inst = self._make_one()
        result = inst.serialize({})
        assert result['creation_date'] == null
        assert result['creator'] == ''
        assert result['item_creation_date'] == null
        assert result['modification_date'] == null
        assert result['modified_by'] == ''
        assert result['deleted'] == 'false'
        assert result['hidden'] == 'false'

    def test_serialize_empty_and_bind(self):
        from datetime import datetime
        inst = self._make_one().bind()
        result = inst.serialize({})
        this_year = str(datetime.now().year)
        assert this_year in result['creation_date']
        assert this_year in result['item_creation_date']
        assert this_year in result['modification_date']


class TestMetadataSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.metadata import metadata_metadata
        return metadata_metadata

    def test_create(self, meta, context):
        from adhocracy_core.sheets.metadata import IMetadata
        from adhocracy_core.sheets.metadata import MetadataSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == IMetadata
        assert inst.meta.schema_class == MetadataSchema
        assert inst.meta.editable is True
        assert inst.meta.creatable is True
        assert inst.meta.readable is True


@fixture
def integration(config):
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.sheets.metadata')


@mark.usefixtures('integration')
def test_includeme_register_metadata_sheet(config):
    from adhocracy_core.sheets.metadata import IMetadata
    from adhocracy_core.utils import get_sheet
    context = testing.DummyResource(__provides__=IMetadata)
    assert get_sheet(context, IMetadata)


@mark.usefixtures('integration')
def test_includeme_register_metadata_update_subscriber(config):
    handlers = config.registry.registeredHandlers()
    handler_names = [x.handler.__name__ for x in handlers]
    assert 'resource_modified_metadata_subscriber' in handler_names


class TestVisibility:

    @fixture
    def resource_with_metadata(self, integration):
        from adhocracy_core.interfaces import IResource
        from adhocracy_core.sheets.metadata import IMetadata
        return testing.DummyResource(__provides__=[IResource, IMetadata])

    def test_is_deleted_attribute_is_true(self, context):
        from adhocracy_core.sheets.metadata import is_deleted
        context.deleted = True
        assert is_deleted(context) is True

    def test_is_deleted_attribute_is_false(self, context):
        from adhocracy_core.sheets.metadata import is_deleted
        context.deleted = False
        assert is_deleted(context) is False

    def test_is_deleted_attribute_not_set(self, context):
        from adhocracy_core.sheets.metadata import is_deleted
        assert is_deleted(context) is False

    def test_is_deleted_parent_attribute_is_true(self, context):
        from adhocracy_core.sheets.metadata import is_deleted
        child = testing.DummyResource()
        context['child'] = child
        context.deleted = True
        assert is_deleted(child) is True

    def test_is_deleted_parent_attribute_is_false(self, context):
        from adhocracy_core.sheets.metadata import is_deleted
        child = testing.DummyResource()
        context['child'] = child
        context.deleted = False
        assert is_deleted(child) is False

    def test_is_deleted_parent_attribute_not_set(self, context):
        from adhocracy_core.sheets.metadata import is_deleted
        child = testing.DummyResource()
        context['child'] = child
        assert is_deleted(child) is False

    def test_is_deleted_parent_attrib_true_child_attrib_false(self, context):
        from adhocracy_core.sheets.metadata import is_deleted
        child = testing.DummyResource()
        context['child'] = child
        context.deleted = True
        child.deleted = False
        assert is_deleted(child) is True

    def test_is_hidden_attribute_is_true(self, context):
        from adhocracy_core.sheets.metadata import is_hidden
        context.hidden = True
        assert is_hidden(context) is True

    def test_is_hidden_attribute_is_false(self, context):
        from adhocracy_core.sheets.metadata import is_hidden
        context.hidden = False
        assert is_hidden(context) is False

    def test_is_hidden_attribute_not_set(self, context):
        from adhocracy_core.sheets.metadata import is_hidden
        assert is_hidden(context) is False

    def test_is_hidden_parent_attribute_is_true(self, context):
        from adhocracy_core.sheets.metadata import is_hidden
        child = testing.DummyResource()
        context['child'] = child
        context.hidden = True
        assert is_hidden(child) is True

    def test_is_hidden_parent_attribute_is_false(self, context):
        from adhocracy_core.sheets.metadata import is_hidden
        child = testing.DummyResource()
        context['child'] = child
        context.hidden = False
        assert is_hidden(child) is False

    def test_is_hidden_parent_attribute_not_set(self, context):
        from adhocracy_core.sheets.metadata import is_hidden
        child = testing.DummyResource()
        context['child'] = child
        assert is_hidden(child) is False

    def test_is_hidden_parent_attrib_true_child_attrib_false(self, context):
        from adhocracy_core.sheets.metadata import is_hidden
        child = testing.DummyResource()
        context['child'] = child
        context.hidden = True
        child.hidden = False
        assert is_hidden(child) is True

    def test_view_blocked_by_metadata_no_metadata(self, registry):
        from adhocracy_core.interfaces import IResource
        from adhocracy_core.sheets.metadata import view_blocked_by_metadata
        resource = testing.DummyResource(__provides__=IResource)
        assert view_blocked_by_metadata(resource, registry) is None

    def test_view_blocked_by_metadata_not_blocked(self, resource_with_metadata,
                                                  registry):
        from adhocracy_core.sheets.metadata import view_blocked_by_metadata
        result = view_blocked_by_metadata(resource_with_metadata, registry)
        assert result is None

    def test_view_blocked_by_metadata_deleted(self, resource_with_metadata,
                                              registry):
        from adhocracy_core.sheets.metadata import view_blocked_by_metadata
        resource_with_metadata.deleted = True
        result = view_blocked_by_metadata(resource_with_metadata, registry)
        assert result['reason'] == 'deleted'

    def test_view_blocked_by_metadata_hidden(self, resource_with_metadata,
                                              registry):
        from adhocracy_core.sheets.metadata import view_blocked_by_metadata
        resource_with_metadata.hidden = True
        result = view_blocked_by_metadata(resource_with_metadata, registry)
        assert result['reason'] == 'hidden'

    def test_view_blocked_by_metadata_both(self, resource_with_metadata,
                                              registry):
        from adhocracy_core.sheets.metadata import view_blocked_by_metadata
        resource_with_metadata.deleted = True
        resource_with_metadata.hidden = True
        result = view_blocked_by_metadata(resource_with_metadata, registry)
        assert result['reason'] == 'both'

    def test_view_blocked_by_metadata_result_fields_correct(
            self, pool_graph, resource_with_metadata, registry):
        from datetime import datetime
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.sheets.metadata import IMetadata
        from adhocracy_core.sheets.metadata import view_blocked_by_metadata
        from adhocracy_core.utils import get_sheet
        pool_graph['res'] = resource_with_metadata
        metadata = get_sheet(resource_with_metadata, IMetadata,
                             registry=registry)
        appstruct = metadata.get()
        user = testing.DummyRequest(__provides__=IUser)
        pool_graph['user'] = user
        now = datetime.now()
        appstruct['modified_by'] = user
        appstruct['modification_date'] = now
        metadata.set(appstruct, force=True, send_event=False)
        resource_with_metadata.hidden = True
        result = view_blocked_by_metadata(resource_with_metadata, registry)
        assert result['modified_by'] == user
        assert result['modification_date'] == now

    def test_index_visibility_visible(self, context):
        from adhocracy_core.sheets.metadata import index_visibility
        assert index_visibility(context, 'default') == ['visible']

    def test_index_visibility_deleted(self, context):
        from adhocracy_core.sheets.metadata import index_visibility
        context.deleted = True
        assert index_visibility(context, 'default') == ['deleted']

    def test_index_visibility_hidden(self, context):
        from adhocracy_core.sheets.metadata import index_visibility
        context.hidden = True
        assert index_visibility(context, 'default') == ['hidden']

    def test_index_visibility_both(self, context):
        from adhocracy_core.sheets.metadata import index_visibility
        context.deleted = True
        context.hidden = True
        assert sorted(index_visibility(context, 'default')) == ['deleted',
                                                                'hidden']

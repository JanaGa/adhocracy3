from pyramid import testing
from pytest import fixture


def test_includeme_register_comment_sheet(config):
    from adhocracy_core.sheets.comment import IComment
    from adhocracy_core.utils import get_sheet
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.comment')
    context = testing.DummyResource(__provides__=IComment)
    assert get_sheet(context, IComment)


class TestCommentableSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.comment import commentable_meta
        return commentable_meta

    @fixture
    def context(self, pool, service, mock_graph):
        pool['comments'] = service
        pool.__graph__ = mock_graph
        return pool

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.comment import ICommentable
        from adhocracy_core.sheets.comment import CommentableSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == ICommentable
        assert inst.meta.schema_class == CommentableSchema

    def test_get_empty(self, meta, context, mock_graph):
        inst = meta.sheet_class(meta, context)
        mock_graph.get_references_for_isheet.return_value = {}
        mock_graph.get_back_references_for_isheet.return_value = {}
        data = inst.get()
        assert data['post_pool'] == context['comments']

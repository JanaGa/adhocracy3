import colander
from pyramid import testing
from pytest import mark
from pytest import fixture
from pytest import raises


@mark.usefixtures('integration')
def test_includeme_register_proposal_sheet(registry):
    from .kiezkassen import IProposal
    context = testing.DummyResource(__provides__=IProposal)
    assert registry.content.get_sheet(context, IProposal)


class TestProposalSheet:

    @fixture
    def meta(self):
        from .kiezkassen import proposal_meta
        return proposal_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from .kiezkassen import IProposal
        from .kiezkassen import ProposalSchema
        inst = meta.sheet_class(meta, context, None)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IProposal
        assert inst.meta.schema_class == ProposalSchema

    def test_get_empty(self, meta, context):
        from decimal import Decimal
        inst = meta.sheet_class(meta, context, None)
        wanted = {'budget': Decimal(0),
                  'creator_participate': False,
                  'location_text': '',
                  }
        assert inst.get() == wanted


class TestProposalSchema:

    @fixture
    def inst(self):
        from .kiezkassen import ProposalSchema
        return ProposalSchema()

    def test_create(self, inst):
        assert inst['budget'].validator.max == 50000
        assert inst['budget'].required
        assert inst['location_text'].validator.max == 100

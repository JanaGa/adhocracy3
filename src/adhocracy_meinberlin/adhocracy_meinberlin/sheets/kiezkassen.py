"""Sheets for Mercator proposals."""
from zope.deprecation import deprecated
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import workflow
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import CurrencyAmount
from adhocracy_core.schema import SingleLine


class IProposal(ISheet):
    """Marker interface for the Kiezkassen proposal sheet."""


class ProposalSchema(colander.MappingSchema):
    """Data structure for organizational information."""

    # TODO: check exact length restrictions

    budget = CurrencyAmount(missing=colander.required,
                            validator=colander.Range(min=0, max=50000))
    creator_participate = Boolean()
    location_text = SingleLine(validator=colander.Length(max=100))

proposal_meta = sheet_meta._replace(isheet=IProposal,
                                    schema_class=ProposalSchema)


class IWorkflowAssignment(workflow.IWorkflowAssignment):
    """Marker interface for the kiezkassen workflow assignment sheet."""


deprecated('IWorkflowAssignment',
           'Backward compatible code use IWorkflowAssignment instead')


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(proposal_meta, config.registry)

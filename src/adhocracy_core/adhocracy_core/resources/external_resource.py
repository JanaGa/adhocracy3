"""External resource content type."""
from adhocracy_core.resources.comment import IComment
from adhocracy_core.resources.comment import add_commentsservice
from adhocracy_core.resources.rate import add_ratesservice
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.pool import IBasicPool
from adhocracy_core.resources.pool import pool_metadata

import adhocracy_core.sheets.document
import adhocracy_core.sheets.comment


class IExternalResource(IBasicPool):

    """An external resource.

    This is currently a commentable simple.
    """


external_resource_meta = pool_metadata._replace(
    content_name='ExternalResource',
    iresource=IExternalResource,
    element_types=[IComment],  # FIXME remove IComment, this is the wrong place
    extended_sheets=[adhocracy_core.sheets.comment.ICommentable],
    after_creation=([add_commentsservice, add_ratesservice]
                    + pool_metadata.after_creation),
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(external_resource_meta, config)

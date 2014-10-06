"""Content registry."""
from copy import copy

from pyramid.request import Request
from pyramid.util import DottedNameResolver
from pyramid.decorator import reify
from substanced.content import ContentRegistry
from substanced.content import add_content_type
from substanced.content import add_service_type
from zope.interface.interfaces import IInterface

from adhocracy_core.utils import get_iresource
from adhocracy_core.interfaces import ISheet


resolver = DottedNameResolver()


class ResourceContentRegistry(ContentRegistry):

    """Extend substanced content registry to work with resources."""

    def __init__(self, registry):
        super().__init__(registry)
        self.resources_meta = {}
        """Resources meta mapping.

        Dictionary with key iresource (`resource type` interface) and value
        :class:`adhocracy_core.interfaces.ResourceMetadata`.
        """
        self.sheets_meta = {}
        """Sheets meta mapping.

        Dictionary with key isheet (`sheet type` interface) and value
        :class:`adhocracy_core.interfaces.SheetMetadata`.
        """

    def get_resources_meta_addable(self, context: object,
                                   request: Request) -> list:
        """Get addable resource meta for context, mind permissions."""
        iresource = get_iresource(context)
        addables = self.resources_meta_addable[iresource]
        addables_allowed = []
        for resource_meta in addables:
            permission = resource_meta.permission_add
            if request.has_permission(permission, context):
                addables_allowed.append(resource_meta)
        return addables_allowed

    @reify
    def resources_meta_addable(self):
        """Addable resources metadata mapping.

        Dictionary with key iresource (`resource type` interface)` and value
        list of :class:`adhocracy_core.interfaces.ResourceMetadata`.
        The value includes only addables for a context with `resource type`.
        """
        resources_addables = {}
        for iresource, resource_meta in self.resources_meta.items():
            addables = resource_meta.element_types
            all_addables = []
            for iresource_, resource_meta_ in self.resources_meta.items():
                is_implicit = resource_meta_.is_implicit_addable
                for iresource_addable in addables:
                    is_subtype = is_implicit\
                        and iresource_.extends(iresource_addable)
                    is_is = iresource_ is iresource_addable
                    if is_subtype or is_is:
                        all_addables.append(resource_meta_)
            resources_addables[iresource] = all_addables
        return resources_addables

    def get_sheets_all(self, context: object) -> list:
        """Get all sheets for `context` and set the 'context' attribute."""
        iresource = get_iresource(context)
        sheets = self.sheets_all[iresource]
        self._add_context(sheets, context)
        return sheets

    def get_sheets_create(self, context: object, request: Request=None,
                          iresource: IInterface=None):
        """Get creatable sheets for `context` and set the 'context' attribute.

        :param iresource: If set return creatable sheets for this resource
                         type. Else return the creatable sheets of `context`.
        :param request: If set check permissions.
        """
        iresource = iresource or get_iresource(context)
        sheets = self.sheets_create[iresource]
        self._add_context(sheets, context)
        self._filter_permission(sheets, 'permission_create', context, request)
        return sheets

    def get_sheets_edit(self, context: object, request: Request=None) -> list:
        """Get editable sheets for `context` and set the 'context' attribute.

        :param request: If set check permissions.
        """
        iresource = get_iresource(context)
        sheets = self.sheets_edit[iresource]
        self._add_context(sheets, context)
        self._filter_permission(sheets, 'permission_edit', context, request)
        return sheets

    def get_sheets_read(self, context: object, request: Request=None) -> list:
        """Get readable sheets for `context` and set the 'context' attribute.

        :param request: If set check permissions.
        """
        iresource = get_iresource(context)
        sheets = self.sheets_read[iresource]
        self._add_context(sheets, context)
        self._filter_permission(sheets, 'permission_view', context, request)
        return sheets

    @staticmethod
    def _add_context(sheets: list, context: object):
        for sheet in sheets:
            sheet.context = context

    @staticmethod
    def _filter_permission(sheets: list, permission_attr: str, context: object,
                           request: Request=None):
        if request is None:
            return
        sheets_candiates = copy(sheets)
        for sheet in sheets_candiates:
            permission = getattr(sheet.meta, permission_attr)
            if not request.has_permission(permission, context):
                sheets.remove(sheet)

    @reify
    def sheets_all(self) -> dict:
        """Sheet mappping.

        Dictionary with key iresource (`resource type` interface) and
        value list of sheets.
        Mind to set the `context` attribute before set/get sheet data.
        """
        resource_sheets_all = {}
        for resource_meta in self.resources_meta.values():
            isheets = set(resource_meta.basic_sheets +
                          resource_meta.extended_sheets)
            sheets = []
            for isheet in isheets:
                sheet_meta = self.sheets_meta[isheet]
                context = None
                sheet = sheet_meta.sheet_class(sheet_meta, context)
                sheets.append(sheet)
            resource_sheets_all[resource_meta.iresource] = sheets
        return resource_sheets_all

    @reify
    def sheets_create(self) -> dict:
        """Createable sheets mapping.

        Dictionary with key `resource type` and value list of creatable sheets.
        """
        return self._filter_sheets_all_by_attribute('creatable')

    @reify
    def sheets_create_mandatory(self) -> dict:
        """CreateMandatory sheets mapping.

        Dictionary with key `resource type` and value list of
        create mandatory sheets.
        """
        return self._filter_sheets_all_by_attribute('create_mandatory')

    @reify
    def sheets_edit(self) -> dict:
        """Editable sheets mapping.

        Dictionary with key `resource type` and value list of
        editable sheets.
        """
        return self._filter_sheets_all_by_attribute('editable')

    @reify
    def sheets_read(self) -> dict:
        """Readable sheets mapping.

        Dictionary with key `resource type` and value list of
        readable sheets.
        """
        return self._filter_sheets_all_by_attribute('readable')

    def _filter_sheets_all_by_attribute(self, attribute: str) -> list:
        sheets_all_filtered = {}
        for iresource, sheets in self.sheets_all.items():
            filtered = filter(lambda s: getattr(s.meta, attribute), sheets)
            sheets_all_filtered[iresource] = [x for x in filtered]
        return sheets_all_filtered

    def resolve_isheet_field_from_dotted_string(self, dotted: str) -> tuple:
        """Resolve `dotted` string to isheet and field name and schema node.

        :dotted: isheet.__identifier__ and field_name separated by ':'
        :return: tuple with isheet (ISheet), field_name (str), field schema
                 node (colander.SchemaNode).
        :raise ValueError: If the string is not dotted or it cannot be
            resolved to isheet and field name.
        """
        if ':' not in dotted:
            raise ValueError
        name = ''.join(dotted.split(':')[:-1])
        field = dotted.split(':')[-1]
        isheet = resolver.resolve(name)
        if not IInterface.providedBy(isheet):
            raise ValueError
        if not isheet.isOrExtends(ISheet):
            raise ValueError
        schema = self.sheets_meta[isheet].schema_class()
        node = schema.get(field, None)
        if not node:
            raise ValueError
        return isheet, field, node


def includeme(config):  # pragma: no cover
    """Run pyramid config."""
    """Add content registry, register substanced content_type decorators."""
    config.registry.content = ResourceContentRegistry(config.registry)
    config.add_directive('add_content_type', add_content_type)
    config.add_directive('add_service_type', add_service_type)
    # FIXME we cannot add the substanced view_predicate `content_type` here,
    # this conflicts with _:class:`cornice.ContentTypePredicate`

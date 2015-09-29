"""Sheets for managing assets."""

import io

from persistent import Persistent
from PIL import Image
from pyramid.registry import Registry
from substanced.file import File
import colander
import transaction

from adhocracy_core.interfaces import Dimensions
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from pyramid.response import FileResponse
from adhocracy_core.schema import FileStore
from adhocracy_core.schema import Integer
from adhocracy_core.schema import PostPool
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.schema import Resource
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.utils import get_sheet_field


class IHasAssetPool(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for resources that have an asset pool."""


class HasAssetPoolSchema(colander.MappingSchema):

    """Data structure pointing to an asset pool."""

    asset_pool = PostPool(iresource_or_service_name='assets')


has_asset_pool_meta = sheet_meta._replace(
    isheet=IHasAssetPool,
    schema_class=HasAssetPoolSchema,
    editable=False,
    creatable=False,
)


class IAssetMetadata(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for asset metadata."""


class AssetReference(SheetToSheet):

    """Reference to an asset."""

    target_isheet = IAssetMetadata


class AssetMetadataSchema(colander.MappingSchema):

    """Data structure storing asset metadata."""

    mime_type = SingleLine(missing=colander.required)
    size = Integer(readonly=True)
    filename = SingleLine(readonly=True)
    attached_to = UniqueReferences(readonly=True,
                                   backref=True,
                                   reftype=AssetReference)
    raw = Resource(readonly=True)


asset_metadata_meta = sheet_meta._replace(
    isheet=IAssetMetadata,
    schema_class=AssetMetadataSchema,
    mime_type_validator=lambda dummy: True,
)


class IAssetData(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the actual asset data."""


class AssetDataSchema(colander.MappingSchema):

    """Data structure storing for the actual asset data."""

    data = FileStore(missing=colander.required)


asset_data_meta = sheet_meta._replace(
    isheet=IAssetData,
    schema_class=AssetDataSchema,
    readable=False,
)


class AssetFileDownload(Persistent):

    """Wrapper for a File object that allows downloading the asset data."""

    def __init__(self, dimensions: Dimensions=None):
        """
        Create a new instance.

        :param dimensions: if specified, the asset is supposed to be an image
                and will be cropped and resized to the required dimensions
        """
        self.dimensions = dimensions
        self.file = None

    def get_response(self,
                     context: IResource,
                     registry: Registry=None) -> FileResponse:
        """
        Return a response object with the binary content of the asset.

        :param parent: the parent of the current resource, used as fallback
               if this view doesn't manage the image by itself
        :param registry: the registry
        """
        if self.file is None:
            if self.dimensions is None:
                # retrieve file from parent
                file = retrieve_asset_file(context.__parent__, registry)
            else:
                file = self._crop_and_resize_image(context, registry)
        else:
            # use locally stored file
            file = self.file
        return file.get_response()

    def _crop_and_resize_image(self,
                               context: IResource,
                               registry: Registry) -> File:
        parent_file = retrieve_asset_file(context.__parent__, registry)
        # Crop and resize image via PIL
        with parent_file.blob.open('r') as blobdata:
            mimetype = parent_file.mimetype
            image = Image.open(blobdata)
            cropped_image = self._crop_if_needed(image)
            resized_image = cropped_image.resize(self.dimensions,
                                                 Image.ANTIALIAS)
            bytestream = io.BytesIO()
            resized_image.save(bytestream, image.format)
            bytestream.seek(0)
        # Store as substanced File and return
        self.file = File(stream=bytestream, mimetype=mimetype)
        transaction.commit()  # to avoid BlobError: Uncommitted changes
        return self.file

    def _crop_if_needed(self, image: Image) -> Image:
        """
        Return a cropped version of if cropping is needed.

        The returned version will have the same aspect ratio as the target
        dimensions, but not necessarily the same size, so a further resizing
        step may be needed. If the original image is wider, it is cropped in
        X direction so that only the middle part remains. If it's higher, it's
        cropped in Y direction.

        If original and target aspect ratio are identical, the image is
        returned unchanged.
        """
        original_aspect_ratio = image.size[0] / image.size[1]
        target_aspect_ratio = self.dimensions.width / self.dimensions.height
        if target_aspect_ratio > original_aspect_ratio:
            # height must be cropped
            cropped_height = round(image.size[0] / target_aspect_ratio)
            if cropped_height == image.size[1]:
                return image  # No cropping necessary
            upper = round((image.size[1] - cropped_height) / 2)
            #          (left, upper, right,      lower)
            crop_box = (0, upper, image.size[0], upper + cropped_height)
        else:
            # width must be cropped
            cropped_width = round(image.size[1] * target_aspect_ratio)
            if cropped_width == image.size[0]:
                return image  # No cropping necessary
            left = round((image.size[0] - cropped_width) / 2)
            #          (left, upper, right,            lower)
            crop_box = (left, 0, left + cropped_width, image.size[1])
        return image.crop(crop_box)


def retrieve_asset_file(context: IResource, registry: Registry=None):
    """Retrieve asset file from content."""
    data = get_sheet_field(context, IAssetData, 'data', registry=registry)
    return data


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(has_asset_pool_meta, config.registry)
    add_sheet_to_registry(asset_metadata_meta, config.registry)
    add_sheet_to_registry(asset_data_meta, config.registry)

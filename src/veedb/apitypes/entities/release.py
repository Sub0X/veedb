from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union, Any, Literal, TYPE_CHECKING

from ..common import (
    VNDBID, ReleaseDate, ImageCommon, Extlink, LanguageEnum, PlatformEnum,
    ProducerTypeEnum # Assuming ProducerTypeEnum is defined in common or producer.py
)

# To handle potential circular dependencies for type hinting if VN, Producer are in other files
if TYPE_CHECKING:
    from .vn import VN  # Or a VNCompact/VNStub if defined
    from .producer import Producer # Or a ProducerCompact/ProducerStub


@dataclass
class ReleaseLanguageSpecific:
    lang: LanguageEnum
    title: Optional[str] = None # Title in original script for this language
    latin: Optional[str] = None # Romanized version of title
    mtl: bool = False           # Machine translation
    main: bool = False          # Is this the main language for the release's title/alttitle fields

@dataclass
class ReleaseMedia:
    medium: str # From schema["enums"]["medium"] - should be an Enum if defined
    qty: Optional[int] = None # Quantity, 0 if unknown/not applicable

@dataclass
class ReleaseVNLink:
    id: VNDBID # VN ID
    rtype: Literal["trial", "partial", "complete"]
    # Allows fetching other VN fields, e.g., title, olang
    # These would be Optional and depend on the 'fields' parameter in the query
    title: Optional[str] = None
    original_language: Optional[LanguageEnum] = None
    # Add other commonly requested VN fields as Optional here
    # Or use a more generic approach if many fields are possible:
    # vn_details: Optional[Dict[str, Any]] = None # For any other requested VN fields


@dataclass
class ReleaseProducerLink:
    id: VNDBID # Producer ID
    developer: bool
    publisher: bool
    # Allows fetching other Producer fields
    name: Optional[str] = None
    original_name: Optional[str] = None
    type: Optional[ProducerTypeEnum] = None
    # lang: Optional[LanguageEnum] = None


@dataclass
class ReleaseImage(ImageCommon): # Inherits from ImageCommon
    # Specific fields for release images from schema:
    # images.type, images.vn, images.languages, images.photo
    type: Literal["pkgfront", "pkgback", "pkgcontent", "pkgside", "pkgmed", "dig"]
    vn: Optional[VNDBID] = None # VN ID this image applies to (for bundles)
    languages: Optional[List[LanguageEnum]] = None # Valid languages for this image, null if all
    photo: bool = False
    # thumbnail and thumbnail_dims are part of ImageCommon via schema for release.images
    thumbnail: Optional[str] = None
    thumbnail_dims: Optional[Tuple[int, int]] = None


@dataclass
class Release:
    id: VNDBID
    title: Optional[str] = None # Main title, typically romanized
    alttitle: Optional[str] = None # Alternative title, original script

    languages: List[ReleaseLanguageSpecific] = field(default_factory=list)
    platforms: List[PlatformEnum] = field(default_factory=list)
    media: List[ReleaseMedia] = field(default_factory=list)

    vns: List[ReleaseVNLink] = field(default_factory=list) # Linked VNs
    producers: List[ReleaseProducerLink] = field(default_factory=list)

    # From schema: release.images is an array of objects.
    # Each object has fields like id, url, dims, sexual, violence, votecount (from ImageCommon)
    # PLUS type, vn, languages, photo, thumbnail, thumbnail_dims
    images: List[ReleaseImage] = field(default_factory=list)

    released: Optional[ReleaseDate] = None
    minage: Optional[int] = None # 0-18, age rating
    patch: bool = False
    freeware: bool = False
    uncensored: Optional[bool] = None
    official: bool = False # Official release
    has_ero: bool = False # If the release contains adult content

    # Resolution: null, "non-standard", or [width, height]
    resolution: Optional[Union[Literal["non-standard"], Tuple[int, int]]] = None
    engine: Optional[str] = None

    # Voiced: null, 1 (not voiced), 2 (ero scenes), 3 (partially), 4 (fully)
    voiced: Optional[Literal[1, 2, 3, 4]] = None
    notes: Optional[str] = None # May contain formatting codes

    gtin: Optional[str] = None # JAN/EAN/UPC code
    catalog: Optional[str] = None # Catalog number

    extlinks: List[Extlink] = field(default_factory=list)

    # animation field is mentioned as undocumented/missing in API docs
    # animation: Optional[Any] = None

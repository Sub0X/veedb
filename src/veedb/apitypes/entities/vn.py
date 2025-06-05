# src/veedb/types/entities/vn.py
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING

from ..common import (
    VNDBID,
    ReleaseDate,
    ImageCommon,
    Extlink,
    LanguageEnum,
    PlatformEnum,
    DevStatusEnum,
    StaffRoleEnum,
)

# Forward declarations for type hinting to avoid circular imports
if TYPE_CHECKING:
    from .release import Release  # Or a more compact version like ReleaseStub
    from .producer import Producer  # Or ProducerStub
    from .staff import Staff  # Or StaffStub
    from .character import Character  # Or CharacterStub
    from .tag import Tag  # Or TagStub


@dataclass
class VNTitle:
    lang: LanguageEnum
    title: str  # Title in original script
    latin: Optional[str] = None  # Romanized version of title
    official: bool = False
    main: bool = False  # Whether this is the "main" title for the VN entry


@dataclass
class VNImageInfo(ImageCommon):  # For vn.image and vn.screenshots
    thumbnail: Optional[str] = None
    thumbnail_dims: Optional[Tuple[int, int]] = None
    # For screenshots, 'release' can be a nested object.
    # Using Dict[str, Any] for simplicity, or define a VNScreenshotReleaseInfo
    release: Optional[Dict[str, Any]] = (
        None  # e.g. {'id': 'r123', 'title': 'Release Title'}
    )


@dataclass
class VNRelation:  # vn.relations
    id: VNDBID  # The related VN's ID
    relation: str  # e.g., "preq", "seq", "alt", "side", "par", "ser", "fan", "orig"
    relation_official: bool
    # Other VN fields can be selected here via dot notation in the 'fields' query param
    # Example: title of the related VN
    title: Optional[str] = None
    original_language: Optional[LanguageEnum] = None  # Example: olang of related VN


@dataclass
class VNTagLink:  # vn.tags
    id: VNDBID  # Tag ID
    rating: float  # Tag rating/score (0.0 to 3.0)
    spoiler: int  # Spoiler level (0, 1, or 2)
    lie: bool
    # Other Tag fields can be selected
    name: Optional[str] = None  # Example: name of the tag
    category: Optional[str] = None  # Example: category of the tag


@dataclass
class VNDeveloper:  # vn.developers - these are Producer objects
    id: VNDBID  # Producer ID
    # Other Producer fields can be selected
    name: Optional[str] = None
    original: Optional[str] = None
    type: Optional[str] = None  # e.g. 'co', 'in', 'ng'
    lang: Optional[LanguageEnum] = None


@dataclass
class VNEdition:  # vn.editions
    eid: int  # Edition identifier (local to the VN, not stable across edits)
    lang: Optional[LanguageEnum] = None
    name: Optional[str] = None  # English name/label identifying this edition
    official: Optional[bool] = None


@dataclass
class VNStaffLink:  # vn.staff
    id: VNDBID  # Staff ID (sid)
    aid: int  # Staff Alias ID (aid) - the specific alias used for this role
    role: StaffRoleEnum
    note: Optional[str] = None
    eid: Optional[int] = None  # Edition ID this staff worked on, null for original
    # Other Staff fields can be selected
    name: Optional[str] = None  # Example: staff member's name (for the given aid)
    original: Optional[str] = None  # Example


@dataclass
class VNVoiceActor:  # vn.va
    note: Optional[str] = None
    # staff and character are nested objects with their own selectable fields
    # Using Dict[str, Any] for simplicity, or define VNStaffInfoForVA, VNCharacterInfoForVA
    staff: Dict[str, Any] = field(
        default_factory=dict
    )  # e.g. {'id': 's1', 'name': 'Staff Name'}
    character: Dict[str, Any] = field(
        default_factory=dict
    )  # e.g. {'id': 'c1', 'name': 'Char Name'}


@dataclass
class VN:
    id: VNDBID
    title: Optional[str] = None  # Main title, typically romanized
    alttitle: Optional[str] = (
        None  # Alternative title, typically original script if olang differs
    )

    titles: List[VNTitle] = field(default_factory=list)  # Full list of titles
    aliases: List[str] = field(default_factory=list)

    olang: Optional[LanguageEnum] = None  # Original language of the VN
    devstatus: Optional[DevStatusEnum] = (
        None  # 0: Finished, 1: In development, 2: Cancelled
    )
    released: Optional[ReleaseDate] = None  # Date of first known release

    languages: List[LanguageEnum] = field(
        default_factory=list
    )  # Languages VN is available in
    platforms: List[PlatformEnum] = field(
        default_factory=list
    )  # Platforms VN is available on

    image: Optional[VNImageInfo] = None  # Main cover image info

    length: Optional[int] = (
        None  # Rough length estimate: 1 (Very short) to 5 (Very long)
    )
    length_minutes: Optional[int] = (
        None  # Average of user-submitted play times in minutes
    )
    length_votes: Optional[int] = None  # Number of submitted play times

    description: Optional[str] = None  # May contain formatting codes

    # API v2 specific rating fields
    average: Optional[float] = None  # Raw vote average (10-100)
    rating: Optional[float] = None  # Bayesian rating (10-100)
    votecount: Optional[int] = None  # Number of votes

    screenshots: List[VNImageInfo] = field(default_factory=list)
    relations: List[VNRelation] = field(default_factory=list)
    tags: List[VNTagLink] = field(default_factory=list)  # Directly applied tags
    developers: List[VNDeveloper] = field(default_factory=list)
    editions: List[VNEdition] = field(default_factory=list)
    staff: List[VNStaffLink] = field(default_factory=list)
    va: List[VNVoiceActor] = field(
        default_factory=list
    )  # Voice actors linked to characters in this VN
    extlinks: List[Extlink] = field(default_factory=list)

    # popularity field was deprecated

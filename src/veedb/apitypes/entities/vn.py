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
    TagCategoryEnum,
)

# Forward declarations for type hinting to avoid circular imports
if TYPE_CHECKING:
    from .release import Release  # Or a more compact version like ReleaseStub
    from .producer import Producer  # Or ProducerStub
    from .staff import Staff  # Or StaffStub
    from .character import Character  # Or CharacterStub
    from .tag import Tag  # Or TagStub
else:
    # Import the actual classes for inheritance
    from .release import Release
    from .producer import Producer
    from .staff import Staff
    from .character import Character
    from .tag import Tag


@dataclass
class VNTitle:
    lang: LanguageEnum
    title: str  # Title in original script
    latin: Optional[str] = None  # Romanized version of title
    official: bool = False
    main: bool = False  # Whether this is the "main" title for the VN entry


@dataclass
class VNImageInfo:  # For vn.image and vn.screenshots
    # All ImageCommon fields as optional
    id: Optional[VNDBID] = None
    url: Optional[str] = None
    dims: Optional[List[int]] = None  # [width, height]
    sexual: Optional[float] = None  # 0.0-2.0 (average flagging vote)
    violence: Optional[float] = None  # 0.0-2.0 (average flagging vote)
    votecount: Optional[int] = None
    
    # VN-specific image fields
    thumbnail: Optional[str] = None
    release: Optional["VNScreenshotRelease"] = None


@dataclass
class VNScreenshotRelease(Release):  # screenshots.release.*
    # All release fields are inherited from Release class
    # This allows selecting any release field according to API docs
    pass


@dataclass
class VNTagLink(Tag):  # vn.tags
    # Tag specific fields for VN links
    rating: float = 0.0  # Tag rating/score (0.0 to 3.0)
    spoiler: int = 0  # Spoiler level (0, 1, or 2)
    lie: bool = False
    
    # All tag fields are inherited from Tag class
    # This allows selecting any tag field according to API docs


@dataclass
class VNDeveloper(Producer):  # vn.developers - these are Producer objects
    # All producer fields are inherited from Producer class
    # This allows selecting any producer field according to API docs
    pass


@dataclass
class VNEdition:  # vn.editions
    eid: int  # Edition identifier (local to the VN, not stable across edits)
    lang: Optional[LanguageEnum] = None
    name: Optional[str] = None  # English name/label identifying this edition
    official: Optional[bool] = None


@dataclass
class VNStaffLink(Staff):  # vn.staff
    # Staff specific fields for VN links
    role: StaffRoleEnum = ""  # Required for VN staff links
    note: Optional[str] = None
    eid: Optional[int] = None  # Edition ID this staff worked on, null for original
    
    # All staff fields are inherited from Staff class
    # This allows selecting any staff field according to API docs


@dataclass
class VNVoiceActor:  # vn.va
    note: Optional[str] = None
    staff: Optional["VNVAStaff"] = None
    character: Optional["VNVACharacter"] = None


@dataclass
class VNVAStaff(Staff):  # va.staff.*
    # All staff fields are inherited from Staff class
    # This allows selecting any staff field according to API docs
    pass


@dataclass
class VNVACharacter(Character):  # va.character.*
    # All character fields are inherited from Character class
    # This allows selecting any character field according to API docs
    pass


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
    relations: List["VNRelation"] = field(default_factory=list)
    tags: List[VNTagLink] = field(default_factory=list)  # Directly applied tags
    developers: List[VNDeveloper] = field(default_factory=list)
    editions: List[VNEdition] = field(default_factory=list)
    staff: List[VNStaffLink] = field(default_factory=list)
    va: List[VNVoiceActor] = field(
        default_factory=list
    )  # Voice actors linked to characters in this VN
    extlinks: List[Extlink] = field(default_factory=list)

    # popularity field was deprecated


# VNRelation defined after VN to allow inheritance
@dataclass
class VNRelation(VN):  # vn.relations
    # VN relation specific fields
    relation: str = ""  # e.g., "preq", "seq", "alt", "side", "par", "ser", "fan", "orig"
    relation_official: bool = False
    
    # All VN fields are inherited from VN class
    # This allows selecting any VN field according to API docs

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union, Literal, TYPE_CHECKING

from ..common import VNDBID, ImageCommon

if TYPE_CHECKING:
    from .vn import VN # Or VNCompact
    from .release import Release # Or ReleaseCompact
    from .trait import TraitLink # Or TraitCompact

BloodTypeEnum = Literal["a", "b", "ab", "o"]
# Sex: null, "m", "f", "b" (both), "n" (sexless)
SexEnum = Literal["m", "f", "b", "n"]
# Gender: null, "m", "f", "o" (non-binary), "a" (ambiguous)
GenderEnum = Literal["m", "f", "o", "a"]
CharacterRoleEnum = Literal["main", "primary", "side", "appears"]


@dataclass
class CharacterImageInfo(ImageCommon):
    # Character images are limited to 256x300px, no thumbnail/thumbnail_dims in docs
    # but ImageCommon includes them as optional, which is fine.
    pass


@dataclass
class CharacterVNLink:
    id: VNDBID # VN ID
    spoiler: Optional[int] = None # Spoiler level for this character in this VN
    role: Optional[CharacterRoleEnum] = None
    # release: Optional[Release] = None # Or ReleaseCompact / VNDBID for release_id
    release: Optional[dict] = None # Placeholder for release object fields
    # Other VN fields can be selected here if requested
    title: Optional[str] = None # Example: VN title


@dataclass
class CharacterTraitLink:
    id: VNDBID # Trait ID
    spoiler: int # 0, 1, or 2
    lie: bool
    # Other Trait fields can be selected
    name: Optional[str] = None # Example: Trait name
    # group_name: Optional[str] = None # Example


@dataclass
class Character:
    id: VNDBID
    name: Optional[str] = None
    original: Optional[str] = None # Name in original script
    aliases: List[str] = field(default_factory=list)
    description: Optional[str] = None # May contain formatting codes

    image: Optional[CharacterImageInfo] = None

    blood_type: Optional[BloodTypeEnum] = None
    height: Optional[int] = None # cm
    weight: Optional[int] = None # kg
    bust: Optional[int] = None # cm (measurement)
    waist: Optional[int] = None # cm (measurement)
    hips: Optional[int] = None # cm (measurement)
    cup: Optional[str] = None # e.g., "AAA", "AA", "A", "B", ...
    age: Optional[int] = None # years

    # birthday: [month, day]
    birthday: Optional[Tuple[int, int]] = None

    # sex: [apparent_sex, real_sex (spoiler)]
    sex: Optional[Tuple[Optional[SexEnum], Optional[SexEnum]]] = None
    # gender: [non_spoiler_gender, spoiler_gender]
    gender: Optional[Tuple[Optional[GenderEnum], Optional[GenderEnum]]] = None

    vns: List[CharacterVNLink] = field(default_factory=list)
    traits: List[CharacterTraitLink] = field(default_factory=list)

    # Missing from API docs: instances, voice actor details (directly on character)
    # Voice actor info is usually fetched via VN's `va` field or staff roles.

# src/veedb/apitypes/entities/staff.py
from dataclasses import dataclass, field
from typing import List, Optional, Literal

from ..common import VNDBID, Extlink, LanguageEnum # Assuming Enums are in common or defined here

StaffGenderEnum = Literal["m", "f"]

@dataclass
class StaffAlias:
    aid: int # Alias ID
    name: str # Name in original script
    ismain: bool # Whether this alias is the "main" name for the staff entry
    latin: Optional[str] = None # Romanized version of 'name' - MOVED AFTER ismain


@dataclass
class Staff:
    id: VNDBID # Main staff ID (e.g., "s81")
    aid: Optional[int] = None # Alias ID for the specific name returned in this result
    ismain: Optional[bool] = None # Whether the 'name' and 'original' fields are the main name

    name: Optional[str] = None # Possibly romanized name (depends on ismain and specific alias)
    original: Optional[str] = None # Name in original script (depends on ismain and specific alias)

    lang: Optional[LanguageEnum] = None # Staff's primary language
    gender: Optional[StaffGenderEnum] = None
    description: Optional[str] = None # May contain formatting codes

    extlinks: List[Extlink] = field(default_factory=list)
    aliases: List[StaffAlias] = field(default_factory=list) # Full list of names for this person

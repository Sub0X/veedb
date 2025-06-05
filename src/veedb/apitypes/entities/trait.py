from dataclasses import dataclass, field
from typing import List, Optional

from ..common import VNDBID

@dataclass
class Trait:
    id: VNDBID
    name: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    description: Optional[str] = None # May contain formatting codes
    searchable: Optional[bool] = None
    applicable: Optional[bool] = None
    group_id: Optional[VNDBID] = None # VNDBID of the top-level parent trait group
    group_name: Optional[str] = None # Name of the top-level parent trait group
    char_count: Optional[int] = None # Number of characters with this trait (incl. children)

    # Missing: parent/child trait fetching mechanism

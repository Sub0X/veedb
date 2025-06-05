from dataclasses import dataclass, field
from typing import List, Optional

from ..common import VNDBID, TagCategoryEnum

@dataclass
class Tag:
    id: VNDBID
    name: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    description: Optional[str] = None # May contain formatting codes
    category: Optional[TagCategoryEnum] = None # "cont", "ero", "tech"
    searchable: Optional[bool] = None
    applicable: Optional[bool] = None
    vn_count: Optional[int] = None # Number of VNs with this tag (incl. children)

    # Missing: parent/child tag fetching mechanism (noted as missing in API docs)

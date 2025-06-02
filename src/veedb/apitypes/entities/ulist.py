# vndb_sdk/types/entities/ulist.py
from dataclasses import dataclass, field
from typing import List, Optional, Literal, TYPE_CHECKING, Dict, Any

from ..common import VNDBID, ReleaseDate

if TYPE_CHECKING:
    from .vn import VN # Or VNCompact
    from .release import Release # Or ReleaseCompact

@dataclass
class UlistLabelInfo: # For UlistItem.labels
    id: int # Label ID
    label: str # Label name (string)

@dataclass
class UlistReleaseInfo: # For UlistItem.releases
    id: VNDBID # Release ID
    # list_status: 0 (Unknown), 1 (Pending), 2 (Obtained), 3 (On loan), 4 (Deleted)
    list_status: Optional[Literal[0, 1, 2, 3, 4]] = None
    # Other release fields can be selected
    title: Optional[str] = None # Example: Release title
    # released: Optional[ReleaseDate] = None # Example
    # Or a more generic way:
    # release_details: Optional[Dict[str, Any]] = None

@dataclass
class UlistItem:
    id: VNDBID # Visual Novel ID
    added: Optional[int] = None # Unix timestamp
    voted: Optional[int] = None # Unix timestamp of vote, can be null
    lastmod: Optional[int] = None # Unix timestamp of last modification
    vote: Optional[int] = None # 10-100, can be null
    started: Optional[ReleaseDate] = None # "YYYY-MM-DD", can be null
    finished: Optional[ReleaseDate] = None # "YYYY-MM-DD", can be null
    notes: Optional[str] = None # Can be null

    labels: List[UlistLabelInfo] = field(default_factory=list) # User labels on this VN

    # vn: Optional[VN] = None # Or VNCompact, or Dict[str, Any]
    vn: Optional[Dict[str, Any]] = field(default_factory=dict) # For selected VN fields

    releases: List[UlistReleaseInfo] = field(default_factory=list) # Releases of this VN on user's list

@dataclass
class UlistLabel: # For GET /ulist_labels response
    id: int
    label: str
    private: bool
    count: Optional[int] = None # Number of VNs with this label

from dataclasses import dataclass, field
from typing import List, Optional, Literal, TYPE_CHECKING, Dict, Any

from ..common import VNDBID, ReleaseDate

if TYPE_CHECKING:
    from .vn import VN
    from .release import Release

@dataclass
class UlistLabelInfo:
    id: int
    label: str

@dataclass
class UlistReleaseInfo:
    id: VNDBID
    list_status: Optional[Literal[0, 1, 2, 3, 4]] = None
    title: Optional[str] = None

@dataclass
class UlistItem:
    id: VNDBID
    added: Optional[int] = None
    voted: Optional[int] = None
    lastmod: Optional[int] = None
    vote: Optional[int] = None
    started: Optional[ReleaseDate] = None
    finished: Optional[ReleaseDate] = None
    notes: Optional[str] = None

    labels: List[UlistLabelInfo] = field(default_factory=list)

    vn: Optional[Dict[str, Any]] = field(default_factory=dict)

    releases: List[UlistReleaseInfo] = field(default_factory=list)

@dataclass
class UlistLabel: # For GET /ulist_labels response
    id: int
    label: str
    private: bool
    count: Optional[int] = None # Number of VNs with this label

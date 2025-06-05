from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Dict, Any

from ..common import VNDBID

if TYPE_CHECKING:
    from .vn import VN # Or VNCompact
    from .character import Character # Or CharacterCompact

@dataclass
class Quote:
    id: VNDBID
    quote: Optional[str] = None
    score: Optional[int] = None

    # vn and character can have their respective fields selected.
    # Using Dict[str, Any] for simplicity, or define VNQuoteInfo, CharacterQuoteInfo
    vn: Optional[Dict[str, Any]] = None # e.g., {"id": "v17", "title": "Example VN"}
    character: Optional[Dict[str, Any]] = None # e.g., {"id": "c123", "name": "Char Name"}

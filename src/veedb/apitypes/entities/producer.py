from dataclasses import dataclass, field
from typing import List, Optional, Literal

from ..common import VNDBID, Extlink, LanguageEnum

ProducerTypeEnum = Literal["co", "in", "ng"] # company, individual, amateur group

@dataclass
class Producer:
    id: VNDBID
    name: Optional[str] = None
    original: Optional[str] = None # Name in original script
    aliases: List[str] = field(default_factory=list)
    lang: Optional[LanguageEnum] = None # Primary language
    type: Optional[ProducerTypeEnum] = None
    description: Optional[str] = None # May contain formatting codes
    extlinks: List[Extlink] = field(default_factory=list)
    # Missing: relations (as per API docs)

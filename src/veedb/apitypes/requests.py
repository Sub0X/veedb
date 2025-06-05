# src/veedb/types/requests.py
from dataclasses import dataclass, field
from typing import Optional, List, Literal
from .common import (
    VNDBID,
    ReleaseDate,
)  # Assuming ReleaseDate is YYYY-MM-DD string or similar


@dataclass
class UlistUpdatePayload:
    vote: Optional[int] = None  # 10-100, or null to remove
    notes: Optional[str] = None  # null to remove
    started: Optional[ReleaseDate] = None  # "YYYY-MM-DD", or null to remove
    finished: Optional[ReleaseDate] = None  # "YYYY-MM-DD", or null to remove
    labels: Optional[List[int]] = None  # Overwrites existing labels
    labels_set: Optional[List[int]] = None  # Adds these labels
    labels_unset: Optional[List[int]] = None  # Removes these labels

    def to_dict(self) -> dict:
        """Converts to dict, removing None values, for JSON payload."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class RlistUpdatePayload:
    # status: 0 for “Unknown”, 1 for “Pending”, 2 for “Obtained”, 3 for “On loan”, 4 for “Deleted”
    status: Optional[Literal[0, 1, 2, 3, 4]] = None

    def to_dict(self) -> dict:
        """Converts to dict, removing None values, for JSON payload."""
        return {k: v for k, v in self.__dict__.items() if v is not None}

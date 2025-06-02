# src/veedb/apitypes/entities/user.py
from dataclasses import dataclass, field
from typing import Optional, List

from ..common import VNDBID # Assuming VNDBID is in common.py

@dataclass
class User:
    """
    Represents a user object as returned by the GET /user endpoint.
    """
    id: VNDBID # User ID, e.g., "u1"
    username: str
    lengthvotes: Optional[int] = None # Number of play time votes submitted
    lengthvotes_sum: Optional[int] = None # Sum of play time votes in minutes

@dataclass
class AuthInfo:
    """
    Represents the authentication information as returned by GET /authinfo.
    """
    id: VNDBID # User ID associated with the token
    username: str
    permissions: List[str] = field(default_factory=list) # e.g., ["listread", "listwrite"]

@dataclass
class UserStats: # Renamed from an earlier version to avoid conflict if there was a User class for /user
    """
    Represents the database statistics as returned by GET /stats.
    Note: The API documentation calls this endpoint GET /stats,
    and the response fields are direct counts for various entities.
    """
    chars: int
    producers: int
    releases: int
    staff: int
    tags: int
    traits: int
    vn: int

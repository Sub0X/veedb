# src/veedb/__init__.py

# Ensure client is imported first if other modules depend on its definitions indirectly
# or if it's the primary export.
from .client import VNDB

from .exceptions import (
    VNDBAPIError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    NotFoundError,
    ServerError,
    TooMuchDataSelectedError
)
# Assuming your types directory was renamed to 'apitypes'
from .apitypes.common import QueryRequest, VNDBID, ReleaseDate, LanguageEnum, PlatformEnum, StaffRoleEnum, TagCategoryEnum, ProducerTypeEnum, DevStatusEnum
from .apitypes.requests import UlistUpdatePayload, RlistUpdatePayload

# Version of the package
__version__ = "0.1.0"

# What is publicly available when someone does 'from veedb import *'
# More importantly, these are the names looked up for 'from veedb import VNDB'
__all__ = [
    "VNDB",
    "QueryRequest",
    "VNDBAPIError",
    "AuthenticationError",
    "RateLimitError",
    "InvalidRequestError",
    "NotFoundError",
    "ServerError",
    "TooMuchDataSelectedError",
    "VNDBID", # Exporting common types can be useful
    "ReleaseDate",
    "LanguageEnum",
    "PlatformEnum",
    "StaffRoleEnum",
    "TagCategoryEnum",
    "ProducerTypeEnum",
    "DevStatusEnum",
    "UlistUpdatePayload",
    "RlistUpdatePayload",
    "__version__",
]

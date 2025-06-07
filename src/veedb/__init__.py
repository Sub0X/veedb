# src/veedb/__init__.py
import os

# Ensure client is imported first if other modules depend on its definitions indirectly
# or if it's the primary export.
from .client import VNDB
from .schema_validator import FilterValidator, SchemaCache

from .exceptions import (
    VNDBAPIError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    NotFoundError,
    ServerError,
    TooMuchDataSelectedError,
)

# Assuming your types directory was renamed to 'apitypes'
from .apitypes.common import (
    QueryRequest,
    VNDBID,
    ReleaseDate,
    LanguageEnum,
    PlatformEnum,
    StaffRoleEnum,
    TagCategoryEnum,
    ProducerTypeEnum,
    DevStatusEnum,
)
from .apitypes.entities.user import UserStats
from .apitypes.requests import UlistUpdatePayload, RlistUpdatePayload

# Read version dynamically from VERSION file
def _get_version():
    """Read version from VERSION file."""
    version_file = os.path.join(os.path.dirname(__file__), "VERSION")
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.1.0"  # fallback version

# Version of the package
__version__ = _get_version()

# What is publicly available when someone does 'from veedb import *'
# More importantly, these are the names looked up for 'from veedb import VNDB'
__all__ = [
    "VNDB",
    "FilterValidator",
    "SchemaCache",
    "QueryRequest",
    "VNDBAPIError",
    "AuthenticationError",
    "RateLimitError",
    "InvalidRequestError",
    "NotFoundError",
    "ServerError",
    "TooMuchDataSelectedError",
    "VNDBID",  # Exporting common types can be useful
    "ReleaseDate",
    "LanguageEnum",
    "PlatformEnum",
    "StaffRoleEnum",
    "TagCategoryEnum",
    "ProducerTypeEnum",
    "DevStatusEnum",
    "UserStats",
    "UlistUpdatePayload",
    "RlistUpdatePayload",
    "__version__",
]

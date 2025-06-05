# src/veedb/types/common.py
from typing import List, Optional, Union, Tuple, TypeVar, Generic, Literal
from dataclasses import dataclass, field

VNDBID = str  # e.g., "v17", "r123", "p5", "sf190"
# ReleaseDate can be "YYYY-MM-DD", "YYYY-MM", "YYYY", or "TBA".
# For filters, "unknown" and "today" are also supported.
ReleaseDate = str

# Based on schema["enums"]["language"]
LanguageEnum = Literal[
    "ar",
    "eu",
    "be",
    "bg",
    "ca",
    "ck",
    "zh",
    "zh-Hans",
    "zh-Hant",
    "hr",
    "cs",
    "da",
    "nl",
    "en",
    "eo",
    "fi",
    "fr",
    "gl",
    "de",
    "el",
    "he",
    "hi",
    "hu",
    "ga",
    "id",
    "it",
    "iu",
    "ja",
    "kk",
    "ko",
    "la",
    "lv",
    "lt",
    "mk",
    "ms",
    "ne",
    "no",
    "fa",
    "pl",
    "pt-br",
    "pt-pt",
    "ro",
    "ru",
    "gd",
    "sr",
    "sk",
    "sl",
    "es",
    "sv",
    "ta",
    "th",
    "tr",
    "uk",
    "ur",
    "vi",
]

# Based on schema["enums"]["platform"]
PlatformEnum = Literal[
    "win",
    "lin",
    "mac",
    "web",
    "tdo",
    "ios",
    "and",
    "bdp",
    "dos",
    "dvd",
    "drc",
    "nes",
    "sfc",
    "fm7",
    "fm8",
    "fmt",
    "gba",
    "gbc",
    "msx",
    "nds",
    "swi",
    "sw2",
    "wii",
    "wiu",
    "n3d",
    "p88",
    "p98",
    "pce",
    "pcf",
    "psp",
    "ps1",
    "ps2",
    "ps3",
    "ps4",
    "ps5",
    "psv",
    "smd",
    "scd",
    "sat",
    "vnd",
    "x1s",
    "x68",
    "xb1",
    "xb3",
    "xbo",
    "xxs",
    "mob",
    "oth",
]

# Based on schema["enums"]["staff_role"]
StaffRoleEnum = Literal[
    "scenario",
    "director",
    "chardesign",
    "art",
    "music",
    "songs",
    "translator",
    "editor",
    "qa",
    "staff",
]

TagCategoryEnum = Literal["cont", "ero", "tech"]
ProducerTypeEnum = Literal["co", "in", "ng"]  # company, individual, amateur group
DevStatusEnum = Literal[0, 1, 2]  # 0: Finished, 1: In development, 2: Cancelled


@dataclass
class ImageCommon:
    id: VNDBID
    url: str
    dims: Tuple[int, int]  # [width, height]
    sexual: float  # 0.0-2.0 (average flagging vote)
    violence: float  # 0.0-2.0 (average flagging vote)
    votecount: int


@dataclass
class Extlink:  # As per API docs for release.extlinks, producer.extlinks etc.
    url: str
    label: str  # English human-readable label
    name: str  # Internal identifier of the site
    id: Optional[Union[str, int]] = None  # Remote identifier, can be null


# --- Request and Response Structures ---
@dataclass
class QueryRequest:
    """Common structure for database querying POST requests."""

    filters: Optional[Union[list, str]] = field(default_factory=list)
    fields: str = "id"  # Default to fetching at least the ID
    sort: str = "id"
    reverse: bool = False
    results: int = 10  # Max 100
    page: int = 1
    user: Optional[VNDBID] = (
        None  # User ID (e.g., "u1") for /ulist or 'label' filter context
    )
    count: bool = False
    compact_filters: bool = False
    normalized_filters: bool = False

    def to_dict(self) -> dict:
        """Converts to dict, removing None values, for JSON payload."""
        # Ensure boolean flags are always present if they are False
        data = {}
        for k, v in self.__dict__.items():
            if v is not None:
                data[k] = v
            elif k in ["reverse", "count", "compact_filters", "normalized_filters"]:
                data[k] = False  # Explicitly include False for these booleans
            elif (
                k == "filters" and not v
            ):  # Ensure filters is an empty list if not provided
                data[k] = []

        # Special handling for 'filters': if it's an empty list and was default, it's fine.
        # If user explicitly set it to None, it should be omitted.
        # However, the default_factory handles the empty list case.
        # The current to_dict will omit 'filters' if it's None, and include it if it's [] or populated.
        # For 'fields', 'sort', 'results', 'page', if they are None (though typed not to be),
        # they would be omitted. They have defaults, so they'll usually be present.
        return data


T = TypeVar("T")  # Generic type for results


@dataclass
class QueryResponse(Generic[T]):
    """Common structure for database querying POST responses."""

    results: List[T]
    more: bool
    count: Optional[int] = None
    compact_filters: Optional[str] = None
    normalized_filters: Optional[list] = None

"""Review entity — VeeSQL-only extension.

VNDB doesn't expose reviews via the kana HTTPS API; this entity
exists on the self-hosted VeeSQL mirror only, populated by the
review-sync job (see VeeSQL/src/monitor_api/jobs/review_sync.py).

The ``Review`` dataclass mirrors what /api/review returns. Field
selection follows the same rules as other entities: ask for fields
in the QueryRequest and the dataclass parses the subset that came
back."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional

from ..common import VNDBID

# 5-field cron from VNDB's review-length classifier (sourced from
# the /w listing column tc4).
ReviewLengthEnum = Literal["Short", "Medium", "Long", "Very Long"]


@dataclass
class Review:
    id: VNDBID                                    # "w16780"
    vid: Optional[VNDBID] = None                  # "v40520"
    uid: Optional[VNDBID] = None                  # "u344867" or "u0" if anonymous
    posted: Optional[str] = None                  # ISO date "YYYY-MM-DD"

    vote: Optional[float] = None                  # 1.0..10.0; None if reviewer
                                                  # didn't pair the review with a vote
    length_tag: Optional[ReviewLengthEnum] = None
    helpfulness: Optional[int] = None
    comment_count: Optional[int] = None
    has_spoiler: Optional[bool] = None

    body_html: Optional[str] = None               # raw inner HTML of the review
                                                  # cell (preserves <br>, <a>, spoiler
                                                  # spans for client-side rendering)
    body_plain: Optional[str] = None              # stripped/normalised text, suitable
                                                  # for excerpts and search

    vn_title_at_post: Optional[str] = None        # h1 title at scrape time — stable
                                                  # display label even if the VN
                                                  # gets renamed later
    release_id: Optional[VNDBID] = None           # "r106564" if Subject row mentions
                                                  # a specific release

    languages: List[str] = field(default_factory=list)   # ['en','ja','zh-Hans']
    platforms: List[str] = field(default_factory=list)   # ['win']

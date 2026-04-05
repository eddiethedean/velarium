"""TypedDict examples without ``from __future__ import annotations`` so PEP 589 keys resolve."""

from typing_extensions import NotRequired, Required, TypedDict


class TDRequiredInTotalFalse(TypedDict, total=False):
    """``Required`` key inside ``total=False``."""

    must: Required[int]
    loose: str


class TDNotRequiredOnly(TypedDict):
    a: int
    b: NotRequired[str]

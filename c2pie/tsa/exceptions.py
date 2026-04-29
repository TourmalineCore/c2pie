from __future__ import annotations


class TSAConnectionError(Exception):
    """Network error while reaching the TSA."""


class TSAResponseError(Exception):
    """TSA returned a non-granted status or an unparseable response."""


class TSATrustError(Exception):
    """TSA certificate chain does not lead to a C2PA Trust List anchor."""


class TSARequiredError(Exception):
    """Signing without a timestamp is forbidden but no TSA URL was provided."""

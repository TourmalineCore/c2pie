class TSAConnectionError(Exception):
    """Network error while reaching the TSA."""


class TSAResponseError(Exception):
    """TSA returned a non-granted status or an unparseable response."""


class TSARequiredError(Exception):
    """Signing without a timestamp is forbidden but no TSA URL was provided."""

from datetime import datetime, timezone


def iso_to_unix(timestamp_str: str):
    """
    Converts an ISO 8601 formatted date string to a UNIX timestamp in nanoseconds.

    This function parses a provided ISO 8601 string, which may or may not include timezone information.
    If no timezone is specified, the function defaults to UTC. It then converts this datetime object to
    the corresponding UNIX timestamp expressed in nanoseconds since the epoch (January 1, 1970, 00:00:00 UTC).

    Parameters:
    - timestamp_str (str): An ISO 8601 formatted datetime string.

    Returns:
    - int: The UNIX timestamp in nanoseconds corresponding to the given ISO 8601 datetime.
    """

    try:
        # Try to parse the timestamp with timezone information
        dt = datetime.fromisoformat(timestamp_str)
    except ValueError:
        # If no timezone is specified, assume UTC
        dt = datetime.fromisoformat(timestamp_str + "Z").replace(tzinfo=timezone.utc)

    # Convert to Unix timestamp (seconds since the epoch, with nanoseconds)
    unix_timestamp = int(dt.timestamp() * 1e9)
    return unix_timestamp

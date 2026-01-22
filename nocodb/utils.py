def get_query_params(filter_obj, params=None) -> dict:
    query_params = params or {}
    if filter_obj:
        query_params["where"] = filter_obj.get_where()
    return query_params


def normalize_v3_record(record: dict) -> dict:
    """
    Convert a v3 API record format to flat dict format for backwards compatibility.

    v3 format stores data in nested structure:
        {"id": 1, "fields": {"Name": "John", "Age": 30}}

    Flat format (v1-style) uses a single level:
        {"Id": 1, "Name": "John", "Age": 30}

    Args:
        record: A single record in v3 format with "id" and "fields" keys.

    Returns:
        A flat dictionary with "Id" and all field values at the top level.
        Returns empty dict if input is None or empty.

    Example:
        >>> normalize_v3_record({"id": 1, "fields": {"Name": "John"}})
        {"Id": 1, "Name": "John"}
    """
    if not record:
        return {}

    # Start with the fields dict (or empty if not present)
    flat = dict(record.get("fields", {}))

    # Add the Id field (converting from lowercase "id" to capitalized "Id")
    if "id" in record:
        flat["Id"] = record["id"]

    return flat


def normalize_v3_response(response: dict) -> dict:
    """
    Convert a v3 API list response to flat format for backwards compatibility.

    v3 format uses nested record structure:
        {
            "records": [
                {"id": 1, "fields": {"Name": "John", "Age": 30}},
                {"id": 2, "fields": {"Name": "Jane", "Age": 25}}
            ],
            "next": "cursor_token_here"
        }

    Flat format (v1-style) uses "list" key and "pageInfo":
        {
            "list": [
                {"Id": 1, "Name": "John", "Age": 30},
                {"Id": 2, "Name": "Jane", "Age": 25}
            ],
            "pageInfo": {"next": "cursor_token_here"}
        }

    Args:
        response: A v3 API response dict containing "records" array and optional "next".

    Returns:
        A dict with "list" containing flat records and "pageInfo" with pagination info.
        Returns {"list": [], "pageInfo": {}} if input is None or empty.

    Example:
        >>> normalize_v3_response({
        ...     "records": [{"id": 1, "fields": {"Name": "John"}}],
        ...     "next": "abc123"
        ... })
        {"list": [{"Id": 1, "Name": "John"}], "pageInfo": {"next": "abc123"}}
    """
    if not response:
        return {"list": [], "pageInfo": {}}

    # Normalize each record in the records array
    records = response.get("records", [])
    flat_list = [normalize_v3_record(record) for record in records]

    # Build pageInfo from pagination fields
    page_info = {}
    if "next" in response:
        page_info["next"] = response["next"]

    return {"list": flat_list, "pageInfo": page_info}

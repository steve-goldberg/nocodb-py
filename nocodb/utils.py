from typing import Callable, Dict, Any, Generator, List, Optional


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


def paginate_v3(
    fetch_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    initial_params: Optional[Dict[str, Any]] = None,
    max_pages: Optional[int] = None,
) -> Generator[Dict[str, Any], None, None]:
    """
    Generator that yields all records across pages from a v3 API endpoint.

    The v3 API uses page/pageSize params and returns a 'next' URL when more
    pages are available. This generator handles the pagination automatically.

    Args:
        fetch_fn: A callable that takes params dict and returns v3 response dict.
            The response must have 'records' array and optional 'next' URL.
        initial_params: Initial query parameters (pageSize, where, sort, etc.)
        max_pages: Optional limit on number of pages to fetch (None = unlimited)

    Yields:
        Individual records from each page (dict with 'id' and 'fields')

    Example:
        def fetch(params):
            return client.records_list_v3(base_id, table_id, params=params)

        for record in paginate_v3(fetch, {"pageSize": 100}):
            print(record["id"], record["fields"]["Name"])
    """
    params = dict(initial_params or {})
    page = 1
    pages_fetched = 0

    while True:
        if max_pages is not None and pages_fetched >= max_pages:
            break

        params["page"] = page
        response = fetch_fn(params)

        records = response.get("records", [])
        for record in records:
            yield record

        pages_fetched += 1

        # Check if there are more pages
        if not response.get("next") or not records:
            break

        page += 1


def collect_all_v3(
    fetch_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    initial_params: Optional[Dict[str, Any]] = None,
    max_pages: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Convenience function that collects all records into a list.

    This is a wrapper around paginate_v3() that returns all records as a list
    instead of a generator. Use this when you need all records in memory.

    Args:
        fetch_fn: A callable that takes params dict and returns v3 response dict
        initial_params: Initial query parameters (pageSize, where, sort, etc.)
        max_pages: Optional limit on number of pages to fetch (None = unlimited)

    Returns:
        List of all records across all pages

    Example:
        all_records = collect_all_v3(
            lambda p: client.records_list_v3(base_id, table_id, params=p),
            {"pageSize": 100}
        )
    """
    return list(paginate_v3(fetch_fn, initial_params, max_pages))

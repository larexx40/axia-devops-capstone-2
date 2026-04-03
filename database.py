def get_users():
    """
    Returns a list of users.
    Only safe, non-sensitive fields are returned.
    Credentials are never exposed in API responses.
    """
    return [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "viewer"}
    ]

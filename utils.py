def calculate_internal_metric(a, b):
    """
    Divides a by b and returns the result.
    Returns None if b is zero to prevent division by zero crash.
    """
    if b == 0:
        return None
    return a / b

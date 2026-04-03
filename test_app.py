import pytest
from app import app


@pytest.fixture
def client():
    """
    Creates a test client for the Flask app.
    TESTING=True disables error propagation so
    we can assert on HTTP responses directly.
    """
    app.config["TESTING"] = True
    return app.test_client()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HOME ENDPOINT TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_home_returns_200(client):
    """Home endpoint returns HTTP 200."""
    res = client.get("/")
    assert res.status_code == 200


def test_home_contains_message(client):
    """Home endpoint returns expected message field."""
    res = client.get("/")
    data = res.get_json()
    assert "message" in data
    assert data["message"] == "Internal Utility Service Running"


def test_home_does_not_leak_db_host(client):
    """
    Security test: home endpoint must NOT expose
    db_host in the response. This was a vulnerability
    in the original code that has been fixed.
    """
    res = client.get("/")
    data = res.get_json()
    assert "db_host" not in data


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEALTH ENDPOINT TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_health_returns_200(client):
    """Health endpoint returns HTTP 200 for Docker healthcheck."""
    res = client.get("/health")
    assert res.status_code == 200


def test_health_returns_up_status(client):
    """Health endpoint returns correct UP status body."""
    res = client.get("/health")
    data = res.get_json()
    assert data == {"status": "UP"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# USERS ENDPOINT TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_users_returns_list(client):
    """Users endpoint returns a non-empty list."""
    res = client.get("/users")
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_users_do_not_leak_credentials(client):
    """
    Security test: users endpoint must NOT expose
    db_user or db_password fields in any user object.
    These were leaked in the original code.
    """
    res = client.get("/users")
    data = res.get_json()
    for user in data:
        assert "db_user" not in user
        assert "db_password" not in user


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# METRIC ENDPOINT TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_metric_division_by_zero_returns_400(client):
    """
    Additional test: metric endpoint returns HTTP 400
    when dividing by zero instead of crashing.
    This validates the fix applied to utils.py.
    """
    res = client.get("/metric/10/0")
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data

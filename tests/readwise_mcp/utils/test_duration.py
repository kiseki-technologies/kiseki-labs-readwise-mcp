# Standard Library
from datetime import datetime, timedelta
from unittest.mock import patch

# Third Party
import pytest

# Internal Libraries
# Adjust import path to correctly import from the package
from readwise_mcp.utils.duration import parse_duration


# Fixture to mock datetime.now()
@pytest.fixture
def mocked_now():
    fixed_time = datetime(2023, 1, 15, 12, 0, 0)
    # Patch the datetime object within the module where it's used
    with patch("readwise_mcp.utils.duration.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)  # Allow creating other datetimes
        yield fixed_time


def test_parse_weeks(mocked_now):
    now = mocked_now
    # Test standard week
    expected_from = now - timedelta(weeks=1)
    assert parse_duration("1w") == (expected_from, now)

    # Test multiple weeks
    expected_from = now - timedelta(weeks=10)
    assert parse_duration("10w") == (expected_from, now)

    # Test zero weeks
    expected_from = now - timedelta(weeks=0)
    assert parse_duration("0w") == (expected_from, now)


def test_parse_hours(mocked_now):
    now = mocked_now
    # Test standard hour
    expected_from = now - timedelta(hours=1)
    assert parse_duration("1h") == (expected_from, now)

    # Test multiple hours
    expected_from = now - timedelta(hours=24)
    assert parse_duration("24h") == (expected_from, now)

    # Test zero hours
    expected_from = now - timedelta(hours=0)
    assert parse_duration("0h") == (expected_from, now)


def test_parse_minutes(mocked_now):
    now = mocked_now
    # Test standard minute
    expected_from = now - timedelta(minutes=1)
    assert parse_duration("1m") == (expected_from, now)

    # Test multiple minutes
    expected_from = now - timedelta(minutes=60)
    assert parse_duration("60m") == (expected_from, now)

    # Test zero minutes
    expected_from = now - timedelta(minutes=0)
    assert parse_duration("0m") == (expected_from, now)


@pytest.mark.parametrize("invalid_input", ["w", "1", "1ww", "1.5w", " 1w", "1w ", "w1", "", "1 day"])
def test_invalid_format(invalid_input):
    # Expect ValueError for invalid format strings
    with pytest.raises(ValueError, match="Invalid duration format"):
        parse_duration(invalid_input)


def test_invalid_format_none():
    # Test None separately as it raises TypeError before regex matching
    with pytest.raises((TypeError, ValueError)):  # Depending on Python version/regex behavior with None
        parse_duration(None)  # type: ignore


@pytest.mark.parametrize("invalid_input", ["1d", "1y", "1s", "1W", "1H", "1M"])  # Units are case-sensitive
def test_invalid_unit(invalid_input):
    # Expect ValueError for invalid units (but caught by the format regex)
    with pytest.raises(ValueError, match="Invalid duration format"):
        parse_duration(invalid_input)

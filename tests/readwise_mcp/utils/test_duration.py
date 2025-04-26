# Standard Library
from datetime import date, timedelta
from unittest.mock import patch

# Third Party
import pytest

# Internal Libraries
# Adjust import path to correctly import from the package
from readwise_mcp.utils.duration import parse_duration


# Fixture to mock date.today()
@pytest.fixture
def mocked_today():
    fixed_date = date(2023, 1, 15)
    # Patch date.today() which is used in the duration module
    with patch("readwise_mcp.utils.duration.date") as mock_date:
        mock_date.today.return_value = fixed_date
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)  # Allow creating other dates
        yield fixed_date


def test_parse_weeks(mocked_today):
    today = mocked_today
    # Test standard week
    expected_from = today - timedelta(weeks=1)
    assert parse_duration("1w") == (expected_from, today)

    # Test multiple weeks
    expected_from = today - timedelta(weeks=10)
    assert parse_duration("10w") == (expected_from, today)

    # Test zero weeks
    expected_from = today - timedelta(weeks=0)
    assert parse_duration("0w") == (expected_from, today)


def test_parse_hours(mocked_today):
    today = mocked_today
    # Test standard hour
    expected_from = today - timedelta(hours=1)
    assert parse_duration("1h") == (expected_from, today)

    # Test multiple hours
    expected_from = today - timedelta(hours=24)
    assert parse_duration("24h") == (expected_from, today)

    # Test zero hours
    expected_from = today - timedelta(hours=0)
    assert parse_duration("0h") == (expected_from, today)


def test_parse_minutes(mocked_today):
    today = mocked_today
    # Test standard minute
    expected_from = today - timedelta(minutes=1)
    assert parse_duration("1m") == (expected_from, today)

    # Test multiple minutes
    expected_from = today - timedelta(minutes=60)
    assert parse_duration("60m") == (expected_from, today)

    # Test zero minutes
    expected_from = today - timedelta(minutes=0)
    assert parse_duration("0m") == (expected_from, today)


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

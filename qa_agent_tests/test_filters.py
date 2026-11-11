"""Tests for filter_test_cases(), used by search and run-tests."""

from agent.cli import filter_test_cases


SAMPLE_TEST_CASES = [
    {"id": "TC-001", "title": "Login with valid credentials", "area_path": "App/Login",
     "assigned_to": "Diogo", "state": "Passed"},
    {"id": "TC-002", "title": "Login with wrong password", "area_path": "App/Login",
     "assigned_to": "Ana", "state": "Failed"},
    {"id": "TC-003", "title": "Checkout with card", "area_path": "App/Checkout",
     "assigned_to": "Diogo", "state": "Failed"},
]


def get_ids(test_cases):
    """Returns only the IDs, to make the results easier to compare."""
    return [tc["id"] for tc in test_cases]


def test_no_filters_returns_all_test_cases():
    results = filter_test_cases(SAMPLE_TEST_CASES)
    assert get_ids(results) == ["TC-001", "TC-002", "TC-003"]


def test_filter_by_state_ignores_case():
    results = filter_test_cases(SAMPLE_TEST_CASES, state="failed")
    assert get_ids(results) == ["TC-002", "TC-003"]


def test_filter_by_area():
    results = filter_test_cases(SAMPLE_TEST_CASES, area="checkout")
    assert get_ids(results) == ["TC-003"]


def test_filters_are_combined():
    results = filter_test_cases(SAMPLE_TEST_CASES, assignee="Diogo", state="Failed")
    assert get_ids(results) == ["TC-003"]


def test_filter_by_ids_ignores_case():
    results = filter_test_cases(SAMPLE_TEST_CASES, ids=["tc-001", "TC-003"])
    assert get_ids(results) == ["TC-001", "TC-003"]


def test_keyword_searches_the_assignee():
    results = filter_test_cases(SAMPLE_TEST_CASES, keyword="ana")
    assert get_ids(results) == ["TC-002"]


def test_no_matches_returns_empty_list():
    results = filter_test_cases(SAMPLE_TEST_CASES, state="Blocked")
    assert results == []
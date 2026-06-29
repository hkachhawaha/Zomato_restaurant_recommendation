import pytest
from zomato_ai.phase2.repository import RestaurantRepository

@pytest.fixture
def repo():
    return RestaurantRepository()

def test_repo_unique_locations(repo):
    """Verify unique locations returns a list of sorted Bangalore cities."""
    locs = repo.get_unique_locations()
    assert isinstance(locs, list)
    assert len(locs) > 0
    assert "Whitefield" in locs
    assert locs == sorted(locs)

def test_repo_unique_cuisines(repo):
    """Verify unique cuisines fetches a list of sorted cuisines."""
    cuisines = repo.get_unique_cuisines()
    assert isinstance(cuisines, list)
    assert len(cuisines) > 0
    assert "Chinese" in cuisines
    assert cuisines == sorted(cuisines)

def test_repo_exact_match(repo):
    """Verify exact match route executes correctly and returns records."""
    # Whitefield is a known city from the cache
    recs = repo.query_restaurants(
        location="Whitefield",
        min_rating=4.0,
        min_cost=200,
        max_cost=1000,
        cuisine="Chinese"
    )
    assert isinstance(recs, list)
    assert len(recs) > 0
    for r in recs:
        assert r["listed_in_city"].lower() == "whitefield"

def test_repo_fuzzy_match(repo):
    """Verify partial string match falls back to LIKE search."""
    # 'White' is a partial prefix match (not an exact city)
    recs = repo.query_restaurants(
        location="White",
        min_rating=4.0,
        min_cost=200,
        max_cost=1000,
        cuisine="Chinese"
    )
    assert isinstance(recs, list)
    assert len(recs) > 0
    for r in recs:
        assert "white" in r["listed_in_city"].lower()

def test_repo_budget_filtering(repo):
    """Verify that matches fit strictly within budget range."""
    min_b, max_b = 300, 800
    recs = repo.query_restaurants(
        location="Whitefield",
        min_rating=3.0,
        min_cost=min_b,
        max_cost=max_b,
        cuisine=""
    )
    for r in recs:
        assert r["approx_cost"] >= min_b and r["approx_cost"] <= max_b

def test_repo_empty_cuisine_fallback(repo):
    """Verify optional cuisine matches all cuisines."""
    recs_empty = repo.query_restaurants(
        location="Whitefield",
        min_rating=3.5,
        min_cost=0,
        max_cost=4000,
        cuisine=""
    )
    recs_none = repo.query_restaurants(
        location="Whitefield",
        min_rating=3.5,
        min_cost=0,
        max_cost=4000,
        cuisine=None
    )
    assert len(recs_empty) == len(recs_none)
    assert len(recs_empty) > 0

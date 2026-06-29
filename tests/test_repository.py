import sqlite3
import pytest
from zomato_ai.phase2.repository import RestaurantRepository

@pytest.fixture
def temp_db(tmp_path):
    """Fixture to set up a mock SQLite database in a temporary directory."""
    db_file = tmp_path / "test_zomato.db"
    conn = sqlite3.connect(db_file)
    try:
        cursor = conn.cursor()
        
        # Create target schema matching production schema columns
        cursor.execute("""
            CREATE TABLE restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT,
                address TEXT,
                online_order TEXT CHECK(online_order IN ('Yes', 'No')),
                book_table TEXT CHECK(book_table IN ('Yes', 'No')),
                rate REAL,
                votes INTEGER,
                phone TEXT,
                location TEXT,
                rest_type TEXT,
                dish_liked TEXT,
                cuisines TEXT,
                approx_cost INTEGER,
                reviews_list TEXT,
                listed_in_type TEXT,
                listed_in_city TEXT
            );
        """)
        
        # Insert mock dataset matching the DB schema
        restaurants_data = [
            ("Nasi And Mee", "http://nasi", "WF 1", "Yes", "Yes", 4.4, 250, "111", "Whitefield Sub", "Casual", "Momos", "Chinese, Thai", 1000, "", "", "Whitefield"),
            ("The Wok Shop", "http://wok", "WF 2", "No", "No", 4.2, 100, "112", "Whitefield Sub", "Quick", "Noodles", "Chinese", 500, "", "", "Whitefield"),
            ("Windmills", "http://wind", "WF 3", "Yes", "Yes", 4.7, 1200, "113", "Whitefield Sub", "Brewery", "Beer", "Continental", 2000, "", "", "Whitefield"),
            ("Empire Restaurant", "http://empire", "IN 1", "Yes", "No", 3.9, 800, "114", "Indiranagar Sub", "Bites", "Kabab", "North Indian", 300, "", "", "Indiranagar"),
        ]
        
        cursor.executemany("""
            INSERT INTO restaurants (name, url, address, online_order, book_table, rate, votes, phone, location, rest_type, dish_liked, cuisines, approx_cost, reviews_list, listed_in_type, listed_in_city)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, restaurants_data)
        
        conn.commit()
    finally:
        conn.close()
    
    yield db_file
    
    # Clean up temp database file using pathlib
    db_file.unlink(missing_ok=True)

def test_query_filter_logic(temp_db):
    # Initialize repository pointing to test database
    repo = RestaurantRepository(db_path=temp_db)
    
    # Test case 1: Query exact listed_in_city (locality), rating, budget, and cuisine matches
    results = repo.query_restaurants(
        location="Whitefield",
        min_rating=4.0,
        min_cost=400,
        max_cost=1200,
        cuisine="Chinese"
    )
    
    # Windmills cost is 2000 (filtered), Empire location is Indiranagar (filtered)
    # Expected matches: Nasi And Mee (1000) and The Wok Shop (500)
    assert len(results) == 2
    names = [r["name"] for r in results]
    assert "Nasi And Mee" in names
    assert "The Wok Shop" in names
    
    # Test case 2: Rating bounds filtering on listed_in_city
    results_high_rate = repo.query_restaurants(
        location="Whitefield",
        min_rating=4.5,
        min_cost=0,
        max_cost=3000,
        cuisine="Continental"
    )
    # Expected: Windmills (4.7)
    assert len(results_high_rate) == 1
    assert results_high_rate[0]["name"] == "Windmills"

    # Test case 3: Fuzzy listed_in_city matches (Testing LIKE %location% query)
    results_fuzzy_loc = repo.query_restaurants(
        location="Indira",
        min_rating=3.0,
        min_cost=0,
        max_cost=1000,
        cuisine="North Indian"
    )
    # Expected: Empire Restaurant (Indiranagar matches 'Indira' via LIKE statement)
    assert len(results_fuzzy_loc) == 1
    assert results_fuzzy_loc[0]["name"] == "Empire Restaurant"

    # Test case 4: Empty / Optional Cuisine matching
    results_empty_cuisine = repo.query_restaurants(
        location="Whitefield",
        min_rating=4.0,
        min_cost=0,
        max_cost=3000,
        cuisine=""
    )
    # Expected: Nasi And Mee (Chinese, Thai), The Wok Shop (Chinese), and Windmills (Continental)
    assert len(results_empty_cuisine) == 3

    # Test case 5: None / Null Cuisine matching (safe fallback check)
    results_null_cuisine = repo.query_restaurants(
        location="Whitefield",
        min_rating=4.0,
        min_cost=0,
        max_cost=3000,
        cuisine=None
    )
    # Expected: Nasi And Mee (Chinese, Thai), The Wok Shop (Chinese), and Windmills (Continental)
    assert len(results_null_cuisine) == 3

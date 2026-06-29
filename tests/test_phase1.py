import sqlite3
import numpy as np
from zomato_ai.config import settings
from zomato_ai.phase1.ingestion import clean_rate, clean_cost

def test_clean_rate_valid():
    """Verify clean_rate parses float representation correctly."""
    assert clean_rate("4.1/5") == 4.1
    assert clean_rate("4.8") == 4.8
    assert clean_rate("3.0/5") == 3.0

def test_clean_rate_invalid():
    """Verify clean_rate disposes of non-numeric tokens."""
    assert clean_rate("NEW") is None
    assert clean_rate("-") is None
    assert clean_rate(np.nan) is None
    assert clean_rate(None) is None

def test_clean_cost_commas():
    """Verify clean_cost parses formatted currency strings."""
    assert clean_cost("1,200") == 1200.0
    assert clean_cost("   500   ") == 500.0
    assert clean_cost("2,500 for two") == 2500.0

def test_clean_cost_empty():
    """Verify clean_cost parses blank or invalid costs."""
    assert clean_cost(np.nan) is None
    assert clean_cost(None) is None
    assert clean_cost("") is None

def test_restaurants_table_exists():
    """Verify the database schema contains the target table and columns."""
    conn = sqlite3.connect(settings.db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(restaurants);")
        columns = cursor.fetchall()
        assert len(columns) > 0, "restaurants table does not exist or has no columns"
        col_names = [col[1] for col in columns]
        assert "listed_in_city" in col_names
        assert "cuisines" in col_names
        assert "approx_cost" in col_names
    finally:
        conn.close()

def test_db_indexes_exists():
    """Verify the sqlite index optimizations are present."""
    conn = sqlite3.connect(settings.db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Verify indexes listed in architecture specs
        assert "idx_restaurants_cost" in indexes
        assert "idx_restaurants_rate" in indexes
        assert "idx_restaurants_listed_in_city" in indexes
    finally:
        conn.close()

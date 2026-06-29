import time
import sqlite3
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from zomato_ai.config import settings
from zomato_ai.phase2.api import app
from zomato_ai.phase2.repository import RestaurantRepository
from zomato_ai.phase3.llm_client import LLMClient

client = TestClient(app)

def test_database_schema_validation():
    """Verifies that the SQLite database matches the schema specification DDL exactly."""
    conn = sqlite3.connect(settings.db_path)
    try:
      cursor = conn.cursor()
      cursor.execute("PRAGMA table_info(restaurants);")
      columns = cursor.fetchall()
      
      # Columns returned as tuple: (cid, name, type, notnull, dflt_value, pk)
      col_names = {col[1]: col[2].upper() for col in columns}
      
      expected_columns = {
          "id": "INTEGER",
          "name": "TEXT",
          "url": "TEXT",
          "address": "TEXT",
          "online_order": "TEXT",
          "book_table": "TEXT",
          "rate": "REAL",
          "votes": "INTEGER",
          "phone": "TEXT",
          "location": "TEXT",
          "rest_type": "TEXT",
          "dish_liked": "TEXT",
          "cuisines": "TEXT",
          "approx_cost": "INTEGER",
          "reviews_list": "TEXT",
          "listed_in_type": "TEXT",
          "listed_in_city": "TEXT"
      }
      
      for col, expected_type in expected_columns.items():
          assert col in col_names, f"Missing expected column: '{col}' in restaurants table"
          # Check for type compatibility (e.g. SQLite types might vary slightly, but base check)
          assert expected_type in col_names[col], f"Type mismatch for '{col}': expected {expected_type}, got {col_names[col]}"
          
      print("Success! Database schema validation passed.")
    finally:
      conn.close()

def test_query_execution_speed():
    """Benchmarks the database search query execution to verify it runs within the 5ms performance budget."""
    conn = sqlite3.connect(settings.db_path)
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                name, url, address, online_order, book_table, rate, votes, 
                phone, location, rest_type, dish_liked, cuisines, approx_cost, listed_in_city
            FROM restaurants
            WHERE 
                listed_in_city = ?
                AND rate >= ?
                AND approx_cost BETWEEN ? AND ?
                AND cuisines LIKE ?;
        """
        
        # Warmup
        cursor.execute(query, ("Whitefield", 4.0, 200, 1000, "%Chinese%"))
        cursor.fetchall()
        
        start_time = time.perf_counter()
        iterations = 200
        for _ in range(iterations):
            cursor.execute(query, ("Whitefield", 4.0, 200, 1000, "%Chinese%"))
            cursor.fetchall()
        end_time = time.perf_counter()
        
        avg_duration_ms = ((end_time - start_time) / iterations) * 1000
        print(f"\nAverage query execution time: {avg_duration_ms:.4f} ms")
        
        # Assert query execution is <= 5ms budget
        assert avg_duration_ms <= 5.0, f"Query execution took {avg_duration_ms:.4f} ms (exceeded 5.0 ms budget)"
    finally:
        conn.close()

def test_api_fallback_response_time():
    """Benchmarks the API fallback response speed to verify it completes within the 100ms budget."""
    # Mock the LLM client to force fallback activation
    with patch.object(LLMClient, 'get_recommendations_with_reasoning', side_effect=RuntimeError("Mock Timeout")):
        payload = {
            "location": "Whitefield",
            "min_budget": 500,
            "max_budget": 1200,
            "cuisine": "Chinese",
            "min_rating": 4.0,
            "additional_preferences": "famous for dim sums"
        }
        
        # Warmup
        client.post("/api/recommend", json=payload)
        
        start_time = time.perf_counter()
        iterations = 50
        for _ in range(iterations):
            response = client.post("/api/recommend", json=payload)
            assert response.status_code == 200
            
        end_time = time.perf_counter()
        avg_response_ms = ((end_time - start_time) / iterations) * 1000
        print(f"\nAverage fallback API response time: {avg_response_ms:.2f} ms")
        
        # Assert fallback API response is <= 100ms budget
        assert avg_response_ms <= 100.0, f"API response took {avg_response_ms:.2f} ms (exceeded 100.0 ms budget)"

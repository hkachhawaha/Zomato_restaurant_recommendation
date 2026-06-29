import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
from zomato_ai.config import settings

class RestaurantRepository:
    _cities_cache = None

    def __init__(self, db_path: Path = settings.db_path):
        self.db_path = db_path
        if RestaurantRepository._cities_cache is None:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT listed_in_city FROM restaurants WHERE listed_in_city IS NOT NULL AND listed_in_city != '';")
                rows = cursor.fetchall()
                RestaurantRepository._cities_cache = {r[0].lower() for r in rows if r[0]}
                conn.close()
            except Exception:
                RestaurantRepository._cities_cache = set()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        # Configure row factory to return dicts instead of tuples for easy model mapping
        conn.row_factory = sqlite3.Row
        return conn

    def get_unique_locations(self) -> List[str]:
        """Fetches distinct localities (listed_in_city) sorted alphabetically."""
        query = """
            SELECT DISTINCT listed_in_city 
            FROM restaurants 
            WHERE listed_in_city IS NOT NULL AND listed_in_city != '' 
            ORDER BY listed_in_city ASC;
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [row["listed_in_city"] for row in rows]
        finally:
            conn.close()

    def get_unique_cuisines(self) -> List[str]:
        """Fetches and normalizes a unique list of all cuisines."""
        query = "SELECT cuisines FROM restaurants WHERE cuisines IS NOT NULL;"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            unique_cuisines = set()
            for row in rows:
                parts = row["cuisines"].split(",")
                for part in parts:
                    cuisine = part.strip()
                    if cuisine:
                        unique_cuisines.add(cuisine)
            return sorted(list(unique_cuisines))
        finally:
            conn.close()

    def query_restaurants(
        self, 
        location: str, 
        min_rating: float, 
        min_cost: int, 
        max_cost: int, 
        cuisine: Optional[str] = ""
    ) -> List[Dict[str, Any]]:
        """Queries the restaurants database with strict and fuzzy constraints."""
        location_lower = location.lower()
        use_exact = location_lower in self._cities_cache
        
        query = f"""
            SELECT 
                name, url, address, online_order, book_table, rate, votes, 
                phone, location, rest_type, dish_liked, cuisines, approx_cost, listed_in_city
            FROM restaurants
            WHERE 
                listed_in_city {"=" if use_exact else "LIKE"} ?
                AND rate >= ?
                AND approx_cost BETWEEN ? AND ?
        """
        params = [location if use_exact else f"%{location}%", min_rating, min_cost, max_cost]
        
        if cuisine and cuisine.strip():
            query += " AND cuisines LIKE ?"
            params.append(f"%{cuisine.strip()}%")
            
        query += ";"
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            # Convert list of sqlite3.Row to list of standard dicts
            return [dict(row) for row in rows]
        except sqlite3.OperationalError as e:
            # Handle missing table or schema issues gracefully
            import logging
            logging.getLogger(__name__).error(f"Database query failed: {e}. Verify zomato_restaurants.db exists and contains the 'restaurants' table.")
            return []
        finally:
            conn.close()

    def get_restaurant_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Queries the restaurants database for a single restaurant by exact name."""
        query = """
            SELECT 
                name, url, address, online_order, book_table, rate, votes, 
                phone, location, rest_type, dish_liked, cuisines, approx_cost, listed_in_city
            FROM restaurants
            WHERE LOWER(name) = LOWER(?)
            LIMIT 1;
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

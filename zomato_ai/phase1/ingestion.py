import sqlite3
import pandas as pd
import numpy as np
import re
from pathlib import Path
from datasets import load_dataset
from zomato_ai.config import settings

def download_raw_data() -> pd.DataFrame:
    """Downloads the raw dataset from Hugging Face and returns it as a pandas DataFrame."""
    print("Downloading dataset 'ManikaSaini/zomato-restaurant-recommendation' from Hugging Face...")
    # Load dataset. Usually it returns a DatasetDict. We fetch the 'train' split.
    dataset = load_dataset("ManikaSaini/zomato-restaurant-recommendation")
    df = dataset["train"].to_pandas()
    print(f"Successfully downloaded raw dataset. Shape: {df.shape}")
    return df

def clean_rate(val) -> float:
    """Cleans a single rating value, parsing it to a float or returning None/NaN."""
    if pd.isna(val):
        return None
    val_str = str(val).strip()
    # Handle NEW, - or empty values
    if val_str.upper() in ("NEW", "-", ""):
        return None
    
    # Remove "/5" if present (e.g. "4.1/5" -> "4.1")
    val_str = val_str.split('/')[0].strip()
    
    try:
        return float(val_str)
    except ValueError:
        return None

def clean_cost(val) -> float:
    """Cleans a cost value, removing commas and parsing to float, or returning None/NaN."""
    if pd.isna(val):
        return None
    val_str = str(val).strip()
    # Remove commas, currency symbols, and extra spaces
    val_str = re.sub(r"[^\d]", "", val_str)
    if not val_str:
        return None
    try:
        return float(val_str)
    except ValueError:
        return None

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and normalizes the raw DataFrame based on design guidelines."""
    print("Cleansing and preprocessing dataset...")
    
    # 1. Column Selection & Renaming
    target_columns = {
        "name": "name",
        "url": "url",
        "address": "address",
        "online_order": "online_order",
        "book_table": "book_table",
        "rate": "rate",
        "votes": "votes",
        "phone": "phone",
        "location": "location",
        "rest_type": "rest_type",
        "dish_liked": "dish_liked",
        "cuisines": "cuisines",
        "approx_cost(for two people)": "approx_cost",
        "reviews_list": "reviews_list",
        "listed_in(type)": "listed_in_type",
        "listed_in(city)": "listed_in_city"
    }
    
    # Keep only the target columns that exist in the raw dataset
    existing_cols = [col for col in target_columns.keys() if col in df.columns]
    df_clean = df[existing_cols].copy()
    
    # Rename them to match the database schema
    df_clean.rename(columns={k: v for k, v in target_columns.items() if k in existing_cols}, inplace=True)
    
    # 2. Missing Value Imputation
    # Drop rows where location is null (crucial filter field)
    df_clean.dropna(subset=["location"], inplace=True)
    
    # Default values for missing strings
    df_clean["cuisines"] = df_clean["cuisines"].fillna("Unknown Cuisines")
    df_clean["online_order"] = df_clean["online_order"].fillna("No")
    df_clean["book_table"] = df_clean["book_table"].fillna("No")
    
    # 3. Numeric Parsing
    # Rate Cleansing
    df_clean["rate"] = df_clean["rate"].apply(clean_rate)
    
    # Cost Normalization
    df_clean["approx_cost"] = df_clean["approx_cost"].apply(clean_cost)
    
    # Ensure votes is integer type, handle null votes as 0
    df_clean["votes"] = df_clean["votes"].fillna(0).astype(int)
    
    # 4. Impute missing costs using median cost of location and rest_type
    # Compute group medians
    group_medians = df_clean.groupby(["location", "rest_type"])["approx_cost"].transform("median")
    df_clean["approx_cost"] = df_clean["approx_cost"].fillna(group_medians)
    
    # Fallback to location median if rest_type median is also NaN
    location_medians = df_clean.groupby("location")["approx_cost"].transform("median")
    df_clean["approx_cost"] = df_clean["approx_cost"].fillna(location_medians)
    
    # Fallback to global median if still NaN
    global_median = df_clean["approx_cost"].median()
    if pd.isna(global_median):
        global_median = 500.0  # default backup
    df_clean["approx_cost"] = df_clean["approx_cost"].fillna(global_median)
    
    # Convert approx_cost to integer
    df_clean["approx_cost"] = df_clean["approx_cost"].round().astype(int)
    
    # 5. Data Deduplication
    # Deduplicate on lowercase name + address to keep unique establishments
    df_clean["name_lower"] = df_clean["name"].astype(str).str.lower().str.strip()
    df_clean["address_lower"] = df_clean["address"].astype(str).str.lower().str.strip()
    
    initial_len = len(df_clean)
    df_clean.drop_duplicates(subset=["name_lower", "address_lower"], keep="first", inplace=True)
    deduped_len = len(df_clean)
    
    # Drop temp columns
    df_clean.drop(columns=["name_lower", "address_lower"], inplace=True)
    
    print(f"Data preprocessing finished. Deduplicated: {initial_len - deduped_len} rows. Remaining: {deduped_len} rows.")
    return df_clean

def save_to_sqlite(df: pd.DataFrame, db_path: Path):
    """Saves the cleaned DataFrame into the SQLite database with exact schema and DDL constraints."""
    print(f"Saving data to SQLite database at {db_path}...")
    # Create parent directories if they don't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Recreate the table with explicit constraints
        cursor.execute("DROP TABLE IF EXISTS restaurants;")
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
        conn.commit()
        
        # Append data to the newly created table
        df.to_sql("restaurants", conn, if_exists="append", index=False)
        print("Data loaded to table 'restaurants' successfully.")
    finally:
        conn.close()

def create_indexes(db_path: Path):
    """Applies indexes on primary filtering columns for high performance."""
    print("Creating indexes on the database tables...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_restaurants_location ON restaurants(location);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_restaurants_cost ON restaurants(approx_cost);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_restaurants_rate ON restaurants(rate);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_restaurants_listed_in_city ON restaurants(listed_in_city COLLATE NOCASE);")
        conn.commit()
        print("Indexes created successfully.")
    except Exception as e:
        print(f"Error creating indexes: {e}")
    finally:
        conn.close()

def run_ingestion():
    """Coordinates the full data ingestion and indexing process."""
    db_path = settings.db_path
    
    # 1. Download data
    df_raw = download_raw_data()
    
    # 2. Clean data
    df_cleaned = clean_dataset(df_raw)
    
    # 3. Save to database
    save_to_sqlite(df_cleaned, db_path)
    
    # 4. Create database indexes
    create_indexes(db_path)
    
    # 5. Print quick summary stats
    print("\n" + "="*40)
    print("INGESTION WORKFLOW COMPLETE")
    print("="*40)
    print(f"Database File: {db_path.name}")
    print(f"Database Size: {db_path.stat().st_size / (1024*1024):.2f} MB")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Check rows
        cursor.execute("SELECT COUNT(*) FROM restaurants;")
        total_rows = cursor.fetchone()[0]
        
        # Check unique locations
        cursor.execute("SELECT COUNT(DISTINCT location) FROM restaurants;")
        total_locations = cursor.fetchone()[0]
        
        # Get location counts snippet
        cursor.execute("SELECT location, COUNT(*) FROM restaurants GROUP BY location ORDER BY COUNT(*) DESC LIMIT 5;")
        top_locations = cursor.fetchall()
        
        print(f"Total Rows Ingested: {total_rows}")
        print(f"Total Unique Locations: {total_locations}")
        print("Top 5 Locations by Restaurant Count:")
        for loc, count in top_locations:
            print(f"  - {loc}: {count} restaurants")
            
    finally:
        conn.close()
    print("="*40)

if __name__ == "__main__":
    run_ingestion()

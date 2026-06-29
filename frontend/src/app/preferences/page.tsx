"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useApp, Preferences } from "@/context/AppContext";
import { API_BASE_URL } from "@/config";

const FALLBACK_LOCATIONS = [
  "Whitefield", "Indiranagar", "Koramangala", "Jayanagar", "JP Nagar", 
  "BTM", "HSR", "Marathahalli", "Bannerghatta Road", "Bellandur", 
  "Malleshwaram", "Rajajinagar", "MG Road", "Brigade Road", "Residency Road", 
  "Lavelle Road", "Church Street"
];

const FALLBACK_CUISINES = [
  "Chinese", "North Indian", "Continental", "South Indian", "Italian", 
  "American", "Asian", "Desserts", "Bakery", "Biryani"
];

export default function PreferencesPage() {
  const router = useRouter();
  const { preferences, setPreferences, setRecommendations, loading, setLoading, setError } = useApp();
  
  const [locations, setLocations] = useState<string[]>(FALLBACK_LOCATIONS);
  const [allCuisines, setAllCuisines] = useState<string[]>(FALLBACK_CUISINES);
  const [showAllCuisines, setShowAllCuisines] = useState<boolean>(false);
  const [locSearch, setLocSearch] = useState<string>(preferences.location || "");
  const [showLocDropdown, setShowLocDropdown] = useState<boolean>(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fetch unique fields from API on mount
  useEffect(() => {
    async function fetchData() {
      try {
        const locRes = await fetch(`${API_BASE_URL}/api/locations`);
        if (locRes.ok) {
          const locs = await locRes.json();
          if (Array.isArray(locs) && locs.length > 0) setLocations(locs);
        }
        
        const cuisRes = await fetch(`${API_BASE_URL}/api/cuisines`);
        if (cuisRes.ok) {
          const cuis = await cuisRes.json();
          if (Array.isArray(cuis) && cuis.length > 0) setAllCuisines(cuis);
        }
      } catch (err) {
        console.warn("Failed fetching autocomplete metadata from backend API. Using local fallbacks.", err);
      }
    }
    fetchData();
  }, []);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowLocDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleInputChange = (field: keyof Preferences, value: any) => {
    setPreferences(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCuisineToggle = (cuisineName: string) => {
    const current = preferences.cuisine;
    if (current.toLowerCase() === cuisineName.toLowerCase()) {
      handleInputChange("cuisine", ""); // Deselect
    } else {
      handleInputChange("cuisine", cuisineName);
    }
  };

  const handleQuickTagClick = (tag: string) => {
    const current = preferences.additional_preferences;
    if (current.includes(tag)) return;
    const separator = current.trim() ? ", " : "";
    handleInputChange("additional_preferences", `${current}${separator}${tag}`);
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    // Make sure location is set
    const finalLocation = locSearch.trim();
    if (!finalLocation) {
      setError("Please select or enter a neighborhood location.");
      setLoading(false);
      return;
    }

    const payload = {
      location: finalLocation,
      min_budget: Number(preferences.min_budget),
      max_budget: Number(preferences.max_budget),
      cuisine: preferences.cuisine || "",
      min_rating: Number(preferences.min_rating),
      additional_preferences: preferences.additional_preferences || ""
    };

    try {
      const res = await fetch(`${API_BASE_URL}/api/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`Server returned error status ${res.status}`);
      }

      const data = await res.json();
      if (data && Array.isArray(data.recommendations)) {
        setRecommendations(data.recommendations);
      } else {
        setRecommendations([]);
      }
      
      // Update saved location
      handleInputChange("location", finalLocation);
      
      // Redirect to recommendations page
      router.push("/recommendations");
    } catch (err: any) {
      console.error("Match retrieval failed: ", err);
      setError(err.message || "Failed to retrieve restaurant recommendations. Ensure the backend server is running.");
      // Redirect anyway so results view can present fallback/error state appropriately
      router.push("/recommendations");
    } finally {
      setLoading(false);
    }
  };

  // Filter locations based on typing
  const filteredLocs = locations.filter(l => 
    l.toLowerCase().includes(locSearch.toLowerCase())
  );

  return (
    <main className="main-wrapper">
      <h2 className="page-title">Set Your Preferences</h2>
      <p className="page-subtitle">Help GourmetAI curate the perfect dining experience tailored just for you.</p>

      <form className="pref-panel" onSubmit={handleFormSubmit}>
        
        {/* Your Location */}
        <div className="pref-section-title">
          <span>📍</span> Your Location
        </div>
        <div className="location-block">
          <div className="form-field-group" ref={dropdownRef}>
            <label className="form-label">City or Neighborhood (Bangalore)</label>
            <div className="search-select-wrapper">
              <input 
                type="text" 
                className="text-input-field"
                placeholder="Search or select neighborhood..."
                value={locSearch}
                onChange={(e) => {
                  setLocSearch(e.target.value);
                  setShowLocDropdown(true);
                }}
                onFocus={() => setShowLocDropdown(true)}
                required
              />
              <span 
                className="dropdown-arrow-caret" 
                onClick={() => setShowLocDropdown(prev => !prev)}
              >
                ▼
              </span>

              {showLocDropdown && (
                <div className="suggestions-dropdown-list">
                  {filteredLocs.length > 0 ? (
                    filteredLocs.map((loc, idx) => (
                      <div 
                        key={idx}
                        className="suggestion-item"
                        onClick={() => {
                          setLocSearch(loc);
                          handleInputChange("location", loc);
                          setShowLocDropdown(false);
                        }}
                      >
                        {loc}
                      </div>
                    ))
                  ) : (
                    <div className="suggestion-item" style={{ color: "var(--text-muted)", cursor: "default" }}>
                      No neighborhoods found
                    </div>
                  )}
                </div>
              )}
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: "0.8rem", marginTop: "0.25rem" }}>
              We will use this to search within corresponding Zomato Listed-In City boundaries.
            </p>
          </div>

          <div className="loc-preview-img-wrapper">
            <img 
              src="https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=600&q=80" 
              alt="Bangalore Skyline" 
              className="loc-preview-img" 
            />
            <span className="loc-preview-badge">🔴 Live View: {locSearch || "Bangalore"}</span>
          </div>
        </div>

        {/* Budget & Ratings */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2.5rem" }}>
          
          <div>
            <div className="pref-section-title">
              <span>💳</span> Budget Range
            </div>
            <div className="budget-rating-block">
              <div className="form-field-group">
                <label className="form-label">Min (₹)</label>
                <div className="budget-input-wrapper">
                  <span className="currency-symbol-label">₹</span>
                  <input 
                    type="number" 
                    className="numeric-input"
                    value={preferences.min_budget}
                    onChange={(e) => handleInputChange("min_budget", Number(e.target.value))}
                    min="0"
                    required
                  />
                </div>
              </div>

              <div className="form-field-group">
                <label className="form-label">Max (₹)</label>
                <div className="budget-input-wrapper">
                  <span className="currency-symbol-label">₹</span>
                  <input 
                    type="number" 
                    className="numeric-input"
                    value={preferences.max_budget}
                    onChange={(e) => handleInputChange("max_budget", Number(e.target.value))}
                    min="0"
                    required
                  />
                </div>
              </div>
            </div>
          </div>

          <div>
            <div className="pref-section-title">
              <span>⭐</span> Minimum Rating
            </div>
            <div className="form-field-group">
              <label className="form-label">Star rating threshold</label>
              <div className="star-rating-holder">
                {[1, 2, 3, 4, 5].map((star) => (
                  <span 
                    key={star} 
                    className={star <= preferences.min_rating ? "active-star" : ""}
                    onClick={() => handleInputChange("min_rating", star)}
                  >
                    ★
                  </span>
                ))}
              </div>
              <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                {preferences.min_rating.toFixed(1)} stars and above selected
              </p>
            </div>
          </div>

        </div>

        {/* Favorite Cuisines */}
        <div className="pref-section-title" style={{ marginTop: "1rem" }}>
          <span>🍴</span> Favorite Cuisines (Optional)
        </div>
        <div className="cuisines-pills-list">
          {(showAllCuisines ? allCuisines : allCuisines.slice(0, 11)).map((c, idx) => (
            <button 
              type="button"
              key={idx}
              className={`cuisine-toggle-pill ${preferences.cuisine.toLowerCase() === c.toLowerCase() ? "active" : ""}`}
              onClick={() => handleCuisineToggle(c)}
            >
              {c}
            </button>
          ))}
          {!showAllCuisines ? (
            <button 
              type="button" 
              className="cuisine-toggle-pill"
              style={{ color: "var(--primary)", borderColor: "var(--primary)" }}
              onClick={() => setShowAllCuisines(true)}
            >
              More
            </button>
          ) : (
            <button 
              type="button" 
              className="cuisine-toggle-pill"
              style={{ color: "var(--primary)", borderColor: "var(--primary)" }}
              onClick={() => setShowAllCuisines(false)}
            >
              Less
            </button>
          )}
        </div>

        {/* Additional Details */}
        <div className="pref-section-title">
          <span>🎚️</span> Additional Details
        </div>
        <div className="form-field-group">
          <label className="form-label">Special Preferences & Vibe</label>
          <textarea 
            className="textarea-field"
            rows={3}
            placeholder="e.g. 'Rooftop seating', 'Valet parking', 'Family-friendly atmosphere', 'Serving craft beer'..."
            value={preferences.additional_preferences}
            onChange={(e) => handleInputChange("additional_preferences", e.target.value)}
          />
          <div className="quick-pref-tags">
            <span className="quick-tag-pill" onClick={() => handleQuickTagClick("rooftop")}>+ rooftop</span>
            <span className="quick-tag-pill" onClick={() => handleQuickTagClick("family friendly")}>+ family friendly</span>
            <span className="quick-tag-pill" onClick={() => handleQuickTagClick("outdoor seating")}>+ outdoor seating</span>
            <span className="quick-tag-pill" onClick={() => handleQuickTagClick("craft beer")}>+ craft beer</span>
            <span className="quick-tag-pill" onClick={() => handleQuickTagClick("live music")}>+ live music</span>
          </div>
        </div>

        {/* Actions bar */}
        <div className="pref-actions-bar">
          <button 
            type="submit" 
            className="hero-btn" 
            style={{ padding: "0.85rem 2rem" }}
            disabled={loading}
          >
            {loading ? "Finding Matches..." : "Find My Match →"}
          </button>
          <button 
            type="button" 
            className="clear-btn"
            onClick={() => {
              setLocSearch("");
              setPreferences({
                location: "",
                min_budget: 200,
                max_budget: 1000,
                cuisine: "",
                min_rating: 3.5,
                additional_preferences: ""
              });
            }}
          >
            Clear All
          </button>
        </div>

      </form>
    </main>
  );
}

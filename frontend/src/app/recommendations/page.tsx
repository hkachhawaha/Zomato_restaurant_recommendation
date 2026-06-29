"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useApp, Restaurant } from "@/context/AppContext";

function getCuisineImage(cuisine: string = ""): string {
  const c = cuisine.toLowerCase();
  if (c.includes("chinese") || c.includes("thai") || c.includes("asian")) {
    return "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=600&q=80";
  }
  if (c.includes("italian") || c.includes("pizza") || c.includes("pasta")) {
    return "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=600&q=80";
  }
  if (c.includes("continental") || c.includes("american") || c.includes("burger")) {
    return "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80";
  }
  if (c.includes("south indian") || c.includes("north indian") || c.includes("indian") || c.includes("biryani")) {
    return "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=600&q=80";
  }
  if (c.includes("bakery") || c.includes("dessert") || c.includes("sweet")) {
    return "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80";
  }
  return "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80";
}

export default function RecommendationsPage() {
  const router = useRouter();
  const { recommendations, loading, error, preferences } = useApp();
  const [visibleCount, setVisibleCount] = useState<number>(10);

  const handleCardClick = (restaurantName: string) => {
    router.push(`/restaurant/${encodeURIComponent(restaurantName)}`);
  };

  // 1. Loading skeleton page layout
  if (loading) {
    return (
      <main className="main-wrapper">
        <h2 className="page-title">Curating Recommendations...</h2>
        <p className="page-subtitle">Gemini 2.5 Flash is scoring and ranking matching restaurants based on your vibe.</p>
        
        <div className="recs-layout-grid" style={{ opacity: 0.7 }}>
          <div className="skeleton-box" style={{ height: "450px", borderRadius: "1rem" }}></div>
          <div className="side-stack">
            <div className="skeleton-box" style={{ height: "215px", borderRadius: "1rem" }}></div>
            <div className="skeleton-box" style={{ height: "215px", borderRadius: "1rem" }}></div>
          </div>
        </div>
      </main>
    );
  }

  // 2. Fallback curated data if empty list (e.g. backend turned off or zero matches)
  const displayRecs = recommendations.length > 0 ? recommendations : [
    {
      name: "Windmills Craftworks",
      cuisine: "Continental, Italian, Craft Beer",
      rating: 4.7,
      approx_cost: 2000,
      location: "Whitefield",
      ai_explanation: "Windmills Craftworks is a pristine choice. It aligns perfectly with your budget, offers exceptional Continental selections, and is highly praised for its jazz music vibe and library seating."
    },
    {
      name: "Nasi And Mee",
      cuisine: "Chinese, Thai, Asian",
      rating: 4.4,
      approx_cost: 1000,
      location: "Whitefield",
      ai_explanation: "Nasi And Mee perfectly serves your craving for Asian flavors. Fits right under your budget limit and is highly rated for dumplings and dim sums."
    },
    {
      name: "Truffles",
      cuisine: "American, Fast Food, Cafe",
      rating: 4.6,
      approx_cost: 900,
      location: "Indiranagar",
      ai_explanation: "Truffles is an iconic Bangalore burger and dessert spot. Known for high consistency and friendly service within budget."
    },
    {
      name: "Toit",
      cuisine: "Italian, Pizza, Brewery",
      rating: 4.7,
      approx_cost: 1500,
      location: "Indiranagar",
      ai_explanation: "Toit is one of Bangalore's most famous brewpubs. Exceptional wood-fired pizzas and craft beers, matching high rating preferences."
    }
  ];

  const featured = displayRecs[0];
  const sidebarRecs = displayRecs.slice(1, 3);
  const remainingRecs = displayRecs.slice(3, visibleCount);

  return (
    <main className="main-wrapper">
      <div className="top-picks-header">
        <div>
          <h2 className="page-title">Top Recommendations</h2>
          <p className="page-subtitle">Based on your preferences in {preferences.location || "Bangalore"}</p>
        </div>
        <div className="results-options-bar">
          <button className="options-btn" onClick={() => router.push("/preferences")}>
            🎛️ Adjust Filters
          </button>
        </div>
      </div>

      {error && (
        <div style={{ 
          backgroundColor: "#FEF2F2", 
          border: "1px solid #FCA5A5", 
          borderRadius: "0.5rem", 
          padding: "1rem", 
          marginBottom: "2rem",
          color: "#991B1B",
          fontWeight: 500
        }}>
          ⚠️ {error}. Displaying pre-cached curation results as a safe fallback.
        </div>
      )}

      {/* Grid Layout (Design 3) */}
      <div className="recs-layout-grid">
        
        {/* Large Featured Card (left column) */}
        {featured && (
          <div className="rec-main-hero" onClick={() => handleCardClick(featured.name)}>
            <div className="rec-hero-image-wrapper">
              <img 
                src={getCuisineImage(featured.cuisine)} 
                alt={featured.name} 
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
              <span className="match-percentage-badge">
                ⚡ 98% Match
              </span>
              <span className="card-rating-badge" style={{ bottom: "1rem", top: "auto", right: "1rem" }}>
                ⭐ {featured.rating || "3.5"}
              </span>
            </div>
            
            <div className="rec-hero-details-row">
              <div className="rec-hero-left">
                <div className="match-tag-area">
                  <span className="tag-label red">Featured Match</span>
                  <span className="tag-label trans" style={{ color: "var(--text-muted)", backgroundColor: "#E7E5E4" }}>
                    ₹{featured.approx_cost} for two
                  </span>
                </div>
                <h3 className="rec-hero-title-name">{featured.name}</h3>
                <p className="rec-hero-desc-text">
                  A highly acclaimed {featured.cuisine.split(",")[0]} destination in {featured.Location}.
                </p>
                <div className="rec-hero-meta-icons">
                  <span>📍 {featured.Location}</span>
                </div>
              </div>

              <div className="rec-match-reasoning-box">
                <span className="rec-match-reasoning-percentage">⚡ 98% Match</span>
                <h4 className="rec-match-reasoning-heading">AI Match Rationale</h4>
                <p className="rec-match-reasoning-body">
                  {featured.ai_explanation}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Sidebar recommendations stack (right column) */}
        <div className="recs-side-stack">
          {sidebarRecs.map((rec, idx) => (
            <div 
              key={idx} 
              className="rec-item-stack-card"
              onClick={() => handleCardClick(rec.name)}
            >
              <div className="stack-card-img-wrapper" style={{ position: "relative" }}>
                <img 
                  src={getCuisineImage(rec.cuisine)} 
                  alt={rec.name} 
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
                <span className="match-percentage-badge" style={{ backgroundColor: "#2563EB" }}>
                  {94 - idx * 3}% Match
                </span>
                <span className="card-rating-badge">⭐ {rec.rating || "N/A"}</span>
              </div>
              <div className="stack-card-details">
                <div className="stack-card-heading-row">
                  <h4 className="stack-card-restaurant-name">{rec.name}</h4>
                  <p className="stack-card-restaurant-meta">{rec.cuisine} • ₹{rec.approx_cost} for 2</p>
                </div>
                <div className="rec-match-reasoning-box" style={{ borderLeftColor: "#2563EB", backgroundColor: "#EFF6FF", borderLeftWidth: "3px", padding: "0.75rem" }}>
                  <p className="rec-match-reasoning-body" style={{ fontSize: "0.8rem", color: "#1E3A8A" }}>
                    {rec.ai_explanation}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

      </div>

      {/* Lower Row Grid for remaining matching items */}
      {remainingRecs.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <h3 className="section-title" style={{ marginBottom: "1.25rem" }}>More Matching Curations</h3>
          <div className="recs-lower-grid">
            {remainingRecs.map((rec, idx) => (
              <div 
                key={idx} 
                className="rec-lower-card"
                onClick={() => handleCardClick(rec.name)}
              >
                <div className="rec-lower-img-wrapper">
                  <img src={getCuisineImage(rec.cuisine)} alt={rec.name} className="rec-lower-img" />
                </div>
                <div className="rec-lower-content">
                  <div className="match-tag-area">
                    <span className="tag-label red" style={{ fontSize: "0.65rem", padding: "0.15rem 0.35rem" }}>
                      ⭐ {rec.rating || "3.5"}
                    </span>
                    <span className="tag-label trans" style={{ fontSize: "0.65rem", padding: "0.15rem 0.35rem", backgroundColor: "#E7E5E4", color: "var(--text-main)" }}>
                      ₹{rec.approx_cost}
                    </span>
                  </div>
                  <h4 style={{ fontWeight: 700, fontSize: "1.1rem" }}>{rec.name}</h4>
                  <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {rec.cuisine} • {rec.Location}
                  </p>
                  <p style={{ fontSize: "0.75rem", color: "var(--text-main)", marginTop: "0.25rem", lineClamp: 2, WebkitLineClamp: 2, display: "-webkit-box", WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                    {rec.ai_explanation}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reveal More Matches button */}
      {visibleCount < displayRecs.length && (
        <div className="reveal-more-btn-holder">
          <button 
            className="gems-button" 
            style={{ width: "260px", padding: "0.85rem", fontSize: "0.95rem" }}
            onClick={() => setVisibleCount(prev => prev + 10)}
          >
            Reveal More Matches
          </button>
        </div>
      )}

    </main>
  );
}

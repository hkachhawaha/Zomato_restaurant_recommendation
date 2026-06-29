"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useApp } from "@/context/AppContext";

export default function Home() {
  const router = useRouter();
  const { setPreferences } = useApp();

  const handleStartMatching = () => {
    router.push("/preferences");
  };

  const handleSpotlightClick = (restaurantName: string, location: string, cuisine: string, cost: number, rating: number) => {
    // Pre-populate preference context and go directly to detail page
    setPreferences(prev => ({
      ...prev,
      location: location,
      cuisine: cuisine,
      min_budget: Math.max(50, cost - 300),
      max_budget: cost + 300,
      min_rating: Math.floor(rating)
    }));
    router.push(`/restaurant/${encodeURIComponent(restaurantName)}`);
  };

  return (
    <main className="main-wrapper">
      {/* Top Picks Section */}
      <section style={{ marginBottom: "3rem" }}>
        <div className="top-picks-header">
          <div>
            <h2 className="page-title">Top Picks for You</h2>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>Curated by our AI based on Bangalore&apos;s highest rated dining experiences</p>
          </div>
          <div className="top-picks-arrows">
            <button className="arrow-btn" aria-label="Previous picks">←</button>
            <button className="arrow-btn" aria-label="Next picks">→</button>
          </div>
        </div>

        <div className="picks-grid">
          {/* Hero spotlight (Design 1 - left card) */}
          <div 
            className="hero-match-card" 
            style={{ backgroundImage: "url('https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=800&q=80')" }}
            onClick={() => handleSpotlightClick("Windmills Craftworks", "Whitefield", "Continental", 2000, 4.7)}
          >
            <span className="match-percentage-badge">⚡ 98% Match</span>
            <div className="hero-content">
              <div className="match-tag-area">
                <span className="tag-label red">Trending #1</span>
                <span className="tag-label trans">Microbrewery</span>
              </div>
              <h3 className="hero-title">Windmills Craftworks</h3>
              <p className="hero-desc">Voted Bangalore&apos;s best microbrewery and live jazz venue. Experience hand-crafted craft beers, gourmet burgers, and dynamic Continental cuisine in a library-like setting.</p>
              <button className="hero-btn" onClick={(e) => {
                e.stopPropagation();
                router.push("/restaurant/Windmills%20Craftworks");
              }}>Book a Table</button>
            </div>
          </div>

          {/* Right stack cards (Design 1 - right stack) */}
          <div className="side-stack">
            <div 
              className="stack-card" 
              style={{ backgroundImage: "url('https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=600&q=80')" }}
              onClick={() => handleSpotlightClick("Nasi And Mee", "Whitefield", "Chinese", 1000, 4.4)}
            >
              <span className="match-percentage-badge">92% Match</span>
              <div className="stack-content">
                <h4 className="stack-title">Nasi And Mee</h4>
                <p className="stack-subtitle">Southeast Asian & Dim Sum • Whitefield</p>
              </div>
            </div>

            <div 
              className="stack-card" 
              style={{ backgroundImage: "url('https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80')" }}
              onClick={() => handleSpotlightClick("Truffles", "Indiranagar", "American", 900, 4.6)}
            >
              <span className="match-percentage-badge">89% Match</span>
              <div className="stack-content">
                <h4 className="stack-title">Truffles</h4>
                <p className="stack-subtitle">Gourmet Burgers & Cafe Bites • Indiranagar</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trending Nearby Section */}
      <section style={{ marginBottom: "3rem" }}>
        <div className="section-headline-bar">
          <h3 className="section-title">Trending Nearby</h3>
          <span className="view-all-link" onClick={handleStartMatching}>Search All Matches →</span>
        </div>

        <div className="horizontal-feed">
          <div className="feed-card" onClick={() => handleSpotlightClick("Toit", "Indiranagar", "Italian", 1500, 4.7)}>
            <div className="card-img-wrapper">
              <img src="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=400&q=80" alt="Toit" className="card-img" />
              <span className="card-rating-badge">⭐ 4.7</span>
            </div>
            <div className="card-details">
              <h4 className="card-name">Toit</h4>
              <p className="card-loc">Indiranagar, Bangalore</p>
              <div className="card-tag-pills">
                <span className="pill-item">Italian</span>
                <span className="pill-item">$$</span>
              </div>
            </div>
          </div>

          <div className="feed-card" onClick={() => handleSpotlightClick("Karavalli", "Residency Road", "South Indian", 3500, 4.5)}>
            <div className="card-img-wrapper">
              <img src="https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=400&q=80" alt="Karavalli" className="card-img" />
              <span className="card-rating-badge">⭐ 4.5</span>
            </div>
            <div className="card-details">
              <h4 className="card-name">Karavalli</h4>
              <p className="card-loc">Residency Road, Bangalore</p>
              <div className="card-tag-pills">
                <span className="pill-item">South Indian</span>
                <span className="pill-item">$$$</span>
              </div>
            </div>
          </div>

          <div className="feed-card" onClick={() => handleSpotlightClick("Empire Restaurant", "Indiranagar", "North Indian", 300, 3.9)}>
            <div className="card-img-wrapper">
              <img src="https://images.unsplash.com/photo-1626132647523-66f5bf380027?auto=format&fit=crop&w=400&q=80" alt="Empire Restaurant" className="card-img" />
              <span className="card-rating-badge">⭐ 3.9</span>
            </div>
            <div className="card-details">
              <h4 className="card-name">Empire Restaurant</h4>
              <p className="card-loc">Indiranagar, Bangalore</p>
              <div className="card-tag-pills">
                <span className="pill-item">North Indian</span>
                <span className="pill-item">$</span>
              </div>
            </div>
          </div>

          <div className="feed-card" onClick={() => handleSpotlightClick("The Wok Shop", "Whitefield", "Chinese", 500, 4.2)}>
            <div className="card-img-wrapper">
              <img src="https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=400&q=80" alt="The Wok Shop" className="card-img" />
              <span className="card-rating-badge">⭐ 4.2</span>
            </div>
            <div className="card-details">
              <h4 className="card-name">The Wok Shop</h4>
              <p className="card-loc">Whitefield, Bangalore</p>
              <div className="card-tag-pills">
                <span className="pill-item">Chinese</span>
                <span className="pill-item">$</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Hidden Gems Section */}
      <section className="gems-banner">
        <div className="gems-text-content">
          <h3 className="gems-headline">Hidden Gems</h3>
          <p className="gems-desc">Discover under-the-radar spots that our AI thinks you&apos;ll love. Less crowded, highly rated, and perfectly matched to your palate.</p>
          <button className="gems-button" onClick={handleStartMatching}>Explore Gems</button>
        </div>

        <div className="gems-cards-area">
          <div 
            className="gem-mini-card"
            onClick={() => handleSpotlightClick("The Secret Cellar", "Koramangala", "Fusion", 1200, 4.5)}
          >
            <img src="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=150&q=80" alt="The Secret Cellar" className="gem-mini-img" />
            <div className="gem-mini-details">
              <h4 className="gem-mini-name">The Secret Cellar</h4>
              <p className="gem-mini-sub">Fusion • 4.5 Rating</p>
              <span className="gem-mini-match">96% AI Match</span>
            </div>
          </div>

          <div 
            className="gem-mini-card"
            onClick={() => handleSpotlightClick("Hygge Bites", "Jayanagar", "Bakery", 400, 4.3)}
          >
            <img src="https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=150&q=80" alt="Hygge Bites" className="gem-mini-img" />
            <div className="gem-mini-details">
              <h4 className="gem-mini-name">Hygge Bites</h4>
              <p className="gem-mini-sub">Bakery • 4.3 Rating</p>
              <span className="gem-mini-match">94% AI Match</span>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

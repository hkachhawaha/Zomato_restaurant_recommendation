// Zomato AI Concierge - Client Controller Logic

document.addEventListener("DOMContentLoaded", () => {
    // Cache UI DOM Elements
    const form = document.getElementById("recommendation-form");
    const submitBtn = document.getElementById("submit-button");
    const btnSpinner = submitBtn.querySelector(".btn-spinner");
    const btnText = submitBtn.querySelector(".btn-text");
    
    // Autocompletes inputs & drop boxes
    const locationInput = document.getElementById("location-input");
    const locationSuggestions = document.getElementById("location-suggestions");
    const locationArrow = document.getElementById("location-arrow");
    const cuisineSelect = document.getElementById("cuisine-select");
    
    // Budget range inputs
    const minBudgetInput = document.getElementById("min-budget-input");
    const maxBudgetInput = document.getElementById("max-budget-input");
    
    // Slider element
    const ratingInput = document.getElementById("rating-input");
    const ratingValueLabel = document.getElementById("rating-value");
    
    // Additional preferences input
    const additionalInput = document.getElementById("additional-input");
    
    // Panel States elements
    const emptyState = document.getElementById("empty-state");
    const loadingState = document.getElementById("loading-state");
    const errorState = document.getElementById("error-state");
    const errorMessage = document.getElementById("error-message");
    const retryBtn = document.getElementById("retry-button");
    
    // Results Grid elements
    const resultsGrid = document.getElementById("results-grid");
    const resultsCount = document.getElementById("results-count");

    // State cache arrays for autocompletion
    let availableLocations = [];
    let availableCuisines = [];

    // Initialize Page Settings
    initPage();

    function initPage() {
        // 1. Fetch autocomplete databases
        fetchAutocompleteData();
        
        // 2. Set range slide dynamics
        ratingInput.addEventListener("input", (e) => {
            ratingValueLabel.textContent = parseFloat(e.target.value).toFixed(1);
        });

        // 3. Register neighborhood dropdown search-select logic
        setupLocationSearchSelect();
        
        // 4. Form Submission
        form.addEventListener("submit", handleFormSubmit);
        retryBtn.addEventListener("click", () => form.dispatchEvent(new Event("submit")));
    }

    // Fetches static locations and cuisines lists from FastAPI endpoints
    async function fetchAutocompleteData() {
        try {
            const [locRes, cuisRes] = await Promise.all([
                fetch("/api/locations"),
                fetch("/api/cuisines")
            ]);
            
            if (locRes.ok) availableLocations = await locRes.json();
            
            if (cuisRes.ok) {
                availableCuisines = await cuisRes.json();
                
                // Populate cuisine select dropdown options dynamically
                cuisineSelect.innerHTML = '<option value="" disabled selected>Select Cuisine...</option>';
                availableCuisines.forEach(cuisine => {
                    const opt = document.createElement("option");
                    opt.value = cuisine;
                    opt.textContent = cuisine;
                    cuisineSelect.appendChild(opt);
                });
            }
            
            console.log(`Preloaded ${availableLocations.length} locations & ${availableCuisines.length} cuisines.`);
        } catch (err) {
            console.warn("Autocomplete data loading error: ", err);
        }
    }

    // Combined Search Bar + Dropdown autocomplete logic for neighborhood location
    function setupLocationSearchSelect() {
        const renderSuggestions = (query = "") => {
            const q = query.toLowerCase().trim();
            locationSuggestions.innerHTML = "";
            
            if (q === "") {
                // Show all available locations by default
                matches = availableLocations;
            } else {
                // Filter all locations based on search query
                matches = availableLocations.filter(item => item.toLowerCase().includes(q));
            }

            if (matches.length === 0) {
                locationSuggestions.style.display = "none";
                return;
            }

            matches.forEach(match => {
                const div = document.createElement("div");
                div.className = "autocomplete-suggestion";
                div.textContent = match;
                div.addEventListener("click", () => {
                    locationInput.value = match;
                    locationSuggestions.innerHTML = "";
                    locationSuggestions.style.display = "none";
                });
                locationSuggestions.appendChild(div);
            });
            locationSuggestions.style.display = "block";
        };

        // Open options when clicking in the box or typing
        locationInput.addEventListener("input", (e) => {
            renderSuggestions(e.target.value);
        });

        locationInput.addEventListener("focus", () => {
            renderSuggestions(locationInput.value);
        });

        // Click arrow opens/closes the dropdown
        locationArrow.addEventListener("click", (e) => {
            e.stopPropagation();
            if (locationSuggestions.style.display === "block") {
                locationSuggestions.style.display = "none";
            } else {
                renderSuggestions(locationInput.value);
                locationInput.focus();
            }
        });

        // Click outside closes the dropdown list
        document.addEventListener("click", (e) => {
            if (e.target !== locationInput && e.target !== locationArrow && !locationSuggestions.contains(e.target)) {
                locationSuggestions.style.display = "none";
            }
        });
    }

    // Submits request parameters to the recommendation API
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const location = locationInput.value.trim();
        const cuisine = cuisineSelect.value;
        const minBudget = parseInt(minBudgetInput.value) || 0;
        const maxBudget = parseInt(maxBudgetInput.value) || 99999;
        const minRating = parseFloat(ratingInput.value);
        const additional = additionalInput.value.trim();



        if (minBudget > maxBudget) {
            alert("Minimum budget cannot exceed maximum budget.");
            return;
        }

        // UI state: Show loading panel
        setUIState("loading");
        
        try {
            const payload = {
                location: location,
                min_budget: minBudget,
                max_budget: maxBudget,
                cuisine: cuisine,
                min_rating: minRating,
                additional_preferences: additional
            };

            const response = await fetch("/api/recommend", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: jsonStringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Server responded with an error.");
            }

            const data = await response.json();
            renderRecommendations(data.recommendations);

        } catch (err) {
            console.error("API error: ", err);
            errorMessage.textContent = err.message || "An unexpected error occurred.";
            setUIState("error");
        }
    }

    // Controls results panel visible widgets
    function setUIState(state) {
        // Toggle elements hidden state classes
        emptyState.classList.add("hidden");
        loadingState.classList.add("hidden");
        errorState.classList.add("hidden");
        resultsGrid.classList.add("hidden");
        resultsCount.classList.add("hidden");

        // Submit Button loaders
        if (state === "loading") {
            btnSpinner.classList.remove("hidden");
            btnText.textContent = "Matching Vibe...";
            submitBtn.disabled = true;
            loadingState.classList.remove("hidden");
        } else {
            btnSpinner.classList.add("hidden");
            btnText.textContent = "Match My Vibe";
            submitBtn.disabled = false;
        }

        if (state === "empty") {
            emptyState.classList.remove("hidden");
        } else if (state === "error") {
            errorState.classList.remove("hidden");
        } else if (state === "results") {
            resultsGrid.classList.remove("hidden");
            resultsCount.classList.remove("hidden");
        }
    }

    // Renders restaurant recommendation items inside the output grids
    function renderRecommendations(recommendations) {
        resultsGrid.innerHTML = "";
        
        if (!recommendations || recommendations.length === 0) {
            resultsCount.textContent = "No Match Found";
            setUIState("empty");
            // Change empty state descriptors
            emptyState.querySelector("h3").textContent = "No Matches Found";
            emptyState.querySelector("p").textContent = "We couldn't find any restaurants that meet your exact ratings, cuisine, or budget criteria in this area. Try lowering your constraints.";
            return;
        }

        resultsCount.textContent = `${recommendations.length} Match${recommendations.length > 1 ? 'es' : ''} Found`;

        recommendations.forEach(rec => {
            const card = document.createElement("article");
            card.className = "restaurant-card";
            
            // Format rating badges
            const rating = rec.rating !== null ? parseFloat(rec.rating).toFixed(1) : "N/A";
            const ratingClass = (rec.rating !== null && rec.rating >= 4.0) ? "rating-high" : "rating-medium";
            const rateBadge = `<span class="rating-badge ${ratingClass}">★ ${rating}</span>`;
            
            // Format cuisine tags
            const cuisineTags = rec.cuisine.split(",").slice(0, 3).map(tag => 
                `<span class="tag-badge">${tag.trim()}</span>`
            ).join(" ");

            card.innerHTML = `
                <div class="card-top">
                    <div>
                        <h3 class="restaurant-title">${rec.name}</h3>
                        <div class="card-meta">
                            <span class="location-label">📍 ${rec.Location}</span>
                            <span class="cost-label">💰 ₹${rec.approx_cost} for two</span>
                        </div>
                    </div>
                    ${rateBadge}
                </div>
                <div class="card-meta">
                    <span class="meta-label">Cuisines:</span>
                    ${cuisineTags}
                </div>
                <div class="ai-reasoning-bubble">
                    <p>${rec.ai_explanation}</p>
                </div>
            `;
            resultsGrid.appendChild(card);
        });

        setUIState("results");
    }

    // Helper to stringify JSON payloads safely
    function jsonStringify(obj) {
        try {
            return JSON.stringify(obj);
        } catch (e) {
            return "{}";
        }
    }
});

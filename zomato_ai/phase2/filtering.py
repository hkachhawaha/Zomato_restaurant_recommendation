import math
from typing import List, Dict, Any

def score_and_select_candidates(candidates: List[Dict[str, Any]], top_n: int = 8) -> List[Dict[str, Any]]:
    """
    Ranks candidate restaurants using a weighted heuristic scoring function.
    Aggregates:
    - 70% Normalized Rating: rating scaled between 1.0 and 5.0.
    - 30% Log-Scaled Votes: log-scaled vote counts to balance popularity.
    """
    if not candidates:
        return []

    # Find the maximum vote count in this specific candidate set for log scaling normalization
    max_votes = max((item.get("votes") or 0) for item in candidates)
    
    scored_candidates = []
    for item in candidates:
        # 1. Rating Normalization: scale float rate [1.0, 5.0] to [0.0, 1.0]
        rate = item.get("rate")
        if rate is None or pd_is_nan(rate):
            rate = 1.0 # Minimal baseline
        
        # Clip just in case
        rate = max(1.0, min(5.0, float(rate)))
        s_rating = (rate - 1.0) / 4.0

        # 2. Vote Normalization: log-scale votes relative to max votes in batch
        votes = item.get("votes") or 0
        votes = max(0, int(votes))
        
        if max_votes > 0:
            s_votes = math.log(votes + 1) / math.log(max_votes + 1)
        else:
            s_votes = 0.0

        # 3. Aggregated Weighted Heuristic Score
        final_score = (s_rating * 0.70) + (s_votes * 0.30)
        
        # Shallow copy to avoid mutating inputs directly
        item_copy = item.copy()
        item_copy["_heuristic_score"] = final_score
        scored_candidates.append(item_copy)

    # Sort descending by heuristic score. In case of ties, use rate as secondary sort
    scored_candidates.sort(key=lambda x: (x["_heuristic_score"], x.get("rate") or 0), reverse=True)
    
    return scored_candidates[:top_n]

def pd_is_nan(val) -> bool:
    """Helper to detect pandas NaN or float NaN values without importing pandas."""
    # float('nan') != float('nan') is True in Python
    return val != val

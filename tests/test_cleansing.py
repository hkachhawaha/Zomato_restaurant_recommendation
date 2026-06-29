import numpy as np
from zomato_ai.phase1.ingestion import clean_rate, clean_cost

def test_clean_rate_parsing():
    assert clean_rate("4.1/5") == 4.1
    assert clean_rate("4.5") == 4.5
    assert clean_rate("NEW") is None
    assert clean_rate("-") is None
    assert clean_rate(np.nan) is None
    assert clean_rate(None) is None

def test_clean_cost_parsing():
    assert clean_cost("1,200") == 1200.0
    assert clean_cost("450") == 450.0
    assert clean_cost("   850   ") == 850.0
    assert clean_cost(np.nan) is None
    assert clean_cost(None) is None

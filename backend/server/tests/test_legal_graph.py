import pytest
from server.legal_graph import traverse_legal_graph, keyword_search

def test_traverse_legal_graph_exact():
    node = traverse_legal_graph("caste_discrimination")
    assert node["matched"] is True
    assert "Atrocities" in node["act"]
    assert "Section 3" in node["sections"][0]
    assert node["helpline"] == "14566"

def test_traverse_legal_graph_alias():
    node = traverse_legal_graph("domestic violence")
    assert node["matched"] is True
    assert "Domestic Violence" in node["act"]
    assert node["helpline"] == "181"

def test_traverse_legal_graph_fallback():
    node = traverse_legal_graph("some unknown random incident type")
    assert node["matched"] is False
    assert node["label"] == "General Grievance"
    assert node["authority"] == "District Collector"

def test_keyword_search():
    node = keyword_search("they refused to give my old age pension")
    assert node is not None
    assert node["node_key"] == "pension_denial"

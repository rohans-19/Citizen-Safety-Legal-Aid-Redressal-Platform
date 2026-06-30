"""
graph_builder.py
Member C — CIVIC-SHIELD Analytics
Reads live incident data from Supabase and constructs a PyTorch Geometric
Data object (district graph) ready for the T-GAT model.
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import torch
from dotenv import load_dotenv
from supabase import create_client
from torch_geometric.data import Data

# ── Bootstrap ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "..", ".env"))

raw_url = os.getenv("SUPABASE_URL", "")
SUPABASE_URL = raw_url.strip('"').strip("'").replace("/rest/v1/", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip('"').strip("'")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

GRAPH_PATH = os.path.join(BASE_DIR, "..", "data", "karnataka_district_graph.json")

# Temporal resolution: number of daily bins for node features
NUM_BINS = 7  # last 7 days


def load_district_graph() -> tuple[list[str], list[list[int]]]:
    """Load district adjacency graph from JSON.

    Returns:
        district_names: ordered list of district name strings
        edges:          list of [src, dst] integer pairs
    """
    with open(GRAPH_PATH, "r") as f:
        graph = json.load(f)
    names = [n["name"] for n in sorted(graph["nodes"], key=lambda x: x["id"])]
    edges = graph["edges"]
    return names, edges


def fetch_incidents(days: int = NUM_BINS) -> list[dict]:
    """Fetch recent incidents from Supabase.

    Args:
        days: How many days back to look (matches NUM_BINS).

    Returns:
        List of incident row dicts.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    response = (
        supabase.table("civic_incidents")
        .select("district, created_at, severity")
        .gte("created_at", cutoff)
        .execute()
    )
    return response.data or []


def build_temporal_features(
    incidents: list[dict],
    district_names: list[str],
    num_bins: int = NUM_BINS,
) -> torch.Tensor:
    """Build temporal node feature matrix of shape [num_nodes, num_bins].

    Each cell [i, t] is the count of incidents in district i on day t
    (0 = most recent day, num_bins-1 = oldest day).

    Args:
        incidents:      Raw Supabase rows.
        district_names: Ordered list of district names (node ordering).
        num_bins:       Number of temporal bins (days).

    Returns:
        Tensor of shape [31, num_bins] with float32 incident counts.
    """
    now = datetime.now(timezone.utc)
    name_to_idx = {name: i for i, name in enumerate(district_names)}
    # counts[node_idx][bin_idx]
    counts = defaultdict(lambda: defaultdict(float))

    for row in incidents:
        district = row.get("district", "")
        if district not in name_to_idx:
            continue
        idx = name_to_idx[district]
        try:
            ts = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        except Exception:
            continue
        days_ago = (now - ts).days
        bin_idx = min(days_ago, num_bins - 1)
        counts[idx][bin_idx] += 1.0

    num_nodes = len(district_names)
    features = torch.zeros((num_nodes, num_bins), dtype=torch.float32)
    for node_idx, bin_dict in counts.items():
        for bin_idx, count in bin_dict.items():
            features[node_idx][bin_idx] = count

    return features


def build_edge_index(edges: list[list[int]]) -> torch.Tensor:
    """Convert edge list to PyG edge_index tensor of shape [2, num_edges].

    Edges are made bidirectional.
    """
    src, dst = [], []
    seen = set()
    for edge in edges:
        a, b = int(edge[0]), int(edge[1])
        if (a, b) not in seen:
            src.append(a)
            dst.append(b)
            seen.add((a, b))
        if (b, a) not in seen:
            src.append(b)
            dst.append(a)
            seen.add((b, a))
    return torch.tensor([src, dst], dtype=torch.long)


def build_graph() -> tuple[Data, list[str], dict[str, int]]:
    """Build the live PyTorch Geometric graph from Supabase.

    Returns:
        data:          PyG Data object with .x (features) and .edge_index
        district_names: Ordered list of district name strings
        raw_counts:    {district_name: total_count_in_window}
    """
    district_names, edges = load_district_graph()
    incidents = fetch_incidents()

    x = build_temporal_features(incidents, district_names)
    edge_index = build_edge_index(edges)

    # Raw counts per district (used by the DP engine)
    raw_counts = {name: int(x[i].sum().item()) for i, name in enumerate(district_names)}

    data = Data(x=x, edge_index=edge_index)
    return data, district_names, raw_counts


# ── Self-test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Building graph from Supabase...")
    data, names, raw = build_graph()
    print(f"  Nodes: {data.x.shape[0]} | Feature dims: {data.x.shape[1]}")
    print(f"  Edges: {data.edge_index.shape[1]}")
    top = sorted(raw.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\nTop 5 districts by raw count (last {NUM_BINS} days):")
    for d, c in top:
        print(f"  {d:<22} {c} incidents")
    print("\n✅ Graph built successfully.")

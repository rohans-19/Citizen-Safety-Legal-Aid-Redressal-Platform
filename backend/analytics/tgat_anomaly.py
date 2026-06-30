"""
tgat_anomaly.py
Member C — CIVIC-SHIELD Analytics
Temporal Graph Attention Network (T-GAT) anomaly detector.
Architecture: GATConv (spatial attention) → GRU (temporal memory) → MLP → anomaly score
Trained on synthetic incident data. Saves weights to tgat_weights.pt.
"""

import json
import os
import random
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GATConv

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_PATH = os.path.join(BASE_DIR, "..", "data", "karnataka_district_graph.json")
WEIGHTS_PATH = os.path.join(BASE_DIR, "tgat_weights.pt")

NUM_BINS = 7       # temporal feature bins (days)
NUM_NODES = 31     # Karnataka districts
GAT_HIDDEN = 32
GAT_HEADS = 4
GRU_HIDDEN = 64


# ── Model Architecture ─────────────────────────────────────────────────────────

class TGATAnomalyDetector(nn.Module):
    """Temporal Graph Attention Network for district anomaly scoring.

    Pipeline per forward pass:
        1. GATConv layer captures spatial neighbourhood correlations.
        2. GRU layer captures temporal patterns in the 7-day feature window.
        3. MLP head maps the concatenated representation to an anomaly probability.
    """

    def __init__(
        self,
        in_channels: int = NUM_BINS,
        gat_hidden: int = GAT_HIDDEN,
        gat_heads: int = GAT_HEADS,
        gru_hidden: int = GRU_HIDDEN,
    ):
        super().__init__()
        # Spatial: GAT over the district adjacency graph
        self.gat1 = GATConv(in_channels, gat_hidden, heads=gat_heads, concat=True, dropout=0.2)
        self.gat2 = GATConv(gat_hidden * gat_heads, gat_hidden, heads=1, concat=False, dropout=0.2)

        # Temporal: GRU applied to the raw per-node feature sequence
        self.gru = nn.GRU(input_size=1, hidden_size=gru_hidden, num_layers=2, batch_first=True)

        # Fusion MLP: combine spatial (GAT) + temporal (GRU) representations
        fusion_dim = gat_hidden + gru_hidden
        self.mlp = nn.Sequential(
            nn.Linear(fusion_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),   # output: anomaly probability ∈ (0, 1)
        )

    def forward(self, data: Data) -> torch.Tensor:
        """
        Args:
            data: PyG Data with:
                  - x: [num_nodes, NUM_BINS] float32 feature matrix
                  - edge_index: [2, num_edges] long tensor

        Returns:
            anomaly_scores: [num_nodes, 1] float tensor, values ∈ (0, 1)
        """
        x, edge_index = data.x, data.edge_index

        # Spatial stream: GAT layers
        h_spatial = F.elu(self.gat1(x, edge_index))
        h_spatial = F.dropout(h_spatial, p=0.2, training=self.training)
        h_spatial = self.gat2(h_spatial, edge_index)  # [N, gat_hidden]

        # Temporal stream: GRU over the 7-day feature sequence per node
        # Reshape x: [N, NUM_BINS] → [N, NUM_BINS, 1] for GRU input
        x_seq = x.unsqueeze(-1)  # [N, 7, 1]
        _, h_n = self.gru(x_seq)  # h_n: [num_layers, N, gru_hidden]
        h_temporal = h_n[-1]      # take last layer hidden state: [N, gru_hidden]

        # Fuse and score
        h_fused = torch.cat([h_spatial, h_temporal], dim=-1)  # [N, fusion_dim]
        scores = self.mlp(h_fused)  # [N, 1]
        return scores


# ── Synthetic Training Data Generator ─────────────────────────────────────────

def load_graph_topology() -> tuple[list[str], list[list[int]]]:
    with open(GRAPH_PATH) as f:
        g = json.load(f)
    names = [n["name"] for n in sorted(g["nodes"], key=lambda x: x["id"])]
    return names, g["edges"]


def make_edge_index(edges: list[list[int]]) -> torch.Tensor:
    src, dst = [], []
    seen = set()
    for a, b in edges:
        if (a, b) not in seen:
            src += [a, b]; dst += [b, a]
            seen.add((a, b)); seen.add((b, a))
    return torch.tensor([src, dst], dtype=torch.long)


# District-level baseline weights for synthetic training
DISTRICT_WEIGHTS = {
    "Bagalkote": 0.4, "Ballari": 0.6, "Belagavi": 0.5,
    "Bengaluru Rural": 0.3, "Bengaluru Urban": 0.7, "Bidar": 0.85,
    "Chamarajanagar": 0.6, "Chikkaballapura": 0.3, "Chikkamagaluru": 0.3,
    "Chitradurga": 0.4, "Dakshina Kannada": 0.4, "Davanagere": 0.5,
    "Dharwad": 0.5, "Gadag": 0.3, "Hassan": 0.3, "Haveri": 0.4,
    "Kalaburagi": 0.75, "Kodagu": 0.2, "Kolar": 0.4, "Koppal": 0.5,
    "Mandya": 0.4, "Mysuru": 0.5, "Raichur": 0.75, "Ramanagara": 0.3,
    "Shivamogga": 0.4, "Tumakuru": 0.4, "Udupi": 0.2, "Uttara Kannada": 0.3,
    "Vijayapura": 0.5, "Yadgir": 0.65, "Vijayanagara": 0.5,
}

ANOMALY_DISTRICTS = {"Bidar", "Raichur", "Kalaburagi", "Ballari", "Yadgir"}


def generate_training_sample(
    district_names: list[str], edge_index: torch.Tensor, inject_spike: bool = False
) -> tuple[Data, torch.Tensor]:
    """Generate one synthetic training sample.

    Args:
        district_names: Ordered list of district names.
        edge_index:     PyG edge_index tensor.
        inject_spike:   If True, amplify anomaly districts by 3–5× for positive labelling.

    Returns:
        (data, labels): PyG Data + label tensor [N, 1]
    """
    features = torch.zeros((NUM_NODES, NUM_BINS), dtype=torch.float32)
    labels = torch.zeros((NUM_NODES, 1), dtype=torch.float32)

    for i, name in enumerate(district_names):
        base_w = DISTRICT_WEIGHTS.get(name, 0.3)
        for t in range(NUM_BINS):
            # Add temporal decay (more recent = higher variance)
            decay = (NUM_BINS - t) / NUM_BINS
            count = max(0, random.gauss(base_w * 10 * decay, 2))
            features[i, t] = count

        # Spike injection for positive training examples
        if inject_spike and name in ANOMALY_DISTRICTS:
            spike_day = random.randint(0, 2)
            features[i, spike_day] += random.uniform(15, 30)
            labels[i] = 1.0
        else:
            # Label based on whether 7-day total exceeds threshold
            total = features[i].sum().item()
            labels[i] = 1.0 if (name in ANOMALY_DISTRICTS and total > 40) else 0.0

    # Normalize features to [0, 1] per-node
    max_vals = features.max(dim=1, keepdim=True).values.clamp(min=1)
    features = features / max_vals

    data = Data(x=features, edge_index=edge_index)
    return data, labels


# ── Training Loop ──────────────────────────────────────────────────────────────

def train():
    print("Loading district topology...")
    district_names, edges = load_graph_topology()
    edge_index = make_edge_index(edges)

    model = TGATAnomalyDetector()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    criterion = nn.BCELoss()

    EPOCHS = 150
    SAMPLES_PER_EPOCH = 20

    print(f"Training T-GAT for {EPOCHS} epochs × {SAMPLES_PER_EPOCH} samples...")
    model.train()

    for epoch in range(1, EPOCHS + 1):
        total_loss = 0.0
        for _ in range(SAMPLES_PER_EPOCH):
            inject = random.random() > 0.4  # 60% chance of spike sample
            data, labels = generate_training_sample(district_names, edge_index, inject)
            optimizer.zero_grad()
            preds = model(data)
            loss = criterion(preds, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / SAMPLES_PER_EPOCH
        if epoch % 25 == 0 or epoch == 1:
            print(f"  Epoch {epoch:>3}/{EPOCHS} — Loss: {avg_loss:.4f}")

    torch.save(model.state_dict(), WEIGHTS_PATH)
    print(f"\nTraining complete. Weights saved to: {WEIGHTS_PATH}")

    # Validation pass
    print("\nValidation on a spike sample:")
    model.eval()
    with torch.no_grad():
        data, labels = generate_training_sample(district_names, edge_index, inject_spike=True)
        scores = model(data).squeeze()
        print(f"{'District':<22} {'Score':>8} {'Label':>7} {'Pass?':>7}")
        print("-" * 50)
        for i, name in enumerate(district_names):
            score = scores[i].item()
            label = labels[i].item()
            check = "[OK]" if (label == 1.0 and score > 0.6) or (label == 0.0 and score < 0.5) else "[!!]"
            if label == 1.0 or score > 0.4:
                print(f"{name:<22} {score:>8.3f} {label:>7.0f} {check:>7}")


def load_model() -> tuple[TGATAnomalyDetector, list[str]]:
    """Load trained model and district names for inference.

    Returns:
        model:          Trained TGATAnomalyDetector in eval mode.
        district_names: Ordered district names corresponding to node indices.
    """
    district_names, _ = load_graph_topology()
    model = TGATAnomalyDetector()
    if os.path.exists(WEIGHTS_PATH):
        model.load_state_dict(torch.load(WEIGHTS_PATH, map_location="cpu"))
    else:
        raise FileNotFoundError(
            f"Weights not found at {WEIGHTS_PATH}. Run tgat_anomaly.py to train first."
        )
    model.eval()
    return model, district_names


if __name__ == "__main__":
    train()

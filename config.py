"""
Konfiguracja projektu.

Najczęstszy run:
    python 00_prepare_data.py
    python 01_build_embeddings.py
    python 02_build_features.py
    python 03_cluster.py
    python 04_describe_clusters.py
    python 05_visualize_umap.py
"""

from pathlib import Path

BASE_URL = "https://api-global-points.easypack24.net/v1/points"

# Dane wejściowe
POINTS_CACHE = Path("all_points_cache.json")
EMBEDDINGS_PATH = Path("all_points_cache_embeddings.npy")

# Dane pośrednie
OPERATING_POINTS_PATH = Path("operating_points.json")
TEXTS_PATH = Path("texts.txt")
FEATURES_PATH = Path("features.npy")
LABELS_PATH = Path("cluster_labels.npy")

# Dane wyjściowe
CLUSTERS_CSV = Path("clusters.csv")
CLUSTER_SUMMARY = Path("cluster_summary.txt")
UMAP_PLOT = Path("umap_clusters.png")

# Parametry
N_POINTS = 2000
K = 16

# PCA
PCA_COMPONENTS = 50

# Pobieranie API
PER_PAGE = 500
COUNTRY = "PL"
REQUEST_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.1

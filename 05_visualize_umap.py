"""
Krok 5:
- Wczytuje features.npy i cluster_labels.npy.
- Robi UMAP 2D tylko do wizualizacji.
- Zapisuje umap_clusters.png.

Uruchom:
    python 05_visualize_umap.py

Wymagane:
    pip install umap-learn matplotlib
"""

import numpy as np
import pandas as pd

import config

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


def main():
    try:
        import umap
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Brakuje umap-learn albo matplotlib.")
        print("Zainstaluj:")
        print("  pip install umap-learn matplotlib")
        return

    features = np.load(config.FEATURES_PATH)
    labels = np.load(config.LABELS_PATH)

    if len(features) != len(labels):
        raise ValueError("Liczba features != liczba labels")

    cluster_names = None

    if config.CLUSTERS_CSV.exists():
        df = pd.read_csv(config.CLUSTERS_CSV)
        cluster_names = (
            df[["cluster_id", "cluster_name"]]
            .drop_duplicates()
            .set_index("cluster_id")["cluster_name"]
            .to_dict()
        )

    print("UMAP 2D — tylko wizualizacja...")
    reducer = umap.UMAP(
        n_components=2,
        random_state=42,
        n_neighbors=50,
        min_dist=0.3,
    )

    xy = reducer.fit_transform(features)

    unique_labels = sorted(np.unique(labels))

    fig, ax = plt.subplots(figsize=(14, 9))
    colors = plt.cm.tab20(np.linspace(0, 1, len(unique_labels)))

    for cid, color in zip(unique_labels, colors):
        mask = labels == cid

        if cluster_names and cid in cluster_names:
            name = cluster_names[cid]
        else:
            name = f"cluster {cid}"

        ax.scatter(
            xy[mask, 0],
            xy[mask, 1],
            c=[color],
            s=6,
            alpha=0.55,
            label=f"{cid}: {name} ({mask.sum()})",
        )

    ax.set_title("Klastry paczkomatów InPost — UMAP 2D")
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.01, 1),
        fontsize=8,
        markerscale=3,
        framealpha=0.9,
    )

    plt.tight_layout()
    plt.savefig(config.UMAP_PLOT, dpi=150, bbox_inches="tight")
    print(f"Zapisano wykres: {config.UMAP_PLOT}")


if __name__ == "__main__":
    main()

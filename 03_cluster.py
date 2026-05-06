"""
Krok 3:
- Wczytuje features.npy.
- Wykonuje KMeans.
- Zapisuje cluster_labels.npy.

Uruchom:
    python 03_cluster.py
"""

import numpy as np
from sklearn.cluster import KMeans

import config


def main():
    print(f"Wczytuję features: {config.FEATURES_PATH}")
    features = np.load(config.FEATURES_PATH)

    print(f"Features shape: {features.shape}")

    if len(features) < config.K:
        raise ValueError(f"Za mało punktów ({len(features)}) dla k={config.K}")

    print(f"\nKMeans k={config.K}...")
    km = KMeans(
        n_clusters=config.K,
        init="k-means++",
        random_state=42,
        n_init=15,
        max_iter=500,
    )

    labels = km.fit_predict(features)

    print(f"Inertia: {km.inertia_:.2f}")

    unique, counts = np.unique(labels, return_counts=True)
    print("\nLiczność klastrów:")
    for cid, count in zip(unique, counts):
        print(f"  cluster {cid:2d}: {count:5d}")

    np.save(config.LABELS_PATH, labels)
    print(f"\nZapisano etykiety: {config.LABELS_PATH}")


if __name__ == "__main__":
    main()

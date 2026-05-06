"""
Opcjonalny krok:
- Wczytuje features.npy.
- Liczy inertia dla różnych k.
- Zapisuje elbow.png.

Uruchom:
    python 06_elbow.py
"""

import numpy as np
from sklearn.cluster import KMeans

import config


def main():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Brakuje matplotlib. Zainstaluj:")
        print("  pip install matplotlib")
        return

    features = np.load(config.FEATURES_PATH)

    k_values = list(range(5, 31, 2))
    inertias = []

    print(f"Elbow curve dla k={k_values}")

    for k in k_values:
        if k >= len(features):
            break

        km = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=5,
            max_iter=200,
        )
        km.fit(features)
        inertias.append(km.inertia_)
        print(f"  k={k:2d}  inertia={km.inertia_:.2f}")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(k_values[:len(inertias)], inertias, "o-", linewidth=2, markersize=6)
    ax.set_xlabel("k")
    ax.set_ylabel("Inertia")
    ax.set_title("Elbow curve — wybór liczby klastrów")
    ax.grid(alpha=0.3)

    out = "elbow.png"
    plt.tight_layout()
    plt.savefig(out, dpi=130)
    print(f"Zapisano: {out}")


if __name__ == "__main__":
    main()

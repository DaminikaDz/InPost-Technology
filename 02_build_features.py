"""
Krok 2:
- Wczytuje operating_points.json i embeddingi.
- Redukuje wymiarowość embeddingów przez PCA.
- Zapisuje features.npy.

Zakładamy, że embeddingi są poprawne i odpowiadają kolejnością punktom po filtrze Operating.

Uruchom:
    python 02_build_features.py
"""

import json

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

import config

def main():
    with open(config.OPERATING_POINTS_PATH, encoding="utf-8") as f:
        points = json.load(f)

    df = pd.DataFrame(points)
    print(f"Liczba punktów: {len(df)}")

    emb = np.load(config.EMBEDDINGS_PATH)
    print(f"Embedding shape: {emb.shape}")

    if emb.shape[0] != len(df):
        raise ValueError(f"Liczba embeddingów ({emb.shape[0]}) != liczba punktów ({len(df)})")

    if np.isnan(emb).any() or np.isinf(emb).any():
        raise ValueError("Embeddingi zawierają NaN albo inf.")

    n_components = min(config.PCA_COMPONENTS, emb.shape[0] - 1, emb.shape[1])
    print(f"\nPCA: {emb.shape[1]}d → {n_components}d")
    pca = PCA(n_components=n_components, random_state=42)
    features = pca.fit_transform(emb).astype(np.float32)
    print(f"Wyjaśniona wariancja PCA: {pca.explained_variance_ratio_.sum():.2%}")

    if np.isnan(features).any() or np.isinf(features).any():
        raise ValueError("Features zawierają NaN albo inf.")

    np.save(config.FEATURES_PATH, features)
    print(f"\nFeatures shape: {features.shape}")
    print(f"Zapisano: {config.FEATURES_PATH}")


if __name__ == "__main__":
    main()

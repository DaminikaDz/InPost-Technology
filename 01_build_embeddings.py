"""
Krok 1:
- Wczytuje operating_points.json .
- Buduje teksty przez build_text_from_point z utils.py.
- Generuje embeddingi przez sentence-transformers.
- Zapisuje embeddingi do pliku .npy wskazanego w config.EMBEDDINGS_PATH.

Wymagane:
    pip install sentence-transformers
"""

import json
from pathlib import Path

import numpy as np

import config
from utils import build_text_from_point

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def main():
    if not config.OPERATING_POINTS_PATH.exists():
        raise FileNotFoundError(
            f"Nie znaleziono {config.OPERATING_POINTS_PATH}. "
            "Najpierw uruchom: python 00_prepare_data.py"
        )

    print(f"Wczytuję punkty: {config.OPERATING_POINTS_PATH}")
    with open(config.OPERATING_POINTS_PATH, encoding="utf-8") as f:
        points = json.load(f)

    print(f"Liczba punktów: {len(points)}")

    if config.EMBEDDINGS_PATH.exists():
        existing = np.load(config.EMBEDDINGS_PATH)
        if existing.shape[0] == len(points):
            print(
                f"\nPlik {config.EMBEDDINGS_PATH} już istnieje "
                f"i ma {existing.shape[0]} wierszy — pasuje do danych."
            )
            answer = input("Nadpisać? [t/N]: ").strip().lower()
            if answer != "t":
                print("Przerwano. Stare embeddingi pozostają.")
                return
        else:
            print(
                f"\n⚠️  Plik {config.EMBEDDINGS_PATH} istnieje, "
                f"ale ma {existing.shape[0]} wierszy zamiast {len(points)}. "
                "Nadpisuję automatycznie."
            )

    print("\nBuduję teksty...")
    texts = [build_text_from_point(p) for p in points]

    print("Pierwsze 5 tekstów (kontrola):")
    for t in texts[:5]:
        print(f"  · {t}")

    print(f"\nGeneruję embeddingi modelem: {MODEL_NAME}")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL_NAME)
        emb = model.encode(
            texts,
            show_progress_bar=True,
            batch_size=64,
            normalize_embeddings=True,
        )
        print(f"Embedding shape: {emb.shape}")
    except ImportError:
        raise ImportError(
            "Brakuje sentence-transformers. Zainstaluj:\n"
            "  pip install sentence-transformers"
        )

    if np.isnan(emb).any() or np.isinf(emb).any():
        raise ValueError("Embeddingi zawierają NaN albo inf — coś poszło nie tak.")

    np.save(config.EMBEDDINGS_PATH, emb)
    print(f"\nZapisano embeddingi: {config.EMBEDDINGS_PATH}")
    print(f"Shape: {emb.shape}  dtype: {emb.dtype}")
    print("\nMożesz teraz uruchomić: python 02_build_features.py")


if __name__ == "__main__":
    main()

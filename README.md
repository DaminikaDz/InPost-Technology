# Klasteryzacja paczkomatów InPost — wersja modularna

Ta wersja jest rozbita na oddzielne pliki, żeby można było po kolei sprawdzać, co się dzieje.

## Założenie

Masz już zapisane embeddingi, np.:

```text
points_cache_2000_embeddings.npy
```

i one odpowiadają kolejnością punktom po filtrze:

```python
points = [p for p in points if p.get("status") == "Operating"]
```

Jeśli embeddingi były liczone dla wszystkich punktów przed filtrem `Operating`, to trzeba je przeliczyć albo filtrować embeddingi dokładnie tak samo jak punkty.

## Kolejność uruchamiania

```bash
python 01_prepare_data.py
python 02_build_features.py
python 03_cluster.py
python 04_describe_clusters.py
python 05_visualize_umap.py
```

Opcjonalnie elbow curve:

```bash
python 06_elbow.py
```

## Pliki

- `config.py` — wszystkie ścieżki i parametry.
- `utils.py` — funkcje pomocnicze.
- `01_prepare_data.py` — pobranie/wczytanie punktów i filtr `Operating`.
- `02_build_features.py` — wczytanie gotowych embeddingów, PCA, cechy numeryczne, `features.npy`.
- `03_cluster.py` — KMeans i zapis `cluster_labels.npy`.
- `04_describe_clusters.py` — nazwy klastrów, `clusters.csv`, `cluster_summary.txt`.
- `05_visualize_umap.py` — wykres UMAP.
- `06_elbow.py` — pomocniczy wykres elbow.

## Najważniejsze parametry

W `config.py`:

```python
K = 20
PCA_COMPONENTS = 50
TEXT_WEIGHT = 4.0
NUM_WEIGHT = 0.5
```

Jeżeli w `02_build_features.py` zobaczysz, że:

```text
Średnia norma text_part dużo większa niż num_part
```

to klastry będą głównie tekstowe.

Jeżeli:

```text
Średnia norma num_part podobna albo większa
```

to cechy binarne będą mocno wpływać na klastry.

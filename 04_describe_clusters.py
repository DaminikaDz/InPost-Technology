"""
Krok 4:
- Wczytuje operating_points.json i cluster_labels.npy.
- Nadaje nazwy klastrów ręcznie (słownik CLUSTER_NAMES).
- Zapisuje clusters.csv i cluster_summary.txt.

Uruchom:
    python 04_describe_clusters.py
"""

import json
from collections import Counter

import numpy as np
import pandas as pd

import config
from utils import ensure_columns, as_list, has_machine_payment


CLUSTER_NAMES = {
    0:  "Dino",
    1:  "Lokalizacje różne",        # mix: delikatesy/moya/blok — śmietnik
    2:  "Sklep osiedlowy",  # nienazwane, lokalne
    3:  "Superpop (wewnątrz sklepu)", # 100% indoor, 84% superpop
    4:  "Parking przy sklepie",     # parking przed/przy sklepie
    5:  "Hipermarket",       # kaufland/biedronka/aldi/żabka
    6:  "Myjnia samochodowa",       # 101× myjnia
    7:  "Parking ogólny",           # na parkingu/przy parkingu
    8:  "Posesja prywatna",         # 174× posesja prywatna
    9:  "Stacja paliw",             # BP/Shell/Mol/Circle K
    10: "Przy budynku mieszkalnym / bloku",    # budynki mieszkalne, lokale, urzędy
    11: "InPost Next",              # 99% maszyn Next
    12: "OSP",                      # 160× przy OSP
    13: "Lidl",                     # 172× Lidl
    14: "Zintegrowany ze sklepem",   # 33% indoor, Duży Ben, przy wejściu
    15: "Sklep convenience", # Lewiatan/Żabka/Groszek/Społem
}



def cluster_stats(cdf: pd.DataFrame) -> dict:
    cdf = ensure_columns(cdf)

    ptype_dist = Counter(cdf["physical_type"].dropna()).most_common()
    indoor_pct = (cdf["location_type"] == "Indoor").mean()
    is247_pct  = cdf["location_247"].fillna(True).astype(float).mean()
    isnxt_pct  = cdf["is_next"].fillna(False).astype(float).mean()
    twin_pct   = cdf["apm_doubled"].notna().mean()

    top_descs = Counter(
        cdf["location_description"].dropna().str.lower()
    ).most_common(20)

    def type_pct(target_type):
        return cdf["type"].apply(lambda x: target_type in as_list(x)).mean()

    return {
        "n":                len(cdf),
        "ptype_dist":       ptype_dist,
        "indoor_pct":       indoor_pct,
        "is247_pct":        is247_pct,
        "isnxt_pct":        isnxt_pct,
        "twin_pct":         twin_pct,
        "top_descs":        top_descs,
        "superpop_pct":     type_pct("parcel_locker_superpop"),
        "pudo_mini_pct":    type_pct("pudo_mini"),
        "refrigerated_pct": type_pct("refrigerated_locker_machine"),
        "payment_pct":      cdf["payment_type"].apply(has_machine_payment).mean(),
    }


def describe_cluster(cdf: pd.DataFrame, top_n: int = 8) -> str:
    cdf = ensure_columns(cdf)
    lines = [f"  n={len(cdf)}"]
    
    superpop_n = cdf["type"].apply(lambda x: "parcel_locker_superpop" in as_list(x)).sum()
    if superpop_n > 0:
        lines.append(f"  Superpop: {superpop_n} ({superpop_n/len(cdf):.1%})")

    top_descs = Counter(
        cdf["location_description"].dropna().str.lower()
    ).most_common(top_n)
    if top_descs:
        lines.append("  Najczęstsze opisy:")
        for value, count in top_descs:
            lines.append(f"    {count:4d}×  {value}")

    ptype_dist = Counter(cdf["physical_type"].dropna()).most_common()
    lines.append("  Typy: " + "  ".join(f"{v}({c})" for v, c in ptype_dist))

    indoor   = (cdf["location_type"] == "Indoor").mean()
    is247    = cdf["location_247"].fillna(True).astype(float).mean()
    isnxt    = cdf["is_next"].fillna(False).astype(float).mean()
    twin_n   = int(cdf["apm_doubled"].notna().sum())
    twin_pct = cdf["apm_doubled"].notna().mean()

    lines.append(f"  Indoor={indoor:.0%}  24/7={is247:.0%}  Next={isnxt:.0%}")
    lines.append(f"  Bliźniaki: {twin_n} ({twin_pct:.1%}) ")

    provinces = cdf["address_details"].apply(
        lambda x: x.get("province", "") if isinstance(x, dict) else ""
    )
    top_provinces = Counter(provinces[provinces != ""]).most_common(3)
    lines.append("  Województwa: " + "  ".join(f"{v}({c})" for v, c in top_provinces))

    return "\n".join(lines)


def main():
    print("Wczytuję punkty i etykiety...")
    with open(config.OPERATING_POINTS_PATH, encoding="utf-8") as f:
        points = json.load(f)

    labels = np.load(config.LABELS_PATH)

    df = pd.DataFrame(points)
    df = ensure_columns(df)

    if len(df) != len(labels):
        raise ValueError(f"Liczba punktów ({len(df)}) != liczba etykiet ({len(labels)})")

    df["cluster_id"] = labels
    unique_ids = sorted(df["cluster_id"].unique())

    # Czy wszystkie klastry mają nazwy
    missing = [cid for cid in unique_ids if cid not in CLUSTER_NAMES]
    if missing:
        print(f"\n⚠️  Brak nazw dla klastrów: {missing}")
        print("Uzupełnij słownik CLUSTER_NAMES w tym pliku.\n")

    # Przypisz nazwy 
    cluster_names = {
        cid: CLUSTER_NAMES.get(cid, f"klaster {cid} — bez nazwy")
        for cid in unique_ids
    }

    print("\nKlastry:")
    for cid in unique_ids:
        cdf    = df[df["cluster_id"] == cid]
        twin_n = cdf["apm_doubled"].notna().sum()
        next_n = cdf["is_next"].fillna(False).astype(float).sum()
        indoor_n = (cdf["location_type"] == "Indoor").sum()
        print(
            f"  {cid:2d}  n={len(cdf):5d}  "
            f"bliźniak={twin_n:3d}  next={next_n:3.0f}  indoor={indoor_n:3d}"
            f"  → {cluster_names[cid]}"
        )

    df["cluster_name"] = df["cluster_id"].map(cluster_names)

    df["latitude"]  = df["location"].apply(
        lambda x: x.get("latitude")  if isinstance(x, dict) else None
    )
    df["longitude"] = df["location"].apply(
        lambda x: x.get("longitude") if isinstance(x, dict) else None
    )
    df["city"]     = df["address_details"].apply(
        lambda x: x.get("city", "")     if isinstance(x, dict) else ""
    )
    df["province"] = df["address_details"].apply(
        lambda x: x.get("province", "") if isinstance(x, dict) else ""
    )

    output_cols = [
        "name", "cluster_id", "cluster_name",
        "location_description", "location_description_2",
        "physical_type", "location_type", "location_247",
        "is_next", "apm_doubled", "opening_hours", "status",
        "latitude", "longitude", "city", "province",
    ]
    existing_cols = [c for c in output_cols if c in df.columns]
    df[existing_cols].to_csv(config.CLUSTERS_CSV, index=False, encoding="utf-8-sig")
    print(f"\nCSV: {config.CLUSTERS_CSV}")

    with open(config.CLUSTER_SUMMARY, "w", encoding="utf-8") as f:
        f.write(f"KLASTRY PACZKOMATÓW INPOST  (n={len(df)})\n")
        f.write("=" * 60 + "\n")
        for cid in unique_ids:
            cdf = df[df["cluster_id"] == cid]
            f.write(f"\n{'─' * 50}\n")
            f.write(f"KLASTER {cid:2d}: {cluster_names[cid]}\n")
            f.write(describe_cluster(cdf) + "\n")

    print(f"Podsumowanie: {config.CLUSTER_SUMMARY}")


if __name__ == "__main__":
    main()

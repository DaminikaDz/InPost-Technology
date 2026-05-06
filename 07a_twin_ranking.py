"""
Wykres 07a: Ranking klastrów po % bliźniaków (słupkowy poziomy).

Uruchom:
    python 07a_twin_ranking.py

Wymagane:
    pip install matplotlib
"""

import json
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import config
from utils import ensure_columns

# Ręczne nazwy — muszą być zgodne z 04_describe_clusters.py
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

THRESHOLD_HIGH = 0.185   # >= 20% — zdecydowanie warto dublować
THRESHOLD_MED  = 0.10   # >= 10% — warto rozważyć


def main():
    with open(config.OPERATING_POINTS_PATH, encoding="utf-8") as f:
        points = json.load(f)

    labels = np.load(config.LABELS_PATH)
    df = pd.DataFrame(points)
    df = ensure_columns(df)
    df["cluster_id"] = labels

    rows = []
    for cid in sorted(df["cluster_id"].unique()):
        cdf = df[df["cluster_id"] == cid]
        twin_pct = cdf["apm_doubled"].notna().mean()
        twin_n   = int(cdf["apm_doubled"].notna().sum())
        rows.append({
            "cluster_id":   cid,
            "name":         CLUSTER_NAMES.get(cid, f"klaster {cid}"),
            "n":            len(cdf),
            "twin_pct":     twin_pct,
            "twin_n":       twin_n,
        })

    data = pd.DataFrame(rows).sort_values("twin_pct", ascending=True)

    # Kolory słupków wg progu
    def bar_color(pct):
        if pct >= THRESHOLD_HIGH: return "#e63946"
        if pct >= THRESHOLD_MED:  return "#f4a261"
        return "#a8dadc"

    colors = [bar_color(p) for p in data["twin_pct"]]

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")

    bars = ax.barh(data["name"], data["twin_pct"] * 100,
                   color=colors, height=0.65, zorder=3)

    # Etykiety wartości
    for bar, pct, n in zip(bars, data["twin_pct"], data["twin_n"]):
        w = bar.get_width()
        ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{pct:.1%}  ({n})",
                va="center", ha="left", fontsize=9,
                color="#e0e0e0", fontfamily="monospace")

    # Linie progów
    ax.axvline(THRESHOLD_HIGH * 100, color="#e63946", linewidth=1,
               linestyle="--", alpha=0.6, zorder=2)
    ax.axvline(THRESHOLD_MED  * 100, color="#f4a261", linewidth=1,
               linestyle="--", alpha=0.6, zorder=2)

    # Siatka
    ax.xaxis.grid(True, color="#2a2a3a", linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)

    # Oś X
    ax.set_xlabel("% paczkomatów z bliźniakiem w klastrze",
                  color="#a0a0b0", fontsize=11, labelpad=10)
    ax.tick_params(axis="x", colors="#a0a0b0", labelsize=9)
    ax.tick_params(axis="y", colors="#e0e0e0", labelsize=10)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Legenda
    legend_patches = [
        mpatches.Patch(color="#e63946", label=f"≥ {THRESHOLD_HIGH:.0%} — zdecydowanie warto dublować"),
        mpatches.Patch(color="#f4a261", label=f"≥ {THRESHOLD_MED:.0%}  — warto rozważyć"),
        mpatches.Patch(color="#a8dadc", label=f"< {THRESHOLD_MED:.0%}  — niski priorytet"),
    ]
    ax.legend(handles=legend_patches, loc="lower right",
              facecolor="#1a1a2e", edgecolor="#2a2a3a",
              labelcolor="#e0e0e0", fontsize=9)

    ax.set_title("Odsetek bliźniaków per klaster paczkomatów InPost",
                 color="#ffffff", fontsize=14, fontweight="bold", pad=18)

    

    plt.tight_layout()
    out = "07a_twin_ranking.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Zapisano: {out}")


if __name__ == "__main__":
    main()

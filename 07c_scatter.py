"""
Wykres 07c: Interaktywny scatter — wielkość klastra vs % bliźniaków (Plotly HTML).

Oś X = liczba paczkomatów w klastrze (skala log)
Oś Y = % bliźniaków
Rozmiar bąbla = liczba bliźniaków
Kolor = klaster

Czytanie wykresu:
  Prawy górny róg  → duży klaster, dużo bliźniaków → priorytet ekspansji
  Lewy górny róg   → mały klaster, dużo bliźniaków → niszowy ale gorący
  Dolna część      → niski odsetek → niski priorytet

Uruchom:
    python 07c_scatter.py

Wymagane:
    pip install plotly

Plik wyjściowy: 07c_scatter.html
"""

import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import config
from utils import ensure_columns

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

COLORS = [
    "#e63946", "#457b9d", "#f4a261", "#2a9d8f", "#e9c46a",
    "#264653", "#a8dadc", "#c77dff", "#f72585", "#4cc9f0",
    "#b5838d", "#6d6875", "#ffb703", "#80b918", "#48cae4",
    "#e76f51", "#90e0ef",
]

THRESHOLD_HIGH = 0.20
THRESHOLD_MED  = 0.10


def main():
    with open(config.OPERATING_POINTS_PATH, encoding="utf-8") as f:
        points = json.load(f)

    labels = np.load(config.LABELS_PATH)
    df = pd.DataFrame(points)
    df = ensure_columns(df)
    df["cluster_id"] = labels

    rows = []
    for cid in sorted(df["cluster_id"].unique()):
        cdf      = df[df["cluster_id"] == cid]
        twin_n   = int(cdf["apm_doubled"].notna().sum())
        twin_pct = cdf["apm_doubled"].notna().mean()
        rows.append({
            "cluster_id": cid,
            "name":       CLUSTER_NAMES.get(cid, f"klaster {cid}"),
            "n":          len(cdf),
            "twin_n":     twin_n,
            "twin_pct":   twin_pct,
            "color":      COLORS[cid % len(COLORS)],
        })

    data = pd.DataFrame(rows)

    fig = go.Figure()

    # Strefy tła
    fig.add_hrect(y0=THRESHOLD_HIGH * 100, y1=100,
                  fillcolor="rgba(230,57,70,0.07)", line_width=0)
    fig.add_hrect(y0=THRESHOLD_MED * 100, y1=THRESHOLD_HIGH * 100,
                  fillcolor="rgba(244,162,97,0.07)", line_width=0)

    # Linie progów
    fig.add_hline(y=THRESHOLD_HIGH * 100, line_dash="dash",
                  line_color="#e63946", line_width=1, opacity=0.5,
                  annotation_text="≥20% — zdecydowanie warto dublować",
                  annotation_position="right",
                  annotation_font=dict(color="#e63946", size=10))
    fig.add_hline(y=THRESHOLD_MED * 100, line_dash="dash",
                  line_color="#f4a261", line_width=1, opacity=0.5,
                  annotation_text="≥10% — warto rozważyć",
                  annotation_position="right",
                  annotation_font=dict(color="#f4a261", size=10))

    # Bąble
    fig.add_trace(go.Scatter(
        x=data["n"],
        y=data["twin_pct"] * 100,
        mode="markers+text",
        marker=dict(
            size=data["twin_n"].apply(lambda x: max(12, min(60, x / 5))),
            color=data["color"],
            opacity=0.85,
            line=dict(width=1.5, color="#ffffff"),
        ),
        text=data["name"],
        textposition="top center",
        textfont=dict(size=9, color="#e0e0e0"),
        customdata=data[["cluster_id", "name", "n", "twin_n", "twin_pct"]].values,
        hovertemplate=(
            "<b>%{customdata[1]}</b><br>"
            "Klaster ID: %{customdata[0]}<br>"
            "Paczkomatów: %{customdata[2]:,}<br>"
            "Bliźniaków: %{customdata[3]}<br>"
            "Odsetek: %{customdata[4]:.1%}<br>"
            "<extra></extra>"
        ),
        showlegend=False,
    ))

    fig.update_layout(
        xaxis=dict(
            title="Liczba paczkomatów w klastrze",
            type="log",
            gridcolor="#2a2a3a",
            linecolor="#2a2a3a",
            tickcolor="#606080",
            tickfont=dict(color="#a0a0b0"),
            title_font=dict(color="#a0a0b0"),
        ),
        yaxis=dict(
            title="% bliźniaków w klastrze",
            range=[0, 40],  
            gridcolor="#2a2a3a",
            linecolor="#2a2a3a",
            tickcolor="#606080",
            tickfont=dict(color="#a0a0b0"),
            ticksuffix="%",
            title_font=dict(color="#a0a0b0"),
        ),
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        font=dict(color="#e0e0e0", family="monospace"),
        title=dict(
            text="Wielkość klastra vs odsetek bliźniaków<br>"
                 "<sup>Rozmiar bąbla = liczba bliźniaków. "
                 "Prawy górny róg = najlepsze miejsca do ekspansji.</sup>",
            font=dict(size=16, color="#ffffff"),
            x=0.5,
        ),
        margin=dict(l=60, r=160, t=100, b=60),
        height=620,
    )

    out = "07c_scatter.html"
    fig.write_html(out, include_plotlyjs="cdn")
    print(f"Zapisano: {out}")
    print("Otwórz w przeglądarce: " + out)


if __name__ == "__main__":
    main()

"""
Wykres 07b: Interaktywna mapa Polski — klastry i bliźniaki (Plotly HTML).

Uruchom:
    python 07b_map.py

Wymagane:
    pip install plotly

Plik wyjściowy: 07b_map.html
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


def main():
    with open(config.OPERATING_POINTS_PATH, encoding="utf-8") as f:
        points = json.load(f)

    labels = np.load(config.LABELS_PATH)
    df = pd.DataFrame(points)
    df = ensure_columns(df)
    df["cluster_id"] = labels
    df["cluster_name"] = df["cluster_id"].map(CLUSTER_NAMES)

    df["lat"] = df["location"].apply(
        lambda x: x.get("latitude")  if isinstance(x, dict) else None
    )
    df["lon"] = df["location"].apply(
        lambda x: x.get("longitude") if isinstance(x, dict) else None
    )
    df["city"] = df["address_details"].apply(
        lambda x: x.get("city", "") if isinstance(x, dict) else ""
    )
    df["is_twin"] = df["apm_doubled"].notna()

    df = df.dropna(subset=["lat", "lon"])

    fig = go.Figure()

    for cid in sorted(df["cluster_id"].unique()):
        cdf    = df[df["cluster_id"] == cid]
        color  = COLORS[cid % len(COLORS)]
        name   = CLUSTER_NAMES.get(cid, f"klaster {cid}")
        twin_pct = cdf["is_twin"].mean()

        # Zwykłe paczkomaty
        single = cdf[~cdf["is_twin"]]
        fig.add_trace(go.Scattermapbox(
            lat=single["lat"],
            lon=single["lon"],
            mode="markers",
            marker=dict(size=5, color=color, opacity=0.55),
            name=f"{cid}: {name} ({len(cdf)}, {twin_pct:.1%} bliźniaków)",
            customdata=single[["name", "cluster_name", "city",
                                "location_description"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Klaster: %{customdata[1]}<br>"
                "Miasto: %{customdata[2]}<br>"
                "Opis: %{customdata[3]}<br>"
                "<extra></extra>"
            ),
            legendgroup=str(cid),
        ))

        # Bliźniaki — większe i z obwódką
        twins = cdf[cdf["is_twin"]]
        if len(twins) > 0:
            fig.add_trace(go.Scattermapbox(
                lat=twins["lat"],
                lon=twins["lon"],
                mode="markers",
                marker=dict(size=10, color=color, opacity=0.9),
                name=f"  ↳ bliźniaki ({len(twins)})",
                customdata=twins[["name", "cluster_name", "city",
                                   "location_description"]].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b> ⭐ BLIŹNIAK<br>"
                    "Klaster: %{customdata[1]}<br>"
                    "Miasto: %{customdata[2]}<br>"
                    "Opis: %{customdata[3]}<br>"
                    "<extra></extra>"
                ),
                legendgroup=str(cid),
                showlegend=False,
            ))

    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=52.0, lon=19.5),
            zoom=5.5,
        ),
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        font=dict(color="#e0e0e0", family="monospace"),
        title=dict(
            text="Klastry paczkomatów InPost — Polska<br>"
                 "<sup>Duże kropki = bliźniaki (wysoki popyt). "
                 "Kliknij legendę żeby ukryć/pokazać klaster.</sup>",
            font=dict(size=16, color="#ffffff"),
            x=0.5,
        ),
        legend=dict(
            bgcolor="#1a1a2e",
            bordercolor="#2a2a3a",
            borderwidth=1,
            font=dict(size=9),
            itemsizing="constant",
        ),
        margin=dict(l=0, r=0, t=80, b=0),
        height=750,
    )

    out = "07b_map.html"
    fig.write_html(out, include_plotlyjs="cdn")
    print(f"Zapisano: {out}")
    print("Otwórz w przeglądarce: " + out)


if __name__ == "__main__":
    main()

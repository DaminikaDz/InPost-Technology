"""
Krok 0:
- Wczytuje punkty z cache JSON (wygenerowanego przez analyze_all.py).
- Filtruje tylko punkty ze statusem Operating.
- Zapisuje operating_points.json.
"""

import json
from pathlib import Path

import config


def main():
    if not config.POINTS_CACHE.exists():
        print(f"Brak cache: {config.POINTS_CACHE}")
        print("Uruchom najpierw analyze_all.py")
        return

    print(f"Wczytuję punkty z cache: {config.POINTS_CACHE}")
    with open(config.POINTS_CACHE, encoding="utf-8") as f:
        points = json.load(f)

    print(f"Wczytano {len(points)} punktów.")

    operating_points = [p for p in points if p.get("status") == "Operating"]
    print(f"Operating: {len(operating_points)}/{len(points)}")

    with open(config.OPERATING_POINTS_PATH, "w", encoding="utf-8") as f:
        json.dump(operating_points, f, ensure_ascii=False, indent=2)

    print(f"Zapisano: {config.OPERATING_POINTS_PATH}")


if __name__ == "__main__":
    main()
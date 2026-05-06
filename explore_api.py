"""
Pełna analiza wszystkich paczkomatów w Polsce
Uruchomienie: python analyze_all.py
Wyniki: full_analysis.txt + all_points_cache.json
"""

import requests
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

BASE_URL = "https://api-global-points.easypack24.net/v1/points"


def fetch_all(country="PL", cache_path="all_points_cache.json"):
    if Path(cache_path).exists():
        print(f"Wczytuję z cache: {cache_path}")
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)

    # Sprawdź meta
    r = requests.get(BASE_URL, params={"country": country, "per_page": 1, "page": 1}, timeout=15)
    r.raise_for_status()
    meta = r.json()
    total_pages = meta["total_pages"]
    print(f"Łącznie stron: {total_pages} (po 500 = ~{total_pages*500} punktów)")

    all_points = []
    per_page = 500

    for page in range(1, total_pages + 1):
        while True:
            try:
                r = requests.get(
                    BASE_URL,
                    params={"country": country, "per_page": per_page, "page": page},
                    timeout=30
                )
                r.raise_for_status()
                break
            except Exception as e:
                print(f"\n  Błąd strona {page}: {e}, retry za 3s...")
                time.sleep(3)

        items = r.json().get("items", [])
        all_points.extend(items)
        print(f"  Strona {page}/{total_pages} — łącznie {len(all_points)} pkt", end="\r")
        time.sleep(0.05)

    print(f"\nPobrano {len(all_points)} punktów.")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(all_points, f, ensure_ascii=False)
    print(f"Cache: {cache_path}")
    return all_points


def analyze(points, output="full_analysis.txt"):
    n = len(points)
    lines = []
    log = lambda s="": lines.append(s)

    log(f"PEŁNA ANALIZA — {n} punktów PL")
    log("=" * 70)

    log("\n── STATUS ──────────────────────────────────────────────────────────")
    for val, cnt in Counter(p.get("status") for p in points).most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── TYPE (lista, może być kilka wartości) ───────────────────────────")
    type_counter = Counter()
    for p in points:
        for v in (p.get("type") or []):
            type_counter[v] += 1
    for val, cnt in type_counter.most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    combo_counter = Counter(tuple(sorted(p.get("type") or [])) for p in points)
    log("  Kombinacje type:")
    for combo, cnt in combo_counter.most_common(10):
        log(f"    {cnt:6d}  {combo}")

    log("\n── PHYSICAL_TYPE ───────────────────────────────────────────────────")
    for val, cnt in Counter(p.get("physical_type") for p in points).most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── LOCATION_TYPE ───────────────────────────────────────────────────")
    for val, cnt in Counter(p.get("location_type") for p in points).most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── LOCATION_247 ────────────────────────────────────────────────────")
    for val, cnt in Counter(p.get("location_247") for p in points).most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── OPENING_HOURS (top 30) ──────────────────────────────────────────")
    for val, cnt in Counter(p.get("opening_hours") for p in points).most_common(30):
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {repr(val)}")

    log("\n── FUNCTIONS — każda funkcja osobno ────────────────────────────────")
    func_counter = Counter()
    for p in points:
        for f in (p.get("functions") or []):
            func_counter[f] += 1
    for val, cnt in func_counter.most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n  Liczba unikalnych zestawów funkcji:")
    func_sets = Counter(tuple(sorted(p.get("functions") or [])) for p in points)
    log(f"  {len(func_sets)} unikalnych kombinacji")
    log("  Top 10 kombinacji (skrócone):")
    for combo, cnt in func_sets.most_common(10):
        short = str(combo)[:100]
        log(f"    {cnt:6d}  {short}")

    log("\n── LOCATION_DESCRIPTION (top 50) ───────────────────────────────────")
    desc_counter = Counter()
    for p in points:
        d = (p.get("location_description") or "").strip()
        if d:
            desc_counter[d.lower()] += 1
    null_desc = sum(1 for p in points if not (p.get("location_description") or "").strip())
    log(f"  Brak opisu: {null_desc} ({null_desc/n*100:.1f}%)")
    log(f"  Unikalnych opisów: {len(desc_counter)}")
    for val, cnt in desc_counter.most_common(50):
        log(f"  {cnt:5d}  {val}")

    log("\n── LOCATION_DESCRIPTION_2 (top 30) ─────────────────────────────────")
    d2_counter = Counter()
    for p in points:
        d = (p.get("location_description_2") or "").strip()
        if d:
            d2_counter[d.lower()] += 1
    log(f"  Wypełnione: {sum(d2_counter.values())} ({sum(d2_counter.values())/n*100:.1f}%)")
    for val, cnt in d2_counter.most_common(30):
        log(f"  {cnt:5d}  {val}")

    log("\n── IS_NEXT ─────────────────────────────────────────────────────────")
    for val, cnt in Counter(p.get("is_next") for p in points).most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── PAYMENT_AVAILABLE ───────────────────────────────────────────────")
    for val, cnt in Counter(p.get("payment_available") for p in points).most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── PAYMENT_TYPE (unikalne wartości) ────────────────────────────────")
    pt_counter = Counter()
    for p in points:
        pt = p.get("payment_type") or {}
        for v in pt.values():
            pt_counter[str(v)] += 1
    for val, cnt in pt_counter.most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── LOCKER_AVAILABILITY status ──────────────────────────────────────")
    la_counter = Counter()
    for p in points:
        la = p.get("locker_availability") or {}
        la_counter[la.get("status", "BRAK")] += 1
    for val, cnt in la_counter.most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n  Przykłady NON-NO_DATA:")
    shown = 0
    for p in points:
        la = p.get("locker_availability") or {}
        if la.get("status") not in ("NO_DATA", None) and shown < 5:
            log(f"    {p['name']}: {json.dumps(la)}")
            shown += 1

    log("\n── EASY_ACCESS_ZONE ────────────────────────────────────────────────")
    for val, cnt in Counter(p.get("easy_access_zone") for p in points).most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── AIR_INDEX_LEVEL ─────────────────────────────────────────────────")
    for val, cnt in Counter(p.get("air_index_level") for p in points).most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── AGENCY (top 20) ─────────────────────────────────────────────────")
    for val, cnt in Counter(p.get("agency") for p in points).most_common(20):
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── EXPRESS_DELIVERY_SEND ───────────────────────────────────────────")
    for val, cnt in Counter(p.get("express_delivery_send") for p in points).most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")
    log("\n── EXPRESS_DELIVERY_COLLECT ────────────────────────────────────────")
    for val, cnt in Counter(p.get("express_delivery_collect") for p in points).most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── WOJEWÓDZTWA ─────────────────────────────────────────────────────")
    prov_counter = Counter()
    for p in points:
        ad = p.get("address_details") or {}
        prov_counter[ad.get("province", "brak")] += 1
    for val, cnt in prov_counter.most_common():
        log(f"  {cnt:6d} ({cnt/n*100:5.1f}%)  {val}")

    log("\n── APM_DOUBLED (podwójne paczkomaty) ───────────────────────────────")
    doubled = [p for p in points if p.get("apm_doubled")]
    log(f"  Wypełnione: {len(doubled)} ({len(doubled)/n*100:.1f}%)")

    log("\n" + "=" * 70)
    log("PODSUMOWANIE DLA FEATURE ENGINEERING")
    log("=" * 70)

    useful = []
    low_var = []

    checks = {
        "location_description": len(desc_counter),
        "physical_type": len(Counter(p.get("physical_type") for p in points)),
        "location_type": len(Counter(p.get("location_type") for p in points)),
        "location_247": len(Counter(p.get("location_247") for p in points)),
        "opening_hours": len(Counter(p.get("opening_hours") for p in points)),
        "functions (zestawy)": len(func_sets),
        "is_next": len(Counter(p.get("is_next") for p in points)),
        "air_index_level": len(Counter(p.get("air_index_level") for p in points)),
        "easy_access_zone": len(Counter(p.get("easy_access_zone") for p in points)),
        "agency": len(Counter(p.get("agency") for p in points)),
        "express_delivery_send": len(Counter(p.get("express_delivery_send") for p in points)),
    }
    for field, n_unique in checks.items():
        if n_unique <= 1:
            low_var.append(f"  ✗ {field} — {n_unique} unikalna wartość (zero wariancji)")
        elif n_unique <= 3:
            low_var.append(f"  ~ {field} — {n_unique} wartości (mała wariancja)")
        else:
            useful.append(f"  ✓ {field} — {n_unique} unikalnych wartości")

    log("\nPrzydatne do klasteryzacji:")
    for l in useful: log(l)
    log("\nMała/zerowa wariancja (ostrożnie):")
    for l in low_var: log(l)

    result = "\n".join(lines)
    print(result)
    with open(output, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"\nZapisano: {output}")


if __name__ == "__main__":
    points = fetch_all()
    # Analizujemy tylko Operating
    operating = [p for p in points if p.get("status") == "Operating"]
    print(f"\nAnalizuję {len(operating)} punktów ze statusem Operating (z {len(points)} łącznie)\n")
    analyze(operating)

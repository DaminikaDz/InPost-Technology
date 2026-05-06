"""
Funkcje pomocnicze używane w kilku plikach.
"""

import pandas as pd


_TYPE_LABELS = {
    "parcel_locker": "",
    "parcel_locker_superpop": "superpop",
    "pudo_mini": "pudo mini",
    "refrigerated_locker_machine": "chłodniczy",
    "pok": "",
    "pop": "",
}


def safe_str(val) -> str:
    """
    Bezpieczna konwersja wartości z pandas/JSON na string.
    None, NaN, 'nan', 'None' i pusty string zamieniamy na "".
    """
    if val is None:
        return ""

    try:
        if pd.isna(val):
            return ""
    except (TypeError, ValueError):
        pass

    s = str(val).strip()
    if s.lower() in ("nan", "none", ""):
        return ""
    return s


def as_list(x):
    """
    API zwykle zwraca type jako listę, ale ta funkcja zabezpiecza też przypadek,
    gdy dostaniemy string albo None.
    """
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        return [x]
    return []


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Dodaje brakujące kolumny z wartościami domyślnymi.
    Dzięki temu kod nie wywali się, jeśli API nie zwróci którejś kolumny.
    """
    defaults = {
        "name": "",
        "status": "",
        "location_description": "",
        "location_description_2": "",
        "physical_type": "",
        "location_type": "",
        "location_247": True,
        "is_next": False,
        "apm_doubled": None,
        "type": [],
        "payment_type": {},
        "easy_access_zone": True,
        "opening_hours": "",
        "address_details": {},
        "location": {},
    }

    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    return df


def build_text_from_point(p: dict) -> str:
    """
    Buduje tekst opisujący paczkomat do embeddingu.
    """
    desc = safe_str(p.get("location_description"))
    desc2 = safe_str(p.get("location_description_2"))
    ltype = safe_str(p.get("location_type"))
    is247 = p.get("location_247", True)
    isnxt = p.get("is_next", False)

    parts = [x for x in [desc, desc2] if x]
    meta = []


    types = as_list(p.get("type"))
    type_labels = [_TYPE_LABELS[t] for t in types if _TYPE_LABELS.get(t)]
    meta.extend(type_labels)

    if ltype == "Indoor":
        meta.append("wewnątrz budynku")

    if not is247:
        hours = safe_str(p.get("opening_hours"))
        if hours and hours not in ("24/7", "24//7"):
            meta.append(f"godziny {hours}")
        else:
            meta.append("z godzinami otwarcia")

    if isnxt:
        meta.append("InPost Next")

    pt = p.get("payment_type") or {}
    if isinstance(pt, dict):
        if any("card" in str(v).lower() or "cash" in str(v).lower() for v in pt.values()):
            meta.append("płatność w maszynie")

    if p.get("easy_access_zone") is False:
        meta.append("brak łatwego dostępu")

    return " | ".join(parts + meta)


def has_machine_payment(pt_dict) -> float:
    """
    Zwraca 1.0, jeśli w payment_type pojawia się płatność kartą lub gotówką.
    Nazwa jest ogólna, bo to nie jest wyłącznie karta.
    """
    if not isinstance(pt_dict, dict):
        return 0.0

    return float(
        any(
            "card" in str(v).lower() or "cash" in str(v).lower()
            for v in pt_dict.values()
        )
    )

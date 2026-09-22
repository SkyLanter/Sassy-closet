#!/usr/bin/env python3
"""Conservative 4.0 kg Cainiao inbound + 50% GM floors. Docs helper only. Never buys."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

FX = Decimal("6.725515")
SEA_PER_KG = Decimal("158") / Decimal("2.547")
AIR_PER_KG = Decimal("375") / Decimal("2.547")
Q2 = Decimal("0.01")
GRAM_TOTAL = Decimal("2620")
SEA_FLOOR_KG = Decimal("0.5")


def d2(value: Decimal) -> Decimal:
    return value.quantize(Q2, rounding=ROUND_HALF_UP)


def usd(cny: Decimal) -> Decimal:
    return cny / FX


ROWS = [
    ("A01", "A", 360, Decimal("90.65"), Decimal("25.00"), "catalog"),
    ("P01", "P", 80, Decimal("7.18"), Decimal("5.00"), "catalog"),
    ("S01", "S", 450, Decimal("114.07"), Decimal("28.00"), "catalog"),
    ("P02", "P", 80, Decimal("63.00"), None, "catalog"),
    ("P05", "P", 80, Decimal("109.90"), Decimal("23.00"), "LIVE_LIST"),
    ("P03", "P", 80, Decimal("31.00"), Decimal("18.00"), "catalog"),
    ("P04", "P", 80, Decimal("15.90"), Decimal("13.00"), "catalog"),
    ("K01", "K", 650, Decimal("125.00"), Decimal("37.00"), "LIVE_LIST"),
    ("H01", "H", 40, Decimal("17.90"), Decimal("8.00"), "LIVE_LIST"),
    ("A02", "A", 360, Decimal("85.90"), Decimal("22.00"), "LIVE_LIST"),
    ("A03", "A", 360, Decimal("59.00"), Decimal("19.00"), "catalog"),
]


def wt_share(total_cny: Decimal, grams: int) -> Decimal:
    return total_cny * Decimal(grams) / GRAM_TOTAL


def floored(share_cny: Decimal, floor_cny: Decimal) -> Decimal:
    return share_cny if share_cny >= floor_cny else floor_cny


def main() -> None:
    sea_3 = Decimal("3") * SEA_PER_KG
    sea_4 = Decimal("4") * SEA_PER_KG
    sea_5 = Decimal("5") * SEA_PER_KG
    air_4 = Decimal("4") * AIR_PER_KG
    air_5 = Decimal("5") * AIR_PER_KG
    sea_05 = SEA_FLOOR_KG * SEA_PER_KG
    air_05 = SEA_FLOOR_KG * AIR_PER_KG
    old_eq = sea_3 / Decimal("11")
    eq_4 = sea_4 / Decimal("11")
    eq_5 = sea_5 / Decimal("11")

    print("=== RATES ===")
    print(f"sea_per_kg {SEA_PER_KG}  ${d2(usd(SEA_PER_KG))}")
    print(f"air_per_kg {AIR_PER_KG}  ${d2(usd(AIR_PER_KG))}")
    print(f"sea_3kg {sea_3} ${d2(usd(sea_3))} eq {old_eq} ${d2(usd(old_eq))}")
    print(f"sea_4kg {sea_4} ${d2(usd(sea_4))} eq {eq_4} ${d2(usd(eq_4))}")
    print(f"sea_5kg {sea_5} ${d2(usd(sea_5))} eq {eq_5} ${d2(usd(eq_5))}")
    print(f"air_4kg {air_4} ${d2(usd(air_4))}")
    print(f"air_5kg {air_5} ${d2(usd(air_5))}")
    print(f"sea_0.5 {sea_05} ${d2(usd(sea_05))}")
    print(f"air_0.5 {air_05} ${d2(usd(air_05))}")
    print()

    header = [
        "ma",
        "kind",
        "grams_model",
        "cost_cny",
        "cost_usd_used",
        "inbound_sea_old_3kg_eq_usd",
        "inbound_sea_4kg_eq_usd",
        "inbound_sea_4kg_wt_usd",
        "inbound_sea_4kg_wt_floor_usd",
        "inbound_air_4kg_wt_floor_usd",
        "inbound_sea_5kg_wt_floor_usd",
        "inbound_air_5kg_wt_floor_usd",
        "landed_item_usd",
        "landed_sea_usd",
        "landed_air_usd",
        "landed_sea_5kg_usd",
        "sell_50pct_item",
        "sell_50pct_sea",
        "sell_50pct_air",
        "sell_50pct_sea_5kg",
        "current_sell_usd",
        "delta_vs_current_sea",
        "flag_vs_sea_50pct",
        "customer_us_flat_ship_usd",
        "notes",
    ]
    lines = [",".join(header)]
    table_rows = []

    catalog_usd = {
        "A01": Decimal("13.51"),
        "P01": Decimal("1.07"),
        "S01": Decimal("17.00"),
        "P02": Decimal("9.39"),
        "P05": None,
        "P03": Decimal("4.62"),
        "P04": Decimal("2.37"),
        "K01": None,
        "H01": None,
        "A02": None,
        "A03": Decimal("8.79"),
    }

    for ma, kind, grams, cost_cny, current, cost_src in ROWS:
        item_full = usd(cost_cny)
        cost_used = d2(item_full)
        old_in = usd(old_eq)
        eq4_in = usd(eq_4)
        wt4_sea = usd(wt_share(sea_4, grams))
        def4_sea = usd(floored(wt_share(sea_4, grams), sea_05))
        def4_air = usd(floored(wt_share(air_4, grams), air_05))
        def5_sea = usd(floored(wt_share(sea_5, grams), sea_05))
        def5_air = usd(floored(wt_share(air_5, grams), air_05))

        landed_item = d2(item_full)
        landed_sea = d2(item_full + def4_sea)
        landed_air = d2(item_full + def4_air)
        landed_sea5 = d2(item_full + def5_sea)
        sell_item = d2(landed_item / Decimal("0.50"))
        sell_sea = d2(landed_sea / Decimal("0.50"))
        sell_air = d2(landed_air / Decimal("0.50"))
        sell_sea5 = d2(landed_sea5 / Decimal("0.50"))

        if current is None:
            delta = ""
            flag = "NO_CURRENT_SELL"
            current_s = ""
        else:
            delta_v = d2(current - sell_sea)
            delta = f"{delta_v}"
            flag = "UNDER_SEA" if delta_v < 0 else "OVER_SEA"
            current_s = f"{current}"

        note_parts = []
        live = {
            "A01": "live available $25",
            "P01": "live available $5",
            "S01": "live available $28",
            "P02": "live hold Inbox",
            "P05": "live hold Inbox",
            "P03": "live available $18",
            "P04": "live available $13",
            "K01": "live available $37",
            "H01": "live available $8",
            "A02": "live available $22",
            "A03": "live hold Inbox",
        }
        if cost_src == "LIVE_LIST":
            if ma == "P05":
                note_parts.append(
                    "LIVE_LIST 109.90 (was 75; short-link meta 98.90 unused); SNAPSHOT_SELL 23.00 not live; do not Save; shop law: P05 never official $23"
                )
            elif ma == "K01":
                note_parts.append("LIVE_LIST 125 (was USD_ONLY ~103.03 / 15.32)")
            elif ma == "H01":
                note_parts.append("LIVE_LIST 17.90 (was USD_ONLY ~13.45 / 2.00)")
            elif ma == "A02":
                note_parts.append("LIVE_LIST 85.90 (was 71)")
        else:
            snap = catalog_usd.get(ma)
            if snap is not None and snap != cost_used:
                note_parts.append(
                    f"FX_CONFLICT catalog_cost_usd {snap} vs used {cost_used} (prefer CNY/6.725515)"
                )
            elif snap == cost_used:
                note_parts.append("FX matches catalog cost_usd at 2dp")
            if ma == "A03":
                note_parts.append(
                    "SNAPSHOT_SELL 19.00 not live; do not Save; live A03 has no sourceLink"
                )
            if ma == "P02":
                note_parts.append("NO_CURRENT_SELL snapshot empty; do not invent $")
        note_parts.append(live[ma])
        if current is not None:
            gm = d2((current - landed_sea) / current * Decimal("100"))
            note_parts.append(
                f"{flag} {delta} (current GM vs sea landed {gm}%)"
            )

        notes = "; ".join(note_parts)
        table_rows.append(
            {
                "ma": ma,
                "kind": kind,
                "grams": grams,
                "cost_cny": cost_cny,
                "cost_used": cost_used,
                "old_in": d2(old_in),
                "eq4": d2(eq4_in),
                "wt4": d2(wt4_sea),
                "def_sea": d2(def4_sea),
                "def_air": d2(def4_air),
                "def5_sea": d2(def5_sea),
                "landed_item": landed_item,
                "landed_sea": landed_sea,
                "landed_air": landed_air,
                "landed_sea5": landed_sea5,
                "sell_item": sell_item,
                "sell_sea": sell_sea,
                "sell_air": sell_air,
                "sell_sea5": sell_sea5,
                "current": current_s,
                "delta": delta,
                "flag": flag,
                "notes": notes,
            }
        )
        lines.append(
            ",".join(
                [
                    ma,
                    kind,
                    str(grams),
                    f"{cost_cny}",
                    f"{cost_used}",
                    f"{d2(old_in)}",
                    f"{d2(eq4_in)}",
                    f"{d2(wt4_sea)}",
                    f"{d2(def4_sea)}",
                    f"{d2(def4_air)}",
                    f"{d2(def5_sea)}",
                    f"{d2(def5_air)}",
                    f"{landed_item}",
                    f"{landed_sea}",
                    f"{landed_air}",
                    f"{landed_sea5}",
                    f"{sell_item}",
                    f"{sell_sea}",
                    f"{sell_air}",
                    f"{sell_sea5}",
                    current_s,
                    delta,
                    flag,
                    "",
                    notes.replace(",", ";"),
                ]
            )
        )

    out = Path("/workspace/docs/MARGIN_50PCT_CONSERVATIVE_2026-09-10.csv")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    print()
    print(
        "ma kind g cost¥ used old$2.52 eq4 wt4 DEF_SEA DEF_AIR def5 "
        "Litem Lsea Lair L5 Sitem S50sea S50air S505 cur Δ flag"
    )
    for r in table_rows:
        print(
            f"{r['ma']} {r['kind']} {r['grams']} {r['cost_cny']} {r['cost_used']} "
            f"{r['old_in']} {r['eq4']} {r['wt4']} {r['def_sea']} {r['def_air']} {r['def5_sea']} "
            f"{r['landed_item']} {r['landed_sea']} {r['landed_air']} {r['landed_sea5']} "
            f"{r['sell_item']} {r['sell_sea']} {r['sell_air']} {r['sell_sea5']} "
            f"{r['current'] or '—'} {r['delta'] or '—'} {r['flag']}"
        )
    print()
    print("=== WT 4kg sea $ (no floor) by kind ===")
    for kind, g in (("A", 360), ("S", 450), ("K", 650), ("P", 80), ("H", 40)):
        raw = usd(wt_share(sea_4, g))
        fl = usd(floored(wt_share(sea_4, g), sea_05))
        air_raw = usd(wt_share(air_4, g))
        air_fl = usd(floored(wt_share(air_4, g), air_05))
        print(
            f"{kind} g={g} sea_wt={raw} {d2(raw)} sea_def={fl} {d2(fl)} "
            f"air_wt={air_raw} {d2(air_raw)} air_def={air_fl} {d2(air_fl)}"
        )

    floor_sum = sum(
        usd(floored(wt_share(sea_4, r[2]), sea_05)) for r in ROWS
    )
    wt_sum = sum(usd(wt_share(sea_4, r[2])) for r in ROWS)
    print(f"sum wt 4kg sea usd {wt_sum} {d2(wt_sum)}")
    print(f"sum floored 4kg sea usd {floor_sum} {d2(floor_sum)}")
    print(f"box 4kg sea usd {usd(sea_4)} {d2(usd(sea_4))}")


if __name__ == "__main__":
    main()

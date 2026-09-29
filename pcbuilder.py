"""PC build planner - command-line version.
Run: python pcbuilder.py
Prices are rough example values in CHF. Edit DB to add real parts.
"""

DB = {
    "cpu": ("CPU", [
        {"n": "Ryzen 5 5600", "sock": "AM4", "tdp": 65, "p": 120},
        {"n": "Ryzen 5 7600", "sock": "AM5", "tdp": 65, "p": 210},
        {"n": "Ryzen 7 7800X3D", "sock": "AM5", "tdp": 120, "p": 400},
        {"n": "Core i5-13400F", "sock": "LGA1700", "tdp": 65, "p": 190},
        {"n": "Core i7-14700K", "sock": "LGA1700", "tdp": 125, "p": 400},
    ]),
    "mb": ("Motherboard", [
        {"n": "B550 ATX", "sock": "AM4", "ram": "DDR4", "ff": "ATX", "p": 120},
        {"n": "B650 ATX", "sock": "AM5", "ram": "DDR5", "ff": "ATX", "p": 180},
        {"n": "B650M mATX", "sock": "AM5", "ram": "DDR5", "ff": "mATX", "p": 140},
        {"n": "B650I ITX", "sock": "AM5", "ram": "DDR5", "ff": "ITX", "p": 230},
        {"n": "B760 ATX", "sock": "LGA1700", "ram": "DDR5", "ff": "ATX", "p": 170},
        {"n": "B760M mATX (DDR4)", "sock": "LGA1700", "ram": "DDR4", "ff": "mATX", "p": 110},
    ]),
    "ram": ("Memory", [
        {"n": "16 GB DDR4", "type": "DDR4", "p": 45},
        {"n": "32 GB DDR4", "type": "DDR4", "p": 80},
        {"n": "16 GB DDR5", "type": "DDR5", "p": 65},
        {"n": "32 GB DDR5", "type": "DDR5", "p": 110},
    ]),
    "gpu": ("Graphics card", [
        {"n": "No card (integrated graphics)", "tdp": 0, "len": 0, "p": 0},
        {"n": "RTX 5060", "tdp": 115, "len": 240, "p": 300},
        {"n": "RTX 5070 Super", "tdp": 220, "len": 245, "p": 600},
        {"n": "RX 7800 XT", "tdp": 263, "len": 267, "p": 500},
        {"n": "RTX 5080 Super", "tdp": 320, "len": 310, "p": 1000},
    ]),
    "sto": ("Storage", [
        {"n": "1 TB NVMe SSD", "p": 70},
        {"n": "2 TB NVMe SSD", "p": 130},
        {"n": "4 TB NVMe SSD", "p": 250},
    ]),
    "cool": ("CPU cooler", [
        {"n": "Stock cooler", "h": 40, "max": 65, "p": 0},
        {"n": "Single tower air cooler", "h": 155, "max": 200, "p": 40},
        {"n": "Dual tower air cooler", "h": 165, "max": 250, "p": 90},
        {"n": "240 mm liquid cooler", "h": 50, "max": 280, "p": 100},
    ]),
    "psu": ("Power supply", [
        {"n": "550 W", "w": 550, "p": 65},
        {"n": "650 W", "w": 650, "p": 80},
        {"n": "750 W", "w": 750, "p": 100},
        {"n": "850 W", "w": 850, "p": 130},
        {"n": "1000 W", "w": 1000, "p": 190},
    ]),
    "case": ("Case", [
        {"n": "Compact ITX case", "ff": ["ITX"], "gpu": 280, "cool": 60, "p": 120},
        {"n": "Micro-ATX case", "ff": ["ITX", "mATX"], "gpu": 320, "cool": 160, "p": 80},
        {"n": "ATX mid tower", "ff": ["ITX", "mATX", "ATX"], "gpu": 400, "cool": 170, "p": 100},
        {"n": "ATX full tower", "ff": ["ITX", "mATX", "ATX"], "gpu": 450, "cool": 185, "p": 180},
    ]),
}


def choose(label, items):
    """Show a menu and return the chosen part (or None to skip)."""
    print(f"\n{label}:")
    for i, it in enumerate(items, 1):
        price = f" - CHF {it['p']}" if it["p"] else ""
        print(f"  {i}) {it['n']}{price}")
    while True:
        text = input("Number (Enter to skip): ").strip()
        if text == "":
            return None
        if text.isdigit() and 1 <= int(text) <= len(items):
            return items[int(text) - 1]
        print("Invalid choice, try again.")


def check(c):
    """Return a list of (level, message) compatibility results."""
    out = []
    cpu, mb, ram, gpu = c["cpu"], c["mb"], c["ram"], c["gpu"]
    cool, psu, case = c["cool"], c["psu"], c["case"]

    if cpu and mb:
        if cpu["sock"] == mb["sock"]:
            out.append(("OK", f"CPU fits the motherboard ({cpu['sock']})."))
        else:
            out.append(("ERROR", f"CPU socket {cpu['sock']} does not match motherboard socket {mb['sock']}."))
    if ram and mb:
        if ram["type"] == mb["ram"]:
            out.append(("OK", f"Memory type matches ({ram['type']})."))
        else:
            out.append(("ERROR", f"Motherboard needs {mb['ram']}, but you picked {ram['type']}."))
    if mb and case:
        if mb["ff"] in case["ff"]:
            out.append(("OK", f"{mb['ff']} board fits the case."))
        else:
            out.append(("ERROR", f"The {case['n']} cannot hold an {mb['ff']} board."))
    if gpu and case and gpu["len"]:
        if gpu["len"] <= case["gpu"]:
            out.append(("OK", f"Graphics card fits ({gpu['len']} of {case['gpu']} mm)."))
        else:
            out.append(("ERROR", f"Graphics card is {gpu['len']} mm, case allows {case['gpu']} mm."))
    if cool and case:
        if cool["h"] <= case["cool"]:
            out.append(("OK", f"Cooler fits the case ({cool['h']} of {case['cool']} mm)."))
        else:
            out.append(("ERROR", f"Cooler is {cool['h']} mm tall, case allows {case['cool']} mm."))
    if cool and cpu:
        if cpu["tdp"] <= cool["max"]:
            out.append(("OK", "Cooler can handle this CPU."))
        else:
            out.append(("WARN", f"{cool['n']} is meant for up to {cool['max']} W, CPU draws {cpu['tdp']} W."))
    if cpu and cpu["n"].endswith("F") and gpu and gpu["tdp"] == 0:
        out.append(("ERROR", "This 'F' CPU has no integrated graphics. Add a graphics card."))
    if cpu and gpu:
        est = cpu["tdp"] + gpu["tdp"] + 100  # +100 W for board, RAM, storage, fans
        out.append(("INFO", f"Estimated power draw under load: about {est} W."))
        if psu:
            if psu["w"] < est:
                out.append(("ERROR", f"Power supply too small. You need at least {est} W."))
            elif psu["w"] < est * 1.3:
                out.append(("WARN", "Power supply has little headroom. Aim for about 30% extra."))
            else:
                out.append(("OK", "Power supply has enough headroom."))
    return out


def main():
    print("=== PC Build Planner ===")
    build = {k: choose(label, items) for k, (label, items) in DB.items()}

    print("\n--- Your build ---")
    total = 0
    for k, (label, _) in DB.items():
        part = build[k]
        print(f"{label:<15} {part['n'] if part else '-'}")
        total += part["p"] if part else 0
    print(f"\nTotal price: CHF {total}")

    print("\n--- Compatibility ---")
    results = check(build)
    order = {"ERROR": 0, "WARN": 1, "INFO": 2, "OK": 3}
    for level, msg in sorted(results, key=lambda r: order[r[0]]):
        print(f"[{level}] {msg}")
    if not results:
        print("Pick more parts to see checks.")


if __name__ == "__main__":
    main()



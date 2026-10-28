"""Generate the invoice batches, the answer key and the lab workloads.

Everything here is synthetic and seeded, so the same seed always writes the
same files. The output is committed with its hashes, so nothing is generated
on the machine that runs the eval. Run from the repo root:

    python3 tools/generate.py

Each invoice is made from a "kind": what was bought, the code the policy in
chart/cost-codes.md gives it, and the policy rules it tests (its tags). The
code comes from the kind, never from reading the invoice back.
"""

import hashlib
import json
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261028
BATCHES = 4
PER_BATCH = 50
FIXTURE = "invoice-coding-eval@1.0"
ROLE = "ap-coder"

D = Decimal


def money(x: Decimal) -> str:
    return f"${x:,.2f}"


# ---------------------------------------------------------------- vendors

# name, street, city line, phone, email domain, invoice prefix, layout, date style
VENDORS = {
    "parts": [
        ("Bellwether Bike Supply", "2209 Foundry Street", "Kessel Point, OR 97998", "(541) 555-0187", "bellwether-bike.example", "BW-", "table", "long"),
        ("Northgrade Cycle Distribution", "77 Quarry Road", "Alden Ford, WA 98997", "(360) 555-0114", "northgrade.example", "NGD", "lines", "iso"),
        ("Pinecut Components", "15 Mill Lane", "Harlow Bend, CA 94997", "(707) 555-0155", "pinecut.example", "PC-", "list", "short"),
    ],
    "bikes": [
        ("Ostrava Bicycle Co.", "900 Assembly Way", "Dunmore, OR 97996", "(503) 555-0170", "ostrava-bikes.example", "OBC-", "table", "iso"),
        ("Fernhill Electric Bikes", "31 Volt Street", "Carrow, WA 98996", "(206) 555-0131", "fernhill-ebikes.example", "FEB", "lines", "long"),
    ],
    "apparel": [
        ("Tailwind Apparel", "4 Loom Court", "Bramwick, CA 94999", "(415) 555-0166", "tailwind-apparel.example", "TWA-", "list", "long"),
        ("Crestline Helmets", "1200 Shell Avenue", "Kessel Point, OR 97998", "(541) 555-0192", "crestline-helmets.example", "CH", "table", "short"),
    ],
    "tools": [
        ("Ridgeline Workshop Equipment", "4410 Millrace Avenue, Suite 12", "Corvale, WA 98999", "(360) 555-0163", "ridgeline-wse.example", "RWE-2026-", "lines", "long"),
        ("Torque & Truing Tool Works", "58 Anvil Row", "Marrow Falls, OR 97999", "(541) 555-0148", "tt-toolworks.example", "TT", "table", "iso"),
    ],
    "carrier": [
        ("Swiftline Freight", "6000 Dock Road", "Portmere, OR 97995", "(503) 555-0109", "swiftline-freight.example", "SWF", "lines", "iso"),
        ("ParcelPath", "20 Sorting Plaza", "Alden Ford, WA 98997", "(360) 555-0102", "parcelpath.example", "PP-", "table", "short"),
    ],
    "service": [
        ("Gravity Suspension Service", "12 Rebound Street", "Harlow Bend, CA 94997", "(707) 555-0122", "gravity-susp.example", "GSS-", "list", "long"),
        ("Wheelwright Builds", "8 Spoke Alley", "Marrow Falls, OR 97999", "(541) 555-0135", "wheelwright.example", "WWB", "table", "iso"),
    ],
    "trades": [
        ("Falls Plumbing & Drain", "301 Pipe Street", "Marrow Falls, OR 97999", "(541) 555-0177", "fallsplumbing.example", "FPD-", "lines", "long"),
        ("Brightwire Electric", "17 Circuit Lane", "Marrow Falls, OR 97999", "(541) 555-0119", "brightwire.example", "BWE", "list", "short"),
        ("Compressor Care NW", "44 Valve Road", "Dunmore, OR 97996", "(503) 555-0143", "compressorcare.example", "CC-", "table", "iso"),
    ],
    "auto": [
        ("Tannery Row Auto", "502 Tannery Row", "Marrow Falls, OR 97999", "(541) 555-0161", "tanneryauto.example", "TRA-", "table", "long"),
        ("Cascade Fuel Card", "1 Pump Plaza", "Portmere, OR 97995", "(503) 555-0105", "cascadefuel.example", "CFC", "lines", "iso"),
    ],
    "landlord": [
        ("Tallow Lane Properties", "1250 Ash Court", "Marrow Falls, OR 97999", "(541) 555-0129", "tallowlane.example", "TLP-", "list", "long"),
        ("Riverbend Storage", "88 Levee Road", "Marrow Falls, OR 97999", "(541) 555-0158", "riverbend-storage.example", "RBS", "table", "short"),
    ],
    "rental": [
        ("Summit Event Rentals", "700 Canopy Drive", "Dunmore, OR 97996", "(503) 555-0137", "summit-rentals.example", "SER-", "table", "long"),
        ("Liftway Equipment Hire", "23 Boom Street", "Portmere, OR 97995", "(503) 555-0184", "liftway.example", "LEH", "lines", "iso"),
    ],
    "utility": [
        ("Marrow Falls Power & Gas", "1 Grid Plaza", "Marrow Falls, OR 97999", "(541) 555-0100", "mfpg.example", "MFPG-", "lines", "long"),
        ("Marrow Falls Water Bureau", "9 Reservoir Way", "Marrow Falls, OR 97999", "(541) 555-0101", "mfwater.example", "WB", "list", "iso"),
        ("Fernwave Fiber", "300 Signal Street", "Portmere, OR 97995", "(503) 555-0199", "fernwave.example", "FW-", "table", "short"),
    ],
    "software": [
        ("Spokeline Software, Inc.", "88 Harrow Lane", "Bramwick, CA 94999", "(415) 555-0142", "spokeline.example", "SPL-", "list", "long"),
        ("Ledgerly", "5 Column Street", "Harlow Bend, CA 94997", "(707) 555-0127", "ledgerly.example", "LDG", "table", "iso"),
        ("TapTill Payments", "40 Swipe Avenue", "Bramwick, CA 94999", "(415) 555-0173", "taptill.example", "TT-PAY-", "lines", "short"),
    ],
    "insurer": [
        ("Harborline Mutual Insurance", "60 Anchor Street", "Portmere, OR 97995", "(503) 555-0151", "harborline.example", "HMI", "lines", "long"),
    ],
    "association": [
        ("Northwest Bicycle Retailers Association", "14 Guild Street", "Portmere, OR 97995", "(503) 555-0116", "nwbra.example", "NWBRA-", "list", "long"),
        ("Marrow Falls Chamber of Commerce", "2 Main Street", "Marrow Falls, OR 97999", "(541) 555-0112", "mfchamber.example", "MFC", "table", "iso"),
    ],
    "office": [
        ("Quillstone Office Supply", "19 Paper Lane", "Kessel Point, OR 97998", "(541) 555-0181", "quillstone.example", "QS-", "table", "short"),
    ],
    "marketing": [
        ("Falls Gazette Media", "120 Press Street", "Marrow Falls, OR 97999", "(541) 555-0124", "fallsgazette.example", "FGM", "lines", "long"),
        ("Inkwell Print Shop", "3 Platen Court", "Marrow Falls, OR 97999", "(541) 555-0168", "inkwell-print.example", "IPS-", "list", "iso"),
    ],
    "events": [
        ("Marrow Falls Gravel Classic", "PO Box 418", "Marrow Falls, OR 97999", "(541) 555-0133", "mfgravel.example", "MFGC-", "list", "long"),
        ("Ridge Riders Cycling Club", "PO Box 77", "Kessel Point, OR 97998", "(541) 555-0144", "ridgeriders.example", "RRC", "table", "short"),
    ],
    "professional": [
        ("Alder & Finch CPAs", "400 Ledger Avenue, Suite 3", "Portmere, OR 97995", "(503) 555-0138", "alderfinch.example", "AF-", "lines", "long"),
        ("Kestrel Law Group", "77 Court Street", "Portmere, OR 97995", "(503) 555-0159", "kestrel-law.example", "KLG", "list", "iso"),
    ],
    "bank": [
        ("First Example Bank", "1 Vault Square", "Portmere, OR 97995", "(503) 555-0190", "firstexample.example", "FEB-SVC-", "lines", "iso"),
        ("TapTill Payments", "40 Swipe Avenue", "Bramwick, CA 94999", "(415) 555-0173", "taptill.example", "TT-PAY-", "lines", "short"),
    ],
    "training": [
        ("Mechanic Pathways Academy", "50 Learning Way", "Bramwick, CA 94999", "(415) 555-0147", "mechpath.example", "MPA-", "table", "long"),
    ],
    "meals": [
        ("Copper Kettle Bistro", "210 Tannery Row", "Marrow Falls, OR 97999", "(541) 555-0153", "copperkettle.example", "CKB", "list", "short"),
    ],
    "travel": [
        ("Harbor Point Hotel", "9 Pier Street", "Portmere, OR 97995", "(503) 555-0186", "harborpoint-hotel.example", "HPH-", "lines", "long"),
        ("Skylark Air", "1 Terminal Way", "Bramwick, CA 94999", "(415) 555-0108", "skylark-air.example", "SKY", "table", "iso"),
    ],
    "cleaning": [
        ("Sparrow Cleaning Co.", "61 Broom Street", "Marrow Falls, OR 97999", "(541) 555-0171", "sparrowclean.example", "SCC-", "table", "long"),
    ],
    "city": [
        ("City of Marrow Falls, Business Licensing", "2 Main Street", "Marrow Falls, OR 97999", "(541) 555-0110", "marrowfalls.example", "BL-", "list", "iso"),
    ],
    "charity": [
        ("Marrow Falls Youth Cycling Fund", "PO Box 12", "Marrow Falls, OR 97999", "(541) 555-0126", "youthcycling.example", "YCF", "list", "long"),
    ],
}

# ---------------------------------------------------------------- catalogues

PARTS = [
    ("Inner tube 700x28-35c, 48 mm presta valve", "5.10"), ("Gravel tire 700x40c, tubeless ready", "31.25"),
    ("Disc brake pads, resin, road/gravel", "9.85"), ("11-speed chain, 116 links", "11.20"),
    ("Cassette 11-34T, 11-speed", "42.90"), ("Brake cable kit, stainless", "6.75"),
    ("Bar tape, cork, black", "8.40"), ("Tubeless valve stems, 44 mm, pair", "6.90"),
    ("Pedals, flat, alloy", "24.00"), ("Saddle, gel comfort", "19.50"), ("Bottle cage, alloy", "4.20"),
    ("Derailleur hanger, model DH-12", "7.95"), ("Rotor 160 mm, 6-bolt", "14.30"), ("Grips, lock-on", "9.10"),
    ("Kickstand, adjustable", "8.80"), ("Rear light, USB rechargeable", "12.60"), ("Fenders, 700c set", "16.45"),
]
BIKES = [
    ("Ostrava Trail 2 hardtail, size M", "612.00"), ("Ostrava Roadster 105, size 56", "845.00"),
    ("Ostrava Kid 20 in.", "189.00"), ("Fernhill Commute e-bike, 500 Wh", "1480.00"),
    ("Fernhill Cargo e-bike, long tail", "2390.00"), ("Ostrava Gravel GRX, size L", "1105.00"),
]
APPAREL = [
    ("Jersey, short sleeve, men's M", "28.00"), ("Bib shorts, women's S", "41.50"), ("Gloves, full finger, L", "12.90"),
    ("Rain jacket, packable, M", "46.00"), ("Helmet, road, MIPS, size M", "54.00"), ("Helmet, kids, size S", "19.75"),
    ("Cycling shoes, SPD, size 42", "63.00"), ("Wool socks, 3-pack", "11.25"),
]
SMALL_TOOLS = [
    ("Professional workshop tool kit, 38 pieces", "389.00"), ("Torque wrench, 2-14 Nm", "54.00"),
    ("Chain wear gauge", "18.50"), ("Bench vise, 5 in.", "142.00"), ("Spoke tension meter", "96.00"),
    ("Cable cutter, heavy duty", "38.40"), ("Workstand, portable", "219.00"), ("Bottom bracket tool set", "64.80"),
    ("Hydraulic brake bleed kit", "72.50"), ("Headset press", "185.00"), ("Shop compressor, 6 gal", "329.00"),
]
BIG_EQUIPMENT = [
    ("Professional wheel truing stand, floor mount", "3200.00"), ("Hydraulic bike lift, 2-post", "4850.00"),
    ("Ultrasonic parts washer, 30 L", "2780.00"), ("Frame alignment table", "6400.00"),
    ("Suspension service station with fork stand", "3950.00"), ("Wheel building jig, pro", "2575.00"),
]
MID_TOOLS = [  # under the threshold each, but bought in a quantity that passes it
    ("Repair workstand, shop grade, clamp head", "1450.00"), ("Wheel truing stand, bench model", "1290.00"),
    ("Workbench with tool board, 6 ft", "1180.00"), ("Rolling tool chest", "960.00"),
]
CONSUMABLES = [
    ("Chain lube, dry, 1 L shop jug", "21.40"), ("Degreaser, citrus, 5 L", "34.90"), ("Shop rags, 25 lb box", "39.00"),
    ("Nitrile gloves, box of 100", "11.80"), ("Waterproof grease, 500 g tub", "16.20"), ("Zip ties, 1,000 pack", "13.50"),
    ("Brake cleaner, 12 cans", "44.40"), ("Carbon assembly paste, 200 g", "17.60"),
]
RETAIL_LUBE = [
    ("Chain lube, wet, 120 ml retail bottle, case of 24", "98.40"), ("Bike wash spray, 1 L retail, case of 12", "79.20"),
    ("Grease, 100 g retail tube, case of 24", "88.80"), ("Tubeless sealant, 120 ml retail, case of 12", "71.40"),
]
OFFICE = [
    ("Printer paper, letter, 10 reams", "48.90"), ("Thermal receipt rolls, 50 pack", "39.50"), ("Toner cartridge, black", "86.00"),
    ("Price tags with strings, 1,000", "14.20"), ("Binder clips, assorted", "7.80"), ("Ballpoint pens, box of 50", "9.60"),
]

# ---------------------------------------------------------------- kinds

OCT = date(2026, 10, 1)


def pick(rng, items, n):
    return rng.sample(items, n)


def qty_lines(rng, catalogue, n, qmin, qmax):
    return [(desc, rng.randint(qmin, qmax), D(price)) for desc, price in pick(rng, catalogue, n)]


def freight_line(rng, label="Freight, ground"):
    return (label, 1, D(rng.choice(["38.50", "62.40", "85.00", "112.75", "24.90", "149.00"])))


def k_parts(rng, inv):
    inv.update(vendor="parts", lines=qty_lines(rng, PARTS, rng.randint(2, 5), 2, 40),
               notes=["Resale certificate on file."])
    if inv["tags"]:
        inv["lines"].append(freight_line(rng))


def k_bikes(rng, inv):
    inv.update(vendor="bikes", lines=qty_lines(rng, BIKES, rng.randint(1, 3), 1, 4))
    if inv["tags"]:
        inv["lines"].append(freight_line(rng, "Freight, palletized delivery"))


def k_apparel(rng, inv):
    vendor = "parts" if "vendor" in inv["tags"] else "apparel"
    lines = qty_lines(rng, APPAREL, rng.randint(2, 4), 3, 12)
    if vendor == "parts":  # a parts distributor's helmet and clothing order
        lines = [(d, q, p) for d, q, p in qty_lines(rng, APPAREL[4:6] + APPAREL[:4], rng.randint(2, 3), 3, 10)]
    inv.update(vendor=vendor, lines=lines)


def k_small_tools(rng, inv):
    tags = inv["tags"]
    if "unit-price" in tags:
        desc, price = rng.choice(MID_TOOLS)
        q = rng.randint(3, 4)
        inv.update(vendor="tools", lines=[(desc, q, D(price))])
        assert D(price) < 2500 <= q * D(price)
    else:
        vendor = "parts" if "vendor" in tags else "tools"
        inv.update(vendor=vendor, lines=qty_lines(rng, SMALL_TOOLS, rng.randint(1, 3), 1, 2))
        if "freight" in tags:
            inv["lines"].append(freight_line(rng))


def k_equipment(rng, inv):
    tags = inv["tags"]
    if "threshold-edge" in tags:
        lines = [("Wheel building and truing station, bench mount", 1, D("2500.00"))]
    else:
        desc, price = rng.choice(BIG_EQUIPMENT)
        lines = [(desc, 1, D(price))]
    if "freight" in tags:
        lines.append(freight_line(rng, "Freight, curbside delivery"))
    inv.update(vendor="tools", lines=lines, notes=["Serial no. " + rng.choice("ABCDEFGH") + str(rng.randint(10000, 99999)) + ". Warranty registered to the buyer."])


def k_consumables(rng, inv):
    vendor = "parts" if "vendor" in inv["tags"] else "tools"
    inv.update(vendor=vendor, lines=qty_lines(rng, CONSUMABLES, rng.randint(2, 4), 1, 6), notes=["Workshop supplies."])


def k_retail_lube(rng, inv):
    inv.update(vendor="parts", lines=qty_lines(rng, RETAIL_LUBE, rng.randint(1, 3), 1, 3),
               notes=[rng.choice(["Retail stock, for resale.", "For resale: retail stock, resale certificate on file."])])


def k_carrier_inbound(rng, inv):
    # Freight billed by a carrier on goods we bought is coded with the goods (rule 3).
    if inv["code"] == "5150":
        supplier, goods = rng.choice(VENDORS["bikes"])[0], f"{rng.randint(2, 6)} boxed bikes for resale"
    else:
        supplier, goods = rng.choice(VENDORS["parts"])[0], f"{rng.randint(2, 9)} cartons of parts and accessories for resale"
    po = f"PO {rng.randint(4100, 4999)}"
    inv.update(vendor="carrier", lines=[(f"Inbound freight: {goods}, from {supplier} to Copperleaf Cycle Works, {po}", 1, D(rng.randint(60, 240)) + D("0.50"))],
               notes=["Shipper: " + supplier + ". Consignee: Copperleaf Cycle Works, 418 Tannery Row, Unit B, Marrow Falls, OR 97999."])


def k_carrier_outbound(rng, inv):
    lines = []
    for _ in range(rng.randint(3, 6)):
        lines.append((f"Parcel to customer, order #{rng.randint(10200, 10999)}, {rng.choice(['ground', '2-day', 'ground'])}", 1, D(rng.randint(9, 38)) + D(rng.choice(["0.15", "0.40", "0.85"]))))
    inv.update(vendor="carrier", lines=lines, notes=["Shipper: Copperleaf Cycle Works. Parcels delivered to the consignees on each line."])


def k_outsourced(rng, inv):
    job = rng.choice([
        ("Fork full service (damper and air spring), customer bike, work order", "185.00"),
        ("Rear shock rebuild, customer bike, work order", "145.00"),
        ("Custom wheel build, customer's hubs and rims, work order", "120.00"),
        ("Carbon frame repair, customer bike, work order", "420.00"),
    ])
    inv.update(vendor="service", lines=[(f"{job[0]} WO-{rng.randint(3000, 3999)}", 1, D(job[1]))],
               notes=["Bike returned to Copperleaf Cycle Works for the customer to collect."])


def k_equipment_repair(rng, inv):
    job = rng.choice([
        ("Service and repair of shop air compressor, replace pressure switch", "265.00"),
        ("Repair of hydraulic bike lift, replace seal kit (lift owned by Copperleaf)", "410.00"),
        ("Recalibrate and repair truing stand gauge", "95.00"),
        ("Parts washer pump replacement and service", "330.00"),
    ])
    inv.update(vendor="trades", lines=[(job[0], 1, D(job[1]))])
    inv["vendor_index"] = 2  # Compressor Care NW


def k_building_repair(rng, inv):
    job, idx = rng.choice([
        (("Repair leaking pipe under workshop sink, 418 Tannery Row Unit B", "240.00"), 0),
        (("Clear blocked floor drain in workshop", "185.00"), 0),
        (("Replace faulty light fixtures in showroom, labor and parts", "390.00"), 1),
        (("Repair tripped circuit and replace outlet, workshop wall", "165.00"), 1),
    ])
    inv.update(vendor="trades", lines=[job[:1] + (1, D(job[1]))], vendor_index=idx)


def k_van_repair(rng, inv):
    job = rng.choice([("Brake pads and rotors, front, shop van (plate CCW-418)", "468.00"), ("Oil change and inspection, shop van (plate CCW-418)", "89.00"), ("Replace alternator, shop van (plate CCW-418)", "612.00")])
    inv.update(vendor="auto", lines=[(job[0], 1, D(job[1]))], vendor_index=0)


def k_fuel(rng, inv):
    lines = [(f"Diesel, shop van, {d}", 1, D(rng.randint(48, 96)) + D("0.37")) for d in ("Oct 3", "Oct 11", "Oct 19", "Oct 27")[: rng.randint(2, 4)]]
    inv.update(vendor="auto", lines=lines, vendor_index=1, date=date(2026, 10, 31))


def period_after(rng, inv, prepaid, months=12):
    start_offset = rng.randint(150, 260) if prepaid else rng.randint(0, 40)
    start = (inv["date"] + timedelta(days=start_offset)).replace(day=1)
    if prepaid:  # clearly past the 90 days, never near the line
        assert (start - inv["date"]).days >= 115
    else:
        assert (start - inv["date"]).days <= 90
    year, month = start.year + (start.month - 1 + months) // 12, (start.month - 1 + months) % 12 + 1
    end = date(year, month, 1) - timedelta(days=1)
    inv["period"] = (start, end)


def k_rent(rng, inv):
    prepaid = "prepaid" in inv["tags"]
    if prepaid:
        period_after(rng, inv, True, months=3)
        inv.update(vendor="landlord", vendor_index=1, lines=[("Seasonal storage unit S-14, rent for the period shown, paid in advance", 1, D("1125.00"))])
    else:
        period_after(rng, inv, False, months=1)
        inv.update(vendor="landlord", vendor_index=0, lines=[("Monthly rent, 418 Tannery Row, Unit B", 1, D("2850.00"))])


def k_deposit(rng, inv):
    vendor, idx, desc, amount = rng.choice([
        ("landlord", 0, "Security deposit for Unit C (storage), refundable at the end of the lease less any damage", "1500.00"),
        ("rental", 0, "Refundable damage deposit, event tent and flooring (returned when the rental items come back undamaged)", "750.00"),
        ("utility", 0, "Refundable service deposit for new account at Unit C, credited back after 12 months of on-time payment", "300.00"),
        ("landlord", 1, "Refundable key and access card deposit, storage unit S-14", "100.00"),
    ])
    inv.update(vendor=vendor, vendor_index=idx, lines=[(desc, 1, D(amount))])


def k_equipment_rental(rng, inv):
    vendor, idx, desc, amount = rng.choice([
        ("rental", 0, "Rental: 10x20 ft event tent with sidewalls, 3 days (Gravel Classic expo)", "640.00"),
        ("rental", 1, "Rental: scissor lift, 2 days, for showroom signage install", "380.00"),
        ("rental", 0, "Rental: PA system and 40 folding chairs, 1 day (customer clinic night)", "295.00"),
    ])
    inv.update(vendor=vendor, vendor_index=idx, lines=[(desc, 1, D(amount))])


def k_utility(rng, inv):
    code = inv["code"]
    idx, desc, lo, hi = {
        "6210": (0, "Electricity and natural gas service, 418 Tannery Row Unit B, September usage", 180, 420),
        "6220": (1, "Water, sewer and trash service, 418 Tannery Row Unit B, bimonthly", 90, 210),
        "6230": (2, "Business fiber internet 500 Mbps and two mobile lines, monthly", 140, 230),
    }[code]
    inv.update(vendor="utility", vendor_index=idx, lines=[(desc, 1, D(rng.randint(lo, hi)) + D("0.64"))])


def k_software(rng, inv):
    tags = inv["tags"]
    if "prepaid" in tags:  # an annual plan billed far ahead: still 6300
        period_after(rng, inv, True, months=12)
        idx, desc, amount = rng.choice([
            (0, "Spokeline Shop Pro: point of sale, service tickets and inventory, 2 seats, annual plan", "1140.00"),
            (1, "Ledgerly Small Business bookkeeping software, annual subscription", "540.00"),
        ])
    elif "vendor" in tags:  # the card processor's own software plan
        idx, desc, amount = 2, "TapTill POS app, Pro plan, 3 registers, monthly subscription", "89.00"
        period_after(rng, inv, False, months=1)
    else:
        idx, desc, amount = rng.choice([
            (0, "Spokeline Shop Pro, 2 seats, monthly plan", "99.00"),
            (1, "Ledgerly Small Business, monthly subscription", "48.00"),
        ])
        period_after(rng, inv, False, months=1)
    inv.update(vendor="software", vendor_index=idx, lines=[(desc, 1, D(amount))])


def k_insurance(rng, inv):
    prepaid = "prepaid" in inv["tags"]
    period_after(rng, inv, prepaid, months=12)
    desc, amount = rng.choice([("Business owner's policy (property and general liability), annual premium", "3180.00"),
                               ("Commercial auto policy, shop van, annual premium", "1640.00")])
    inv.update(vendor="insurer", lines=[(desc, 1, D(amount))])


def k_membership(rng, inv):
    prepaid = "prepaid" in inv["tags"]
    period_after(rng, inv, prepaid, months=12)
    idx, desc, amount = rng.choice([(0, "Retail member dues, annual", "395.00"), (1, "Chamber membership, small business tier, annual", "285.00")])
    inv.update(vendor="association", vendor_index=idx, lines=[(desc, 1, D(amount))])


def k_office(rng, inv):
    inv.update(vendor="office", lines=qty_lines(rng, OFFICE, rng.randint(2, 4), 1, 5))


def k_advertising(rng, inv):
    idx, desc, amount = rng.choice([(0, "Half-page ad, Falls Gazette weekend edition, Nov 7 and Nov 14", "520.00"),
                                    (0, "Online banner campaign, fallsgazette.example, 30 days", "350.00"),
                                    (1, "Printed flyers, A5 full color, 2,000 copies (winter tune-up promotion)", "214.00")])
    inv.update(vendor="marketing", vendor_index=idx, lines=[(desc, 1, D(amount))])


def k_sponsorship(rng, inv):
    idx, desc, amount = rng.choice([(0, "Silver sponsorship, Marrow Falls Gravel Classic 2027, logo on finisher medals", "1500.00"),
                                    (1, "Club kit sponsorship, Ridge Riders Cycling Club, 2027 season", "800.00")])
    inv.update(vendor="events", vendor_index=idx, lines=[(desc, 1, D(amount))])


def k_professional(rng, inv):
    if inv["code"] == "6700":
        inv.update(vendor="professional", vendor_index=0, lines=[("Monthly bookkeeping and bank reconciliation, September", 1, D("650.00")), ("Quarterly payroll tax filings", 1, D("180.00"))])
    else:
        inv.update(vendor="professional", vendor_index=1, lines=[("Review of storage unit lease (Unit C), 2.5 hours", 1, D("775.00")), ("Trademark search, shop name", 1, D("240.00"))])


def k_bank_fees(rng, inv):
    idx = rng.randint(0, 1)
    if idx == 0:
        lines = [("Monthly account maintenance fee", 1, D("25.00")), ("Incoming wire fees, 3 at $15.00", 1, D("45.00"))]
    else:
        lines = [("Card processing fees, September (2.6% + $0.10 per transaction)", 1, D(rng.randint(380, 760)) + D("0.18")), ("Chargeback fee", 1, D("15.00"))]
    inv.update(vendor="bank", vendor_index=idx, lines=lines)


def k_training(rng, inv):
    desc, amount = rng.choice([("Online course: Hydraulic brake service certification, 1 seat, self-paced", "349.00"),
                               ("Online course: E-bike motor and battery diagnostics, 2 seats", "698.00"),
                               ("In-person workshop: wheel building fundamentals, 1 seat", "425.00")])
    inv.update(vendor="training", lines=[(desc, 1, D(amount))])


def k_meals(rng, inv):
    inv.update(vendor="meals", lines=[(rng.choice(["Lunch for 4, supplier meeting with Bellwether rep", "Team dinner after inventory count, 6 guests", "Breakfast, customer clinic volunteers, 8 guests"]), 1, D(rng.randint(70, 240)) + D("0.50"))])


def k_travel(rng, inv):
    idx = rng.randint(0, 1)
    lines = [("Room, 2 nights, Northwest Bicycle Retailers trade show", 2, D("189.00"))] if idx == 0 else [("Airfare, round trip PDX-SFO, bike industry dealer summit, 1 passenger", 1, D("312.00"))]
    inv.update(vendor="travel", vendor_index=idx, lines=lines)


def k_cleaning(rng, inv):
    inv.update(vendor="cleaning", lines=[("Weekly cleaning, showroom and workshop, October (4 visits)", 4, D("95.00"))])


def k_license(rng, inv):
    inv.update(vendor="city", lines=[("Business license renewal, retail and repair, Copperleaf Cycle Works", 1, D("150.00")), ("Sidewalk display permit", 1, D("45.00"))])


def k_donation(rng, inv):
    inv.update(vendor="charity", lines=[("Donation pledge: youth learn-to-ride program, fall session", 1, D(rng.choice(["250.00", "500.00", "300.00"])))],
               notes=["Thank you for your charitable gift. No goods, services or advertising were provided in return. Receipt for your records."])


# kind name -> (code, tags, builder). Every kind appears in every batch at least once.
KINDS = {
    "parts": ("5100", [], k_parts),
    "parts+freight": ("5100", ["freight"], k_parts),
    "carrier-inbound": ("5100", ["freight", "carrier"], k_carrier_inbound),
    "carrier-inbound-bikes": ("5150", ["freight", "carrier"], k_carrier_inbound),
    "retail-lube": ("5100", ["retail-pack"], k_retail_lube),
    "bikes": ("5150", [], k_bikes),
    "bikes+freight": ("5150", ["freight"], k_bikes),
    "apparel": ("5200", [], k_apparel),
    "apparel-from-parts-vendor": ("5200", ["vendor"], k_apparel),
    "outsourced-repair": ("5300", ["repair"], k_outsourced),
    "rent": ("6100", [], k_rent),
    "rent-prepaid": ("1400", ["prepaid"], k_rent),
    "deposit": ("1300", ["deposit"], k_deposit),
    "equipment-rental": ("6150", [], k_equipment_rental),
    "electricity": ("6210", [], k_utility),
    "water": ("6220", [], k_utility),
    "internet": ("6230", [], k_utility),
    "software": ("6300", [], k_software),
    "software-annual-ahead": ("6300", ["prepaid", "software-exception"], k_software),
    "software-from-card-processor": ("6300", ["vendor"], k_software),
    "building-repair": ("6400", ["repair"], k_building_repair),
    "equipment-repair": ("6410", ["repair"], k_equipment_repair),
    "small-tools": ("6450", [], k_small_tools),
    "small-tools-from-parts-vendor": ("6450", ["vendor"], k_small_tools),
    "small-tools-qty-over-threshold": ("6450", ["unit-price"], k_small_tools),
    "equipment": ("1500", ["threshold"], k_equipment),
    "equipment+freight": ("1500", ["threshold", "freight"], k_equipment),
    "equipment-at-threshold": ("1500", ["threshold", "threshold-edge"], k_equipment),
    "consumables": ("6460", ["consumable"], k_consumables),
    "consumables-from-parts-vendor": ("6460", ["consumable", "vendor"], k_consumables),
    "office": ("6500", [], k_office),
    "carrier-outbound": ("6550", ["outbound"], k_carrier_outbound),
    "advertising": ("6600", [], k_advertising),
    "sponsorship": ("6610", [], k_sponsorship),
    "accounting": ("6700", [], k_professional),
    "legal": ("6710", [], k_professional),
    "insurance": ("6800", [], k_insurance),
    "insurance-prepaid": ("1400", ["prepaid"], k_insurance),
    "membership": ("7200", [], k_membership),
    "membership-prepaid": ("1400", ["prepaid"], k_membership),
    "bank-fees": ("6900", [], k_bank_fees),
    "training-online": ("6950", ["online-training"], k_training),
    "meals": ("7000", [], k_meals),
    "travel": ("7100", [], k_travel),
    "cleaning": ("7300", [], k_cleaning),
    "fuel": ("7400", [], k_fuel),
    "van-repair": ("7450", ["repair"], k_van_repair),
    "license": ("7500", [], k_license),
    "donation": ("7600", [], k_donation),
}

# ---------------------------------------------------------------- rendering

BILL_TO = "Copperleaf Cycle Works, 418 Tannery Row, Unit B, Marrow Falls, OR 97999"


def fmt_date(d: date, style: str) -> str:
    if style == "iso":
        return d.isoformat()
    if style == "short":
        return d.strftime("%d %b %Y")
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


def render(inv) -> str:
    name, street, city, phone, domain, _, layout, style = inv["vendor_row"]
    d = lambda x: fmt_date(x, style)  # noqa: E731
    lines = inv["lines"]
    subtotal = sum((q * p for _, q, p in lines), D("0"))
    terms = inv["terms"]
    period = inv.get("period")
    out = []
    if layout == "table":
        out += [f"# {name}", "", f"{street}, {city} · {phone} · billing@{domain}", "",
                "| Invoice no. | Invoice date | Terms |", "| --- | --- | --- |", f"| {inv['number']} | {d(inv['date'])} | {terms} |", "",
                f"**Bill to:** {BILL_TO}", ""]
        if period:
            out += [f"Period covered: {d(period[0])} to {d(period[1])}", ""]
        out += ["| Description | Qty | Unit price | Amount |", "| --- | --- | --- | --- |"]
        out += [f"| {desc} | {q} | {money(p)} | {money(q * p)} |" for desc, q, p in lines]
        out += ["", f"**Total due: {money(subtotal)}**"]
    elif layout == "lines":
        out += [f"{name.upper()}", f"{street} · {city} · {phone}", "", f"INVOICE {inv['number']}", f"Date: {d(inv['date'])}", f"Terms: {terms}",
                f"Customer: {BILL_TO}"]
        if period:
            out += [f"Service period: {d(period[0])} - {d(period[1])}"]
        out += [""]
        for i, (desc, q, p) in enumerate(lines, 1):
            out.append(f"{i}. {desc} | qty {q} @ {money(p)} = {money(q * p)}")
        out += ["", f"Amount due: {money(subtotal)}"]
    else:
        out += [f"## {name}", f"{street}, {city}", f"{phone} · accounts@{domain}", "", f"- Invoice: {inv['number']}", f"- Issued: {d(inv['date'])}",
                f"- Billed to: {BILL_TO}", f"- Payment terms: {terms}"]
        if period:
            out += [f"- Coverage: {d(period[0])} through {d(period[1])}"]
        out += ["", "Items:"]
        for desc, q, p in lines:
            out.append(f"- {q} × {desc}, {money(p)} each, {money(q * p)}" if q > 1 else f"- {desc}: {money(p)}")
        out += ["", f"Total: {money(subtotal)}"]
    if inv.get("notes"):
        out += [""] + inv["notes"]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- batches

def build_batch(rng, batch_no, counters):
    names = list(KINDS)
    picks = names + [rng.choice(names) for _ in range(PER_BATCH - len(names))]
    rng.shuffle(picks)
    invoices = []
    for kind in picks:
        code, tags, builder = KINDS[kind]
        inv = {"kind": kind, "code": code, "tags": list(tags), "notes": [],
               "date": OCT + timedelta(days=rng.randint(0, 30)), "terms": rng.choice(["Net 30", "Net 15", "Due on receipt", "Net 30"])}
        builder(rng, inv)
        rows = VENDORS[inv["vendor"]]
        row = rows[inv["vendor_index"]] if "vendor_index" in inv else rng.choice(rows)
        counters[row[0]] = counters.get(row[0], rng.randint(1100, 8800)) + rng.randint(1, 37)
        inv["vendor_row"] = row
        inv["number"] = f"{row[5]}{counters[row[0]]}"
        invoices.append(inv)
    numbers = [i["number"] for i in invoices]
    assert len(set(numbers)) == len(numbers)
    return invoices


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    rng = random.Random(SEED)
    chart = (ROOT / "chart" / "cost-codes.md").read_text().rstrip()
    counters, key, manifest_cases = {}, {}, []
    for b in range(1, BATCHES + 1):
        batch = f"batch-{b:02d}"
        invoices = build_batch(rng, b, counters)
        inv_dir = ROOT / "invoices" / batch
        inv_dir.mkdir(parents=True, exist_ok=True)
        parts = [chart, "", "# Invoices to code", "", f"There are {len(invoices)} invoices in this batch."]
        for inv in invoices:
            text = render(inv)
            (inv_dir / f"{inv['number']}.md").write_text(text)
            parts += ["", f"=== INVOICE {inv['number']} ===", "", text.rstrip()]
        prompt = ROOT / "inputs" / f"{batch}.txt"
        prompt.parent.mkdir(parents=True, exist_ok=True)
        prompt.write_text("\n".join(parts) + "\n")
        key[batch] = {inv["number"]: {"code": inv["code"], "kind": inv["kind"], "tags": inv["tags"]} for inv in invoices}
        expect = {inv["number"]: {"anyOf": [inv["code"], int(inv["code"])]} for inv in invoices}
        write_json(ROOT / "eval" / "workloads" / f"invoice-coding-{batch}.json", {
            "schema_version": "1.1",
            "workload": {"id": f"invoice-coding-{batch}", "provider": "prompt", "role": ROLE, "requires_fixture": FIXTURE,
                         "promptFile": f"inputs/{batch}.txt", "replyRoom": "context", "verify": {"expect": expect}},
        })
        manifest_cases.append({"id": batch, "input": f"inputs/{batch}.txt", "input_sha256": sha256(prompt), "invoices": len(invoices)})
    write_json(ROOT / "eval" / "answer-key.json", key)
    write_json(ROOT / "evals" / "invoice-coding.json", {
        "id": "invoice-coding",
        "satisfies": "invoice-coding@1.0",
        "description": (
            f"The model is handed Copperleaf Cycle Works' cost-code chart (34 codes), its coding policy and a batch of "
            f"{PER_BATCH} synthetic vendor invoices as one text, and replies with one JSON object giving each invoice one "
            f"cost code. {BATCHES} batches, generated once by tools/generate.py (seed {SEED}) and committed with their hashes. No tools."
        ),
        "role": ROLE,
        "role_sha256": {f"roles/{ROLE}.{ext}": sha256(ROOT / "roles" / f"{ROLE}.{ext}") for ext in ("json", "md")},
        "cases": manifest_cases,
        "reply_room": "context: the run's context window (the profile's n_ctx) minus the prompt. Context is the run's configuration, recorded with it, not part of the eval.",
        "pass": "a batch passes when every invoice gets the code in eval/answer-key.json; fields correct out of the batch's invoices are recorded beside the verdict and are the score. eval/grade.py is the stdlib reference and also breaks misses down by policy rule.",
    })


if __name__ == "__main__":
    main()

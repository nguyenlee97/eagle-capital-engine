#!/usr/bin/env python3
"""
Phase A1/A2 — Master Database & Crosswalk Extractor for EagleCapitalEngine (WSR + Capitalism Lab Unified DB)
Extracts, decodes, normalizes, and cross-links:
  1. Wall Street Raider (C:\\Program Files (x86)\\wsr):
     - CORPNAME.DAT: 1,590 Corporations (ID 11..1600) + 54 Countries
     - wsr101.dat: 70 Industries (**IND=01..70 with IDGRO%, IDVOL%, INDNAM) +
       Initial Corporate Balance Sheet parameters (ST, CASH, PL1, DV%, JBOS, BCOUP, BA%, GR%, CR, MAG) +
       Cross-ownership Holding/Subsidiary graph (< and > relations)
     - Mscnews.dat & quotewsr.dat: Losslessly decoded via exact WSR.EXE VA 0x00696454 stream cipher
  2. Capitalism Lab (C:\\Users\\LENOVO\\Downloads\\capitalism lab\\[tamhongame.com]_CL\\Capitalism Lab):
     - gameset/1STD.SET: All 56 embedded dBase III (.DBF) tables (null-byte sanitized):
       * 135 Products (PRODUCT_TYPES with PRICE, RD_PREMIUM, FREIGHT, DEMAND, NECESSITY, PRICE_CN, QUALITY_CN, BRAND_CN)
       * 99 Manufacturing Recipes (MANUFACTURING: Output <- Input1 + Input2 + Input3)
       * 29 Product Classes & 5 Mega Classes
       * 48 Firm Types (FIRM) & 142 Building Specifications (FBUILDSTD)
       * 33 Functional Department Jobs (JOB) & 52 Firm-Job mappings (FIRMJOB)
       * 86 Retail Store Product Mappings (RETAIL_STORE_PRODUCTS)
       * 9 Natural Resources (NATURAL_RESOURCES) & 12 Farm Crops / 4 Livestock
       * 20 Software Types & 10 Software Classes (Digital Age DLC)
       * 38 R&D Technologies (TECH)
       * 128 Real Cities (CITIES with POPULATION & WAGE_RATE) + 64 AI Executive Personas (PERSONS)
     - firm/*.BLD: Metadata inventory of all 66 physical building resource files
  3. Unified Crosswalk (industry_supply_chain_crosswalk):
     - Deterministic bidirectional mapping between all 70 WSR Industries and Capitalism Lab's
       29 Product Classes, 135 Products, 99 Recipes, 20 Software Types, 38 R&D Tech Nodes,
       9 Natural Resources, and 48 Firm Types.
"""

import json
import os
import re
import struct
from datetime import datetime, timezone

WSR_DIR = r"C:\Program Files (x86)\wsr"
CL_DIR = r"C:\Users\LENOVO\Downloads\capitalism lab\[tamhongame.com]_CL\Capitalism Lab"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def decode_wsr_cipher_line(raw_bytes: bytes) -> str:
    """
    Exact stream cipher decoder reverse-engineered from WSR.EXE VA 0x00696454:
      For 1-based byte index pos = 1..len(line):
        if 40 <= b <= 170:
          if pos < 6: b -= (2 * pos + 26)
          else:       b -= 39
    """
    s_check = raw_bytes.decode("latin1", errors="replace").strip()
    if s_check.startswith("@IT") or s_check.startswith("@END") or not s_check:
        return s_check
    out = bytearray()
    for idx, b in enumerate(raw_bytes):
        pos = idx + 1
        if 40 <= b <= 170:
            if pos < 6:
                b = b - (2 * pos + 26)
            else:
                b = b - 39
        out.append(b & 0xFF)
    return out.decode("latin1", errors="replace").strip()


def parse_wsr_mscnews(path: str):
    items = {}
    current_tag = None
    current_lines = []
    with open(path, "rb") as f:
        for raw_line in f:
            line_bytes = raw_line.rstrip(b"\r\n")
            if not line_bytes:
                continue
            decoded = decode_wsr_cipher_line(line_bytes)
            if decoded.startswith("@IT"):
                if current_tag is not None:
                    items[current_tag] = " ".join(current_lines).strip()
                current_tag = decoded.split()[0]
                current_lines = []
            elif decoded.startswith("@END"):
                if current_tag is not None:
                    items[current_tag] = " ".join(current_lines).strip()
                break
            else:
                current_lines.append(decoded)
    return items


def parse_wsr_quotes(path: str):
    quotes = []
    current_lines = []
    with open(path, "rb") as f:
        for raw_line in f:
            line_bytes = raw_line.rstrip(b"\r\n")
            if not line_bytes:
                continue
            decoded = decode_wsr_cipher_line(line_bytes)
            if decoded.startswith("@IT"):
                if current_lines:
                    quotes.append(" ".join(current_lines).strip())
                current_lines = []
            elif decoded.startswith("@END"):
                if current_lines:
                    quotes.append(" ".join(current_lines).strip())
                break
            else:
                current_lines.append(decoded)
    return quotes


def parse_wsr_corpname(path: str):
    countries = {}
    corporations = {}
    with open(path, "r", encoding="latin1") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("'"):
                m_ctry = re.match(r"^'\s+([A-Z \.]+?)\s*=(\d{2})\s+(.+)$", line)
                if m_ctry:
                    ccode = int(m_ctry.group(2))
                    countries[ccode] = {
                        "code": ccode,
                        "name": m_ctry.group(1).strip(),
                        "financial_city": m_ctry.group(3).strip(),
                    }
                continue
            if "|" not in line:
                continue
            parts = line.split("|")
            if len(parts) >= 4 and parts[0].strip().isdigit():
                cid = int(parts[0].strip())
                country_code = int(parts[1].strip()) if parts[1].strip().isdigit() else 0
                ticker = parts[2].strip()
                name = parts[3].strip()
                corporations[cid] = {
                    "id": cid,
                    "country_code": country_code,
                    "ticker": ticker,
                    "name": name,
                }
    return countries, corporations


def parse_wsr101(path: str, corporations: dict):
    industries = {}
    current_ind_id = None
    current_corp_id = None

    with open(path, "r", encoding="latin1") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("REM") or line == "@END":
                continue

            if line.startswith("**IND="):
                m_ind = re.search(r"\*\*IND=(\d+)", line)
                m_gro = re.search(r"IDGRO%=(\d+)", line)
                m_vol = re.search(r"IDVOL%=(\d+)", line)
                m_nam = re.search(r"INDNAM=(.+)$", line)
                if m_ind:
                    current_ind_id = int(m_ind.group(1))
                    industries[current_ind_id] = {
                        "industry_id": current_ind_id,
                        "name": m_nam.group(1).strip() if m_nam else f"INDUSTRY_{current_ind_id}",
                        "growth_rate_pct": int(m_gro.group(1)) if m_gro else 0,
                        "volatility_pct": int(m_vol.group(1)) if m_vol else 0,
                        "corporation_ids": [],
                    }
                continue

            if line.startswith("#"):
                tokens = line.split()
                cid = int(tokens[0][1:])
                current_corp_id = cid
                corp = corporations.setdefault(
                    cid,
                    {"id": cid, "country_code": 1, "ticker": f"C{cid}", "name": f"Corp {cid}"},
                )
                corp["industry_id"] = current_ind_id
                if current_ind_id in industries:
                    industries[current_ind_id]["corporation_ids"].append(cid)

                params = {}
                for tok in tokens[1:]:
                    if "=" in tok:
                        k, v = tok.split("=", 1)
                        if k == "BCOUP" and "@" in v:
                            mat_yr, coup = v.split("@", 1)
                            params["bond_maturity_year"] = int(mat_yr)
                            params["bond_coupon_pct"] = float(coup)
                        else:
                            try:
                                params[k] = int(v) if v.isdigit() or (v.startswith("-") and v[1:].isdigit()) else float(v)
                            except ValueError:
                                params[k] = v
                corp["initial_state"] = {
                    "status": params.get("ST", 0),
                    "cash_millions": float(params.get("CASH", 0.0)),
                    "capital_assets_millions": float(params.get("PL1", 0.0)),
                    "dividend_payout_pct": float(params.get("DV%", 0.0)),
                    "bonds_outstanding_millions": float(params.get("JBOS", 0.0)),
                    "bond_maturity_year": params.get("bond_maturity_year"),
                    "bond_coupon_pct": params.get("bond_coupon_pct"),
                    "business_assets_pct": params.get("BA%"),
                    "growth_rate_override_pct": params.get("GR%"),
                    "credit_rating_override": params.get("CR"),
                    "mag_factor": params.get("MAG"),
                }
                corp.setdefault("parents", [])
                corp.setdefault("subsidiaries", [])
                continue

            if current_corp_id is not None and ("<" in line or ">" in line):
                m_rel = re.match(r"^(\d+)\s*([<>])\s*(\d+(?:\.\d+)?)%", line)
                if m_rel:
                    other_id = int(m_rel.group(1))
                    rel_op = m_rel.group(2)
                    pct = float(m_rel.group(3))
                    corp = corporations[current_corp_id]
                    if rel_op == "<":
                        corp["parents"].append({"parent_id": other_id, "ownership_pct": pct})
                    else:
                        corp["subsidiaries"].append({"subsidiary_id": other_id, "ownership_pct": pct})

    # Reconcile bidirectional parent/subsidiary links across all corporations
    for cid, corp in corporations.items():
        for p in corp.get("parents", []):
            pid = p["parent_id"]
            if pid in corporations:
                subs = corporations[pid].setdefault("subsidiaries", [])
                if not any(s["subsidiary_id"] == cid for s in subs):
                    subs.append({"subsidiary_id": cid, "ownership_pct": p["ownership_pct"]})
        for s in corp.get("subsidiaries", []):
            sid = s["subsidiary_id"]
            if sid in corporations:
                pars = corporations[sid].setdefault("parents", [])
                if not any(pr["parent_id"] == cid for pr in pars):
                    pars.append({"parent_id": cid, "ownership_pct": s["ownership_pct"]})

    # Assign Industry 71 (EXCHANGE-TRADED FUNDS) to Entity IDs 1581..1600 per WSR.EXE ETF setup
    etf_specs = {
        1581: ("GOVT_BOND", [], 1.0, 0.25, 2000.0, 37),
        1582: ("CORP_BOND_IG", [], 1.0, 0.35, 2000.0, 37),
        1583: ("JUNK_BOND", [], 1.0, 0.50, 1500.0, 37),
        1584: ("LEVERAGED_BULL", list(range(3, 70)), 2.0, 0.75, 1500.0, 37),
        1585: ("LEVERAGED_BEAR", list(range(3, 70)), -2.0, 0.75, 1500.0, 37),
        1586: ("SECTOR_EQUITY", [3, 55, 67, 68], 1.0, 0.40, 1200.0, 1),
        1587: ("SECTOR_EQUITY", [4, 10, 24, 26, 35, 39, 40, 61], 1.0, 0.45, 2500.0, 37),
        1588: ("SECTOR_EQUITY", [7, 8, 69], 1.0, 0.40, 1800.0, 1),
        1589: ("SECTOR_EQUITY", [15, 17, 28, 34], 1.0, 0.40, 1200.0, 1),
        1590: ("SECTOR_EQUITY", [4, 21, 22, 43, 56], 1.0, 0.45, 1800.0, 2),
        1591: ("SECTOR_EQUITY", [41, 42, 43, 44, 45, 46, 47, 48], 1.0, 0.40, 1400.0, 1),
        1592: ("SECTOR_EQUITY", [11, 16, 23, 25, 52, 53], 1.0, 0.40, 1200.0, 1),
        1593: ("REGIONAL_EQUITY", [10, 24, 35, 68], 1.0, 0.50, 1600.0, 70),
        1594: ("SECTOR_EQUITY", [6, 9, 12, 13, 14, 20, 49, 54], 1.0, 0.40, 1500.0, 1),
        1595: ("SECTOR_EQUITY", [1, 2, 37, 70], 1.0, 0.40, 2000.0, 37),
        1596: ("SECTOR_EQUITY", [18, 19, 31, 32, 33, 58, 60, 66], 1.0, 0.40, 1400.0, 1),
        1597: ("SECTOR_EQUITY", [5, 59, 63], 1.0, 0.45, 1300.0, 2),
        1598: ("SECTOR_EQUITY", [27, 29, 30, 36, 57, 62, 65], 1.0, 0.45, 1400.0, 37),
        1599: ("SECTOR_EQUITY", [7, 9, 33, 50], 1.0, 0.45, 1500.0, 70),
        1600: ("COMMODITY_FUTURES", [7, 9, 15, 50], 1.0, 0.60, 1200.0, 37),
    }
    industries[71] = {
        "industry_id": 71,
        "name": "EXCHANGE-TRADED FUNDS (ETFs)",
        "growth_rate_pct": 0,
        "volatility_pct": 0,
        "corporation_ids": list(range(1581, 1601)),
    }
    if 70 in industries:
        industries[70]["corporation_ids"] = [c for c in industries[70]["corporation_ids"] if c < 1581]
    for etf_id, (etype, t_inds, lev, fee_pct, nav_m, adv_ind) in etf_specs.items():
        if etf_id in corporations:
            c = corporations[etf_id]
            c["industry_id"] = 71
            c["initial_state"] = {
                "status": 1,
                "cash_millions": nav_m,
                "capital_assets_millions": 0.0,
                "dividend_payout_pct": 0.0,
                "bonds_outstanding_millions": 0.0,
                "bond_maturity_year": None,
                "bond_coupon_pct": None,
                "business_assets_pct": 0,
                "growth_rate_override_pct": 0,
                "credit_rating_override": None,
                "mag_factor": None,
                "etf_type": etype,
                "target_industries": t_inds,
                "leverage_factor": lev,
                "advisory_fee_pct": fee_pct,
                "preferred_advisor_industry": adv_ind,
            }
            c.setdefault("parents", [])
            c.setdefault("subsidiaries", [])

    return industries


def parse_dbf_buffer(buf: bytes):
    if len(buf) < 32:
        return [], []
    _, _, _, _, num_records, header_len, record_len = struct.unpack_from("<BBBB I H H", buf, 0)
    fields = []
    pos = 32
    while pos + 32 <= header_len and buf[pos] != 0x0D:
        fname = buf[pos : pos + 11].split(b"\x00")[0].decode("latin1").strip()
        ftype = chr(buf[pos + 11])
        flen = buf[pos + 16]
        fdec = buf[pos + 17]
        fields.append((fname, ftype, flen, fdec))
        pos += 32

    rows = []
    rpos = header_len
    for _ in range(num_records):
        if rpos + record_len > len(buf):
            break
        rec = buf[rpos : rpos + record_len]
        rpos += record_len
        if rec[0] == 0x2A:  # deleted row
            continue
        fpos = 1
        row = {}
        for fname, ftype, flen, fdec in fields:
            # Strip trailing null bytes (\x00) used by CapLab dBase padding before stripping whitespace
            val_raw = rec[fpos : fpos + flen].split(b"\x00")[0].decode("latin1", errors="replace").strip()
            fpos += flen
            if ftype == "N":
                if val_raw == "":
                    row[fname] = 0
                elif "." in val_raw or fdec > 0:
                    try:
                        row[fname] = float(val_raw)
                    except ValueError:
                        row[fname] = val_raw
                else:
                    try:
                        row[fname] = int(val_raw)
                    except ValueError:
                        row[fname] = val_raw
            else:
                row[fname] = val_raw
        rows.append(row)
    return [f[0] for f in fields], rows


def parse_caplab_1std_set(path: str):
    with open(path, "rb") as f:
        raw = f.read()
    rec_count = struct.unpack_from("<H", raw, 0)[0]
    entries = []
    for i in range(rec_count + 1):
        pos = 2 + i * 35
        name = raw[pos : pos + 31].split(b"\x00")[0].decode("latin1")
        offset = struct.unpack_from("<I", raw, pos + 31)[0]
        entries.append((name, offset))

    tables = {}
    for i in range(rec_count):
        name, start = entries[i]
        end = entries[i + 1][1]
        fields, rows = parse_dbf_buffer(raw[start:end])
        tables[name] = {
            "table_name": name,
            "fields": fields,
            "row_count": len(rows),
            "rows": rows,
        }
    return tables


def build_industry_supply_chain_crosswalk(industries: dict, caplab_tables: dict) -> dict:
    """
    Constructs the deterministic crosswalk linking all 70 WSR Industries (1..70)
    to Capitalism Lab's 29 Product Classes, 135 Products, 99 Manufacturing Recipes,
    20 Software Types, 38 R&D Tech Nodes, 9 Natural Resources, and 48 Firm Types.
    """
    products_by_class = {}
    for p in caplab_tables["PRODUCT_TYPES"]["rows"]:
        products_by_class.setdefault(p["CLASS"], []).append(p["CODE"])

    recipes_by_output = {}
    for r in caplab_tables["MANUFACTURING"]["rows"]:
        recipes_by_output[r["OUTPUT"]] = r

    software_all = [s["CODE"] for s in caplab_tables["SOFTWARE_TYPES"]["rows"]]
    tech_all = [t["CODE"] for t in caplab_tables["TECH"]["rows"]]

    # Explicit mapping configuration per WSR Industry ID (1..70)
    SPEC = {
        1:  ("BANKING", ["BANK_HQ", "BANK_BR", "INVEST"], [], [], [], [], []),
        2:  ("INSURANCE", ["INSUR_HQ", "INSUR_BR"], [], [], [], [], []),
        3:  ("MANUFACTURING", ["FACTORY", "RD", "RETAIL"], ["AUTO"], ["AUTO", "SEMI"], ["CAR", "MOTORCYC", "ENGINE", "CAR_BODY", "WHEEL_T"], ["AIR_ALU_B", "LITHIUM_B", "GPS_NAV"], []),
        4:  ("MANUFACTURING", ["RD", "FACTORY"], ["DRUG"], ["DRUGS", "BODYCARE"], [], ["HEART_RATE", "FINGERPRIN", "DEEP_LEARN"], ["CHEMICAL"]),
        5:  ("REAL_ESTATE_CONSTRUCTION", ["APARTMEN", "COMMERCI", "MALL", "MANSION"], [], ["FURN", "HOUSE"], [], [], ["TIMBER"]),
        6:  ("MANUFACTURING", ["FACTORY", "MINE", "FOREST"], ["FURNITUR"], ["RAW", "SEMI", "FURN"], ["TIMBER", "GLASS", "STEEL", "PLASTIC", "DYESTUFF"], [], ["TIMBER", "SILICA", "IRON"]),
        7:  ("EXTRACTION_ENERGY", ["OIL", "FACTORY", "MINE"], [], ["RAW", "SEMI"], ["OIL", "PLASTIC", "POLYESTE", "CHEMICAL"], ["WIND_TURB"], ["OIL", "COAL", "CHEMICAL"]),
        8:  ("EXTRACTION_ENERGY", ["OIL", "MINE", "FACTORY"], [], ["RAW", "SEMI"], ["OIL", "STEEL"], ["WIND_TURB"], ["OIL", "COAL"]),
        9:  ("EXTRACTION_ENERGY", ["MINE", "FACTORY"], [], ["RAW", "SEMI"], ["IRON", "ALUMINIU", "COAL", "SILICA", "STEEL"], [], ["IRON", "ALUMINIU", "COAL", "SILICA"]),
        10: ("MANUFACTURING", ["FACTORY", "RD", "RETAIL"], ["ELECTRON"], ["ELECTRON", "PHOTO", "WATCH"], [], ["TOUCH_SCR", "DIGITPHOTO", "3D_RENDER", "VR", "AUGMENTED", "MOTIONSEN", "LITHIUM_B"], ["SILICA"]),
        11: ("TRANSPORT_LOGISTICS", ["LOGIST", "WAREHOUS"], [], ["RAW", "SEMI"], ["COAL", "STEEL", "TIMBER"], ["GPS_NAV"], ["COAL", "IRON"]),
        12: ("MANUFACTURING", ["FACTORY", "MINE"], [], ["RAW", "SEMI"], ["STEEL", "IRON", "COAL", "ALUMINIU"], [], ["IRON", "COAL", "ALUMINIU"]),
        13: ("MANUFACTURING", ["FACTORY", "RD"], [], ["SEMI", "HOMEAPP"], ["STEEL", "ENGINE", "EL_COMP", "COMPRESS"], ["WIND_TURB", "AIR_ALU_B"], ["IRON", "ALUMINIU"]),
        14: ("MANUFACTURING", ["FACTORY", "RD"], [], ["AUTO", "ELECTRON", "COMMUN"], ["ENGINE", "EL_COMP", "CPU", "CCD"], ["GPS_NAV", "QUANTUMCO", "MOTIONSEN", "VR", "AUGMENTED"], ["ALUMINIU", "SILICA"]),
        15: ("AGRIBUSINESS", ["FARM", "FACTORY", "WAREHOUS"], ["SUPERMAR"], ["PLANT", "PSEMI", "LSTOCK", "LSEMI", "LPRODUCT", "FOOD"], [], [], []),
        16: ("TRANSPORT_LOGISTICS", ["LOGIST", "WAREHOUS", "IMPORT", "EXPORT"], [], ["SEMI"], ["OIL", "ENGINE"], ["GPS_NAV", "CLOUD_COMP"], ["OIL"]),
        17: ("MANUFACTURING", ["FACTORY", "FARM"], ["SUPERMAR", "CONVENIE"], ["BEVERAGE", "PLANT"], ["WINE", "SPIRITS", "GRAPE", "SUGAR", "WHEAT", "BOTTLE"], [], ["SILICA"]),
        18: ("MANUFACTURING", ["FACTORY", "FARM"], ["AUTO"], ["SEMI", "AUTO", "PLANT"], ["RUBBER", "WHEEL_T", "CAR", "MOTORCYC"], [], []),
        19: ("MANUFACTURING", ["FACTORY", "FARM"], ["APPAREL"], ["APPAREL", "LEATHER", "PSEMI"], ["BLAZER", "JACKET", "JEAN", "SWEATER", "COTTON", "WOOL", "TEXTILE", "LEATHER", "FLAXFIBR"], [], []),
        20: ("MANUFACTURING", ["MINE", "OIL", "FACTORY"], [], ["RAW", "SEMI"], ["CHEMICAL", "PLASTIC", "POLYESTE", "DYESTUFF", "GLASS"], [], ["CHEMICAL", "OIL", "SILICA"]),
        21: ("MANUFACTURING", ["FACTORY", "RD", "RETAIL"], ["DRUG"], ["DRUGS"], ["COUGH_SY", "HEADACHE", "HERBAL_M", "COLD_MED", "NASAL_SP", "THROAT_L", "VITAMIN", "ANTIBIOT"], ["HEART_RATE"], ["CHEMICAL"]),
        22: ("MANUFACTURING", ["FACTORY", "RD"], ["DRUG"], ["DRUGS", "BODYCARE", "PHOTO"], ["GLASSES", "FIRSTAID", "THERMOME", "BANDAGE"], ["HEART_RATE", "FITNESS_TR", "FINGERPRIN"], ["SILICA", "PLASTIC"]),
        23: ("TRANSPORT_LOGISTICS", ["LOGIST", "IMPORT", "EXPORT", "WAREHOUS"], [], ["RAW", "SEMI"], ["OIL", "STEEL", "COAL", "TIMBER"], ["GPS_NAV"], ["OIL"]),
        24: ("MANUFACTURING", ["FACTORY", "RD", "RETAIL"], ["COMPUTER"], ["COMPUTER"], ["DESKTOP", "NOTEBOOK", "TABLET", "SERVER", "CPU", "SSD"], ["SSD", "QUANTUMCO", "CLOUD_COMP", "DESKTOP_UI", "TOUCH_SCR"], ["SILICA"]),
        25: ("TRANSPORT_LOGISTICS", ["LOGIST", "WAREHOUS"], [], ["AUTO", "SEMI"], ["CAR", "ENGINE", "WHEEL_T", "OIL"], ["GPS_NAV"], ["OIL"]),
        26: ("SOFTWARE_DIGITAL", ["SOFTWARE", "RD", "ACCEL"], [], ["COMPUTER"], [], ["CLOUD_COMP", "DEEP_LEARN", "BIG_DATA", "DATA_MINE", "Desktop_UI", "MOBILE_UI", "WEB_UI", "VOICE_RECO", "SPEECH_SYN", "TRANSLAT", "PHOTO_EDIT", "VIDEO_EDIT", "3D_RENDER"], [], software_all),
        27: ("TELECOM_MEDIA", ["PUBLISH", "INTERNET"], [], ["SEMI"], ["PAPER", "WOODPULP", "BOOK", "MAGAZINE"], ["WEB_UI", "AD_ENGINE", "TRANSLAT"], ["TIMBER"]),
        28: ("MANUFACTURING", ["FACTORY", "FARM"], ["SUPERMAR", "CONVENIE"], ["FOOD", "SNACKS", "LPRODUCT", "PSEMI"], [], [], []),
        29: ("TELECOM_MEDIA", ["TV", "RADIO", "INTERNET"], [], ["TOY", "ELECTRON"], ["VIDEO_G", "HANDGAME", "TV_SET", "HIFI"], ["VIDEO_ST", "AUDIO_ST", "VR", "3D_RENDER", "VIDEO_EDIT"], []),
        30: ("TELECOM_MEDIA", ["TELECOM", "INTERNET", "RD"], [], ["COMMUN"], ["SMARTPHO", "MOBILE_P"], ["3G_TELECOM", "4G_TELECOM", "CLOUD_COMP", "VIDEO_CHAT", "MOBILE_PAY"], []),
        31: ("MANUFACTURING", ["FACTORY", "FARM"], ["CONVENIE", "SUPERMAR"], ["TOBACCO", "PLANT"], ["CIGARET", "CIGARS", "TOBACCO", "PAPER"], [], []),
        32: ("MANUFACTURING", ["FACTORY", "RD", "RETAIL"], ["COSMETIC", "SUPERMAR"], ["BODYCARE", "COSMETIC", "HOUSE"], [], [], ["CHEMICAL"]),
        33: ("MANUFACTURING", ["FOREST", "FACTORY"], ["SUPERMAR"], ["RAW", "SEMI", "HOUSE"], ["TIMBER", "WOODPULP", "PAPER", "TISSUE", "DIAPERS"], [], ["TIMBER"]),
        34: ("MANUFACTURING", ["FACTORY", "FARM"], ["SUPERMAR", "CONVENIE"], ["BEVERAGE"], ["COLA", "B_MILK", "G_JUICE", "O_JUICE", "WINE", "SPIRITS", "CAN_COFF", "GREEN_T", "ENERG_DR"], [], []),
        35: ("MANUFACTURING", ["FACTORY", "RD"], ["COMPUTER", "ELECTRON"], ["SEMI", "COMPUTER", "ELECTRON", "COMMUN"], ["CPU", "EL_COMP", "CCD", "LCD", "SILICA", "SSD"], ["SSD", "QUANTUMCO", "TOUCH_SCR", "FINGERPRIN", "MOTIONSEN", "DEEP_LEARN"], ["SILICA", "GOLD", "SILVER"]),
        36: ("TELECOM_MEDIA", ["TV", "RADIO", "PUBLISH", "INTERNET"], [], [], [], ["AD_ENGINE", "BIG_DATA", "DATA_MINE", "SOCIAL_NET", "WEB_UI"], []),
        37: ("SECURITIES_HOLDING", ["INVEST", "BANK_HQ", "BANK_BR"], [], [], [], ["BIG_DATA", "DATA_MINE", "QUANTUMCO", "MOBILE_PAY"], []),
        38: ("MANUFACTURING", ["FACTORY", "RD"], ["COMPUTER", "FURNITUR"], ["COMPUTER", "FURN", "SEMI"], ["PRINTER", "DESKTOP", "SERVER", "PAPER", "CHAIR", "DESK"], ["DESKTOP_UI", "CLOUD_COMP", "HANDWRITE"], ["TIMBER", "SILICA"]),
        39: ("SOFTWARE_DIGITAL", ["INTERNET", "SOFTWARE", "RD", "ACCEL"], [], [], [], ["SEARCH_EN", "SOCIAL_NET", "VIDEO_ST", "AUDIO_ST", "CLOUD_COMP", "AD_ENGINE", "WEB_UI", "MOBILE_PAY", "CROWD-SOU", "VIDEO_CHAT", "BIG_DATA", "DEEP_LEARN"], [], ["SAVIRUS", "SENCRYPT", "SINTSEC", "SDB"]),
        40: ("MANUFACTURING", ["FACTORY", "RD"], ["COMPUTER"], ["COMPUTER", "PHOTO", "ELECTRON"], ["PRINTER", "CAMCORDE", "DCAMERA", "SSD", "LCD"], ["SSD", "TOUCH_SCR", "DIGITPHOTO", "3D_RENDER", "VR"], ["SILICA", "PLASTIC"]),
        41: ("RETAIL", ["RETAIL", "MALL"], ["JEWELRY", "COSMETIC", "LEATHER", "TOY", "ELECTRON"], ["JEWELRY", "WATCH", "COSMETIC", "LEATHER", "TOY", "PHOTO"], [], [], []),
        42: ("RETAIL", ["RETAIL", "MALL"], ["DEPARTME", "GENSTORE"], ["APPAREL", "HOMEAPP", "HOUSE", "FURN", "ELECTRON", "COSMETIC", "LEATHER", "WATCH"], [], [], []),
        43: ("RETAIL", ["RETAIL"], ["DRUG", "COSMETIC"], ["DRUGS", "BODYCARE", "COSMETIC"], [], [], []),
        44: ("RETAIL", ["RETAIL", "PUBLISH"], ["GENSTORE", "DEPARTME"], ["SEMI", "TOY"], ["PAPER", "WOODPULP", "VIDEO_G", "HANDGAME"], ["WEB_UI", "SEARCH_EN"], []),
        45: ("RETAIL", ["RETAIL"], ["SPORT", "FOOTWEAR"], ["SPORT_EQ", "FOOTWEAR", "APPAREL"], ["BACKPACK", "GOLFCLUB", "SKATES", "TENNIS_R", "SOCCER_B", "S_SHOE", "S_WATCH"], ["FITNESS_TR", "HEART_RATE"], []),
        46: ("RETAIL", ["RETAIL"], ["SUPERMAR", "CONVENIE"], ["FOOD", "BEVERAGE", "SNACKS", "LPRODUCT", "HOUSE", "BODYCARE", "TOBACCO"], [], [], []),
        47: ("RETAIL", ["RETAIL", "MALL"], ["APPAREL", "FOOTWEAR", "LEATHER"], ["APPAREL", "FOOTWEAR", "LEATHER"], [], [], []),
        48: ("RETAIL", ["RETAIL", "MALL"], ["DISCOUNT", "SUPERMAR", "GENSTORE"], ["HOUSE", "FOOD", "BEVERAGE", "SNACKS", "APPAREL", "BODYCARE", "HOMEAPP", "TOY"], [], [], []),
        49: ("MANUFACTURING", ["FACTORY", "RD"], ["ELECTRON"], ["HOMEAPP", "SEMI", "ELECTRON"], ["EL_COMP", "COMPRESS", "ENGINE", "AIR_COND", "REFRIG", "WASHING", "LIGHT_B"], ["AIR_ALU_B", "LITHIUM_B", "WIND_TURB"], ["ALUMINIU", "IRON", "SILICA"]),
        50: ("EXTRACTION_ENERGY", ["MINE", "FACTORY", "RETAIL"], ["JEWELRY"], ["RAW", "JEWELRY", "WATCH"], ["GOLD", "SILVER", "GOLD_R", "SILVER_N", "BRACELET", "EARRINGS", "PENDANT", "E_WATCH", "SILWATCH"], [], ["GOLD", "SILVER"]),
        51: ("MANUFACTURING", ["FACTORY", "RD", "MINE"], ["COSMETIC", "DRUG"], ["SEMI", "COSMETIC", "BODYCARE", "PHOTO"], ["CHEMICAL", "DYESTUFF", "PLASTIC", "POLYESTE", "PERFUME", "HAIR_COL", "LIPSTICK", "SKIN_CR"], ["LITHIUM_B", "AIR_ALU_B"], ["CHEMICAL", "OIL"]),
        52: ("TRANSPORT_LOGISTICS", ["LOGIST", "WAREHOUS", "IMPORT", "EXPORT"], [], ["SEMI"], ["OIL", "PAPER"], ["GPS_NAV", "CLOUD_COMP", "MOBILE_PAY"], ["OIL"]),
        53: ("MANUFACTURING", ["FACTORY", "RD"], ["AUTO"], ["AUTO", "SEMI"], ["CAR", "MOTORCYC", "BICYCLE", "ENGINE", "CAR_BODY", "STEEL"], ["AIR_ALU_B", "LITHIUM_B", "GPS_NAV"], ["IRON", "ALUMINIU"]),
        54: ("MANUFACTURING", ["FACTORY", "MINE"], [], ["SEMI", "AUTO"], ["STEEL", "ENGINE", "CAR_BODY", "COMPRESS", "IRON", "ALUMINIU"], ["WIND_TURB"], ["IRON", "COAL", "ALUMINIU"]),
        55: ("MANUFACTURING", ["FACTORY", "RD"], ["AUTO"], ["SEMI", "AUTO"], ["ENGINE", "CAR_BODY", "WHEEL_T", "EL_COMP", "GLASS", "STEEL", "RUBBER"], ["GPS_NAV", "LITHIUM_B", "AIR_ALU_B"], ["IRON", "ALUMINIU", "SILICA"]),
        56: ("HEALTHCARE_SERVICE", ["SERVICE", "RD", "RETAIL"], ["DRUG"], ["DRUGS", "BODYCARE"], [], ["HEART_RATE", "FITNESS_TR", "DEEP_LEARN", "BIG_DATA"], []),
        57: ("HOSPITALITY_RESTAURANT", ["SERVICE", "RETAIL", "FARM"], ["SUPERMAR", "CONVENIE"], ["FOOD", "BEVERAGE", "SNACKS", "LPRODUCT"], ["BURGER", "PIZZA", "CAKE", "ICE_CREA", "COLA", "CAN_COFF", "BREAD", "CHOC_BAR"], ["MOBILE_PAY", "CROWD-SOU"], []),
        58: ("MANUFACTURING", ["FACTORY", "RD", "RETAIL"], ["TOY", "SPORT"], ["TOY", "SPORT_EQ", "PHOTO"], ["TOY_CAR", "TOY_DOLL", "VIDEO_G", "HANDGAME", "BICYCLE", "GOLFCLUB", "SKATES", "BACKPACK", "DCAMERA", "CAMCORDE"], ["3D_RENDER", "VR", "AUGMENTED", "MOTIONSEN", "DIGITPHOTO", "FITNESS_TR"], ["PLASTIC"]),
        59: ("HOSPITALITY_RESTAURANT", ["COMMERCI", "APARTMEN", "MALL", "SERVICE"], [], ["BEVERAGE", "FOOD", "LUXURY"], ["WINE", "SPIRITS", "CIGARS"], ["MOBILE_PAY", "WEB_UI"], []),
        60: ("MANUFACTURING", ["FACTORY", "RETAIL"], ["FURNITUR", "ELECTRON", "DEPARTME"], ["FURN", "HOMEAPP", "HOUSE"], [], [], ["TIMBER", "IRON", "ALUMINIU"]),
        61: ("TELECOM_MEDIA", ["TELECOM", "FACTORY", "RD"], ["ELECTRON", "COMPUTER"], ["COMMUN", "COMPUTER"], ["SMARTPHO", "MOBILE_P", "SERVER", "CPU", "EL_COMP"], ["3G_TELECOM", "4G_TELECOM", "CLOUD_COMP", "TOUCH_SCR", "MOBILE_UI", "VOICE_RECO", "FINGERPRIN", "GPS_NAV"], ["SILICA"]),
        62: ("SOFTWARE_DIGITAL", ["SOFTWARE", "SERVICE", "RD"], [], ["ELECTRON"], ["CAMCORDE", "EL_COMP"], ["FINGERPRIN", "VOICE_RECO", "HANDWRITE", "CLOUD_COMP", "BIG_DATA"], [], ["SAVIRUS", "SENCRYPT", "SINTSEC", "SBACKUP", "SDIAG"]),
        63: ("REAL_ESTATE_CONSTRUCTION", ["COMMERCI", "APARTMEN", "MALL", "FACTORY"], [], ["RAW", "SEMI", "FURN"], ["STEEL", "TIMBER", "GLASS"], [], ["IRON", "TIMBER", "SILICA"]),
        64: ("UTILITIES_ENV", ["FACTORY", "RD", "MINE"], [], ["RAW", "SEMI"], ["CHEMICAL", "PLASTIC", "PAPER", "STEEL"], ["WIND_TURB", "AIR_ALU_B", "LITHIUM_B"], ["COAL", "CHEMICAL"]),
        65: ("TELECOM_MEDIA", ["TV", "TELECOM", "INTERNET"], [], ["ELECTRON", "COMMUN"], ["TV_SET", "HIFI"], ["VIDEO_ST", "AUDIO_ST", "3G_TELECOM", "4G_TELECOM", "WEB_UI", "AD_ENGINE"], []),
        66: ("MANUFACTURING", ["FACTORY", "RETAIL"], ["FOOTWEAR", "SPORT"], ["FOOTWEAR", "LEATHER"], ["L_SHOE", "M_SHOE", "S_SHOE", "SLIPPERS", "LEATHER", "RUBBER", "TEXTILE"], ["FITNESS_TR"], []),
        67: ("MANUFACTURING", ["FACTORY", "RD", "RETAIL"], ["AUTO"], ["AUTO", "SEMI"], ["CAR", "MOTORCYC", "ENGINE", "CAR_BODY", "WHEEL_T"], ["AIR_ALU_B", "LITHIUM_B", "GPS_NAV"], ["IRON", "ALUMINIU"]),
        68: ("MANUFACTURING", ["FACTORY", "RD", "RETAIL"], ["AUTO"], ["AUTO", "SEMI"], ["CAR", "MOTORCYC", "BICYCLE", "ENGINE", "CAR_BODY", "WHEEL_T"], ["AIR_ALU_B", "LITHIUM_B", "GPS_NAV"], ["IRON", "ALUMINIU"]),
        69: ("UTILITIES_ENV", ["OIL", "MINE", "FACTORY"], [], ["RAW"], ["OIL", "COAL"], ["WIND_TURB", "AIR_ALU_B", "LITHIUM_B"], ["COAL", "OIL"]),
        70: ("SECURITIES_HOLDING", ["HQ", "INVEST", "BANK_HQ", "COMMERCI", "MALL"], ["DEPARTME", "DISCOUNT"], ["AUTO", "ELECTRON", "COMPUTER", "FOOD", "BEVERAGE", "APPAREL", "DRUGS"], [], tech_all[:10], [], software_all[:5]),
        71: ("ETF_FUND", ["INVEST", "STOCK"], [], [], [], [], []),
    }

    valid_products = {p["CODE"] for p in caplab_tables["PRODUCT_TYPES"]["rows"]}
    valid_tech = set(tech_all)
    valid_soft = set(software_all)

    crosswalk = {}
    for ind_id in range(1, 72):
        ind_info = industries.get(ind_id, {"name": f"INDUSTRY_{ind_id}", "growth_rate_pct": 5, "volatility_pct": 5})
        entry_tuple = SPEC[ind_id]
        archetype = entry_tuple[0]
        firm_types = entry_tuple[1]
        retail_stores = entry_tuple[2]
        prod_classes = entry_tuple[3]
        explicit_prods = entry_tuple[4]
        tech_codes = [t for t in entry_tuple[5] if t in valid_tech]
        nat_res = entry_tuple[6]
        soft_codes = [s for s in (entry_tuple[7] if len(entry_tuple) > 7 else []) if s in valid_soft]

        # Collect all valid product codes from both explicit list and mapped product classes
        prod_set = []
        for pc in explicit_prods:
            if pc in valid_products and pc not in prod_set:
                prod_set.append(pc)
        for pcls in prod_classes:
            for pc in products_by_class.get(pcls, []):
                if pc not in prod_set:
                    prod_set.append(pc)

        recipe_codes = [pc for pc in prod_set if pc in recipes_by_output]

        crosswalk[str(ind_id)] = {
            "wsr_industry_id": ind_id,
            "wsr_industry_name": ind_info["name"],
            "sector_archetype": archetype,
            "base_growth_rate_pct": ind_info["growth_rate_pct"],
            "base_volatility_pct": ind_info["volatility_pct"],
            "primary_firm_types": firm_types,
            "retail_store_codes": retail_stores,
            "product_classes": prod_classes,
            "product_codes": prod_set,
            "manufacturing_recipe_outputs": recipe_codes,
            "software_codes": soft_codes,
            "tech_codes": tech_codes,
            "natural_resources": nat_res,
        }

    return crosswalk


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    countries, corporations = parse_wsr_corpname(os.path.join(WSR_DIR, "CORPNAME.DAT"))
    industries = parse_wsr101(os.path.join(WSR_DIR, "wsr101.dat"), corporations)
    mscnews_items = parse_wsr_mscnews(os.path.join(WSR_DIR, "Mscnews.dat"))
    quotes = parse_wsr_quotes(os.path.join(WSR_DIR, "quotewsr.dat"))
    caplab_tables = parse_caplab_1std_set(os.path.join(CL_DIR, "gameset", "1STD.SET"))
    crosswalk = build_industry_supply_chain_crosswalk(industries, caplab_tables)

    firm_dir = os.path.join(CL_DIR, "firm")
    bld_files = []
    for fn in sorted(os.listdir(firm_dir)):
        if fn.upper().endswith(".BLD"):
            fp = os.path.join(firm_dir, fn)
            bld_files.append({"filename": fn, "code": os.path.splitext(fn)[0], "size_bytes": os.path.getsize(fp)})

    active_corps = sum(1 for c in corporations.values() if c.get("initial_state", {}).get("status") == 1)
    cross_links = sum(len(c.get("subsidiaries", [])) for c in corporations.values())

    master_db = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "wsr_source_dir": WSR_DIR,
            "caplab_source_dir": CL_DIR,
            "summary": {
                "wsr_countries": len(countries),
                "wsr_industries": len(industries),
                "wsr_total_corporations": len(corporations),
                "wsr_active_initial_corporations": active_corps,
                "wsr_cross_ownership_links": cross_links,
                "wsr_mscnews_items": len(mscnews_items),
                "wsr_quotes": len(quotes),
                "caplab_dbf_tables": len(caplab_tables),
                "caplab_products": caplab_tables.get("PRODUCT_TYPES", {}).get("row_count", 0),
                "caplab_manufacturing_recipes": caplab_tables.get("MANUFACTURING", {}).get("row_count", 0),
                "caplab_building_specs": caplab_tables.get("FBUILDSTD", {}).get("row_count", 0),
                "caplab_firm_types": caplab_tables.get("FIRM", {}).get("row_count", 0),
                "caplab_software_types": caplab_tables.get("SOFTWARE_TYPES", {}).get("row_count", 0),
                "caplab_tech_nodes": caplab_tables.get("TECH", {}).get("row_count", 0),
                "caplab_cities": caplab_tables.get("CITIES", {}).get("row_count", 0),
                "caplab_ai_persons": caplab_tables.get("PERSONS", {}).get("row_count", 0),
                "caplab_bld_files": len(bld_files),
                "crosswalk_industries_mapped": len(crosswalk),
            },
        },
        "wsr": {
            "countries": countries,
            "industries": industries,
            "corporations": corporations,
            "mscnews_items": mscnews_items,
            "quotes": quotes,
        },
        "capitalism_lab": {
            "tables": caplab_tables,
            "bld_files": bld_files,
        },
        "industry_supply_chain_crosswalk": crosswalk,
    }

    out_path = os.path.join(OUT_DIR, "eagle_wsr_caplab_db.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(master_db, f, indent=2, ensure_ascii=False)

    print("=== EagleCapitalEngine Phase A1/A2 Database & Crosswalk Extraction Complete ===")
    print(f"Saved unified DB to: {out_path} ({os.path.getsize(out_path):,} bytes)")
    for k, v in master_db["metadata"]["summary"].items():
        print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()

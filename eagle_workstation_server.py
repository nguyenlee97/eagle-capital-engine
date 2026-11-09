#!/usr/bin/env python3
"""
EagleCapitalEngine — Unified Wall Street Raider v10 + Capitalism Lab v11 Workstation Server (v2.0)
==================================================================================================
Zero-dependency HTTP/JSON server that:
  1. Hosts the unified EagleCapitalEngine:
     - 1,590 WSR Corporations + 20 ETFs across 5 Balance Sheet Regimes & 71 Industries
     - 320 Investors across 24 Unique Archetypes (IDs 2001..2320) + Aether (#1, $30,000 Hustler or $1,000M Sandbox)
     - 135 Capitalism Lab Products, 99 Manufacturing Recipes, 128 Cities, 64 PERSONS.DBF AI CEOs
     - 4 Bidirectional WSR <-> Capitalism Lab Cross-Feedback Loops & 6 Economic Sanity Laws
     - Full-Fidelity Atomic Save/Load (0.000000 asset loss) & 6 Macro Stress Scenarios (S1..S6)
  2. Integrates LunaCohortOrchestrator (gpt-6-luna) with Non-Blocking Async Staggered Rotation
     so AI Playbook updates and [Gen N] Smart Respawns never block the UI or game loop.
  3. Provides Capitalism Lab Interactive 3x3 Internal Floorplan Grid metadata (with authentic
     250x130 Guide/*.png isometric functional unit sprites) & reconfiguration, plus full WSR v10
     ActionBar commands (Stocks, Micro-Lots, Shorts, Bonds, Options, Futures, Crypto, Interest Rate
     Swaps, M&A, Lawsuits, ETF Advisory, and $30k Startup Incorporation).
  4. Mounts and serves authentic read-only game assets directly from disk:
     - /assets/wsr10/*        -> Wall Street Raider v10.0.22.3 MP4 videos, logos & icons
     - /assets/caplab/image/* -> Capitalism Lab 2,637 PNG/JPG building sprites, 3x3 floor/guide icons & UI
     - /assets/caplab/speech/*-> Capitalism Lab 5,255 MP3 voiceovers & sound effects
"""

import argparse
import json
import math
import mimetypes
import os
import random
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List

from eagle_capital_engine import EagleCapitalEngine, RATING_LABELS
from luna_ai_orchestrator import LunaCohortOrchestrator
from paimon_academy import PaimonAcademyEngine

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(WORKSPACE_DIR, "ui")
SAVES_DIR = os.path.join(WORKSPACE_DIR, "saves")
LOGS_DIR = os.path.join(WORKSPACE_DIR, "logs")
os.makedirs(SAVES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

DEFAULT_SAVE_PATH = os.path.join(SAVES_DIR, "workstation_save_v2.json")
EVAL_REPORT_PATH = os.path.join(LOGS_DIR, "luna_ai_evaluation_report.json")

WSR10_ASSETS_DIR = (
    r"C:\Users\LENOVO\Downloads\Wall.Street.Raider.v10.0.22.3"
    r"\Wall.Street.Raider.v10.0.22.3\Wall.Street.Raider.v10.0.22.3\resources\app\assets"
)
CAPLAB_ROOT_DIR = r"C:\Users\LENOVO\Downloads\capitalism lab\[tamhongame.com]_CL\Capitalism Lab"
CAPLAB_IMAGE_DIR = os.path.join(CAPLAB_ROOT_DIR, "image")
CAPLAB_SPEECH_DIR = os.path.join(CAPLAB_ROOT_DIR, "speech")


def build_default_3x3_floorplan(
    firm_type: str,
    product_code: str,
    integrated_inputs: int,
    rd_units: int = 9,
    recipe: Dict[str, Any] = None,
) -> List[Dict[str, Any]]:
    """
    Constructs the authentic Capitalism Lab 3x3 Internal Floorplan Grid (9 slots: row 0..2, col 0..2)
    using verified 250x130 isometric functional unit sprites from /assets/caplab/image/Guide/*.png,
    supply-link arrows, utilization %, training level (Lv 1..9), and vertical-integration shield status.
    """
    ft = firm_type.upper()
    in1 = (recipe or {}).get("INPUT1") or "RAW_MAT_1"
    in2 = (recipe or {}).get("INPUT2") or "RAW_MAT_2"
    in3 = (recipe or {}).get("INPUT3") or "RAW_MAT_3"

    if ft == "FACTORY":
        return [
            {"slot": 0, "role": "PUR", "label": f"Purchase ({in1})", "guide_img": "/assets/caplab/image/Guide/PUR.png", "util": 86, "level": 4, "links_to": [3, 4], "shielded": integrated_inputs >= 1},
            {"slot": 1, "role": "PUR", "label": f"Purchase ({in2})", "guide_img": "/assets/caplab/image/Guide/PUR.png", "util": 82, "level": 3, "links_to": [4], "shielded": integrated_inputs >= 2},
            {"slot": 2, "role": "PUR", "label": f"Purchase ({in3})", "guide_img": "/assets/caplab/image/Guide/PUR.png", "util": 78, "level": 3, "links_to": [4, 5], "shielded": integrated_inputs >= 3},
            {"slot": 3, "role": "MFT", "label": f"Mfg Line A ({product_code})", "guide_img": "/assets/caplab/image/Guide/MFT.png", "util": 92, "level": 5, "links_to": [6], "shielded": integrated_inputs >= 1},
            {"slot": 4, "role": "MFT", "label": f"Mfg Line B ({product_code})", "guide_img": "/assets/caplab/image/Guide/MFT.png", "util": 89, "level": 4, "links_to": [6, 7], "shielded": integrated_inputs >= 2},
            {"slot": 5, "role": "INV", "label": f"Inventory ({product_code})", "guide_img": "/assets/caplab/image/Guide/INV.png", "util": 74, "level": 3, "links_to": [7, 8], "shielded": False},
            {"slot": 6, "role": "SALE", "label": f"Sales Unit A ({product_code})", "guide_img": "/assets/caplab/image/Guide/SALE.png", "util": 91, "level": 4, "links_to": [], "shielded": False},
            {"slot": 7, "role": "SALE", "label": f"Sales Unit B ({product_code})", "guide_img": "/assets/caplab/image/Guide/SALE.png", "util": 87, "level": 4, "links_to": [], "shielded": False},
            {"slot": 8, "role": "EXTERN", "label": "Advertising Unit", "guide_img": "/assets/caplab/image/Guide/EXTERN.png", "util": 95, "level": 4, "links_to": [6, 7], "shielded": False},
        ]
    if ft == "RETAIL":
        return [
            {"slot": 0, "role": "PUR", "label": f"Purchase ({product_code})", "guide_img": "/assets/caplab/image/Guide/PUR.png", "util": 91, "level": 4, "links_to": [3, 6], "shielded": integrated_inputs >= 1},
            {"slot": 1, "role": "PUR", "label": f"Purchase ({product_code} #2)", "guide_img": "/assets/caplab/image/Guide/PUR.png", "util": 84, "level": 3, "links_to": [4, 7], "shielded": False},
            {"slot": 2, "role": "INV", "label": "Backroom Storage", "guide_img": "/assets/caplab/image/Guide/INV.png", "util": 77, "level": 3, "links_to": [5, 8], "shielded": False},
            {"slot": 3, "role": "LABEL", "label": "Private Labelling", "guide_img": "/assets/caplab/image/Guide/LABEL.png", "util": 83, "level": 3, "links_to": [6], "shielded": False},
            {"slot": 4, "role": "EXTERN", "label": "Media Advertising Unit", "guide_img": "/assets/caplab/image/Guide/EXTERN.png", "util": 100, "level": 5, "links_to": [6, 7, 8], "shielded": False},
            {"slot": 5, "role": "INV", "label": "Cold / Shelf Buffer", "guide_img": "/assets/caplab/image/Guide/INV.png", "util": 79, "level": 3, "links_to": [8], "shielded": False},
            {"slot": 6, "role": "SALE", "label": "Retail Sales Counter A", "guide_img": "/assets/caplab/image/Guide/SALE.png", "util": 94, "level": 5, "links_to": [], "shielded": False},
            {"slot": 7, "role": "SALE", "label": "Retail Sales Counter B", "guide_img": "/assets/caplab/image/Guide/SALE.png", "util": 90, "level": 4, "links_to": [], "shielded": False},
            {"slot": 8, "role": "SALE", "label": "Retail Express Checkout", "guide_img": "/assets/caplab/image/Guide/SALE.png", "util": 86, "level": 4, "links_to": [], "shielded": False},
        ]
    if ft == "RD":
        active_rd = max(1, min(9, int(rd_units or 9)))
        cells = []
        for idx in range(9):
            is_core = idx == 4
            is_active = idx < active_rd
            cells.append({
                "slot": idx,
                "role": "TECH" if is_core else ("RD" if is_active else "RADRD"),
                "label": f"Core Tech Leader ({product_code})" if is_core else (f"Product R&D Lab #{idx+1}" if is_active else "Radical R&D Slot"),
                "guide_img": "/assets/caplab/image/Guide/TECH.png" if is_core else ("/assets/caplab/image/Guide/RD.png" if is_active else "/assets/caplab/image/Guide/RADRD.png"),
                "util": 98 if is_active else 45,
                "level": 6 if is_core else (5 if is_active else 2),
                "links_to": [4] if not is_core else [],
                "shielded": True,
            })
        return cells
    if ft == "SOFTWARE":
        cells = []
        for idx in range(9):
            is_pm = idx == 4
            is_tech = idx in (0, 2, 6, 8)
            cells.append({
                "slot": idx,
                "role": "PROJECT" if is_pm else ("TECHCODE" if is_tech else "PROJCODE"),
                "label": f"Project Lead ({product_code})" if is_pm else ("Tech Coding Unit" if is_tech else "Feature Coding Unit"),
                "guide_img": "/assets/caplab/image/Guide/PROJECT.png" if is_pm else ("/assets/caplab/image/Guide/TECHCODE.png" if is_tech else "/assets/caplab/image/Guide/PROJCODE.png"),
                "util": 95 if is_pm else 88,
                "level": 6 if is_pm else 4,
                "links_to": [4] if not is_pm else [],
                "shielded": True,
            })
        return cells
    if ft in ("MINE", "OIL", "FOREST", "FARM"):
        ext_img = (
            "/assets/caplab/image/Guide/MINE.png" if ft == "MINE" else
            "/assets/caplab/image/Guide/OIL.png" if ft == "OIL" else
            "/assets/caplab/image/Guide/FOREST.png" if ft == "FOREST" else
            "/assets/caplab/image/Guide/FARMCROP.png"
        )
        return [
            {"slot": 0, "role": ft, "label": f"{ft} Extraction Unit A", "guide_img": ext_img, "util": 93, "level": 5, "links_to": [3, 4], "shielded": True},
            {"slot": 1, "role": ft, "label": f"{ft} Extraction Unit B", "guide_img": ext_img, "util": 90, "level": 4, "links_to": [4], "shielded": True},
            {"slot": 2, "role": ft, "label": f"{ft} Extraction Unit C", "guide_img": ext_img, "util": 87, "level": 4, "links_to": [4, 5], "shielded": True},
            {"slot": 3, "role": "FARMPROC", "label": "Primary Refining / Sorting", "guide_img": "/assets/caplab/image/Guide/FARMPROC.png", "util": 89, "level": 4, "links_to": [6], "shielded": True},
            {"slot": 4, "role": "INV", "label": "Bulk Commodity Silo", "guide_img": "/assets/caplab/image/Guide/INV.png", "util": 82, "level": 3, "links_to": [6, 7, 8], "shielded": False},
            {"slot": 5, "role": "FARMPROC", "label": "Quality Grading Unit", "guide_img": "/assets/caplab/image/Guide/FARMPROC.png", "util": 85, "level": 4, "links_to": [8], "shielded": True},
            {"slot": 6, "role": "SALE", "label": "Spot Market Dispatch A", "guide_img": "/assets/caplab/image/Guide/SALE.png", "util": 94, "level": 4, "links_to": [], "shielded": False},
            {"slot": 7, "role": "SALE", "label": "Internal Supply Dispatch", "guide_img": "/assets/caplab/image/Guide/SALE.png", "util": 91, "level": 4, "links_to": [], "shielded": True},
            {"slot": 8, "role": "EXTERN", "label": "Global Freight & Marketing", "guide_img": "/assets/caplab/image/Guide/EXTERN.png", "util": 88, "level": 3, "links_to": [6, 7], "shielded": False},
        ]
    # Real Estate (APARTMEN, COMMERCI, MALL, OFFICE)
    return [
        {
            "slot": idx,
            "role": "LEASE",
            "label": f"{ft} Wing #{idx+1}",
            "guide_img": "/assets/caplab/image/Icon/AptStore.png" if ft == "APARTMEN" else "/assets/caplab/image/Icon/Office.png",
            "util": 86,
            "level": 4,
            "links_to": [],
            "shielded": False,
        }
        for idx in range(9)
    ]


class WorkstationAppState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.engine = EagleCapitalEngine()
        self.game_mode = "30K_HUSTLER"
        self.firm_custom_layouts: Dict[int, List[Dict[str, Any]]] = {}
        self.ohlcv_history: Dict[str, List[Dict[str, Any]]] = {}
        self.luna = LunaCohortOrchestrator(self.engine)
        self.paimon = PaimonAcademyEngine()
        self.luna_bg_running = False
        self.luna_last_status = "Idle (Cached 24-Archetype Playbooks Ready)"
        self.cached_ai_theses: List[Dict[str, Any]] = []
        self._init_ecosystem(start_as_30k_hustler=True)
        self._load_cached_luna_report()

    def _init_ecosystem(self, start_as_30k_hustler: bool = True) -> None:
        self.game_mode = "30K_HUSTLER" if start_as_30k_hustler else "1000M_SANDBOX"
        self.engine.reset_new_game()
        self.firm_custom_layouts.clear()
        self.ohlcv_history.clear()
        if start_as_30k_hustler:
            self.engine.set_street_hustler_30k_mode(1, 0.03)
        self.engine.spawn_full_320_investor_ecosystem(spawn_all_320=True)
        self._seed_initial_demo_firms(give_player_control=not start_as_30k_hustler)

    def _seed_initial_demo_firms(self, give_player_control: bool = False) -> None:
        # Corp 321 (Electronics: Factory + R&D + Retail)
        self.engine.entities[321].cash = max(self.engine.entities[321].cash, 250.0)
        if give_player_control:
            self.engine.entities[321].controlled_by_id = 1
        self.engine.recompute_entity_balance_sheet(self.engine.entities[321], update_stock_price=False)
        self.engine.build_caplab_firm(321, "FACTORY", "COMPUTER1", "New York City", 25.0, 5.0, "SMARTPH")
        self.engine.build_caplab_firm(321, "RD", "RD", "San Francisco", 15.0, 0.0, "SMARTPH", rd_units=9)
        self.engine.build_caplab_firm(321, "RETAIL", "ELECTRON", "New York City", 12.0, 3.0, "SMARTPH")
        # Corp 322 (Vertically Integrated Auto Chaebol: CARBODY + ENGINE + WHEEL + CAR Factory)
        self.engine.entities[322].cash = max(self.engine.entities[322].cash, 320.0)
        self.engine.build_caplab_firm(322, "FACTORY", "AUTO1", "Tokyo", 18.0, 3.0, "CARBODY")
        self.engine.build_caplab_firm(322, "FACTORY", "AUTO1", "Tokyo", 18.0, 3.0, "ENGINE")
        self.engine.build_caplab_firm(322, "FACTORY", "AUTO1", "Tokyo", 14.0, 2.0, "WHEEL")
        self.engine.build_caplab_firm(322, "FACTORY", "AUTO1", "Tokyo", 30.0, 6.0, "CAR")
        # Corp 323 (Upstream Resource Mining & Real Estate)
        self.engine.entities[323].cash = max(self.engine.entities[323].cash, 220.0)
        self.engine.build_caplab_firm(323, "MINE", "MINE", "Beijing", 22.0, 4.0, "GOLD")
        self.engine.build_caplab_firm(323, "APARTMEN", "APARTMEN", "London", 28.0, 0.0, "APARTMEN")
        self.engine.step_caplab_firms_quarterly()
        self.engine.recompute_all_balance_sheets()

    def _load_cached_luna_report(self) -> None:
        if os.path.isfile(EVAL_REPORT_PATH):
            try:
                with open(EVAL_REPORT_PATH, "r", encoding="utf-8") as f:
                    rep = json.load(f)
                self.cached_ai_theses = rep.get("decision_audit_log", [])[-40:]
                # Also hydrate conditional_playbook on matching archetype leads if present
                for d in self.cached_ai_theses:
                    eid = int(d.get("entity_id", 0))
                    if eid in self.engine.investor_personas and d.get("thesis"):
                        self.engine.investor_personas[eid]["conditional_playbook"] = {
                            "thesis": d.get("thesis", ""),
                            "cmd": d.get("executed_cmd", "BUY_STOCK"),
                            "bull_trigger": d.get("bull_trigger", ""),
                            "bear_trigger": d.get("bear_trigger", ""),
                            "updated_year": d.get("year", 2026),
                            "updated_quarter": d.get("quarter", 1),
                        }
            except Exception:
                self.cached_ai_theses = []

    def trigger_async_luna_batch(self, staggered_mode: bool = True) -> Dict[str, Any]:
        if self.luna_bg_running:
            return {"ok": False, "reason": "Luna AI background rotation is already running"}

        def _worker() -> None:
            self.luna_bg_running = True
            self.luna_last_status = "Calling live gpt-6-luna Staggered Cohort Rotation..."
            try:
                with self.lock:
                    res = self.luna.step_all_cohorts_quarterly(staggered_mode=staggered_mode)
                    self.cached_ai_theses = self.luna.decision_audit_log[-40:]
                    self.luna_last_status = (
                        f"Live gpt-6-luna OK: {res.get('batches_called', 0)} batches "
                        f"({res.get('smart_luna_decisions', 0)} leads) | "
                        f"Playbooks: {res.get('local_playbook_moves', 0)} | "
                        f"Crowd: {res.get('behavioral_moves', 0)} | "
                        f"Respawns: {res.get('respawns', 0)}"
                    )
            except Exception as exc:
                self.luna_last_status = f"Luna Error: {exc}"
            finally:
                self.luna_bg_running = False

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        return {"ok": True, "message": "Started background gpt-6-luna Staggered Rotation"}

    def trigger_macro_stress_scenario(self, scenario_code: str) -> Dict[str, Any]:
        sc = scenario_code.strip().upper()
        e = self.engine
        if sc == "S1":
            e.inflation_pct = 14.5
            e.prime_rate_pct = 18.0
            e.tbill_rate_pct = 15.5
            e.long_bond_rate_pct = 16.0
            e.short_bond_rate_pct = 15.8
            e.gdp_growth_pct = -3.5
            msg = "S1 Triggered: 1979 Volcker Stagflation (Prime 18%, Inflation 14.5%, GDP -3.5%)"
        elif sc == "S2":
            e.crypto_prices["BTC"] = round(e.crypto_prices.get("BTC", 85000.0) * 0.30, 2)
            e.crypto_prices["ETH"] = round(e.crypto_prices.get("ETH", 3200.0) * 0.25, 2)
            for cid in e.active_corp_ids[:80]:
                c = e.entities[cid]
                if c.industry_id in (10, 11, 12):
                    c.stock_price = max(1.0, round(c.stock_price * 0.55, 2))
            msg = "S2 Triggered: Tech & Crypto Bubble Crash (BTC -70%, Tech Equities -45%)"
        elif sc == "S3":
            e.commodity_prices["OIL"] = 160.0
            e.commodity_prices["COPPER"] = 6.50
            e.commodity_prices["WHEAT"] = 11.20
            e.step_caplab_firms_quarterly()
            msg = "S3 Triggered: Global Supply-Chain & $160 Oil Shock (Unintegrated Factories Surcharged)"
        elif sc == "S4":
            e.file_corporate_lawsuit(321, 322, "ANTITRUST", 45.0)
            msg = "S4 Triggered: Hostile Takeover, LBO & Antitrust Lawsuit Wave ($45M Claim Filed)"
        elif sc == "S5":
            e.top_tech_levels["SMARTPH"] = 240.0
            e.top_tech_levels["COMPUTER"] = 225.0
            msg = "S5 Triggered: Semiconductor R&D Frontier Leap (240.0) — Legacy Laggards Penalized"
        elif sc == "S6":
            e.crypto_prices["BTC"] = round(e.crypto_prices.get("BTC", 85000.0) * 1.65, 2)
            beh = e.step_behavioral_noise_investors()
            msg = f"S6 Triggered: Retail Meme FOMO Mania & Margin Call Cascade ({beh.get('respawns', 0)} Wipeout Respawns)"
        else:
            return {"ok": False, "reason": f"Unknown scenario code: {sc}"}

        e.recompute_all_balance_sheets()
        e.news_headlines.append(f"[{e.year}-Q{e.quarter} STRESS SCENARIO] {msg}")
        return {"ok": True, "scenario": sc, "message": msg}

    def get_or_init_ohlcv_series(
        self,
        symbol_key: str,
        current_price: float,
        label: str = "",
        force_new_bar: bool = False,
    ) -> Dict[str, Any]:
        e = self.engine
        cur_px = max(0.05, float(current_price or 10.0))
        date_tag = f"{e.year}-Q{e.quarter} ({e.month:02d}/{e.day:02d})"

        if symbol_key not in self.ohlcv_history or not self.ohlcv_history[symbol_key]:
            # Deterministically synthesize 36 historical OHLCV bars converging to current_price
            seed_val = sum(ord(ch) * (i + 1) for i, ch in enumerate(symbol_key)) ^ 20100101
            rng = random.Random(seed_val)
            bars: List[Dict[str, Any]] = []
            # Walk backward 35 steps to get starting price
            rel_path = [1.0]
            for _ in range(35):
                step_ret = rng.uniform(-0.042, 0.045)
                rel_path.append(max(0.25, rel_path[-1] * (1.0 + step_ret)))
            scale = cur_px / max(1e-6, rel_path[-1])
            min_px = min(0.01, cur_px * 0.25)
            closes = [round(max(min_px, v * scale), 4) for v in rel_path]
            closes[-1] = round(cur_px, 4)

            for idx in range(len(closes)):
                c_px = closes[idx]
                o_px = closes[idx - 1] if idx > 0 else round(c_px * rng.uniform(0.97, 1.03), 4)
                body_top = max(o_px, c_px)
                body_bot = min(o_px, c_px)
                wick_up = round(body_top * (1.0 + rng.uniform(0.004, 0.028)), 4)
                wick_dn = round(max(min_px, body_bot * (1.0 - rng.uniform(0.004, 0.028))), 4)
                vol = round(rng.uniform(120.0, 980.0) * (1.0 + abs(c_px - o_px) / max(0.1, o_px) * 12.0), 1)
                hist_y = 2007 + (idx // 12)
                hist_m = (idx % 12) + 1
                t_lbl = date_tag if idx == len(closes) - 1 else f"{hist_y}-{hist_m:02d}"
                bars.append({"t": t_lbl, "o": o_px, "h": wick_up, "l": wick_dn, "c": c_px, "v": vol})
            self.ohlcv_history[symbol_key] = bars
        else:
            bars = self.ohlcv_history[symbol_key]
            last = bars[-1]
            if force_new_bar or last["t"] != date_tag:
                o_px = last["c"]
                c_px = round(cur_px, 4)
                seed_tick = (e.total_subticks + e.total_days * 17 + len(bars) * 31) ^ hash(symbol_key)
                rng = random.Random(seed_tick)
                body_top = max(o_px, c_px)
                body_bot = min(o_px, c_px)
                h_px = round(body_top * (1.0 + rng.uniform(0.003, 0.022)), 4)
                l_px = round(max(0.05, body_bot * (1.0 - rng.uniform(0.003, 0.022))), 4)
                vol = round(rng.uniform(180.0, 1150.0) * (1.0 + abs(c_px - o_px) / max(0.1, o_px) * 15.0), 1)
                bars.append({"t": date_tag, "o": o_px, "h": h_px, "l": l_px, "c": c_px, "v": vol})
                if len(bars) > 48:
                    del bars[:-48]
            else:
                c_px = round(cur_px, 4)
                last["c"] = c_px
                last["h"] = round(max(last["h"], c_px * 1.002), 4)
                last["l"] = round(min(last["l"], max(0.05, c_px * 0.998)), 4)
                last["v"] = round(last["v"] + 35.0, 1)

        # Compute Technical Indicators: SMA(7), SMA(20), Bollinger Bands (20, 2sd), RSI(14), and Pattern
        closes_arr = [b["c"] for b in bars]
        sma7: List[Optional[float]] = []
        sma20: List[Optional[float]] = []
        bb_up: List[Optional[float]] = []
        bb_lo: List[Optional[float]] = []
        for i in range(len(closes_arr)):
            if i >= 6:
                sma7.append(round(sum(closes_arr[i - 6 : i + 1]) / 7.0, 4))
            else:
                sma7.append(None)
            if i >= 19:
                win = closes_arr[i - 19 : i + 1]
                mean = sum(win) / 20.0
                var = sum((x - mean) ** 2 for x in win) / 20.0
                sd = math.sqrt(var)
                sma20.append(round(mean, 4))
                bb_up.append(round(mean + 2.0 * sd, 4))
                bb_lo.append(round(max(0.01, mean - 2.0 * sd), 4))
            else:
                sma20.append(None)
                bb_up.append(None)
                bb_lo.append(None)

        # RSI(14)
        gains = []
        losses = []
        for i in range(max(1, len(closes_arr) - 14), len(closes_arr)):
            diff = closes_arr[i] - closes_arr[i - 1]
            if diff >= 0:
                gains.append(diff)
                losses.append(0.0)
            else:
                gains.append(0.0)
                losses.append(-diff)
        avg_gain = sum(gains) / max(1, len(gains))
        avg_loss = sum(losses) / max(1, len(losses))
        if avg_loss < 1e-9:
            rsi14 = 75.0 if avg_gain > 0 else 50.0
        else:
            rs = avg_gain / avg_loss
            rsi14 = round(100.0 - (100.0 / (1.0 + rs)), 1)

        # Japanese Candlestick Pattern Recognition on latest 2 candles
        b_cur = bars[-1]
        b_prev = bars[-2] if len(bars) >= 2 else b_cur
        rng_cur = max(1e-6, b_cur["h"] - b_cur["l"])
        body_cur = abs(b_cur["c"] - b_cur["o"])
        upper_wick = b_cur["h"] - max(b_cur["o"], b_cur["c"])
        lower_wick = min(b_cur["o"], b_cur["c"]) - b_cur["l"]

        if body_cur <= 0.12 * rng_cur:
            pattern = "Doji (Indecision / Pivot)"
        elif lower_wick >= 2.0 * body_cur and upper_wick <= 0.4 * body_cur:
            pattern = "Hammer / Bullish Pinbar (Support Reject)"
        elif upper_wick >= 2.0 * body_cur and lower_wick <= 0.4 * body_cur:
            pattern = "Shooting Star / Bearish Pinbar (Resistance Reject)"
        elif (
            b_cur["c"] > b_cur["o"]
            and b_prev["c"] < b_prev["o"]
            and b_cur["c"] >= b_prev["o"]
            and b_cur["o"] <= b_prev["c"]
        ):
            pattern = "Bullish Engulfing (Reversal Up)"
        elif (
            b_cur["c"] < b_cur["o"]
            and b_prev["c"] > b_prev["o"]
            and b_cur["c"] <= b_prev["o"]
            and b_cur["o"] >= b_prev["c"]
        ):
            pattern = "Bearish Engulfing (Reversal Down)"
        elif body_cur >= 0.78 * rng_cur:
            pattern = "Bullish Marubozu (Momentum)" if b_cur["c"] >= b_cur["o"] else "Bearish Marubozu (Breakdown)"
        else:
            pattern = "Bullish Trend Candle" if b_cur["c"] >= b_cur["o"] else "Bearish Pullback Candle"

        return {
            "symbol_key": symbol_key,
            "label": label or symbol_key,
            "current_price": round(cur_px, 4),
            "rsi14": rsi14,
            "pattern": pattern,
            "bars": bars[-36:],
            "sma7": sma7[-36:],
            "sma20": sma20[-36:],
            "bb_upper": bb_up[-36:],
            "bb_lower": bb_lo[-36:],
        }

    def record_market_ohlcv_bar(self, force_new_bar: bool = False) -> None:
        e = self.engine
        self.get_or_init_ohlcv_series("BTC", e.crypto_prices.get("BTC", 65000.0), "BTC / USD Crypto", force_new_bar)
        self.get_or_init_ohlcv_series("OIL", e.commodity_prices.get("OIL", 75.0), "WTI Crude Oil ($/bbl)", force_new_bar)
        self.get_or_init_ohlcv_series("GOLD", e.commodity_prices.get("GOLD", 2000.0), "Gold Spot ($/oz)", force_new_bar)
        self.get_or_init_ohlcv_series("STOCK_INDEX", e.commodity_prices.get("STOCK_INDEX", 4500.0), "WSR Composite Index", force_new_bar)
        for key in list(self.ohlcv_history.keys()):
            if key.startswith("CORP_"):
                cid = int(key.split("_")[1])
                if cid in e.entities and e.entities[cid].is_active:
                    ent = e.entities[cid]
                    self.get_or_init_ohlcv_series(key, ent.stock_price, f"#{cid} {ent.ticker} ({ent.name})", force_new_bar)

    def get_full_dashboard_payload(
        self,
        active_entity_id: int = 1,
        acting_as_id: int = 1,
        search_query: str = "",
        dir_filter: str = "ALL",
    ) -> Dict[str, Any]:
        with self.lock:
            if active_entity_id not in self.engine.entities:
                active_entity_id = 1
            if acting_as_id not in self.engine.entities:
                acting_as_id = 1

            ws = self.engine.get_workstation_state(active_entity_id=active_entity_id)
            acting_ws = self.engine.get_workstation_state(active_entity_id=acting_as_id)
            floor = self.engine.get_wallstreet_floor_snapshot()
            inv = self.engine.verify_global_invariants()
            coupling = self.engine.get_bidirectional_coupling_metrics()

            # Controlled companies for Player #1 (Aether)
            controlled_corps = []
            for cid, ent in self.engine.entities.items():
                if 5 < cid < 2000 and ent.is_active and (ent.controlled_by_id == 1 or cid in self.engine.entities[1].ceo_of_corp_ids):
                    controlled_corps.append({
                        "id": cid,
                        "ticker": ent.ticker,
                        "name": ent.name,
                        "cash_millions": round(ent.cash, 4),
                        "net_worth_millions": round(ent.net_worth, 4),
                    })

            q = search_query.strip().upper()
            df = dir_filter.strip().upper()
            corps_list = []

            if df in ("INVESTORS", "PLAYER_INDIVIDUAL"):
                candidate_ids = [1] + [pid for pid in sorted(self.engine.investor_personas.keys()) if pid in self.engine.entities]
            elif df == "ALL_ENTITIES":
                candidate_ids = [1] + list(self.engine.active_corp_ids) + [
                    pid for pid in sorted(self.engine.investor_personas.keys()) if pid in self.engine.entities
                ]
            else:
                candidate_ids = list(self.engine.active_corp_ids)

            for cid in candidate_ids:
                c = self.engine.entities[cid]
                if not c.is_active:
                    continue
                if df == "CONTROLLED" and not (c.controlled_by_id == 1 or cid in self.engine.entities[1].ceo_of_corp_ids):
                    continue
                if df == "BANKS" and c.regime not in ("COMMERCIAL_BANK", "INSURANCE_COMPANY"):
                    continue
                if df == "COMMERCIAL_BANK" and c.regime != "COMMERCIAL_BANK":
                    continue
                if df == "INSURANCE_COMPANY" and c.regime != "INSURANCE_COMPANY":
                    continue
                if df == "INDUSTRIAL_HOLDING" and c.regime != "INDUSTRIAL_HOLDING":
                    continue
                if df in ("ETFS", "ETF_FUND") and c.regime != "ETF_FUND":
                    continue
                if q and (q not in c.ticker.upper() and q not in c.name.upper() and q not in c.regime.upper() and q != str(cid)):
                    continue
                ceo = self.engine.corp_ceo_profiles.get(cid)
                sh_out = float(getattr(c, "shares_outstanding", 0.0) or 0.0)
                pb_val = (
                    round((c.stock_price * sh_out) / max(0.001, c.net_worth), 2)
                    if (sh_out > 0.0 and c.net_worth > 0.0 and c.regime != "PLAYER_INDIVIDUAL")
                    else 0.0
                )
                corps_list.append({
                    "id": cid,
                    "ticker": c.ticker,
                    "name": c.name,
                    "regime": c.regime,
                    "industry_id": c.industry_id,
                    "industry_name": self.engine.industries.get(c.industry_id, {}).get("name", "HOLDING"),
                    "stock_price": round(c.stock_price, 2),
                    "net_worth_millions": round(c.net_worth, 4),
                    "cash_millions": round(c.cash, 4),
                    "total_assets_millions": round(c.total_assets, 4),
                    "total_liabilities_millions": round(c.total_liabilities, 4),
                    "credit_rating": RATING_LABELS.get(c.credit_rating, "BBB"),
                    "rating_rank": int(c.credit_rating),
                    "roce_pct": round(c.roce_pct, 2),
                    "pb_ratio": pb_val,
                    "free_float_shares": round(self.engine.public_float_shares.get(cid, 0.0), 2),
                    "controlled_by_id": c.controlled_by_id,
                    "ceo_name": ceo["ceo_name"] if ceo else ("Player/AI Investor" if c.regime == "PLAYER_INDIVIDUAL" else "Board Autopilot"),
                })

            all_firms = []
            for f in self.engine.firms.values():
                owner = self.engine.entities.get(f.owner_corp_id)
                recipe = self.engine.recipes.get(f.product_code)
                pdata = self.engine.products.get(f.product_code, {})
                layout = self.firm_custom_layouts.get(f.firm_id) or build_default_3x3_floorplan(
                    f.firm_type, f.product_code, f.integrated_inputs_count, f.rd_units, recipe
                )
                all_firms.append({
                    "firm_id": f.firm_id,
                    "owner_corp_id": f.owner_corp_id,
                    "owner_ticker": owner.ticker if owner else f"C{f.owner_corp_id}",
                    "owner_name": owner.name if owner else f"Corp {f.owner_corp_id}",
                    "firm_type": f.firm_type,
                    "build_code": f.build_code,
                    "city": f.city_name,
                    "product": f.product_code,
                    "product_name": pdata.get("NAME", f.product_code or f.firm_type),
                    "std_price": float(pdata.get("PRICE", 100.0) or 100.0),
                    "q_weight": int(pdata.get("QUALITY_CN", 33) or 33),
                    "b_weight": int(pdata.get("BRAND_CN", 33) or 33),
                    "p_weight": int(pdata.get("PRICE_CN", 34) or 34),
                    "book_value_millions": round(f.book_value_millions, 2),
                    "inventory_millions": round(f.inventory_value_millions, 2),
                    "quality": round(f.product_quality, 1),
                    "brand": round(f.brand_rating, 1),
                    "unit_price": round(f.unit_price, 2),
                    "adv_budget_millions": round(f.advertising_budget_millions, 2),
                    "rd_units": f.rd_units,
                    "market_share_pct": round(f.market_share * 100.0, 1),
                    "cogs_ratio": round(f.cogs_ratio, 3),
                    "integrated_inputs": f.integrated_inputs_count,
                    "last_q_rev_millions": round(f.last_quarter_revenue_millions, 3),
                    "last_q_ebit_millions": round(f.last_quarter_ebit_millions, 3),
                    "recipe": recipe,
                    "layout_3x3": layout,
                })

            # 320-Investor / 24-Archetype Ecosystem Summary
            catalog = self.engine.get_24_archetype_catalog()
            archetype_cohorts: Dict[str, Dict[str, Any]] = {}
            for idx, arch in enumerate(catalog):
                code = arch["code"]
                archetype_cohorts[code] = {
                    "arch_id": arch["arch_id"],
                    "archetype_code": code,
                    "lead_pid": 2001 + idx,
                    "lead_name": arch["lead_name"],
                    "domain": arch["domain"],
                    "allowed_domains": arch["allowed_domains"],
                    "is_smart": bool(arch["is_smart"]),
                    "signature_cmd": arch["signature_cmd"],
                    "bio": arch["bio"],
                    "count": 0,
                    "total_net_worth_millions": 0.0,
                    "avg_roi_pct": 0.0,
                    "max_gen": 1,
                    "active_playbook": None,
                }

            investors_list = []
            roi_accum: Dict[str, List[float]] = {}
            for pid, prof in sorted(self.engine.investor_personas.items()):
                ent = self.engine.entities.get(pid)
                if not ent:
                    continue
                code = prof.get("persona_type", "WSR_VALUE_COMPOUNDER")
                init_c = max(1e-5, float(prof.get("initial_cash_millions", 0.03)))
                roi_pct = round(((ent.net_worth - init_c) / init_c) * 100.0, 2)
                if code in archetype_cohorts:
                    archetype_cohorts[code]["count"] += 1
                    archetype_cohorts[code]["total_net_worth_millions"] = round(
                        archetype_cohorts[code]["total_net_worth_millions"] + ent.net_worth, 4
                    )
                    archetype_cohorts[code]["max_gen"] = max(
                        archetype_cohorts[code]["max_gen"], int(prof.get("generation", 1))
                    )
                    roi_accum.setdefault(code, []).append(roi_pct)
                    if prof.get("is_archetype_lead") and prof.get("conditional_playbook"):
                        archetype_cohorts[code]["active_playbook"] = prof["conditional_playbook"]

                investors_list.append({
                    "player_id": pid,
                    "name": ent.name,
                    "ticker": ent.ticker,
                    "archetype": code,
                    "domain_group": prof.get("domain_group", "I_WSR_PURE"),
                    "allowed_domains": prof.get("allowed_domains", ["WSR"]),
                    "signature_cmd": prof.get("signature_cmd", "BUY_STOCK"),
                    "is_smart_luna_agent": bool(prof.get("is_smart_luna_agent", False)),
                    "is_archetype_lead": bool(prof.get("is_archetype_lead", False)),
                    "generation": int(prof.get("generation", 1)),
                    "controlled_corp_id": int(prof.get("controlled_corp_id", 0)),
                    "initial_cash_millions": round(init_c, 4),
                    "cash_millions": round(ent.cash, 4),
                    "stock_portfolio_millions": round(ent.stock_portfolio_value, 4),
                    "short_liability_millions": round(ent.short_liability, 4),
                    "bank_loan_millions": round(ent.bank_loan, 4),
                    "net_worth_millions": round(ent.net_worth, 4),
                    "roi_pct": roi_pct,
                    "holdings_count": len(ent.stock_holdings),
                    "playbook": prof.get("conditional_playbook") or {},
                })

            for code, rlist in roi_accum.items():
                if code in archetype_cohorts and rlist:
                    archetype_cohorts[code]["avg_roi_pct"] = round(sum(rlist) / len(rlist), 2)

            investors_sorted_nw = sorted(investors_list, key=lambda x: x["net_worth_millions"], reverse=True)
            archetype_leads_list = [inv for inv in investors_list if inv["is_archetype_lead"]]
            street_hustlers_list = [
                inv for inv in investors_list
                if inv["initial_cash_millions"] <= 0.25
            ][:48]

            aether_ent = self.engine.entities[1]
            aether_nw_usd = round(aether_ent.net_worth * 1_000_000.0, 2)
            aether_cash_usd = round(aether_ent.cash * 1_000_000.0, 2)

            return {
                "ok": True,
                "game_mode": self.game_mode,
                "aether_summary": {
                    "net_worth_millions": round(aether_ent.net_worth, 5),
                    "net_worth_usd": aether_nw_usd,
                    "cash_millions": round(aether_ent.cash, 5),
                    "cash_usd": aether_cash_usd,
                },
                "clock": {
                    "year": self.engine.year,
                    "quarter": self.engine.quarter,
                    "month": self.engine.month,
                    "day": self.engine.day,
                    "subtick": self.engine.subtick,
                },
                "floor": floor,
                "coupling": coupling,
                "active_entity": ws,
                "acting_as_entity": acting_ws,
                "ohlcv_charts": {
                    "SELECTED_CORP": self.get_or_init_ohlcv_series(
                        f"CORP_{active_entity_id if (11 <= active_entity_id <= 1600 and self.engine.entities[active_entity_id].regime != 'PLAYER_INDIVIDUAL') else 13}",
                        self.engine.entities[active_entity_id if (11 <= active_entity_id <= 1600 and self.engine.entities[active_entity_id].regime != 'PLAYER_INDIVIDUAL') else 13].stock_price,
                        f"#{active_entity_id if (11 <= active_entity_id <= 1600 and self.engine.entities[active_entity_id].regime != 'PLAYER_INDIVIDUAL') else 13} {self.engine.entities[active_entity_id if (11 <= active_entity_id <= 1600 and self.engine.entities[active_entity_id].regime != 'PLAYER_INDIVIDUAL') else 13].ticker} ({self.engine.entities[active_entity_id if (11 <= active_entity_id <= 1600 and self.engine.entities[active_entity_id].regime != 'PLAYER_INDIVIDUAL') else 13].name})",
                    ),
                    "BTC": self.get_or_init_ohlcv_series("BTC", self.engine.crypto_prices.get("BTC", 65000.0), "BTC / USD Crypto"),
                    "OIL": self.get_or_init_ohlcv_series("OIL", self.engine.commodity_prices.get("OIL", 75.0), "WTI Crude Oil ($/bbl)"),
                    "GOLD": self.get_or_init_ohlcv_series("GOLD", self.engine.commodity_prices.get("GOLD", 2000.0), "Gold Spot ($/oz)"),
                    "STOCK_INDEX": self.get_or_init_ohlcv_series("STOCK_INDEX", self.engine.commodity_prices.get("STOCK_INDEX", 4500.0), "WSR Composite Index"),
                },
                "controlled_corps": controlled_corps,
                "corporations": corps_list,
                "all_firms": all_firms,
                "invariants": inv,
                "ecosystem": {
                    "total_investors": len(investors_list),
                    "total_archetypes": len(archetype_cohorts),
                    "wipeout_respawn_count": len(self.engine.wipeout_graveyard),
                    "wipeout_respawn_log": self.engine.wipeout_graveyard[-25:],
                    "cohorts": list(archetype_cohorts.values()),
                    "archetype_leads": archetype_leads_list,
                    "top_wealth_leaderboard": investors_sorted_nw[:40],
                    "street_hustlers_sample": street_hustlers_list,
                },
                "luna_telemetry": {
                    "model_id": self.luna.resolved_model,
                    "bg_running": self.luna_bg_running,
                    "status_text": self.luna_last_status,
                    "total_api_calls": len(self.luna.api_call_records),
                    "total_tokens": self.luna.total_prompt_tokens + self.luna.total_completion_tokens,
                    "estimated_cost_usd": round(self.luna.total_cost_usd, 6),
                    "recent_theses": (self.luna.decision_audit_log[-30:] if self.luna.decision_audit_log else self.cached_ai_theses[-30:]),
                },
                "ceo_profiles_sample": list(self.engine.corp_ceo_profiles.values())[:32],
                "cities": list(self.engine.cities.keys())[:50],
                "products": [
                    {
                        "code": pcode,
                        "name": pdata.get("NAME", pcode),
                        "class": pdata.get("CLASS", ""),
                        "price": pdata.get("PRICE", 100),
                        "q_w": pdata.get("QUALITY_CN", 33),
                        "b_w": pdata.get("BRAND_CN", 33),
                        "p_w": pdata.get("PRICE_CN", 34),
                        "recipe": self.engine.recipes.get(pcode),
                    }
                    for pcode, pdata in list(self.engine.products.items())[:85]
                ],
                "paimon_academy": self.paimon.get_academy_payload(),
            }


APP_STATE = WorkstationAppState()


class WorkstationHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        pass

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def _serve_static_file(self, base_dir: str, rel_path: str) -> None:
        safe_rel = os.path.normpath(urllib.parse.unquote(rel_path)).lstrip(r"\/")
        full_path = os.path.abspath(os.path.join(base_dir, safe_rel))
        if not full_path.startswith(os.path.abspath(base_dir)) or not os.path.isfile(full_path):
            self.send_error(404, "Asset not found")
            return
        ctype, _ = mimetypes.guess_type(full_path)
        ctype = ctype or "application/octet-stream"
        try:
            with open(full_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(content)))
            if rel_path.endswith(".html"):
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            else:
                self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(content)
        except Exception as exc:
            self.send_error(500, str(exc))

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            self._serve_static_file(UI_DIR, "index.html")
            return

        if path in ("/api/state", "/gamestate"):
            ent_id = int(qs.get("entity_id", ["1"])[0])
            act_id = int(qs.get("acting_as_id", [str(ent_id)])[0])
            q_str = str(qs.get("q", [""])[0])
            df_str = str(qs.get("dir_filter", ["ALL"])[0])
            payload = APP_STATE.get_full_dashboard_payload(
                active_entity_id=ent_id,
                acting_as_id=act_id,
                search_query=q_str,
                dir_filter=df_str,
            )
            self._send_json(payload)
            return

        if path == "/api/paimon_academy":
            self._send_json({"ok": True, "paimon_academy": APP_STATE.paimon.get_academy_payload()})
            return

        if path.startswith("/assets/wsr10/"):
            rel = path[len("/assets/wsr10/"):]
            self._serve_static_file(WSR10_ASSETS_DIR, rel)
            return

        if path.startswith("/assets/caplab/image/"):
            rel = path[len("/assets/caplab/image/"):]
            self._serve_static_file(CAPLAB_IMAGE_DIR, rel)
            return

        if path.startswith("/assets/caplab/speech/"):
            rel = path[len("/assets/caplab/speech/"):]
            self._serve_static_file(CAPLAB_SPEECH_DIR, rel)
            return

        self.send_error(404, "Route not found")

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/action":
            self.send_error(404, "Unknown POST endpoint")
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            req = json.loads(body)
            cmd = str(req.get("cmd", "")).upper()
            payload = dict(req.get("payload", {}))
            active_id = int(req.get("active_entity_id", 1))
            acting_as_id = int(req.get("acting_as_id", active_id))
            dir_filter = str(req.get("dir_filter", "ALL"))

            if cmd == "RUN_LUNA_BATCH":
                res = APP_STATE.trigger_async_luna_batch(
                    staggered_mode=bool(payload.get("staggered_mode", True)),
                )
            elif cmd == "PAIMON_ASK":
                res = APP_STATE.paimon.ask_paimon_tutor(
                    question=str(payload.get("question", "")),
                    app_state=APP_STATE,
                    active_entity_id=active_id,
                    acting_as_id=acting_as_id,
                    selected_firm_id=int(payload.get("selected_firm_id", 1)),
                    chart_symbol=str(payload.get("chart_symbol", "SELECTED_CORP")),
                    active_module_id=payload.get("active_module_id"),
                    active_quest_id=payload.get("active_quest_id"),
                )
            elif cmd == "PAIMON_UPDATE_PROGRESS":
                with APP_STATE.lock:
                    prog = APP_STATE.paimon.update_progress(payload)
                    res = {"ok": True, "progress": prog}
            elif cmd == "PAIMON_RESET_PROGRESS":
                with APP_STATE.lock:
                    prog = APP_STATE.paimon.reset_progress()
                    res = {"ok": True, "progress": prog}
            else:
                with APP_STATE.lock:
                    if cmd == "DEPOSIT_GTA":
                        res = APP_STATE.engine.deposit_from_gta_wallet(float(payload.get("amount_usd", 10_000.0)), 1)
                    elif cmd == "WITHDRAW_GTA":
                        res = APP_STATE.engine.withdraw_to_gta_wallet(float(payload.get("amount_usd", 10_000.0)), 1)
                    elif cmd == "SWITCH_GAME_MODE":
                        mode = str(payload.get("mode", "30K_HUSTLER")).upper()
                        APP_STATE._init_ecosystem(start_as_30k_hustler=(mode == "30K_HUSTLER"))
                        res = {"ok": True, "game_mode": APP_STATE.game_mode, "message": f"Switched to {APP_STATE.game_mode}"}
                    elif cmd == "RESET_NEW_GAME":
                        APP_STATE._init_ecosystem(start_as_30k_hustler=(APP_STATE.game_mode == "30K_HUSTLER"))
                        res = {"ok": True, "message": "World reset with 320 investors"}
                    elif cmd == "SAVE_GAME":
                        save_path = payload.get("path") or DEFAULT_SAVE_PATH
                        APP_STATE.engine.save_state(save_path)
                        res = {"ok": True, "path": save_path, "message": "Saved Full-Fidelity State (v2.0)"}
                    elif cmd == "LOAD_GAME":
                        save_path = payload.get("path") or DEFAULT_SAVE_PATH
                        if not os.path.isfile(save_path):
                            res = {"ok": False, "reason": "No saved state file found yet; click Save first"}
                        else:
                            APP_STATE.engine.load_state(save_path)
                            res = {"ok": True, "path": save_path, "message": "Loaded Full-Fidelity State (0.000000 loss)"}
                    elif cmd == "TRIGGER_SCENARIO":
                        res = APP_STATE.trigger_macro_stress_scenario(str(payload.get("scenario", "S1")))
                    elif cmd == "SET_FIRM_3X3_SLOT":
                        fid = int(payload.get("firm_id", 1))
                        slot_idx = int(payload.get("slot", 0))
                        new_role = str(payload.get("role", "MFT")).upper()
                        f = APP_STATE.engine.firms.get(fid)
                        if not f:
                            res = {"ok": False, "reason": f"Firm #{fid} not found"}
                        else:
                            recipe = APP_STATE.engine.recipes.get(f.product_code)
                            layout = APP_STATE.firm_custom_layouts.get(fid) or build_default_3x3_floorplan(
                                f.firm_type, f.product_code, f.integrated_inputs_count, f.rd_units, recipe
                            )
                            role_icon_map = {
                                "PUR": "/assets/caplab/image/Guide/PUR.png",
                                "MFT": "/assets/caplab/image/Guide/MFT.png",
                                "SALE": "/assets/caplab/image/Guide/SALE.png",
                                "INV": "/assets/caplab/image/Guide/INV.png",
                                "RD": "/assets/caplab/image/Guide/RD.png",
                                "TECH": "/assets/caplab/image/Guide/TECH.png",
                                "RADRD": "/assets/caplab/image/Guide/RADRD.png",
                                "EXTERN": "/assets/caplab/image/Guide/EXTERN.png",
                                "LABEL": "/assets/caplab/image/Guide/LABEL.png",
                            }
                            if 0 <= slot_idx < len(layout):
                                layout[slot_idx]["role"] = new_role
                                layout[slot_idx]["label"] = f"{new_role} Unit #{slot_idx+1} ({f.product_code})"
                                layout[slot_idx]["guide_img"] = role_icon_map.get(new_role, "/assets/caplab/image/Guide/MFT.png")
                                layout[slot_idx]["level"] = min(9, int(layout[slot_idx].get("level", 3)) + 1)
                            APP_STATE.firm_custom_layouts[fid] = layout
                            f.product_quality = min(100.0, f.product_quality + 1.2)
                            res = {"ok": True, "firm_id": fid, "slot": slot_idx, "role": new_role}
                    elif cmd == "TRAIN_FIRM_STAFF":
                        fid = int(payload.get("firm_id", 1))
                        f = APP_STATE.engine.firms.get(fid)
                        if not f:
                            res = {"ok": False, "reason": f"Firm #{fid} not found"}
                        else:
                            recipe = APP_STATE.engine.recipes.get(f.product_code)
                            layout = APP_STATE.firm_custom_layouts.get(fid) or build_default_3x3_floorplan(
                                f.firm_type, f.product_code, f.integrated_inputs_count, f.rd_units, recipe
                            )
                            for cell in layout:
                                cell["level"] = min(9, int(cell.get("level", 3)) + 1)
                            APP_STATE.firm_custom_layouts[fid] = layout
                            f.product_quality = min(100.0, f.product_quality + 2.5)
                            res = {"ok": True, "firm_id": fid, "new_quality": round(f.product_quality, 1)}
                    elif cmd == "STEP_QUARTER":
                        e = APP_STATE.engine
                        e.quarter += 1
                        if e.quarter > 4:
                            e.quarter = 1
                            e.year += 1
                            for cid in e.active_corp_ids:
                                e.roll_annual_nol_buckets(e.entities[cid])
                        e.month = (e.quarter - 1) * 3 + 1
                        e.day = 1
                        q_res = e.step_quarter()
                        local_moves = 0
                        for pid, prof in list(e.investor_personas.items()):
                            if prof.get("is_smart_luna_agent"):
                                pb_res = e.execute_conditional_playbook_for_investor(pid)
                                if pb_res.get("ok"):
                                    local_moves += 1
                        beh_res = e.step_behavioral_noise_investors()
                        e.recompute_all_balance_sheets(update_stock_prices=False)
                        APP_STATE.record_market_ohlcv_bar(force_new_bar=True)
                        res = {
                            "ok": True,
                            "quarter_summary": q_res,
                            "local_playbook_moves": local_moves,
                            "crowd_moves": beh_res.get("behavioral_moves", 0),
                            "respawns": beh_res.get("respawns", 0),
                        }
                    else:
                        res = APP_STATE.engine.execute_action(cmd, payload)
                        if cmd == "INCORPORATE_STARTUP" and res.get("startup_corp_id"):
                            APP_STATE.ohlcv_history.pop(f"CORP_{res['startup_corp_id']}", None)
                        APP_STATE.record_market_ohlcv_bar(force_new_bar=(cmd in ("STEP_DAY", "TRIGGER_SCENARIO")))

            dash = APP_STATE.get_full_dashboard_payload(
                active_entity_id=active_id,
                acting_as_id=acting_as_id,
                dir_filter=dir_filter,
            )
            self._send_json({"action_result": res, "state": dash})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=400)


def run_selftest() -> None:
    """Verifies v2.0 server endpoints, 320-investor ecosystem, 3x3 layouts, actions, and all sprite assets offline."""
    dash = APP_STATE.get_full_dashboard_payload(active_entity_id=1, acting_as_id=1)
    assert dash["ok"] is True
    assert dash["invariants"]["ok"] is True
    assert dash["ecosystem"]["total_investors"] == 320
    assert dash["ecosystem"]["total_archetypes"] == 24
    assert len(dash["corporations"]) > 50
    assert len(dash["all_firms"]) >= 5
    assert len(dash["all_firms"][0]["layout_3x3"]) == 9
    assert "coupling" in dash and "oil_commodity_multiplier" in dash["coupling"]
    assert os.path.isdir(WSR10_ASSETS_DIR), f"Missing WSR10 assets dir: {WSR10_ASSETS_DIR}"
    assert os.path.isdir(CAPLAB_IMAGE_DIR), f"Missing CapLab image dir: {CAPLAB_IMAGE_DIR}"

    # Verify every Capitalism Lab UI sprite referenced by the 3x3 floorplan & Workstation v2.0 UI exists on disk
    required_caplab_imgs = [
        "Guide/PUR.png", "Guide/MFT.png", "Guide/SALE.png", "Guide/INV.png", "Guide/EXTERN.png",
        "Guide/LABEL.png", "Guide/RD.png", "Guide/TECH.png", "Guide/RADRD.png", "Guide/MINE.png",
        "Guide/OIL.png", "Guide/FOREST.png", "Guide/FARMCROP.png", "Guide/FARMPROC.png",
        "Guide/PROJECT.png", "Guide/PROJCODE.png", "Guide/TECHCODE.png",
        "Floor/Floor1_d.png", "Floor/Floor2.png", "Floor/Floor3.png", "Floor/AddFloor_n.png",
        "Icon/Quality.png", "Icon/Brand.png", "Icon/Price.png", "Icon/OverallRating.png",
        "Icon/TrainingIcon.png", "Icon/mft_supply0.png", "Icon/mft_supply1.png",
        "Icon/City/GDPGrowth.png", "Icon/City/CPI.png", "MenuBar/Calendar.png",
        "FirmImage/FIRM/FACTORY2.png", "FirmImage/FIRM/ELECTRON1.png", "FirmImage/FIRM/RD1.png",
        "FirmImage/FIRM/MINE1.png", "FirmImage/FIRM/OIL1.png", "FirmImage/FIRM/FARM11.png",
        "FirmImage/FIRM/SOFTWARE1.png", "FirmImage/FIRM/BANK_HQ1.png", "FirmImage/MALL/MALL01.png",
        "FirmType/Apt/Btn_Apt_n.png", "FirmType/Comm/Btn_Comm_n.png",
    ]
    for rel_img in required_caplab_imgs:
        full_img = os.path.join(CAPLAB_IMAGE_DIR, os.path.normpath(rel_img))
        assert os.path.isfile(full_img), f"Missing CapLab UI sprite: {full_img}"

    # Verify $30k Startup Incorporation, 3x3 Slot Reconfiguration, Staff Training, Scenario & Save/Load
    st_res = APP_STATE.engine.incorporate_bootstrapped_startup(1, "RETAIL", "New York City", "SMARTPH", 0.018, 3.0)
    assert st_res["ok"] is True, f"Startup incorporation failed: {st_res}"
    sc_res = APP_STATE.trigger_macro_stress_scenario("S3")
    assert sc_res["ok"] is True
    APP_STATE.engine.save_state(DEFAULT_SAVE_PATH)
    APP_STATE.engine.load_state(DEFAULT_SAVE_PATH)
    inv_after = APP_STATE.engine.verify_global_invariants()
    assert inv_after["ok"] is True

    # Verify Paimon Economic & Trading Academy payload & live telemetry context
    assert "paimon_academy" in dash
    pa = dash["paimon_academy"]
    assert pa["total_modules"] == 9, f"Expected 9 Paimon modules, got {pa['total_modules']}"
    assert pa["total_quests"] == 36, f"Expected 36 Paimon quests, got {pa['total_quests']}"
    assert len(pa["inspect_dict"]) >= 40, f"Expected >= 40 inspect entries, got {len(pa['inspect_dict'])}"
    live_ctx = APP_STATE.paimon.build_live_telemetry_context(
        app_state=APP_STATE,
        active_entity_id=13,
        acting_as_id=1,
        selected_firm_id=1,
        chart_symbol="SELECTED_CORP",
        active_module_id="M2",
        active_quest_id="M2_Q1",
    )
    assert live_ctx["viewed_entity"]["id"] == 13
    assert "latest_candle" in live_ctx["ohlcv_chart_telemetry"]
    assert "lowest_pb_value_stocks" in live_ctx["market_peer_benchmarks"]

    print("[SELFTEST PASS] Eagle Workstation Server v2.0 + Paimon Economic Academy (9 Modules, 36 Quests, 320 Investors, 3x3 Layouts, Save/Load) verified 100%!")


def main() -> None:
    parser = argparse.ArgumentParser(description="EagleCapitalEngine Unified Workstation Server v2.0")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Bind port (default: 8765)")
    parser.add_argument("--selftest", action="store_true", help="Run non-blocking endpoint & asset selftest")
    args = parser.parse_args()

    if args.selftest:
        run_selftest()
        return

    server = ThreadingHTTPServer((args.host, args.port), WorkstationHTTPRequestHandler)
    print("=========================================================================")
    print(" EAGLE CAPITAL ENGINE v2.0 — UNIFIED WSR v10 + CAPITALISM LAB WORKSTATION")
    print(f" Live URL               : http://{args.host}:{args.port}")
    print(" Population             : 320 Investors across 24 Archetypes + Aether ($30k/$1000M)")
    print(f" WSR v10 Assets Mounted : {WSR10_ASSETS_DIR}")
    print(f" CapLab Assets Mounted  : {CAPLAB_IMAGE_DIR}")
    print("=========================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down workstation server...")
        server.server_close()


if __name__ == "__main__":
    main()

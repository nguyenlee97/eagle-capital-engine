#!/usr/bin/env python3
"""
EagleCapitalEngine — Unified Wall Street Raider v10 + Capitalism Lab Workstation Server
=======================================================================================
Zero-dependency HTTP/JSON server that:
  1. Hosts the unified EagleCapitalEngine (1,595 entities, 5 Balance Sheet Regimes,
     71 WSR Industries, 135 Capitalism Lab Products, 99 Manufacturing Recipes,
     128 Cities, 64 PERSONS.DBF AI CEOs, and 4 WSR Billionaire Raider AIs).
  2. Exposes real-time JSON endpoints (/api/state, /api/action, /api/catalog)
     compatible with WSR v10's Electron frontend AND Stage B GTA San Andreas (EaglePhone OS).
  3. Mounts and serves authentic read-only game assets directly from disk:
     - /assets/wsr10/*        -> Wall Street Raider v10.0.22.3 MP4 videos, logos & icons
     - /assets/caplab/image/* -> Capitalism Lab 2,637 PNG/JPG building sprites & UI icons
     - /assets/caplab/speech/*-> Capitalism Lab 5,255 MP3 voiceovers & sound effects
"""

import argparse
import json
import mimetypes
import os
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict

from eagle_capital_engine import EagleCapitalEngine, RATING_LABELS

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(WORKSPACE_DIR, "ui")

WSR10_ASSETS_DIR = (
    r"C:\Users\LENOVO\Downloads\Wall.Street.Raider.v10.0.22.3"
    r"\Wall.Street.Raider.v10.0.22.3\Wall.Street.Raider.v10.0.22.3\resources\app\assets"
)
CAPLAB_ROOT_DIR = r"C:\Users\LENOVO\Downloads\capitalism lab\[tamhongame.com]_CL\Capitalism Lab"
CAPLAB_IMAGE_DIR = os.path.join(CAPLAB_ROOT_DIR, "image")
CAPLAB_SPEECH_DIR = os.path.join(CAPLAB_ROOT_DIR, "speech")


class WorkstationAppState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.engine = EagleCapitalEngine()
        # Seed initial Capitalism Lab supply chain firms for Player 1 & rival corporations
        self._seed_initial_demo_firms()

    def _seed_initial_demo_firms(self) -> None:
        # Give Player 1 control of Corp 321 (Electronics) and build initial Factory + R&D + Retail
        self.engine.entities[321].cash = max(self.engine.entities[321].cash, 250.0)
        self.engine.recompute_entity_balance_sheet(self.engine.entities[321], update_stock_price=False)
        self.engine.build_caplab_firm(321, "FACTORY", "COMPUTER1", "New York City", 25.0, 5.0, "SMARTPH")
        self.engine.build_caplab_firm(321, "RD", "RD", "San Francisco", 15.0, 0.0, "SMARTPH", rd_units=9)
        self.engine.build_caplab_firm(321, "RETAIL", "ELECTRON", "New York City", 12.0, 3.0, "SMARTPH")
        self.engine.step_caplab_firms_quarterly()
        self.engine.recompute_all_balance_sheets()

    def get_full_dashboard_payload(self, active_entity_id: int = 1, search_query: str = "") -> Dict[str, Any]:
        with self.lock:
            ws = self.engine.get_workstation_state(active_entity_id=active_entity_id)
            floor = self.engine.get_wallstreet_floor_snapshot()
            inv = self.engine.verify_global_invariants()

            q = search_query.strip().upper()
            corps_list = []
            for cid in self.engine.active_corp_ids:
                c = self.engine.entities[cid]
                if q and (q not in c.ticker.upper() and q not in c.name.upper() and q != str(cid)):
                    continue
                ceo = self.engine.corp_ceo_profiles.get(cid)
                corps_list.append({
                    "id": cid,
                    "ticker": c.ticker,
                    "name": c.name,
                    "regime": c.regime,
                    "industry_id": c.industry_id,
                    "industry_name": self.engine.industries.get(c.industry_id, {}).get("name", "HOLDING"),
                    "stock_price": round(c.stock_price, 2),
                    "net_worth_millions": round(c.net_worth, 2),
                    "cash_millions": round(c.cash, 2),
                    "total_assets_millions": round(c.total_assets, 2),
                    "total_liabilities_millions": round(c.total_liabilities, 2),
                    "credit_rating": RATING_LABELS.get(c.credit_rating, "BBB"),
                    "roce_pct": round(c.roce_pct, 2),
                    "free_float_shares": round(self.engine.public_float_shares.get(cid, 0.0), 2),
                    "controlled_by_id": c.controlled_by_id,
                    "ceo_name": ceo["ceo_name"] if ceo else "Board Autopilot",
                })
                if len(corps_list) >= 80:
                    break

            all_firms = []
            for f in self.engine.firms.values():
                owner = self.engine.entities.get(f.owner_corp_id)
                all_firms.append({
                    "firm_id": f.firm_id,
                    "owner_corp_id": f.owner_corp_id,
                    "owner_ticker": owner.ticker if owner else f"C{f.owner_corp_id}",
                    "owner_name": owner.name if owner else f"Corp {f.owner_corp_id}",
                    "firm_type": f.firm_type,
                    "build_code": f.build_code,
                    "city": f.city_name,
                    "product": f.product_code,
                    "book_value_millions": round(f.book_value_millions, 2),
                    "quality": round(f.product_quality, 1),
                    "brand": round(f.brand_rating, 1),
                    "unit_price": round(f.unit_price, 2),
                    "adv_budget_millions": round(f.advertising_budget_millions, 2),
                    "market_share_pct": round(f.market_share * 100.0, 1),
                    "cogs_ratio": round(f.cogs_ratio, 3),
                    "integrated_inputs": f.integrated_inputs_count,
                    "last_q_rev_millions": round(f.last_quarter_revenue_millions, 2),
                    "last_q_ebit_millions": round(f.last_quarter_ebit_millions, 2),
                })

            return {
                "ok": True,
                "clock": {
                    "year": self.engine.year,
                    "quarter": self.engine.quarter,
                    "month": self.engine.month,
                    "day": self.engine.day,
                    "subtick": self.engine.subtick,
                },
                "floor": floor,
                "active_entity": ws,
                "corporations": corps_list,
                "all_firms": all_firms,
                "invariants": inv,
                "ceo_profiles_sample": list(self.engine.corp_ceo_profiles.values())[:24],
                "cities": list(self.engine.cities.keys())[:40],
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
                    for pcode, pdata in list(self.engine.products.items())[:60]
                ],
            }


APP_STATE = WorkstationAppState()


class WorkstationHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        # Quiet clean logging
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

        if path == "/api/state" or path == "/gamestate":
            ent_id = int(qs.get("entity_id", ["1"])[0])
            q_str = str(qs.get("q", [""])[0])
            payload = APP_STATE.get_full_dashboard_payload(active_entity_id=ent_id, search_query=q_str)
            self._send_json(payload)
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
            with APP_STATE.lock:
                if cmd == "DEPOSIT_GTA":
                    res = APP_STATE.engine.deposit_from_gta_wallet(float(payload.get("amount_usd", 1_000_000.0)), 1)
                elif cmd == "WITHDRAW_GTA":
                    res = APP_STATE.engine.withdraw_to_gta_wallet(float(payload.get("amount_usd", 1_000_000.0)), 1)
                elif cmd == "RESET_NEW_GAME":
                    APP_STATE.engine.reset_new_game()
                    APP_STATE._seed_initial_demo_firms()
                    res = {"ok": True, "message": "World reset"}
                else:
                    res = APP_STATE.engine.execute_action(cmd, payload)
            dash = APP_STATE.get_full_dashboard_payload(active_entity_id=active_id)
            self._send_json({"action_result": res, "state": dash})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=400)


def run_selftest() -> None:
    """Verifies server endpoints & asset mounts offline without blocking."""
    dash = APP_STATE.get_full_dashboard_payload(active_entity_id=1)
    assert dash["ok"] is True
    assert dash["invariants"]["ok"] is True
    assert len(dash["corporations"]) > 50
    assert len(dash["all_firms"]) >= 3
    assert os.path.isdir(WSR10_ASSETS_DIR), f"Missing WSR10 assets dir: {WSR10_ASSETS_DIR}"
    assert os.path.isdir(CAPLAB_IMAGE_DIR), f"Missing CapLab image dir: {CAPLAB_IMAGE_DIR}"
    print("[SELFTEST PASS] Eagle Workstation Server state & asset mounts verified 100%!")


def main() -> None:
    parser = argparse.ArgumentParser(description="EagleCapitalEngine Unified Workstation Server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Bind port (default: 8765)")
    parser.add_argument("--selftest", action="store_true", help="Run non-blocking endpoint & asset selftest")
    args = parser.parse_args()

    if args.selftest:
        run_selftest()
        return

    server = ThreadingHTTPServer((args.host, args.port), WorkstationHTTPRequestHandler)
    print(f"=========================================================================")
    print(f" EAGLE CAPITAL ENGINE — UNIFIED WSR v10 + CAPITALISM LAB WORKSTATION")
    print(f" Live URL: http://{args.host}:{args.port}")
    print(f" WSR v10 Assets Mounted : {WSR10_ASSETS_DIR}")
    print(f" CapLab Assets Mounted  : {CAPLAB_IMAGE_DIR}")
    print(f"=========================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down workstation server...")
        server.server_close()


if __name__ == "__main__":
    main()

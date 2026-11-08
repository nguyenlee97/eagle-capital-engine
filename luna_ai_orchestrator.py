#!/usr/bin/env python3
"""
Multi-Batch Cohort AI Orchestrator & Telemetry Auditor (gpt-6-luna)
===================================================================
Coordinates 320 Investors across 24 Unique Archetypes spanning Wall Street Raider & Capitalism Lab:
  - Domain I   (Archetypes #1..#7):   Pure WSR Financial, Credit, Bond, Swap, Option & Commodity Whales
  - Domain II  (Archetypes #8..#13):  Pure Capitalism Lab Real-Economy Builders (R&D, Retail, Brand, Mine, REIT, Software)
  - Domain III (Archetypes #14..#18): Cross-Domain Chaebols, Bank/Insurance Float, ETF Advisors & $30k Bootstrapped Startups
  - Domain IV  (Archetypes #19..#24): Smart Retail Snipers (#19..#20) + 160 Behavioral Savers/FOMO/WSB Crowd (#21..#24, 0 API calls)
"""

import concurrent.futures
import json
import os
import time
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from eagle_capital_engine import EagleCapitalEngine, RATING_LABELS

DEFAULT_API_KEY = os.environ.get(
    "OPENAI_API_KEY",
    "os.environ.get(OPENAI_API_KEY, ...)",
)

# Pricing estimate for lightweight Luna tier ($0.15 / 1M input tokens, $0.60 / 1M output tokens)
INPUT_COST_PER_1M = 0.15
OUTPUT_COST_PER_1M = 0.60

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")


class LunaCohortOrchestrator:
    def __init__(
        self,
        engine: EagleCapitalEngine,
        api_key: str = DEFAULT_API_KEY,
        model_name: str = "gpt-6.1-luna",
    ) -> None:
        self.engine = engine
        self.api_key = api_key
        # Alias gpt-6.1-luna -> gpt-6-luna (verified active ID on endpoint)
        self.requested_model = model_name
        self.resolved_model = "gpt-6-luna" if model_name in ("gpt-6.1-luna", "gpt-6-luna") else model_name

        os.makedirs(LOG_DIR, exist_ok=True)
        self.jsonl_log_path = os.path.join(LOG_DIR, "luna_ai_calls.jsonl")
        self.report_path = os.path.join(LOG_DIR, "luna_ai_evaluation_report.json")

        self.api_call_records: List[Dict[str, Any]] = []
        self.decision_audit_log: List[Dict[str, Any]] = []
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_cost_usd: float = 0.0

    def _build_compact_market_context(self) -> Dict[str, Any]:
        """Builds a compact (<550 tokens) market, derivative, commodity & supply-chain snapshot for gpt-6-luna."""
        reserved = {131, 132, 133, 181, 200, 201, 202, 203, 205, 221, 222, 300, 321, 322, 620}
        candidates = []
        for cid in self.engine.active_corp_ids[:90]:
            if cid in reserved:
                continue
            c = self.engine.entities[cid]
            ff = self.engine.public_float_shares.get(cid, 0.0)
            if not c.is_active or c.net_worth <= 0 or ff < 2.0:
                continue
            pb = (c.stock_price * c.shares_outstanding) / max(1.0, c.net_worth)
            candidates.append({
                "corp_id": cid,
                "ticker": c.ticker,
                "ind": self.engine.industries.get(c.industry_id, {}).get("name", "IND")[:16],
                "price": round(c.stock_price, 2),
                "pb": round(pb, 2),
                "roce_pct": round(c.roce_pct, 1),
                "rating": RATING_LABELS.get(c.credit_rating, "BBB"),
            })
        undervalued = sorted(candidates, key=lambda x: x["pb"])[:6]
        high_roce = sorted(candidates, key=lambda x: x["roce_pct"], reverse=True)[:5]
        weak_short_targets = [x for x in candidates if x["rating"] in ("BBB", "BB", "B", "CCC")][:5]
        return {
            "date": f"{self.engine.year}-Q{self.engine.quarter}",
            "macro": {
                "gdp_growth_pct": round(self.engine.gdp_growth_pct, 2),
                "inflation_pct": round(self.engine.inflation_pct, 2),
                "prime_rate_pct": self.engine.prime_rate_pct,
                "long_bond_price": round(self.engine.get_long_gov_bond_price(), 2),
            },
            "commodities": {k: round(v, 2) for k, v in self.engine.commodity_prices.items()},
            "crypto": {k: round(v, 2) for k, v in self.engine.crypto_prices.items()},
            "undervalued_stocks": undervalued,
            "high_roce_momentum_stocks": high_roce,
            "weak_short_candidates": weak_short_targets,
            "etf_ids": self.engine.etf_corp_ids[:5],
            "caplab_hot_cities": ["New York City", "Tokyo", "London", "Beijing", "Seoul", "San Francisco"],
            "caplab_hot_products": ["SMARTPH", "NOTEBOOK", "CAR", "APPAREL", "COMPUTER", "GOLD"],
        }

    def _build_investor_dossier(self, eid: int) -> Dict[str, Any]:
        ent = self.engine.entities[eid]
        persona = self.engine.investor_personas[eid]
        ctrl_cid = int(persona.get("controlled_corp_id") or 0)
        if not ctrl_cid and ent.ceo_of_corp_ids:
            ctrl_cid = next(iter(ent.ceo_of_corp_ids))
        ctrl_firms = [
            {"firm_id": f.firm_id, "type": f.firm_type, "city": f.city_name, "prod": f.product_code, "price": f.unit_price, "mkt_share": f.market_share}
            for f in self.engine.firms.values()
            if f.owner_corp_id == ctrl_cid
        ]
        sub_cids = []
        if ctrl_cid in self.engine.entities:
            c_ent = self.engine.entities[ctrl_cid]
            for s_cid, sh in c_ent.stock_holdings.items():
                if s_cid in self.engine.entities and sh > 0:
                    sub_cids.append(s_cid)
        return {
            "entity_id": eid,
            "name": ent.name,
            "persona_type": persona["persona_type"],
            "signature_cmd": persona.get("signature_cmd", "BUY_STOCK"),
            "firm_focus": persona.get("firm_focus", ""),
            "product_focus": persona.get("product_focus", ""),
            "allowed_domains": persona["allowed_domains"],
            "bio": persona["bio"],
            "personal_cash_millions": round(ent.cash, 4),
            "personal_net_worth_millions": round(ent.net_worth, 4),
            "holdings": {str(k): round(v, 4) for k, v in list(ent.stock_holdings.items())[:4]},
            "shorts": {str(k): round(v, 4) for k, v in list(ent.short_positions.items())[:4]},
            "controlled_corp_id": ctrl_cid,
            "controlled_subsidiaries": sub_cids[:2],
            "controlled_corp_firms": ctrl_firms[:3],
        }

    def _call_luna_batch(self, batch_name: str, dossiers: List[Dict[str, Any]], mkt_ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Calls gpt-6-luna for a cohort of distinct investors and returns structured JSON playbooks."""
        sys_prompt = (
            "You are the Strategic AI Director for EagleCapitalEngine (Wall Street Raider + Capitalism Lab). "
            "Given the Market Snapshot and a cohort of Investors, generate a unique, persona-authentic "
            "quarterly decision and 3-quarter conditional playbook for EACH investor.\n"
            "STRICT 24-ARCHETYPE RULES (Respect each investor's persona_type & signature_cmd):\n"
            "- WSR_VALUE_COMPOUNDER, BANK_INSURANCE_FLOAT_TYCOON, KELLY_VALUE_SNIPER, SUPPLY_CHAIN_MOMENTUM_TRADER, PURE_WSR_WHALE, SMART_TRADER: "
            "Use BUY_STOCK or SELL_STOCK.\n"
            "- QUANT_LONG_SHORT_WHALE, HEDGE_FUND_SHARK: Use SHORT_STOCK or BUY_STOCK.\n"
            "- CORPORATE_RAIDER_LBO: Use SPINOFF_SUB or LIQUIDATE_SUB on controlled_corp_id/controlled_subsidiaries, or BUY_STOCK.\n"
            "- FORENSIC_SHORT_ACTIVIST: Use SHORT_STOCK or FILE_LAWSUIT.\n"
            "- FIXED_INCOME_BOND_KING: Use BUY_GOV_BOND, BUY_CORP_BOND, or ISSUE_CV.\n"
            "- DERIVATIVES_SWAP_MACRO: Use CREATE_SWAP or BUY_OPTION.\n"
            "- COMMODITY_CRYPTO_WHALE: Use TRADE_FUTURES (OIL, GOLD, WHEAT, COPPER) or TRADE_CRYPTO (BTC, ETH).\n"
            "- RD_SEMICONDUCTOR_MOGUL, HYPERMARKET_RETAIL_BARON, RESOURCE_MINING_BARON, REAL_ESTATE_REIT_LANDLORD, DIGITAL_SOFTWARE_FOUNDER, PURE_CAPLAB_BUILDER: "
            "Must ONLY use Capitalism Lab commands on controlled_corp_id: BUILD_FIRM (using their firm_focus & product_focus), SET_FIRM_PARAMS, or SET_BRAND_STRATEGY.\n"
            "- LUXURY_BRAND_TITAN: Use SET_BRAND_STRATEGY (UNIQUE or RANGE) or BUILD_FIRM (RETAIL, APPAREL).\n"
            "- VERTICAL_CHAEBOL_EMPIRE, HYBRID_EMPIRE: Use BUILD_FIRM, SET_FIRM_PARAMS, or BUY_STOCK.\n"
            "- ETF_INSTITUTIONAL_ADVISOR: Use ADVISOR_ETF (etf_id in 1581..1600).\n"
            "- BOOTSTRAP_RETAIL_HUSTLER, BOOTSTRAP_TECH_WORKSHOP, STARTUP_HUSTLER: If controlled_corp_id == 0, MUST use INCORPORATE_STARTUP; if controlled_corp_id > 0, use SET_FIRM_PARAMS.\n"
            "Return JSON with key 'decisions': list of objects: "
            "{'entity_id': int, 'thesis': str, 'cmd': str, 'payload': dict, 'bull_trigger': str, 'bear_trigger': str}."
        )
        user_prompt = json.dumps({"market": mkt_ctx, "investors": dossiers}, separators=(",", ":"))

        req_body = json.dumps({
            "model": self.resolved_model,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }).encode("utf-8")

        t0 = time.perf_counter()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=req_body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=35) as resp:
            raw_resp = json.loads(resp.read().decode("utf-8"))
        latency_ms = (time.perf_counter() - t0) * 1000.0

        usage = raw_resp.get("usage", {})
        p_tok = int(usage.get("prompt_tokens", 0))
        c_tok = int(usage.get("completion_tokens", 0))
        cost_usd = (p_tok / 1_000_000.0) * INPUT_COST_PER_1M + (c_tok / 1_000_000.0) * OUTPUT_COST_PER_1M

        content_str = raw_resp["choices"][0]["message"]["content"]
        parsed = json.loads(content_str)

        call_rec = {
            "year": self.engine.year,
            "quarter": self.engine.quarter,
            "batch_name": batch_name,
            "requested_model": self.requested_model,
            "resolved_model": raw_resp.get("model", self.resolved_model),
            "investor_ids": [d["entity_id"] for d in dossiers],
            "latency_ms": round(latency_ms, 2),
            "prompt_tokens": p_tok,
            "completion_tokens": c_tok,
            "total_tokens": p_tok + c_tok,
            "estimated_cost_usd": round(cost_usd, 6),
            "decisions_count": len(parsed.get("decisions", [])),
        }
        return {"call_record": call_rec, "decisions": parsed.get("decisions", [])}

    def call_luna_for_smart_respawn_init(self, eid: int) -> Dict[str, Any]:
        """
        When a Smart Investor wipes out and a Fresh Entrant spawns in that slot,
        calls gpt-6-luna to initialize a brand-new strategy & first trade for the newcomer.
        """
        mkt_ctx = self._build_compact_market_context()
        dossier = self._build_investor_dossier(eid)
        res = self._call_luna_batch(f"SMART_RESPAWN_INIT_{eid}", [dossier], mkt_ctx)
        self._record_and_execute_batch_result(res, mkt_ctx)
        self.engine.investor_personas[eid]["needs_smart_ai_init"] = False
        return res

    def _normalize_and_validate_decision(self, eid: int, dec: Dict[str, Any], mkt_ctx: Dict[str, Any]) -> Tuple[str, Dict[str, Any], bool]:
        """
        Maps gpt-6-luna's decision JSON into exact EagleCapitalEngine.execute_action() parameters
        across all 24 Archetypes and verifies Persona domain constraints.
        """
        persona = self.engine.investor_personas[eid]
        ptype = persona["persona_type"]
        ent = self.engine.entities[eid]
        cmd = str(dec.get("cmd", persona.get("signature_cmd", "BUY_STOCK"))).upper().strip()
        raw_p = dict(dec.get("payload") or {})

        wsr_cmds = {
            "BUY_STOCK", "SELL_STOCK", "SHORT_STOCK", "COVER_SHORT",
            "BUY_GOV_BOND", "SELL_GOV_BOND", "BUY_CORP_BOND", "SELL_CORP_BOND",
            "ISSUE_CV", "CONVERT_CV", "CREATE_SWAP", "BUY_OPTION", "WRITE_OPTION",
            "TRADE_FUTURES", "TRADE_CRYPTO", "SPINOFF_SUB", "LIQUIDATE_SUB",
            "FILE_LAWSUIT", "ADVISOR_ETF",
        }
        caplab_cmds = {"BUILD_FIRM", "SET_FIRM_PARAMS", "SET_BRAND_STRATEGY"}

        ctrl_cid = int(persona.get("controlled_corp_id") or 0)
        if not ctrl_cid and ent.ceo_of_corp_ids:
            ctrl_cid = next(iter(ent.ceo_of_corp_ids))

        # Check Persona Domain Fidelity
        fidelity_ok = True
        allowed = set(persona.get("allowed_domains", ["WSR"]))
        if allowed == {"WSR"} and cmd not in wsr_cmds:
            fidelity_ok = False
            cmd = persona.get("signature_cmd", "BUY_STOCK")
        elif allowed == {"CAPLAB"} and cmd not in caplab_cmds:
            fidelity_ok = False
            cmd = persona.get("signature_cmd", "BUILD_FIRM")
        elif ptype in ("STARTUP_HUSTLER", "BOOTSTRAP_RETAIL_HUSTLER", "BOOTSTRAP_TECH_WORKSHOP"):
            if ctrl_cid == 0 and cmd != "INCORPORATE_STARTUP":
                fidelity_ok = False
                cmd = "INCORPORATE_STARTUP"

        default_target = mkt_ctx["undervalued_stocks"][0]["corp_id"] if mkt_ctx["undervalued_stocks"] else 350

        # 1. Bootstrapped Startup Incorporation
        if cmd == "INCORPORATE_STARTUP":
            if ctrl_cid > 0:
                # Already incorporated in an earlier quarter -> switch to SET_FIRM_PARAMS
                cmd = "SET_FIRM_PARAMS"
            else:
                payload = {
                    "founder_id": eid,
                    "firm_type": str(raw_p.get("firm_type", persona.get("firm_focus", "RETAIL"))).upper(),
                    "city_name": str(raw_p.get("city_name", "New York City")),
                    "product_code": str(raw_p.get("product_code", persona.get("product_focus", "SMARTPH"))),
                    "equity_invest_millions": min(ent.cash * 0.75, max(0.01, float(raw_p.get("equity_invest_millions", ent.cash * 0.6)))),
                    "loan_multiple": float(raw_p.get("loan_multiple", 3.0)),
                }
                return cmd, payload, fidelity_ok

        # 2. Fixed Income / Bonds
        if cmd in ("BUY_GOV_BOND", "BUY_CORP_BOND"):
            par_m = min(ent.cash * 0.30, max(0.5, float(raw_p.get("par_millions", ent.cash * 0.20))))
            return cmd, {"buyer_id": eid, "par_millions": round(par_m, 3)}, fidelity_ok

        if cmd == "ISSUE_CV":
            iss_cid = int(raw_p.get("issuer_corp_id") or default_target)
            if iss_cid not in self.engine.entities or self.engine.entities[iss_cid].regime == "ETF_FUND":
                iss_cid = default_target
            spot = self.engine.entities[iss_cid].stock_price
            par_m = min(ent.cash * 0.25, max(5.0, float(raw_p.get("par_millions", 20.0))))
            return "ISSUE_CV", {
                "issuer_corp_id": iss_cid,
                "par_millions": round(par_m, 2),
                "conversion_price": round(spot * 1.10, 2),
                "coupon_pct": 5.5,
                "maturity_year": self.engine.year + 5,
                "buyer_id": eid,
            }, fidelity_ok

        # 3. Derivatives: Interest Rate Swaps & Options
        if cmd == "CREATE_SWAP":
            notional = min(ent.net_worth * 0.30, max(10.0, float(raw_p.get("notional_millions", 40.0))))
            return "CREATE_SWAP", {
                "party_a_id": eid,
                "party_b_id": 0,
                "notional_millions": round(notional, 2),
                "fixed_rate_pct": self.engine.prime_rate_pct,
                "floating_benchmark": str(raw_p.get("floating_benchmark", "PRIME")).upper(),
                "party_a_pays_fixed": bool(raw_p.get("party_a_pays_fixed", True)),
                "duration_quarters": 8,
            }, fidelity_ok

        if cmd in ("BUY_OPTION", "WRITE_OPTION"):
            u_cid = int(raw_p.get("underlying_corp_id") or raw_p.get("target_corp_id") or default_target)
            if u_cid not in self.engine.entities or u_cid <= 10:
                u_cid = default_target
            spot = self.engine.entities[u_cid].stock_price
            return cmd, {
                "holder_id": eid if cmd == "BUY_OPTION" else 0,
                "writer_id": eid if cmd == "WRITE_OPTION" else 0,
                "underlying_corp_id": u_cid,
                "opt_type": str(raw_p.get("opt_type", "CALL")).upper(),
                "strike_price": round(spot * 1.05, 2),
                "shares_covered_millions": 0.2,
                "months_to_expiry": 6.0,
            }, fidelity_ok

        # 4. Commodities & Crypto
        if cmd == "TRADE_FUTURES":
            comm = str(raw_p.get("commodity_code", "OIL")).upper()
            notional = min(ent.cash * 0.35, max(2.0, float(raw_p.get("notional_millions", 15.0))))
            return "TRADE_FUTURES", {"trader_id": eid, "commodity_code": comm, "notional_millions": round(notional, 2)}, fidelity_ok

        if cmd == "TRADE_CRYPTO":
            sym = str(raw_p.get("symbol", "BTC")).upper()
            usd_m = min(ent.cash * 0.25, max(1.0, float(raw_p.get("usd_millions_delta", 10.0))))
            return "TRADE_CRYPTO", {"trader_id": eid, "symbol": sym, "usd_millions_delta": round(usd_m, 3)}, fidelity_ok

        # 5. Corporate Raider Spin-Off / Liquidation / Lawsuit / ETF Advisor
        if cmd in ("SPINOFF_SUB", "LIQUIDATE_SUB") and ctrl_cid in self.engine.entities:
            c_ent = self.engine.entities[ctrl_cid]
            subs = [scid for scid, sh in c_ent.stock_holdings.items() if sh > 0 and scid in self.engine.entities and self.engine.entities[scid].is_active]
            if subs:
                return cmd, {"parent_corp_id": ctrl_cid, "sub_corp_id": subs[0]}, fidelity_ok
            cmd = "BUY_STOCK"

        if cmd == "FILE_LAWSUIT":
            def_cid = int(raw_p.get("defendant_id") or default_target)
            if def_cid not in self.engine.entities or def_cid <= 10:
                def_cid = default_target
            return "FILE_LAWSUIT", {
                "plaintiff_id": eid,
                "defendant_id": def_cid,
                "lawsuit_type": str(raw_p.get("lawsuit_type", "ANTITRUST")).upper(),
                "claim_millions": 25.0,
            }, fidelity_ok

        if cmd == "ADVISOR_ETF":
            etf_id = int(raw_p.get("etf_id") or (self.engine.etf_corp_ids[0] if self.engine.etf_corp_ids else 1581))
            return "ADVISOR_ETF", {"advisor_id": eid, "etf_id": etf_id}, fidelity_ok

        # 6. Capitalism Lab Brand Strategy, Firm Build & Pricing
        if cmd == "SET_BRAND_STRATEGY":
            strat = str(raw_p.get("brand_strategy", "UNIQUE")).upper()
            if strat not in ("CORPORATE", "RANGE", "UNIQUE"):
                strat = "UNIQUE"
            return "SET_BRAND_STRATEGY", {"corp_id": ctrl_cid or 350, "brand_strategy": strat}, fidelity_ok

        if cmd == "BUILD_FIRM":
            if not ctrl_cid:
                ctrl_cid = 350
            ftype = str(raw_p.get("firm_type") or persona.get("firm_focus") or "FACTORY").upper()
            if ftype not in ("FACTORY", "RETAIL", "RD", "MINE", "OIL", "FOREST", "FARM", "APARTMEN", "COMMERCI", "MALL", "SOFTWARE", "INTERNET", "TELECOM"):
                ftype = persona.get("firm_focus", "FACTORY")
            pcode = str(raw_p.get("product_code") or persona.get("product_focus") or "SMARTPH").upper()
            payload = {
                "owner_corp_id": ctrl_cid,
                "firm_type": ftype,
                "build_code": ftype,
                "city_name": str(raw_p.get("city_name", "New York City")),
                "product_code": pcode,
                "capex_millions": min(25.0, max(5.0, float(raw_p.get("capex_millions", 15.0)))),
                "initial_inventory_millions": 0.0 if ftype in ("RD", "APARTMEN", "MALL", "SOFTWARE") else min(5.0, max(1.0, float(raw_p.get("initial_inventory_millions", 2.0)))),
            }
            return cmd, payload, fidelity_ok

        if cmd == "SET_FIRM_PARAMS":
            owned_fids = [f.firm_id for f in self.engine.firms.values() if f.owner_corp_id == ctrl_cid]
            fid = int(raw_p.get("firm_id", owned_fids[0] if owned_fids else 0))
            if fid not in self.engine.firms and owned_fids:
                fid = owned_fids[0]
            if fid in self.engine.firms:
                payload = {
                    "firm_id": fid,
                    "unit_price": float(raw_p.get("unit_price", self.engine.firms[fid].unit_price * 0.97)),
                    "advertising_budget_millions": float(raw_p.get("advertising_budget_millions", 1.2)),
                }
                return cmd, payload, fidelity_ok
            return "BUILD_FIRM", {
                "owner_corp_id": ctrl_cid or 350,
                "firm_type": persona.get("firm_focus", "RETAIL"),
                "build_code": persona.get("firm_focus", "RETAIL"),
                "city_name": "Tokyo",
                "product_code": persona.get("product_focus", "SMARTPH"),
                "capex_millions": 12.0,
                "initial_inventory_millions": 2.0,
            }, fidelity_ok

        # 7. Default WSR Stock / Short commands
        t_cid = int(raw_p.get("target_corp_id") or raw_p.get("corp_id") or default_target)
        if t_cid not in self.engine.entities or not self.engine.entities[t_cid].is_active or t_cid <= 10:
            t_cid = default_target
        px = max(1.0, self.engine.entities[t_cid].stock_price)

        if cmd == "SHORT_STOCK":
            max_sh = (ent.net_worth * 0.35) / px
            req_sh = float(raw_p.get("shares_millions", max_sh * 0.5))
            sh = max(0.0001, min(max_sh, req_sh))
            return "SHORT_STOCK", {"shorter_id": eid, "target_corp_id": t_cid, "shares_millions": round(sh, 5)}, fidelity_ok

        if cmd == "SELL_STOCK" and ent.stock_holdings:
            held_cid = next(iter(ent.stock_holdings.keys()))
            sh = ent.stock_holdings[held_cid] * 0.5
            return "SELL_STOCK", {"seller_id": eid, "target_corp_id": held_cid, "shares_millions": round(sh, 5)}, fidelity_ok

        max_affordable_sh = (ent.cash * 0.45) / (px * 1.02)
        req_sh = float(raw_p.get("shares_millions", max_affordable_sh * 0.6))
        sh = max(0.0001, min(max_affordable_sh, req_sh))
        return "BUY_STOCK", {"buyer_id": eid, "target_corp_id": t_cid, "shares_millions": round(sh, 5)}, fidelity_ok

    def _record_and_execute_batch_result(self, batch_res: Dict[str, Any], mkt_ctx: Optional[Dict[str, Any]] = None) -> None:
        if mkt_ctx is None:
            mkt_ctx = self._build_compact_market_context()
        crec = batch_res["call_record"]
        self.api_call_records.append(crec)
        self.total_prompt_tokens += crec["prompt_tokens"]
        self.total_completion_tokens += crec["completion_tokens"]
        self.total_cost_usd += crec["estimated_cost_usd"]

        with open(self.jsonl_log_path, "a", encoding="utf-8") as jf:
            jf.write(json.dumps(batch_res, ensure_ascii=False) + "\n")

        for dec in batch_res.get("decisions", []):
            eid = int(dec.get("entity_id", 0))
            if eid not in self.engine.investor_personas:
                continue
            persona = self.engine.investor_personas[eid]
            cmd, payload, fidelity_ok = self._normalize_and_validate_decision(eid, dec, mkt_ctx)
            exec_res = self.engine.execute_action(cmd, payload)
            if cmd == "INCORPORATE_STARTUP" and exec_res.get("ok"):
                persona["controlled_corp_id"] = exec_res["startup_corp_id"]

            # Save the 3-quarter conditional playbook on the investor persona
            persona["conditional_playbook"] = {
                "last_cmd": cmd,
                "bull_trigger": str(dec.get("bull_trigger", "")),
                "bear_trigger": str(dec.get("bear_trigger", "")),
                "updated_year": self.engine.year,
                "updated_quarter": self.engine.quarter,
            }

            audit_item = {
                "year": self.engine.year,
                "quarter": self.engine.quarter,
                "entity_id": eid,
                "investor_name": self.engine.entities[eid].name,
                "persona_type": persona["persona_type"],
                "allowed_domains": persona["allowed_domains"],
                "ai_raw_cmd": dec.get("cmd"),
                "executed_cmd": cmd,
                "payload": payload,
                "persona_fidelity_ok": fidelity_ok,
                "execution_ok": bool(exec_res.get("ok")),
                "thesis": str(dec.get("thesis", "")),
                "bull_trigger": str(dec.get("bull_trigger", "")),
                "bear_trigger": str(dec.get("bear_trigger", "")),
                "post_net_worth_millions": round(self.engine.entities[eid].net_worth, 5),
            }
            self.decision_audit_log.append(audit_item)
            self.engine.ai_action_log.append({
                "year": self.engine.year,
                "quarter": self.engine.quarter,
                "actor_id": eid,
                "actor_name": self.engine.entities[eid].name,
                "source": f"LUNA_{persona['persona_type']}",
                "cmd": cmd,
                "target_ticker": str(payload.get("target_corp_id") or payload.get("product_code") or payload.get("commodity_code") or ""),
            })

    def step_all_cohorts_quarterly(self, staggered_mode: bool = False) -> Dict[str, Any]:
        """
        Coordinates the quarterly AI turn across the investor population (up to 320 investors across 24 Archetypes):
          1. Identifies active Smart Archetype Leads (or staggered slice) for gpt-6-luna parallel batch calls.
          2. Executes local DNA-perturbed Conditional Playbooks (< 0.1 ms, 0 API cost) for non-calling smart cohort peers.
          3. Executes local Behavioral Crowd algorithms (< 0.15 ms, 0 API cost) for Bogleheads, Retirees, FOMO Sleepers & WSB YOLO Degens.
          4. Handles AI Respawn Initialization for any smart investor who wiped out and respawned.
        """
        mkt_ctx = self._build_compact_market_context()

        # Select smart leads to call gpt-6-luna
        smart_leads = [
            eid for eid, p in sorted(self.engine.investor_personas.items())
            if p.get("is_smart_luna_agent", True) and p.get("is_archetype_lead", eid <= 2020)
        ]
        if staggered_mode and len(smart_leads) > 10:
            q_mod = (self.engine.year * 4 + self.engine.quarter) % 2
            active_luna_eids = [eid for idx, eid in enumerate(smart_leads) if idx % 2 == q_mod]
        else:
            active_luna_eids = smart_leads

        # Chunk active_luna_eids into parallel batches of up to 5-6 investors per call
        chunk_size = 5
        batches = []
        for i in range(0, len(active_luna_eids), chunk_size):
            chunk = active_luna_eids[i : i + chunk_size]
            batches.append((f"BATCH_{i // chunk_size + 1}_ARCHETYPES_{chunk[0]}_{chunk[-1]}", chunk))

        batch_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            future_map = {
                pool.submit(
                    self._call_luna_batch,
                    bname,
                    [self._build_investor_dossier(eid) for eid in eids],
                    mkt_ctx,
                ): bname
                for bname, eids in batches
            }
            for fut in concurrent.futures.as_completed(future_map):
                batch_results.append(fut.result())

        batch_results.sort(key=lambda x: x["call_record"]["batch_name"])
        for bres in batch_results:
            self._record_and_execute_batch_result(bres, mkt_ctx)

        # Execute Conditional Playbooks locally (0 API cost) for all other smart investors in the 320 ecosystem
        called_set = set(active_luna_eids)
        playbook_moves = 0
        for eid, persona in self.engine.investor_personas.items():
            if persona.get("is_smart_luna_agent") and eid not in called_set:
                res_pb = self.engine.execute_conditional_playbook_for_investor(eid)
                if res_pb.get("ok"):
                    playbook_moves += 1

        # Step Behavioral Savers, Retirees, FOMO Sleepers & WSB YOLO Gamblers (0 API cost)
        beh_res = self.engine.step_behavioral_noise_investors()

        # Check if any Smart Lead needs AI Respawn Initialization
        for eid in active_luna_eids:
            if self.engine.investor_personas[eid].get("needs_smart_ai_init"):
                self.call_luna_for_smart_respawn_init(eid)

        return {
            "ok": True,
            "batches_called": len(batch_results),
            "smart_luna_decisions": len(active_luna_eids),
            "local_playbook_moves": playbook_moves,
            "behavioral_moves": beh_res["behavioral_moves"],
            "respawns": beh_res["respawns"],
        }

    def generate_evaluation_report(self) -> Dict[str, Any]:
        """Generates a comprehensive AI Output Quality, 24-Archetype Fidelity, ROI & Token Cost Report."""
        total_decisions = max(1, len(self.decision_audit_log))
        fidelity_hits = sum(1 for d in self.decision_audit_log if d["persona_fidelity_ok"])
        exec_hits = sum(1 for d in self.decision_audit_log if d["execution_ok"])
        unique_theses = len({d["thesis"] for d in self.decision_audit_log if d["thesis"]})

        persona_summary: Dict[str, List[Dict[str, Any]]] = {}
        for eid, p in sorted(self.engine.investor_personas.items()):
            ent = self.engine.entities[eid]
            init_c = float(p["initial_cash_millions"])
            roi_pct = ((ent.net_worth - init_c) / max(1e-6, init_c)) * 100.0
            persona_summary.setdefault(p["persona_type"], []).append({
                "entity_id": eid,
                "name": ent.name,
                "is_lead": bool(p.get("is_archetype_lead", False)),
                "generation": p["generation"],
                "initial_cash_millions": init_c,
                "final_net_worth_millions": round(ent.net_worth, 5),
                "roi_pct": round(roi_pct, 2),
                "controlled_corp_id": p.get("controlled_corp_id", 0),
                "holdings_count": len(ent.stock_holdings),
                "shorts_count": len(ent.short_positions),
            })

        report = {
            "model_evaluated": self.resolved_model,
            "requested_alias": self.requested_model,
            "total_investor_population": len(self.engine.investor_personas),
            "unique_archetypes_count": len(persona_summary),
            "api_cost_and_latency_summary": {
                "total_api_calls": len(self.api_call_records),
                "total_prompt_tokens": self.total_prompt_tokens,
                "total_completion_tokens": self.total_completion_tokens,
                "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
                "total_estimated_cost_usd": round(self.total_cost_usd, 6),
                "avg_cost_per_quarter_usd": round(self.total_cost_usd / max(1, len(self.api_call_records) // 4), 6),
                "call_records": self.api_call_records,
            },
            "ai_quality_and_diversity_metrics": {
                "total_ai_decisions_evaluated": len(self.decision_audit_log),
                "persona_domain_fidelity_rate_pct": round(100.0 * fidelity_hits / total_decisions, 2),
                "engine_action_execution_success_rate_pct": round(100.0 * exec_hits / total_decisions, 2),
                "unique_strategic_theses_count": unique_theses,
            },
            "bidirectional_wsr_caplab_coupling": self.engine.get_bidirectional_coupling_metrics(),
            "persona_group_outcomes": {
                k: {
                    "members_count": len(v),
                    "avg_roi_pct": round(sum(m["roi_pct"] for m in v) / max(1, len(v)), 2),
                    "lead_sample": v[:2],
                }
                for k, v in persona_summary.items()
            },
            "wipeout_and_respawn_graveyard": self.engine.wipeout_graveyard,
            "global_accounting_invariants": self.engine.verify_global_invariants(),
            "decision_audit_log": self.decision_audit_log,
        }
        with open(self.report_path, "w", encoding="utf-8") as rf:
            json.dump(report, rf, indent=2, ensure_ascii=False)
        return report

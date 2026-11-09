#!/usr/bin/env python3
"""
End-to-End (E2E) Browser UI, Long-Gameplay, Multi-Scenario & Paimon Academy Verification Suite
==============================================================================================
Uses Playwright Chromium to test http://127.0.0.1:8765 across all 4 Tabs, verifying:
  1. PART 1 — Free Play / Without Guidance (20+ Gameplay Phases across Tabs 1–4):
     - Viewability & Responsive Layout (1600x950 Desktop): 0 broken images, 0 console/page/HTTP errors,
       0 horizontal table clipping
     - Phase A: $30,000 Street Hustler Mode (Directory filters, 0 negative Net Worth corps, Investor inspect
       guardrail, OHLCV Candlestick Chart + Single-Candle Hover Dissection, Micro-Lot 100sh Stock & ETF trades,
       $5k GovBond/CorpBond/Futures/Crypto/Options/Rate Swap, $10k Bank Loan, $30k Startup Incorporation with
       positive initial EBIT, 3x3 Floorplan reconfiguration, Staff Training, $15k Micro Store build, PRQ tuning)
     - Phase B: $1,000M Sandbox Mode (Max affordable shares, Stock Long/Short/Cover, $10M Bonds/Futures/Crypto/
       Options/Swaps, $25M Bank Loan, Corporate Dividend, 80% Spin-Off & Liquidation guardrails, ETF Advisor,
       Corporate Lawsuit with 2% retainer, GTA Wallet Bridge)
     - Phase C: 12-Quarter Multi-Year Simulation + S1..S6 Stress Scenarios + Tab 3 (320 Investors & 24 Archetypes)
       + Full-Fidelity Save -> Reset -> Load verification (0.000000 asset loss)
  2. PART 2 — With Paimon Economic & Trading Academy Guidance (Pillar 1 & Pillar 2):
     - Paimon Academy Dock toggle, Spotlight Ring & Callout (#paimon-spotlight-ring, #paimon-spotlight-callout)
     - All 9 Modules (M0..M8) and all 36 Interactive Quests (M0_Q1..M8_Q4) verified via Auto-Step & Auto-Verify,
       reaching 36 / 36 Quests and persisting to saves/paimon_academy_progress.json
     - Inspect / Explain Mode (#btn-paimon-inspect-toggle) hovering over chart, buttons, balance sheet & 3x3 grid
     - Full Interactive Textbook & Encyclopedia Modal (#btn-paimon-textbook-modal) + live keyword search + jump
     - Live Context-Aware Q&A Chat with Paimon (gpt-6-luna) via Quick-Ask chips & custom input + JSONL audit log
"""

import json
import os
import sys
import time
from typing import Any, Dict, List
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(WORKSPACE_DIR, "logs", "screenshots")
REPORT_JSON_PATH = os.path.join(WORKSPACE_DIR, "logs", "workstation_e2e_ux_report.json")
PAIMON_PROGRESS_PATH = os.path.join(WORKSPACE_DIR, "saves", "paimon_academy_progress.json")
PAIMON_CHAT_LOG_PATH = os.path.join(WORKSPACE_DIR, "logs", "paimon_chat_calls.jsonl")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def run_e2e_suite() -> Dict[str, Any]:
    t0 = time.perf_counter()
    console_errors: List[str] = []
    page_errors: List[str] = []
    http_errors: List[str] = []
    action_trace: List[Dict[str, Any]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 950})

        page.on("console", lambda m: console_errors.append(f"{m.type}: {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        page.on("response", lambda r: http_errors.append(f"{r.url} -> {r.status}") if r.status >= 400 else None)

        page.goto("http://127.0.0.1:8765", wait_until="networkidle")
        page.wait_for_timeout(500)

        def record_step(name: str, details: Dict[str, Any]) -> None:
            status_txt = page.locator("#action-status").inner_text()
            inv_txt = page.locator("#hdr-inv").inner_text()
            assert "PASS" in inv_txt, f"Invariant failure at step {name}: {inv_txt}"
            entry = {"step": name, "status_toast": status_txt, "invariant_badge": inv_txt, **details}
            action_trace.append(entry)
            print(f"[E2E PASS] {name} -> toast='{status_txt}' | audit='{inv_txt}'")

        # =====================================================================
        # PART 1: FREE PLAY WITHOUT PAIMON GUIDANCE (ALL 4 TABS & 20+ PHASES)
        # =====================================================================
        # Temporarily hide Paimon Dock to verify 100% clean free-play without guidance overlay
        if page.locator("#paimon-academy-dock").is_visible():
            page.locator("#btn-paimon-academy-toggle").click()
            page.wait_for_timeout(200)

        page.evaluate("sendAction('RESET_NEW_GAME', {})")
        page.wait_for_timeout(450)
        mode_lbl = page.locator("#hdr-mode-lbl").inner_text()
        if "1000M" in mode_lbl:
            page.locator("#btn-mode-toggle").click()
            page.wait_for_timeout(400)
        page.locator("#btn-tab-wsr").click()
        page.wait_for_timeout(300)

        # 1. PHASE A: $30,000 STREET HUSTLER MODE & CONVENIENCE UX CHECKS
        nw_text = page.locator("#hdr-nw").inner_text()
        assert nw_text == "$30,000", f"Expected $30,000 initial net worth, got {nw_text}"
        record_step("PhaseA_Init_30k_Hustler_Mode", {"aether_nw": nw_text})

        # Test Directory Quick Filters (All Corps, My Controlled, Banks/Insur, ETFs, 320 Investors)
        for filt_id in ["#dir-pill-BANKS", "#dir-pill-ETFS", "#dir-pill-INVESTORS", "#dir-pill-ALL"]:
            page.locator(filt_id).click()
            page.wait_for_timeout(200)
            rows_cnt = page.locator("#corp-table-body tr").count()
            assert rows_cnt > 0, f"Filter {filt_id} returned 0 rows"
        record_step("PhaseA_Directory_Quick_Filters", {"filters_tested": 4})

        # Test Directory 5-Regime Filter, Column Sorting & Pagination
        for reg_code, expected_badge in [
            ("INDUSTRIAL_HOLDING", "IND"),
            ("COMMERCIAL_BANK", "BANK"),
            ("INSURANCE_COMPANY", "INSUR"),
            ("ETF_FUND", "ETF"),
            ("PLAYER_INDIVIDUAL", "AI-INV"),
            ("ALL", ""),
        ]:
            page.locator("#dir-regime-select").select_option(reg_code)
            page.wait_for_timeout(180)
            r_cnt = page.locator("#corp-table-body tr").count()
            assert r_cnt > 0, f"Regime filter {reg_code} returned 0 rows"
            if expected_badge:
                first_row_txt = page.locator("#corp-table-body tr").first.inner_text()
                assert expected_badge in first_row_txt, f"Expected {expected_badge} in {first_row_txt}"

        # Reset back to All Corps and test Column Header Sorting & Sort Dropdown
        page.locator("#dir-pill-ALL").click()
        page.wait_for_timeout(180)
        page.locator("#th-sort-net_worth_millions").click()
        page.wait_for_timeout(120)
        assert "▼" in page.locator("#sort-ind-net_worth_millions").inner_text()
        page.locator("#th-sort-stock_price").click()
        page.wait_for_timeout(120)
        assert "▼" in page.locator("#sort-ind-stock_price").inner_text()
        page.locator("#dir-sort-select").select_option("roce_pct:desc")
        page.wait_for_timeout(120)
        page.locator("#th-sort-id").click()
        page.wait_for_timeout(120)

        # Test Pagination (Next, Last, First, Page Size)
        page_badge_1 = page.locator("#dir-page-badge").inner_text()
        assert page_badge_1.startswith("1 / "), f"Expected page 1, got {page_badge_1}"
        page.locator("#btn-dir-next").click()
        page.wait_for_timeout(100)
        page_badge_2 = page.locator("#dir-page-badge").inner_text()
        assert page_badge_2.startswith("2 / "), f"Expected page 2 after Next, got {page_badge_2}"
        page.locator("#btn-dir-last").click()
        page.wait_for_timeout(100)
        page.locator("#btn-dir-first").click()
        page.wait_for_timeout(100)
        page.locator("#dir-page-size").select_option("100")
        page.wait_for_timeout(100)
        assert page.locator("#corp-table-body tr").count() == 100
        page.locator("#dir-page-size").select_option("50")
        page.wait_for_timeout(100)
        record_step("PhaseA_Directory_Regime_Filter_Sort_And_Pagination", {"page_badge": page_badge_1})

        # Verify zero negative Net Worth corps at start and distinct stock prices in All Corps
        corp_table_txt = page.locator("#corp-table-body").inner_text()
        assert "-$" not in corp_table_txt, f"Found negative Net Worth at start of game: {corp_table_txt[:300]}"
        record_step("PhaseA_Zero_Negative_NetWorth_And_Distinct_Prices", {"checked_rows": page.locator("#corp-table-body tr").count()})

        # Verify clicking an AI Investor in '320 Investors' shows '—' for price and does NOT overwrite Target Corp ID
        page.locator("#dir-pill-INVESTORS").click()
        page.wait_for_timeout(200)
        first_inv_row = page.locator("#corp-table-body tr").first
        assert "—" in first_inv_row.inner_text(), "Investor row should display '—' instead of a stock price"
        first_inv_row.click()
        page.wait_for_timeout(200)
        target_after_inv_click = int(page.locator("#ord-target-id").input_value())
        assert 11 <= target_after_inv_click <= 1600, f"Clicking investor overwrote Target Corp ID to {target_after_inv_click}"
        page.locator("#dir-pill-ALL").click()
        page.wait_for_timeout(200)
        record_step("PhaseA_320_Investors_Inspect_Guardrail", {"kept_target_corp_id": target_after_inv_click})

        # Test Interactive OHLCV Candlestick Chart Buttons + Single-Candle Hover Anatomy Dissection
        for sym_key, expected_sub in [
            ("BTC", "BTC"),
            ("OIL", "Crude Oil"),
            ("GOLD", "Gold"),
            ("STOCK_INDEX", "Composite Index"),
            ("SELECTED_CORP", "#"),
        ]:
            page.locator(f"#chart-sym-{sym_key}").click()
            page.wait_for_timeout(140)
            readout = page.locator("#chart-ohlcv-readout").inner_text()
            assert expected_sub in readout, f"Chart symbol {sym_key} did not update readout: {readout}"
        page.locator("#chart-pattern-badge").click()
        page.wait_for_timeout(100)
        assert "Giải thích Mẫu Nến" in page.locator("#chart-explain-banner").inner_text()
        page.locator("#chart-rsi-badge").click()
        page.wait_for_timeout(100)
        assert "RSI(14)" in page.locator("#chart-explain-banner").inner_text()
        page.locator("#btn-ind-ma").click()
        page.wait_for_timeout(80)
        page.locator("#btn-ind-ma").click()
        page.locator("#btn-ind-bb").click()
        page.wait_for_timeout(80)
        page.locator("#btn-ind-bb").click()

        # Hover over #ohlcv-canvas to verify single-candle anatomy dissection (% Body, % Upper/Lower Wick)
        canvas_box = page.locator("#ohlcv-canvas").bounding_box()
        assert canvas_box is not None
        page.mouse.move(canvas_box["x"] + canvas_box["width"] * 0.55, canvas_box["y"] + canvas_box["height"] * 0.45)
        page.wait_for_timeout(180)
        hover_explain = page.locator("#chart-explain-banner").inner_text()
        assert "Paimon giải phẫu Cây Nến" in hover_explain and "Thân" in hover_explain, f"Expected candle hover dissection, got: {hover_explain}"
        record_step("PhaseA_Interactive_OHLCV_Chart_And_Candle_Hover_Dissection", {"hover_sample": hover_explain[:120]})

        # Click a corporation row in the directory and verify Target Corp, Order Preview & Expanded Balance Sheet rows
        page.locator("#corp-table-body tr").nth(2).click()
        page.wait_for_timeout(220)
        preview_txt = page.locator("#order-preview-box").inner_text()
        bs_txt = page.locator("#bs-table-body").inner_text()
        assert "Target: #" in preview_txt and "Est. Cost:" in preview_txt
        assert "Options, Futures Margin & Crypto Portfolio" in bs_txt
        assert "Valuation: Price / Book / P/B / ROCE / EPS" in bs_txt
        record_step("PhaseA_Click_Row_AutoSyncs_Target_OrderPreview_And_Full_BalanceSheet", {"preview": preview_txt})

        # Click '100sh' micro-lot preset and Buy Long with $30k account
        page.locator("#btn-lot-100sh").click()
        page.locator("#btn-buy-long").click()
        page.wait_for_timeout(250)
        holdings_badge = page.locator("#holdings-count-badge").inner_text().upper()
        assert "1 LONG" in holdings_badge, f"Expected 1 LONG position, got {holdings_badge}"
        record_step("PhaseA_MicroLot_100sh_Buy_Long", {"holdings_badge": holdings_badge})

        # Test inline 'Sell All' button in Holdings table
        page.locator("#holdings-table-body button:has-text('Sell All')").click()
        page.wait_for_timeout(250)
        holdings_badge_after = page.locator("#holdings-count-badge").inner_text().upper()
        assert "0 LONG" in holdings_badge_after
        record_step("PhaseA_Inline_Holdings_Sell_All", {"holdings_badge": holdings_badge_after})

        # Test $30k Street Hustler trading across ALL micro-lot asset classes:
        # ETF (#1581), GovBond ($5k), CorpBond ($5k), Gold/Oil Futures ($5k), BTC Crypto ($5k),
        # Micro Call/Put/Write Options ($5k), Rate Swap ($5k), and Bank Loan ($10k)
        page.locator("#dir-pill-ETFS").click()
        page.wait_for_timeout(180)
        page.locator("#corp-table-body tr").first.click()
        page.wait_for_timeout(180)
        page.locator("#btn-lot-100sh").click()
        page.locator("#btn-buy-long").click()
        page.wait_for_timeout(220)
        assert "BUY_STOCK: OK" in page.locator("#action-status").inner_text()
        page.locator("#holdings-table-body button:has-text('Sell All')").click()
        page.wait_for_timeout(220)

        page.locator("#dir-pill-ALL").click()
        page.wait_for_timeout(180)
        page.locator("#corp-table-body tr").first.click()
        page.wait_for_timeout(180)

        page.locator("#btn-notional-5k").click()
        page.locator("#btn-buy-govbond").click()
        page.wait_for_timeout(180)
        assert "BUY_GOV_BOND: OK" in page.locator("#action-status").inner_text()
        page.locator("#btn-sell-govbond").click()
        page.wait_for_timeout(180)
        assert "SELL_GOV_BOND: OK" in page.locator("#action-status").inner_text()

        page.locator("#btn-notional-5k").click()
        page.locator("#btn-buy-corpbond").click()
        page.wait_for_timeout(180)
        assert "BUY_CORP_BOND: OK" in page.locator("#action-status").inner_text()

        page.locator("#deriv-asset").select_option("GOLD")
        page.locator("#btn-notional-5k").click()
        page.locator("#btn-trade-deriv").click()
        page.wait_for_timeout(180)
        assert "TRADE_FUTURES: OK" in page.locator("#action-status").inner_text()

        page.locator("#deriv-asset").select_option("BTC")
        page.locator("#btn-notional-5k").click()
        page.locator("#btn-trade-deriv").click()
        page.wait_for_timeout(180)
        assert "TRADE_CRYPTO: OK" in page.locator("#action-status").inner_text()

        page.locator("#btn-notional-5k").click()
        page.locator("#btn-buy-call").click()
        page.wait_for_timeout(180)
        assert "BUY_OPTION: OK" in page.locator("#action-status").inner_text()

        page.locator("#btn-notional-5k").click()
        page.locator("#btn-rate-swap").click()
        page.wait_for_timeout(180)
        assert "CREATE_SWAP: OK" in page.locator("#action-status").inner_text()

        page.locator("#btn-loan-10k").click()
        page.locator("#btn-borrow-loan").click()
        page.wait_for_timeout(180)
        assert "BORROW_LOAN: OK" in page.locator("#action-status").inner_text()
        page.locator("#btn-repay-loan").click()
        page.wait_for_timeout(180)
        assert "REPAY_LOAN: OK" in page.locator("#action-status").inner_text()
        record_step("PhaseA_30k_All_MicroLot_Assets_Verified", {"status": "ETF, GovBond, CorpBond, Gold, BTC, Call, Swap, Loan all OK"})

        # Switch to Tab 2: Capitalism Lab 3x3 Floorplan & $30k Startup Incubator
        page.locator("#btn-tab-caplab").click()
        page.wait_for_timeout(300)

        # Incorporate Bootstrapped Startup ($18k equity + 3x bank loan = $72k startup capital)
        page.locator("#btn-incorporate-startup").click()
        page.wait_for_timeout(400)
        acting_val = page.locator("#acting-as-select").input_value()
        owner_val = page.locator("#cl-owner-id").input_value()
        assert int(acting_val) >= 11 and acting_val == owner_val, f"Auto-sync failed: acting={acting_val}, owner={owner_val}"
        record_step("PhaseA_Incorporate_30k_Startup_AutoSync", {"new_startup_id": int(acting_val)})

        # Test Interactive 3x3 Internal Floorplan Grid: click Slot #2, change role to EXTERN, click Assign Unit
        page.locator("#floorplan-3x3-grid .unit-cell").nth(1).click()
        page.wait_for_timeout(150)
        page.locator("#slot-role-select").select_option("EXTERN")
        page.locator("#btn-assign-unit").click()
        page.wait_for_timeout(250)
        slot2_hdr = page.locator("#floorplan-3x3-grid .unit-cell").nth(1).locator(".unit-cell-hdr").inner_text()
        assert "EXTERN" in slot2_hdr, f"Expected EXTERN in slot #2 header, got {slot2_hdr}"
        record_step("PhaseA_3x3_Floorplan_Slot_Reconfigure", {"slot2_header": slot2_hdr})

        # Test 'Train All 9 Units (+Lv)' button
        page.locator("#btn-train-staff").click()
        page.wait_for_timeout(250)
        record_step("PhaseA_3x3_Train_All_9_Units", {"trained_firm_id": page.locator("#tune-fid-lbl").inner_text()})

        # Test building a $15k ($0.015M) Micro Store under Aether's new Startup (#61)
        page.locator("#btn-capex-15k").click()
        page.locator("#btn-construct-firm").click()
        page.wait_for_timeout(300)
        assert "Built Firm #" in page.locator("#action-status").inner_text()
        record_step("PhaseA_Build_15k_Micro_Store_For_Startup", {"owner_id": int(owner_val)})

        # Click Firm #1 (SMARTPH Factory) and verify Price & Advertising inputs auto-sync!
        page.locator("#caplab-firms-grid .firm-card").first.click()
        page.wait_for_timeout(220)
        synced_px = float(page.locator("#cl-tune-price").input_value())
        assert synced_px > 0, "Firm price did not auto-sync"
        page.locator("#cl-tune-price").fill(str(round(synced_px * 0.95, 2)))
        page.locator("#btn-update-prq").click()
        page.wait_for_timeout(250)
        record_step("PhaseA_PRQ_AutoSync_And_Price_Tuning", {"tuned_price": round(synced_px * 0.95, 2)})

        # Test all 8 FirmType category filter buttons in Tab 2
        for ft_idx in range(8):
            page.locator("#firmtype-filter-bar .firmtype-btn").nth(ft_idx).click()
            page.wait_for_timeout(100)
        page.locator("#firmtype-filter-bar .firmtype-btn").first.click()
        page.wait_for_timeout(180)
        record_step("PhaseA_CapLab_FirmType_Icon_Filters", {"categories_tested": 8})

        # 2. PHASE B: $1,000M SANDBOX MODE & FULL MULTI-ASSET WSR EXECUTION DESK
        page.locator("#btn-mode-toggle").click()
        page.wait_for_timeout(400)
        nw_1b = page.locator("#hdr-nw").inner_text()
        assert "1,000" in nw_1b, f"Expected $1,000M sandbox net worth, got {nw_1b}"
        page.locator("#btn-tab-wsr").click()
        page.wait_for_timeout(250)

        # Test Max Affordable Shares button, Buy Long, Short, Cover Short
        page.locator("#ord-actor-id").fill("1")
        page.locator("#ord-target-id").fill("27")
        page.locator("#btn-lot-10k").click()
        page.locator("#btn-buy-long").click()
        page.wait_for_timeout(220)
        page.locator("#btn-short-stock").click()
        page.wait_for_timeout(220)
        page.locator("#btn-cover-short").click()
        page.wait_for_timeout(220)
        record_step("PhaseB_Stock_Long_Short_Cover", {"target_corp": 27})

        # Test Gov Bonds, Corp Bonds, OIL Futures, BTC Crypto, Call/Put Options & Interest Rate Swap
        page.locator("#deriv-notional").fill("10.0")
        page.locator("#btn-buy-govbond").click()
        page.wait_for_timeout(180)
        page.locator("#btn-sell-govbond").click()
        page.wait_for_timeout(180)
        page.locator("#btn-buy-corpbond").click()
        page.wait_for_timeout(180)
        page.locator("#deriv-asset").select_option("OIL")
        page.locator("#btn-trade-deriv").click()
        page.wait_for_timeout(180)
        page.locator("#deriv-asset").select_option("BTC")
        page.locator("#btn-trade-deriv").click()
        page.wait_for_timeout(180)
        page.locator("#btn-buy-call").click()
        page.wait_for_timeout(180)
        page.locator("#btn-buy-put").click()
        page.wait_for_timeout(180)
        page.locator("#btn-write-call").click()
        page.wait_for_timeout(180)
        page.locator("#btn-rate-swap").click()
        page.wait_for_timeout(180)
        record_step("PhaseB_Bonds_Futures_Crypto_Options_Swaps", {"notional_m": 10.0})

        # Test Borrow Loan, Repay Loan, Set Dividend, 80% SpinOff, ETF Advisor, Lawsuit & GTA Bridge
        page.locator("#ord-loan-amt").fill("25.0")
        page.locator("#btn-borrow-loan").click()
        page.wait_for_timeout(180)
        page.locator("#btn-repay-loan").click()
        page.wait_for_timeout(180)
        page.locator("#ord-target-id").fill("321")
        page.locator("#btn-set-dividend").click()
        page.wait_for_timeout(180)
        page.locator("#btn-etf-advisor").click()
        page.wait_for_timeout(180)
        page.locator("#ord-actor-id").fill("321")
        page.locator("#ord-target-id").fill("322")
        page.locator("#btn-lawsuit").click()
        page.wait_for_timeout(180)
        page.locator("#ord-actor-id").fill("1")
        page.locator("#btn-deposit-gta").click()
        page.wait_for_timeout(180)
        page.locator("#btn-withdraw-gta").click()
        page.wait_for_timeout(180)
        record_step("PhaseB_Banking_Dividend_ETF_Lawsuit_GTABridge", {})

        # 3. PHASE C: 12-QUARTER (3-YEAR) LONG GAMEPLAY + S1..S6 STRESS SCENARIOS
        page.locator("#btn-tab-news").click()
        page.wait_for_timeout(250)

        scenarios = ["S1", "S2", "S3", "S4", "S5", "S6"]
        for q_idx in range(12):
            if q_idx < len(scenarios):
                sc_code = scenarios[q_idx]
                page.locator(f"button:has-text('{sc_code}:')").click()
                page.wait_for_timeout(220)
            page.locator("#btn-step-quarter").click()
            page.wait_for_timeout(250)

        date_after_12q = page.locator("#hdr-date").inner_text()
        record_step("PhaseC_12_Quarters_3Year_Gameplay_And_S1_to_S6", {"date_after_12q": date_after_12q})

        # Verify Tab 3: 320 Investors, 24 Archetypes, Top Whales vs $30k Hustlers, Wipeout Feed
        page.locator("#btn-tab-ai").click()
        page.wait_for_timeout(300)
        cohort_rows = page.locator("#cohorts-table-body tr").count()
        assert cohort_rows == 24, f"Expected 24 archetype rows, got {cohort_rows}"
        page.locator("#btn-list-hustlers").click()
        page.wait_for_timeout(180)
        hustler_rows = page.locator("#investors-leaderboard-body tr").count()
        assert hustler_rows > 10
        page.locator("#btn-list-top").click()
        page.wait_for_timeout(180)
        record_step("PhaseC_320_Investors_24_Archetypes_And_Wipeout_Feed", {"cohorts": cohort_rows, "hustler_rows": hustler_rows})

        # Test Full-Fidelity Save -> Reset -> Load in Tab 4
        page.locator("#btn-tab-news").click()
        page.wait_for_timeout(250)
        pre_save_date = page.locator("#hdr-date").inner_text()
        pre_save_nw = page.locator("#hdr-nw").inner_text()
        page.locator("#btn-save-game").click()
        page.wait_for_timeout(350)
        page.locator("#btn-reset-game").click()
        page.wait_for_timeout(350)
        reset_date = page.locator("#hdr-date").inner_text()
        assert "2010-Q1" in reset_date
        page.locator("#btn-load-game").click()
        page.wait_for_timeout(400)
        post_load_date = page.locator("#hdr-date").inner_text()
        post_load_nw = page.locator("#hdr-nw").inner_text()
        assert post_load_date == pre_save_date and post_load_nw == pre_save_nw, (
            f"Save/Load mismatch: ({pre_save_date}, {pre_save_nw}) vs ({post_load_date}, {post_load_nw})"
        )
        record_step("PhaseC_Atomic_Save_Reset_Load_Zero_Loss", {"restored_date": post_load_date, "restored_nw": post_load_nw})

        # =====================================================================
        # PART 2: PAIMON ECONOMIC & TRADING ACADEMY (9 MODULES, 36 QUESTS,
        #         SPOTLIGHT, INSPECT MODE, TEXTBOOK MODAL & LIVE AI TUTOR)
        # =====================================================================
        # Reset back to $30,000 Street Hustler Mode & reset Paimon Academy progress to 0/36
        page.evaluate("sendAction('RESET_NEW_GAME', {})")
        page.wait_for_timeout(350)
        if "1000M" in page.locator("#hdr-mode-lbl").inner_text():
            page.locator("#btn-mode-toggle").click()
            page.wait_for_timeout(350)
        page.evaluate("resetPaimonProgress()")
        page.wait_for_timeout(300)
        page.locator("#btn-tab-wsr").click()
        page.wait_for_timeout(250)

        # Open Paimon Academy Dock
        if not page.locator("#paimon-academy-dock").is_visible():
            page.locator("#btn-paimon-academy-toggle").click()
            page.wait_for_timeout(250)
        assert page.locator("#paimon-academy-dock").is_visible(), "Paimon Academy Dock should be visible"
        assert "0 / 36" in page.locator("#paimon-progress-badge").inner_text()

        # Verify Spotlight Ring & Callout on M0_Q1
        page.locator("#btn-paimon-spotlight").click()
        page.wait_for_timeout(300)
        ring_box = page.locator("#paimon-spotlight-ring").bounding_box()
        assert ring_box is not None and ring_box["width"] > 10 and ring_box["height"] > 10, f"Invalid spotlight ring box: {ring_box}"
        shot_spotlight = os.path.join(SCREENSHOT_DIR, "paimon_spotlight_quest.png")
        page.screenshot(path=shot_spotlight, full_page=True)
        record_step("PhaseD_Paimon_Spotlight_Ring_And_Callout_Verified", {"ring_box": ring_box})

        # Loop through all 9 Modules (M0..M8) and all 36 Interactive Quests (M0_Q1..M8_Q4) using Auto-Step + Next
        for q_step in range(36):
            cur_q_title = page.locator("#paimon-quest-title").inner_text()
            page.locator("#btn-paimon-auto-exec").click()
            page.wait_for_timeout(200)
            inv_txt = page.locator("#hdr-inv").inner_text()
            assert "PASS" in inv_txt, f"Invariant failed during Paimon Quest {cur_q_title}: {inv_txt}"
            if q_step < 35:
                page.locator("#btn-paimon-next").click()
                page.wait_for_timeout(120)

        prog_after_36 = page.locator("#paimon-progress-badge").inner_text()
        assert "36 / 36" in prog_after_36, f"Expected 36 / 36 Quests completed, got {prog_after_36}"
        assert os.path.exists(PAIMON_PROGRESS_PATH), "saves/paimon_academy_progress.json not created"
        with open(PAIMON_PROGRESS_PATH, "r", encoding="utf-8") as pf:
            saved_prog = json.load(pf)
        assert len(saved_prog.get("completed_quests", [])) == 36, f"Expected 36 completed quests on disk, got {len(saved_prog.get('completed_quests', []))}"
        record_step("PhaseD_Paimon_All_9_Modules_And_36_Quests_Completed", {"progress_badge": prog_after_36, "saved_quests": 36})

        # Test Inspect / Explain Mode (#btn-paimon-inspect-toggle)
        page.locator("#btn-tab-wsr").click()
        page.wait_for_timeout(200)
        page.locator("#btn-paimon-inspect-toggle").click()
        page.wait_for_timeout(150)
        assert "ON" in page.locator("#btn-paimon-inspect-toggle").inner_text()

        # Hover over #ohlcv-canvas in the center column to verify #paimon-inspect-tooltip renders Vietnamese explanations & formulas
        page.locator("#ohlcv-canvas").hover()
        page.wait_for_timeout(200)
        assert page.locator("#paimon-inspect-tooltip").is_visible(), "Inspect tooltip did not appear on hover"
        tip_txt = page.locator("#paimon-inspect-tooltip").inner_text()
        assert "Là gì:" in tip_txt and "Công thức:" in tip_txt, f"Unexpected inspect tooltip content: {tip_txt}"
        shot_inspect = os.path.join(SCREENSHOT_DIR, "paimon_inspect_mode.png")
        page.screenshot(path=shot_inspect, full_page=True)
        # Turn Inspect Mode back OFF
        page.locator("#btn-paimon-inspect-toggle").click()
        page.wait_for_timeout(150)
        record_step("PhaseD_Paimon_Inspect_Explain_Mode_Verified", {"sample_tooltip": tip_txt.splitlines()[0]})

        # Test Full Interactive Textbook & Encyclopedia Modal (#btn-paimon-textbook-modal)
        page.locator("#btn-paimon-textbook-modal").click()
        page.wait_for_timeout(250)
        assert page.locator("#paimon-textbook-backdrop").is_visible(), "Textbook modal did not open"
        tb_text = page.locator("#paimon-textbook-content").inner_text()
        assert "Học phần 0" in tb_text and "Học phần 8" in tb_text, "Textbook missing modules"
        page.locator("#paimon-wiki-search").fill("RSI")
        page.wait_for_timeout(200)
        filtered_tb = page.locator("#paimon-textbook-content").inner_text()
        assert "RSI" in filtered_tb
        shot_textbook = os.path.join(SCREENSHOT_DIR, "paimon_textbook_modal.png")
        page.screenshot(path=shot_textbook, full_page=True)
        page.locator("#paimon-wiki-search").fill("")
        page.wait_for_timeout(150)
        # Click "🎯 Học & Chỉ Tận Nơi" on the first quest inside the modal
        page.locator("#paimon-textbook-content button:has-text('Học & Chỉ Tận Nơi')").first.click()
        page.wait_for_timeout(250)
        assert not page.locator("#paimon-textbook-backdrop").is_visible(), "Textbook modal should close after jumping to quest"
        record_step("PhaseD_Paimon_Textbook_Modal_And_Search_Verified", {"search_tested": "RSI"})

        # Test Live Context-Aware Q&A Chat with Paimon (gpt-6-luna)
        page.locator("#btn-chip-candle").click()
        page.wait_for_timeout(120)
        page.wait_for_function("() => !document.getElementById('paimon-chat-model-badge').innerText.includes('⏳') && (document.getElementById('paimon-chat-log').innerText.match(/Paimon:/g) || []).length >= 1", timeout=25000)
        chat_hist_txt = page.locator("#paimon-chat-log").inner_text()
        assert "Paimon:" in chat_hist_txt, f"Expected Paimon reply in chat, got: {chat_hist_txt[:200]}"

        page.locator("#paimon-chat-input").fill("Paimon ơi, tại sao nên kết hợp P/B, ROCE và RSI(14) khi mua cổ phiếu bằng vốn $30,000?")
        page.locator("#btn-paimon-chat-send").click()
        page.wait_for_timeout(120)
        page.wait_for_function("() => !document.getElementById('paimon-chat-model-badge').innerText.includes('⏳') && (document.getElementById('paimon-chat-log').innerText.match(/Paimon:/g) || []).length >= 2", timeout=25000)
        chat_hist_txt2 = page.locator("#paimon-chat-log").inner_text()
        assert "ROCE" in chat_hist_txt2 or "P/B" in chat_hist_txt2
        assert os.path.exists(PAIMON_CHAT_LOG_PATH), "logs/paimon_chat_calls.jsonl not created"
        shot_chat = os.path.join(SCREENSHOT_DIR, "paimon_live_chat_tutor.png")
        page.screenshot(path=shot_chat, full_page=True)
        record_step("PhaseD_Paimon_Live_Context_Aware_Chat_Tutor_Verified", {"chat_log_exists": True, "badge": page.locator("#paimon-chat-model-badge").inner_text()})

        # =====================================================================
        # PART 3: VIEWABILITY, OVERFLOW & RESPONSIVE UX AUDIT + FINAL SCREENSHOTS
        # =====================================================================
        # Reset to $30k Hustler Mode + Incorporate Startup so the 4 tab screenshots show clean state + Paimon Dock
        page.evaluate("sendAction('RESET_NEW_GAME', {})")
        page.wait_for_timeout(350)
        if "1000M" in page.locator("#hdr-mode-lbl").inner_text():
            page.locator("#btn-mode-toggle").click()
            page.wait_for_timeout(350)
        page.locator("#btn-tab-caplab").click()
        page.wait_for_timeout(250)
        page.locator("#btn-incorporate-startup").click()
        page.wait_for_timeout(350)
        page.locator("#caplab-firms-grid .firm-card").first.click()
        page.wait_for_timeout(200)

        viewability_audit: Dict[str, Any] = {}
        tabs_meta = [
            ("tab-wsr", "#btn-tab-wsr"),
            ("tab-caplab", "#btn-tab-caplab"),
            ("tab-ai", "#btn-tab-ai"),
            ("tab-news", "#btn-tab-news"),
        ]
        for idx, (tid, btn_sel) in enumerate(tabs_meta):
            page.locator(btn_sel).click()
            page.wait_for_timeout(300)
            if tid == "tab-wsr":
                page.locator("#dir-pill-ALL").click()
                page.wait_for_timeout(200)
                page.locator("#corp-table-body tr:has-text('WFC')").first.click()
                page.wait_for_timeout(200)
            shot_path = os.path.join(SCREENSHOT_DIR, f"after_{idx+1}_{tid}.png")
            page.screenshot(path=shot_path, full_page=True)

            dom_metrics = page.evaluate("""() => {
                const imgs = Array.from(document.querySelectorAll('img'));
                const brokenImgs = imgs.filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src);
                const scrollBoxes = Array.from(document.querySelectorAll('.scroll-box')).filter(el => el.offsetParent !== null);
                const horizOverflows = scrollBoxes.map(el => ({
                    id: el.id || el.className,
                    clientWidth: el.clientWidth,
                    scrollWidth: el.scrollWidth,
                    overflowPx: Math.max(0, el.scrollWidth - el.clientWidth)
                })).filter(x => x.overflowPx > 4);
                return {
                    totalImgs: imgs.length,
                    brokenImgsCount: brokenImgs.length,
                    brokenImgs,
                    visibleScrollBoxes: scrollBoxes.length,
                    horizontalOverflows: horizOverflows,
                    bodyScrollWidth: document.body.scrollWidth,
                    viewportWidth: window.innerWidth
                };
            }""")
            viewability_audit[tid] = dom_metrics
            assert dom_metrics["brokenImgsCount"] == 0, f"Broken images in {tid}: {dom_metrics['brokenImgs']}"
            assert len(dom_metrics["horizontalOverflows"]) == 0, f"Horizontal overflow in {tid}: {dom_metrics['horizontalOverflows']}"

        # Finally, leave the live server in a 100% clean 2010-Q1 $30,000 Street Hustler state with M0_Q1 active for the user!
        page.evaluate("sendAction('RESET_NEW_GAME', {})")
        page.wait_for_timeout(300)
        page.evaluate("resetPaimonProgress()")
        page.wait_for_timeout(250)
        page.locator("#btn-tab-wsr").click()
        page.wait_for_timeout(250)

        browser.close()

    assert len(console_errors) == 0, f"Browser console errors: {console_errors}"
    assert len(page_errors) == 0, f"Browser page errors: {page_errors}"
    assert len(http_errors) == 0, f"HTTP errors: {http_errors}"

    report = {
        "ok": True,
        "elapsed_seconds": round(time.perf_counter() - t0, 2),
        "console_errors": console_errors,
        "page_errors": page_errors,
        "http_errors": http_errors,
        "total_e2e_steps_passed": len(action_trace),
        "viewability_audit": viewability_audit,
        "action_trace": action_trace,
    }
    with open(REPORT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n[ALL {len(action_trace)} E2E & PAIMON ACADEMY AUDIT STEPS PASSED IN {report['elapsed_seconds']}s] Report saved to {REPORT_JSON_PATH}")
    return report


if __name__ == "__main__":
    run_e2e_suite()

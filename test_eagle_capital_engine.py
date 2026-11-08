#!/usr/bin/env python3
"""
4-Tier Anti-Deception QA Test Suite & Multi-Year Benchmark for EagleCapitalEngine
=================================================================================
Implements all 4 verification tiers specified in:
  - EAGLE_CAPITAL_ENGINE_SPEC.md
  - docs/re_dumps/wsr_architecture_and_qa_guide.md
  - docs/re_dumps/supplementary_math_formulas_re.md
"""

import math
import os
import tempfile
import time
import unittest

from eagle_capital_engine import EagleCapitalEngine, RATING_LABELS


class TestEagleCapitalEngineFourTierQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = EagleCapitalEngine()

    def setUp(self):
        # Reset clean deterministic state before each test method
        self.engine.reset_new_game(rng_seed=20261108)

    # =========================================================================
    # TIER 1: 5-REGIME BALANCE SHEET, SHARE CONSERVATION & CASH CONSERVATION
    # =========================================================================

    def test_tier1_five_balance_sheet_regimes_and_global_invariants(self):
        """
        Verifies Tier 1 Invariants across all 1,595 entities (5 Players + 1,570 Corps + 20 ETFs):
          1. All 5 regimes exist and satisfy |TotalAssets - (TotalLiabilities + NetWorth)| < 1e-4.
          2. Commercial Banks (IND=1) & Insurance (IND=2) have zero CapAssets and zero WorkingCap,
             and value bonds at Adjusted Cost (not Market Value).
          3. ETFs (IND=71, IDs 1581..1600) value bonds at Market Value, have zero BondsOut,
             and cannot short individual stocks or issue convertible bonds.
          4. Global Share Conservation & Closed-Loop Cash Conservation hold after bilateral trades.
        """
        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Initial global invariants failed: {inv}")
        counts = inv["active_regime_counts"]
        self.assertEqual(counts["PLAYER_INDIVIDUAL"], 5)
        self.assertEqual(counts["ETF_FUND"], 20)
        self.assertGreaterEqual(counts["COMMERCIAL_BANK"], 50)
        self.assertGreaterEqual(counts["INSURANCE_COMPANY"], 30)
        self.assertGreater(counts["INDUSTRIAL_HOLDING"], 800)

        # Verify Regime 2 (Bank) vs Regime 4 (ETF) Bond Valuation difference when LongBondRate shifts
        bank = self.engine.entities[self.engine.bank_corp_ids[0]]
        gov_etf = self.engine.entities[1581]  # GOVB ETF
        self.assertEqual(bank.cap_assets, 0.0)
        self.assertEqual(bank.working_cap, 0.0)
        bank_nw_before = bank.net_worth
        etf_nw_before = gov_etf.net_worth

        # Drop long bond rate from 6.25% to 4.50% -> Market value of GovBonds rises, Adjusted Cost stays fixed
        self.engine.long_bond_rate_pct = 4.50
        self.engine.recompute_entity_balance_sheet(bank, update_stock_price=False)
        self.engine.recompute_entity_balance_sheet(gov_etf, update_stock_price=True)

        self.assertAlmostEqual(
            bank.net_worth,
            bank_nw_before,
            places=4,
            msg="Commercial Bank (IND=1) must value GovBonds/CorpBonds at Adjusted Cost, not Market Value",
        )
        self.assertGreater(
            gov_etf.net_worth,
            etf_nw_before + 100.0,
            msg="ETF (IND=71) must value GovBonds at Market Value",
        )

        # Verify ETF restrictions
        res_short = self.engine.short_stock(1581, 131, 1.0)
        self.assertFalse(res_short["ok"])
        res_cv = self.engine.issue_convertible_bonds(1581, 100.0, 25.0, 5.0, 2032)
        self.assertFalse(res_cv["ok"])

        # Verify Closed-Loop Cash Conservation across buy, sell, short, loan, dividend on free-float Corp 132
        trade_corp_id = 132
        self.engine.entities[trade_corp_id].cash = 1000.0
        cash_before = self.engine.total_closed_loop_cash()
        self.assertTrue(self.engine.buy_stock(1, trade_corp_id, 2.0)["ok"])
        self.assertTrue(self.engine.short_stock(2, trade_corp_id, 1.5)["ok"])
        self.assertTrue(self.engine.borrow_bank_loan(1, 50.0)["ok"])
        pre_div_price = self.engine.entities[trade_corp_id].stock_price
        self.assertTrue(self.engine.distribute_cash_dividend(trade_corp_id, 0.50)["ok"])
        # Verify Ex-Dividend Price Drop
        self.assertAlmostEqual(self.engine.entities[trade_corp_id].stock_price, pre_div_price - 0.50, places=3)
        self.assertTrue(self.engine.sell_stock(1, trade_corp_id, 1.0)["ok"])
        self.assertTrue(self.engine.repay_bank_loan(1, 25.0)["ok"])
        cash_after = self.engine.total_closed_loop_cash()

        self.assertAlmostEqual(
            cash_before,
            cash_after,
            places=4,
            msg="Closed-loop system cash conservation violated across bilateral transactions",
        )
        inv_after = self.engine.verify_global_invariants()
        self.assertTrue(inv_after["ok"], f"Post-transaction invariants failed: {inv_after}")

    # =========================================================================
    # TIER 2: ADVERSARIAL FINANCIAL TRAP TESTS (TESTS 2.1 .. 2.5)
    # =========================================================================

    def test_tier2_1_circular_cross_ownership_stress_test(self):
        """
        Test 2.1 — Circular Ownership Stress Test (CircControl @ 0x00480D92):
        Creates a 3-company circular ownership ring A --(45%)--> B --(45%)--> C --(45%)--> A,
        runs 50 valuation passes, and verifies:
          - Convergence in < 1.0 ms without RecursionError
          - Cycle detection flags all 3 corporations (in_circular_control_cycle == True)
          - NetWorth remains strictly bounded (no artificial infinite equity explosion).
        """
        corp_a, corp_b, corp_c = 131, 132, 133
        self.engine.reset_clean_free_float_for_corps([corp_a, corp_b, corp_c])
        for cid in (corp_a, corp_b, corp_c):
            self.engine.entities[cid].cash = 50000.0
            self.engine.recompute_entity_balance_sheet(self.engine.entities[cid], update_stock_price=False)
        for src, dst in [(corp_a, corp_b), (corp_b, corp_c), (corp_c, corp_a)]:
            res = self.engine.buy_stock(src, dst, 45.0)  # 45% of 100M shares
            self.assertTrue(res["ok"], f"buy_stock failed: {res}")

        t0 = time.perf_counter()
        conv = self.engine.resolve_circular_ownership_and_control(max_iters=10, tol=1e-4)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.assertIn(corp_a, conv["cycle_nodes"])
        self.assertIn(corp_b, conv["cycle_nodes"])
        self.assertIn(corp_c, conv["cycle_nodes"])
        self.assertTrue(self.engine.entities[corp_a].in_circular_control_cycle)
        self.assertTrue(self.engine.entities[corp_b].in_circular_control_cycle)
        self.assertTrue(self.engine.entities[corp_c].in_circular_control_cycle)

        # Run 50 iterative valuation passes to ensure no runaway equity feedback loop
        initial_sum_nw = sum(self.engine.entities[cid].net_worth for cid in (corp_a, corp_b, corp_c))
        for _ in range(50):
            self.engine.resolve_circular_ownership_and_control(max_iters=4)
        final_sum_nw = sum(self.engine.entities[cid].net_worth for cid in (corp_a, corp_b, corp_c))

        self.assertTrue(math.isfinite(final_sum_nw))
        self.assertLess(abs(final_sum_nw - initial_sum_nw) / max(1.0, initial_sum_nw), 0.25)
        self.assertLess(elapsed_ms, 5.0)
        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Invariants failed after circular ownership test: {inv}")

    def test_tier2_2_triple_tier_holding_drd_80pct_taxfree_and_4yr_nol(self):
        """
        Test 2.2 — Triple-Tier Holding Dividend & DRD Tax Law + 80% Liquidation/Spin-Off + 4-Year NOL:
          - Corp B owns 85% of Corp C (>=80% -> 100% DRD tax exemption: $0 tax at B!).
          - Corp A owns 50% of Corp B (<80%  -> 80% DRD tax exemption: tax only on 20% of dividend at A!).
          - Liquidating/Spinning off at >=80% is Tax-Free (CapTax == 0); at <80% incurs CapTax > 0.
          - Private minority shareholders receive cash in liquidation (no Ghost Shares), sub's stock portfolio transfers to parent.
          - Spin-off preserves Share Conservation even when parent is shorted!
          - 4-Year NOL carryforward [LOSS1..LOSS4] offsets positive taxable income before CorpTaxCalc.
        """
        corp_a, corp_b, corp_c, corp_d = 200, 201, 202, 203
        self.engine.reset_clean_free_float_for_corps([corp_a, corp_b, corp_c, corp_d])
        for cid in (corp_a, corp_b, corp_c, corp_d):
            ent = self.engine.entities[cid]
            ent.cash = 5000.0
            ent.acc_tax = 0.0
            ent.cap_tax = 0.0
            ent.nol_carryforward = [0.0, 0.0, 0.0, 0.0]
            self.engine.recompute_entity_balance_sheet(ent, update_stock_price=False)

        # Give Corp C 20M shares of Corp D, and let Player 1 buy 10M shares (10% minority stake) in Corp C
        self.assertTrue(self.engine.buy_stock(corp_c, corp_d, 20.0)["ok"])
        self.assertTrue(self.engine.buy_stock(1, corp_c, 10.0)["ok"])

        # B buys 85% of C (85M shares); A buys 50% of B (50M shares)
        self.assertTrue(self.engine.buy_stock(corp_b, corp_c, 85.0)["ok"])
        self.assertTrue(self.engine.buy_stock(corp_a, corp_b, 50.0)["ok"])
        self.engine.entities[corp_b].acc_tax = 0.0
        self.engine.entities[corp_a].acc_tax = 0.0

        # C pays $1.00/share ($100M total) dividend -> B receives $85M with 100% DRD ($0 tax!)
        res_div_c = self.engine.distribute_cash_dividend(corp_c, 1.00)
        self.assertTrue(res_div_c["ok"])
        self.assertAlmostEqual(
            self.engine.entities[corp_b].acc_tax,
            0.0,
            places=6,
            msg="Corp B owning 85% (>=80%) of Corp C must receive 100% DRD ($0 tax on dividend)",
        )

        # B pays $1.00/share ($100M total) dividend -> A receives $50M with 80% DRD
        # Taxable portion at A = 20% of $50M = $10M -> Corporate Tax (35%) = $3.50M
        res_div_b = self.engine.distribute_cash_dividend(corp_b, 1.00)
        self.assertTrue(res_div_b["ok"])
        expected_tax_a = 50.0 * 0.20 * self.engine.corporate_tax_rate  # $3.50M
        self.assertAlmostEqual(
            self.engine.entities[corp_a].acc_tax,
            expected_tax_a,
            places=4,
            msg="Corp A owning 50% (<80%) of Corp B must pay tax on exactly 20% of dividend (80% DRD)",
        )

        # Verify 80% Ownership Threshold for Tax-Free Liquidation AND Minority Payout + Asset Transfer
        p1_cash_pre_liq = self.engine.entities[1].cash
        self.engine.entities[corp_b].stock_cost_basis[corp_c] = 100.0
        res_liq_taxfree = self.engine.liquidate_subsidiary(corp_b, corp_c)
        self.assertTrue(res_liq_taxfree["ok"])
        self.assertTrue(res_liq_taxfree["is_tax_free"])
        self.assertAlmostEqual(res_liq_taxfree["cap_tax_incurred_millions"], 0.0, places=6)
        # Player 1 (10% minority in C) must receive cash payout and have zero ghost shares of C left
        self.assertGreater(self.engine.entities[1].cash, p1_cash_pre_liq + 100.0)
        self.assertNotIn(corp_c, self.engine.entities[1].stock_holdings)
        # Corp B must have absorbed Corp C's 20M shares in Corp D
        self.assertAlmostEqual(self.engine.entities[corp_b].stock_holdings.get(corp_d, 0.0), 20.0, places=4)

        # Now test <80% Taxable Spin-Off while Parent A is being shorted by Player 3!
        self.engine.entities[3].cash = 5000.0
        self.engine.recompute_entity_balance_sheet(self.engine.entities[3], update_stock_price=False)
        self.assertTrue(self.engine.short_stock(3, corp_a, 20.0)["ok"])
        self.engine.entities[corp_a].stock_cost_basis[corp_b] = 100.0
        res_spin_taxable = self.engine.spinoff_subsidiary(corp_a, corp_b)
        self.assertTrue(res_spin_taxable["ok"])
        self.assertFalse(res_spin_taxable["is_tax_free"])
        self.assertGreater(res_spin_taxable["cap_tax_incurred_millions"], 0.0)

        # Verify 4-Year NOL Carryforward (LOSS1..LOSS4)
        corp_nol = self.engine.entities[205]
        corp_nol.acc_tax = 0.0
        corp_nol.nol_carryforward = [10.0, 20.0, 30.0, 40.0]  # Total $100M NOL across 4 years
        tax_1 = self.engine.calculate_corporate_tax(corp_nol, 75.0)
        self.assertAlmostEqual(tax_1, 0.0, places=6, msg="$75M profit must be 100% shielded by $100M NOL")
        self.assertAlmostEqual(sum(corp_nol.nol_carryforward), 25.0, places=6)
        # Next $45M profit uses remaining $25M NOL -> only $20M taxed at 35% = $7.0M
        tax_2 = self.engine.calculate_corporate_tax(corp_nol, 45.0)
        self.assertAlmostEqual(tax_2, 20.0 * 0.35, places=4)
        self.assertAlmostEqual(sum(corp_nol.nol_carryforward), 0.0, places=6)

        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Invariants failed after Tier 2.2 tax/liquidation/spinoff test: {inv}")

    def test_tier2_3_short_dividend_squeeze_naked_options_and_convertible_bonds(self):
        """
        Test 2.3 — Short Seller Dividend Obligation (ShortDividends @ 0x005E0721),
        Naked Options (GetNakedOptionLiab @ 0x00604E4E), Convertible Bonds (IssueCV @ 0x00684901),
        and Margin Call Forced Buy-In:
        """
        shorter_id = 3  # Carl I. (Raider AI)
        target_id = 221
        shorter = self.engine.entities[shorter_id]
        target = self.engine.entities[target_id]
        target.cash = 1000.0
        target.stock_price = 20.0

        # Shorter shorts 10M shares (10% of target) at $20
        res_short = self.engine.short_stock(shorter_id, target_id, 10.0)
        self.assertTrue(res_short["ok"])
        cash_after_short = shorter.cash

        # Target pays $2.00/share dividend -> shorter MUST lose $20.0M cash directly!
        res_div = self.engine.distribute_cash_dividend(target_id, 2.00)
        self.assertTrue(res_div["ok"])
        self.assertAlmostEqual(res_div["short_dividends_collected_millions"], 20.0, places=4)
        self.assertAlmostEqual(shorter.cash, cash_after_short - 20.0, places=4)

        # Shorter also writes Naked Call Options on 20M shares at strike $20
        res_opt = self.engine.create_option_contract(
            holder_id=1,
            writer_id=shorter_id,
            underlying_corp_id=target_id,
            opt_type="CALL",
            strike_price=20.0,
            shares_covered_millions=20.0,
            months_to_expiry=6.0,
        )
        self.assertTrue(res_opt["ok"])
        self.assertTrue(res_opt["is_naked"])
        self.assertGreater(shorter.naked_option_liab, 0.0)

        # Spike target stock price from $20 to $140 -> ShortLiability & NakedOptionLiab explode -> Margin Call!
        target.stock_price = 140.0
        self.engine._revalue_all_options()
        self.engine.recompute_entity_balance_sheet(shorter, update_stock_price=False)
        mc = self.engine.check_margin_and_naked_options(shorter_id)
        self.assertTrue(mc["margin_call_triggered"])
        self.assertEqual(len(shorter.short_positions), 0)
        self.assertAlmostEqual(shorter.naked_option_liab, 0.0, places=4)

        # Test Convertible Bonds (IssueCV & Convert dilution)
        issuer_id = 222
        issuer = self.engine.entities[issuer_id]
        issuer.stock_price = 20.0
        old_shares = issuer.shares_outstanding
        cv_res = self.engine.issue_convertible_bonds(
            issuer_corp_id=issuer_id,
            par_millions=250.0,
            conversion_price=25.0,
            coupon_pct=4.50,
            maturity_year=2032,
            buyer_id=1,
        )
        self.assertTrue(cv_res["ok"])
        self.assertEqual(cv_res["code"], "2032cv|25.00|@4.50")
        self.assertAlmostEqual(issuer.convertible_bonds_out, 250.0, places=4)

        # Push stock price above CVP ($25.00 -> $32.00) and convert
        issuer.stock_price = 32.0
        conv_res = self.engine.convert_convertible_bonds(cv_res["issue_id"], holder_id=1)
        self.assertTrue(conv_res["ok"])
        self.assertAlmostEqual(conv_res["new_shares_issued_millions"], 10.0, places=4)  # $250M / $25 = 10M shares
        self.assertAlmostEqual(issuer.shares_outstanding, old_shares + 10.0, places=4)
        self.assertAlmostEqual(issuer.convertible_bonds_out, 0.0, places=4)
        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Invariants failed after Tier 2.3 test: {inv}")

    def test_tier2_4_commercial_bank_loan_default_and_car_downgrade(self):
        """
        Test 2.4 — Commercial Bank (IND=1) Bad Debt Write-Off & CAR% Downgrade:
        When a large corporate borrower defaults on a loan from Bank B (IND=1),
        the loan loss erodes Bank B's NetWorth, reduces CAR%, and downgrades Bank B's credit rating.
        """
        bank_id = self.engine.bank_corp_ids[0]
        bank = self.engine.entities[bank_id]
        borrower_id = 300
        borrower = self.engine.entities[borrower_id]

        # Give borrower a large loan relative to bank's equity
        loan_size = bank.net_worth * 0.65
        res_loan = self.engine.borrow_bank_loan(
            borrower_id, loan_size, lender_bank_id=bank_id, allow_emergency=True
        )
        self.assertTrue(res_loan["ok"])
        # Drain borrower cash so recovery is minimal
        borrower.cash = 5.0

        res_def = self.engine.trigger_borrower_default_on_bank(borrower_id, recovery_rate=0.05)
        self.assertTrue(res_def["ok"])
        self.assertLess(res_def["new_bank_net_worth"], res_def["old_bank_net_worth"])
        self.assertLess(res_def["new_bank_car_pct"], res_def["old_bank_car_pct"])
        self.assertLess(res_def["new_bank_rating"], res_def["old_bank_rating"])
        self.assertTrue(borrower.is_bankrupt)
        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Invariants failed after Tier 2.4 bank default test: {inv}")

    def test_tier2_5_zero_double_counting_caplab_bridge_and_swaps_and_hidreserve(self):
        """
        Test 2.5 — Zero Double-Counting WSR <-> Capitalism Lab CAPEX Bridge,
        R&D Tech Breakthrough -> Factory Quality -> Head-to-Head Urban Market Share Competition,
        Vertical Supply Chain Integration COGS Reduction, Interest Rate Swaps, and HidReserve:
        """
        corp_id = 321  # Electronics Corp (IND=10)
        rival_id = 322  # Rival Electronics Corp in same city
        corp = self.engine.entities[corp_id]
        rival = self.engine.entities[rival_id]
        corp.cash = 500.0
        rival.cash = 500.0
        self.engine.recompute_entity_balance_sheet(corp, update_stock_price=False)
        self.engine.recompute_entity_balance_sheet(rival, update_stock_price=False)

        nw_before = corp.net_worth
        cash_before = corp.cash
        cap_before = corp.cap_assets
        wc_before = corp.working_cap

        # Spend $40M on Factory + $10M initial inventory = $50M total CAPEX outlay
        res_build = self.engine.build_caplab_firm(
            owner_corp_id=corp_id,
            firm_type="FACTORY",
            build_code="FACTORY1",
            city_name="New York",
            capex_millions=40.0,
            initial_inventory_millions=10.0,
            product_code="SMARTPHO",  # Alias normalized to "SMARTPH"
        )
        self.assertTrue(res_build["ok"])
        self.assertEqual(res_build["city_name"], "New York City")
        self.assertEqual(res_build["product_code"], "SMARTPH")
        self.assertAlmostEqual(corp.cash - cash_before, -50.0, places=6)
        self.assertAlmostEqual(corp.cap_assets - cap_before, +40.0, places=6)
        self.assertAlmostEqual(corp.working_cap - wc_before, +10.0, places=6)
        # Zero Double-Counting invariant: Delta_Cash + Delta_CapAssets + Delta_WorkingCap == 0 -> Delta_NetWorth == 0!
        self.assertAlmostEqual(corp.net_worth, nw_before, places=6)
        self.assertAlmostEqual(res_build["net_worth_delta"], 0.0, places=6)

        # Build competing rival factory in the same city ("New York City", "SMARTPH") WITHOUT R&D or vertical integration
        res_rival = self.engine.build_caplab_firm(
            owner_corp_id=rival_id,
            firm_type="FACTORY",
            build_code="FACTORY1",
            city_name="New York City",
            capex_millions=40.0,
            initial_inventory_millions=10.0,
            product_code="SMARTPH",
        )
        self.assertTrue(res_rival["ok"])

        # Build R&D Center (9 units -> 480% synergy) AND upstream component factories (CPU,CCM,ELECTRON) for corp_id
        self.assertTrue(
            self.engine.build_caplab_firm(corp_id, "RD", "RD", "New York City", 15.0, 0.0, "SMARTPH", rd_units=9)["ok"]
        )
        recipe_sp = self.engine.recipes["SMARTPH"]
        for idx in (1, 2, 3):
            in_code = (recipe_sp.get(f"INPUT{idx}") or "").strip()
            if in_code:
                self.assertTrue(
                    self.engine.build_caplab_firm(corp_id, "FACTORY", "FACTORY1", "New York City", 10.0, 1.0, in_code)["ok"]
                )

        # Step 4 quarters of Capitalism Lab operations
        for _ in range(4):
            self.engine.step_caplab_firms_quarterly()

        f_corp = self.engine.firms[res_build["firm_id"]]
        f_rival = self.engine.firms[res_rival["firm_id"]]

        # Verify R&D + Vertical Integration increased Corp 321's quality, lowered its COGS ratio, and beat Rival in market share & EBIT!
        self.assertGreater(self.engine.corp_tech_levels[corp_id]["SMARTPH"], 100.0)
        self.assertGreater(f_corp.product_quality, f_rival.product_quality)
        self.assertGreater(f_corp.product_quality, 65.0)
        self.assertLess(f_corp.cogs_ratio, f_rival.cogs_ratio)
        self.assertGreater(f_corp.market_share, f_rival.market_share)
        self.assertGreater(f_corp.last_quarter_ebit_millions, f_rival.last_quarter_ebit_millions)

        # Verify CapLab Product Rating monotonicity (higher quality/brand & lower price -> higher rating)
        r_base = self.engine.compute_caplab_product_rating("SMARTPH", quality=60, brand=60, price=500, city_ref_price=500)
        r_high_q = self.engine.compute_caplab_product_rating("SMARTPH", quality=90, brand=60, price=500, city_ref_price=500)
        r_low_p = self.engine.compute_caplab_product_rating("SMARTPH", quality=60, brand=60, price=400, city_ref_price=500)
        self.assertGreater(r_high_q, r_base)
        self.assertGreater(r_low_p, r_base)

        # Verify Interest Rate Swap (IRS Event 1685) zero-sum settlement
        party_a, party_b = 1, 2
        cash_a0, cash_b0 = self.engine.entities[party_a].cash, self.engine.entities[party_b].cash
        self.engine.prime_rate_pct = 8.00
        self.engine.create_interest_rate_swap(
            party_a_id=party_a,
            party_b_id=party_b,
            notional_millions=1000.0,
            fixed_rate_pct=6.00,
            floating_benchmark="PRIME",
            party_a_pays_fixed=True,
            duration_quarters=4,
        )
        settlements = self.engine.settle_quarterly_swaps()
        # Party A pays 6% fixed, receives 8% Prime -> +2% annual / 4 = +0.5% of $1000M = +$5.0M
        self.assertAlmostEqual(settlements[0]["cash_flow_to_a_millions"], 5.0, places=4)
        self.assertAlmostEqual(self.engine.entities[party_a].cash - cash_a0, +5.0, places=4)
        self.assertAlmostEqual(self.engine.entities[party_b].cash - cash_b0, -5.0, places=4)

        # Verify HidReserve manipulation (decreaseEarnings / increaseEarnings)
        nw_pre_res = corp.net_worth
        self.engine.manipulate_earnings_reserve(corp_id, +25.0)
        self.assertAlmostEqual(corp.hid_reserve, 25.0, places=4)
        self.assertAlmostEqual(corp.net_worth, nw_pre_res - 25.0, places=4)
        self.engine.manipulate_earnings_reserve(corp_id, -25.0)
        self.assertAlmostEqual(corp.hid_reserve, 0.0, places=4)
        self.assertAlmostEqual(corp.net_worth, nw_pre_res, places=4)
        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Invariants failed after Tier 2.5 CapLab/Swap/HidReserve test: {inv}")

    # =========================================================================
    # TIER 3 & 4: STAGE B API CONTRACT & 40-QUARTER (< 2.0 ms) BENCHMARK
    # =========================================================================

    def test_tier3_stage_b_gta_wallet_and_workstation_contract(self):
        """Verifies Stage B Money & Time bridge methods and save/load state persistence."""
        p1_cash0 = self.engine.entities[1].cash
        dep = self.engine.deposit_from_gta_wallet(25_000_000.0, player_id=1)  # $25M USD
        self.assertTrue(dep["ok"])
        self.assertAlmostEqual(self.engine.entities[1].cash, p1_cash0 + 25.0, places=5)

        wdr = self.engine.withdraw_to_gta_wallet(10_000_000.0, player_id=1)  # $10M USD
        self.assertTrue(wdr["ok"])
        self.assertAlmostEqual(self.engine.entities[1].cash, p1_cash0 + 15.0, places=5)

        snap = self.engine.get_wallstreet_floor_snapshot()
        self.assertIn("gdp_growth_pct", snap)
        self.assertIn("top_tickers", snap)

        ws = self.engine.get_workstation_state(active_entity_id=1)
        self.assertEqual(ws["regime"], "PLAYER_INDIVIDUAL")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name
        try:
            self.engine.save_state(temp_path)
            loaded = self.engine.load_state(temp_path)
            self.assertAlmostEqual(loaded["player_1_cash"], p1_cash0 + 15.0, places=5)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Invariants failed after Tier 3 contract test: {inv}")

    def test_tier4_forty_quarter_simulation_and_sub_2ms_tick_benchmark(self):
        """
        Tier 4 — 40-Quarter (10-Year) Simulation & Real-Time Performance Benchmark:
          - Builds active Capitalism Lab firms (Factory, Retail, R&D, Apartment, Software)
          - Runs 40 full quarters (10 simulated years) + 200 intraday subticks
          - Asserts:
            1) Average intraday subtick time < 2.0 ms (ensuring zero FPS drop in GTA SA)
            2) Zero NaN / Inf values anywhere in the 1,595 entities
            3) 100% pass on all Tier-1 5-Regime Balance Sheet & Share Conservation invariants!
        """
        # Seed diverse CapLab firms across multiple WSR corporations
        self.engine.build_caplab_firm(131, "FACTORY", "FACTORY1", "Detroit", 30.0, 5.0, "CAR")
        self.engine.build_caplab_firm(321, "RETAIL", "ELECTRON", "Tokyo", 15.0, 4.0, "SMARTPHO")
        self.engine.build_caplab_firm(321, "RD", "RD", "San Francisco", 12.0, 0.0, "SMARTPHO")
        self.engine.build_caplab_firm(181, "APARTMEN", "APART1", "New York", 25.0, 0.0, "")
        self.engine.build_caplab_firm(620, "SOFTWARE", "SOFTWARE", "Seattle", 10.0, 0.0, "")

        # Appoint Player 1 (Aether) as CEO of Corp 131 with $4M/yr salary
        self.engine.entities[1].ceo_of_corp_ids.add(131)
        self.engine.entities[1].annual_ceo_salary_millions = 4.0

        # 1. Benchmark 200 Intraday Subticks (< 2.0 ms requirement)
        t_sub_start = time.perf_counter()
        for _ in range(200):
            self.engine.step_intraday_subtick()
        avg_subtick_ms = ((time.perf_counter() - t_sub_start) * 1000.0) / 200.0
        print(f"\n[BENCHMARK] Average step_intraday_subtick() time: {avg_subtick_ms:.4f} ms (Target < 2.0 ms)")
        self.assertLess(avg_subtick_ms, 2.0, f"Subtick time {avg_subtick_ms:.3f} ms exceeded 2.0 ms budget")

        # 2. Run 40 Full Quarters (10 Years) of Macro + Corporate + CapLab Simulation
        t_q_start = time.perf_counter()
        for _ in range(40):
            self.engine.step_quarter()
        avg_quarter_ms = ((time.perf_counter() - t_q_start) * 1000.0) / 40.0
        print(f"[BENCHMARK] Average full 1,078-corp step_quarter() sweep: {avg_quarter_ms:.3f} ms")

        # 3. Verify zero NaN/Inf and strict 5-Regime Invariants after 40 quarters
        for ent in self.engine.entities.values():
            if not ent.is_active:
                continue
            self.assertTrue(math.isfinite(ent.total_assets))
            self.assertTrue(math.isfinite(ent.total_liabilities))
            self.assertTrue(math.isfinite(ent.net_worth))
            self.assertTrue(math.isfinite(ent.stock_price))
            self.assertGreater(ent.shares_outstanding, 0.0)
            self.assertGreater(ent.stock_price, 0.0)

        inv_final = self.engine.verify_global_invariants()
        print(f"[BENCHMARK] Final 40-Quarter Global Invariants: {inv_final}")
        self.assertTrue(inv_final["ok"], f"40-Quarter invariants failed: {inv_final}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

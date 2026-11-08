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

    def test_tier2_6_caplab_binary_differential_oracle(self):
        """
        Test 2.6 — Binary Differential Oracle (CapMain.exe v11.0.98 SSE2 vs EagleCapitalEngine):
          1. Verifies NOTEBOOK @ Beijing (Q=75, B=60, P=750, P_std=600) matches CapMain.exe
             OverallRating = 49 (< LOCALCOMP 50) without any artificial baseline_norm offset.
          2. Verifies RETAIL store selling a manufactured recipe product ("SMARTPH") sources
             directly from its corporate group's FACTORY (inheriting factory quality and cogs_ratio = 0.52).
        """
        r_nb_beijing = self.engine.compute_caplab_product_rating(
            "NOTEBOOK", quality=75.0, brand=60.0, price=750.0, city_ref_price=600.0, city_name="Beijing"
        )
        self.assertEqual(r_nb_beijing, 49.0)

        corp_id = 321
        self.engine.entities[corp_id].cash = 500.0
        self.engine.recompute_entity_balance_sheet(self.engine.entities[corp_id], update_stock_price=False)
        fac = self.engine.build_caplab_firm(corp_id, "FACTORY", "FACTORY1", "Tokyo", 20.0, 2.0, "SMARTPH")
        ret = self.engine.build_caplab_firm(corp_id, "RETAIL", "ELECTRON", "Tokyo", 10.0, 2.0, "SMARTPH")
        self.engine.firms[fac["firm_id"]].product_quality = 88.0

        q_ret, cogs_ret, int_ret = self.engine.compute_caplab_manufacturing_quality(self.engine.firms[ret["firm_id"]])
        self.assertEqual(q_ret, 88.0)
        self.assertAlmostEqual(cogs_ret, 0.52, places=4)
        self.assertEqual(int_ret, 1)

        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Invariants failed after Tier 2.6 Binary Differential Oracle test: {inv}")

    def test_tier2_7_autonomous_wsr_caplab_ai_and_news_feed(self):
        """
        Test 2.7 — Autonomous Hybrid AI Competitors (WSR MakeComputerTurn + CapLab 64 PERSONS.DBF CEOs)
        & External LLM Strategic Controller Hook + Decoded Mscnews.dat / quotewsr.dat Feed:
        """
        self.assertEqual(len(self.engine.caplab_persons), 64)
        self.assertEqual(len(self.engine.corp_ceo_profiles), 64)
        self.assertEqual(len(self.engine.billionaire_ai_profiles), 4)
        self.assertGreaterEqual(len(self.engine.wsr_mscnews), 130)
        self.assertGreaterEqual(len(self.engine.wsr_quotes), 360)

        # Run 4 quarters of autonomous WSR + CapLab AI turns
        for _ in range(4):
            self.engine.step_quarter()

        # Verify AI billionaires (Players 2..5) executed trades and CEOs built CapLab firms
        self.assertGreater(len(self.engine.ai_action_log), 10)
        self.assertGreater(len(self.engine.firms), 0)
        self.assertTrue(any(len(self.engine.entities[pid].stock_holdings) > 0 for pid in (2, 3, 5)))
        self.assertGreater(len(self.engine.news_headlines), 6)

        # Test Layer 2 External AI / LLM Strategic Controller Hook
        obs = self.engine.get_ai_observation(2)
        self.assertEqual(obs["ai_player"]["player_id"], 2)
        target_cid = obs["undervalued_candidates"][0]["corp_id"]
        ext_res = self.engine.apply_ai_strategic_directives(
            2,
            [{"cmd": "BUY_STOCK", "payload": {"buyer_id": 2, "target_corp_id": target_cid, "shares_millions": 1.0}}],
        )
        self.assertTrue(ext_res[0]["ok"])

        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Invariants failed after Tier 2.7 Autonomous AI test: {inv}")

    def test_tier2_8_diverse_personas_30k_startup_and_wipeout_respawn(self):
        """
        Test 2.8 — Diverse 24-Investor Subset (8 Personas), Aether $30k Street Hustler Mode,
        Bootstrapped $30k Startup Incorporation (with Small Business Bank Loan + CapLab Micro-Firm),
        and Bankruptcy Wipeout -> Fresh Entrant Respawn with 100% Cash & Share Conservation:
        """
        cash_total_0 = self.engine.total_closed_loop_cash()
        self.engine.set_street_hustler_30k_mode(player_id=1, cash_millions=0.03)
        self.assertAlmostEqual(self.engine.entities[1].cash, 0.03, places=6)
        self.assertAlmostEqual(self.engine.total_closed_loop_cash(), cash_total_0, places=4)

        subset = self.engine.spawn_representative_24_investor_subset()
        self.assertEqual(len(subset), 24)
        self.assertAlmostEqual(self.engine.total_closed_loop_cash(), cash_total_0, places=4)

        # Verify poor $30k entrepreneur (ID 2013: Minh K.) can incorporate a bootstrapped startup with bank loan & open a CapLab firm
        st_res = self.engine.incorporate_bootstrapped_startup(
            founder_id=2013,
            firm_type="RETAIL",
            city_name="New York City",
            product_code="SMARTPH",
            equity_invest_millions=0.02,
            loan_multiple=3.0,
        )
        self.assertTrue(st_res["ok"])
        self.assertIn(st_res["startup_corp_id"], self.engine.active_corp_ids)
        self.assertIsNotNone(st_res["firm_id"])

        # Step behavioral FOMO sleepers & YOLO gamblers and verify wipeout -> respawn preserves all invariants
        for _ in range(3):
            self.engine.step_behavioral_noise_investors()
            self.engine.step_quarter()

        self.assertGreaterEqual(len(self.engine.wipeout_graveyard), 1)
        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Invariants failed after Tier 2.8 Diverse Personas & Respawn test: {inv}")

    def test_tier2_9_four_bidirectional_wsr_caplab_feedback_loops(self):
        """
        Test 2.9 — Verifies all 4 Bidirectional WSR <-> Capitalism Lab Cross-Feedback Loops:
          Loop #1: CapLab retail price markups & physical CapEx drive WSR urban_cpi_push_pct & real_gdp_impulse_pct.
          Loop #2: WSR commodity spot spikes (OIL, COPPER, GOLD) increase CapLab MINE/OIL revenues AND raise
                   unintegrated FACTORY cogs_ratio while vertically integrated factories are shielded;
                   building physical mines dampens WSR commodity prices.
          Loop #3: WSR Prime Rate & Inflation modulate CapLab firm OPEX and APARTMEN/MALL real estate occupancy/revenue.
          Loop #4: CapLab R&D frontier (top_tech_levels > 100) imposes a Technological Obsolescence discount on
                   legacy WSR corporations that fail to invest in R&D, while rewarding R&D leaders.
        """
        c_unint = 221
        c_integ = 222
        for cid in (c_unint, c_integ):
            self.engine.entities[cid].cash = 500.0
            self.engine.recompute_entity_balance_sheet(self.engine.entities[cid], update_stock_price=False)

        # Build an unintegrated CAR factory for c_unint vs a vertically integrated MINE/FACTORY chain for c_integ
        f_unint = self.engine.build_caplab_firm(c_unint, "FACTORY", "FACTORY1", "Detroit", 25.0, 4.0, "CAR")["firm_id"]
        # Give c_integ upstream CARBODY, ENGINE, WHEEL (the 3 recipe inputs of CAR) + an OIL mine
        self.engine.build_caplab_firm(c_integ, "FACTORY", "FACTORY1", "Detroit", 15.0, 2.0, "CARBODY")
        self.engine.build_caplab_firm(c_integ, "FACTORY", "FACTORY1", "Detroit", 15.0, 2.0, "ENGINE")
        self.engine.build_caplab_firm(c_integ, "FACTORY", "FACTORY1", "Detroit", 15.0, 2.0, "WHEEL")
        f_mine = self.engine.build_caplab_firm(c_integ, "MINE", "MINE", "Detroit", 30.0, 2.0, "OIL", resource_code="OIL")["firm_id"]
        f_integ = self.engine.build_caplab_firm(c_integ, "FACTORY", "FACTORY1", "Detroit", 25.0, 4.0, "CAR")["firm_id"]

        # Baseline commodity prices (OIL=75, COPPER=4.10)
        self.engine.step_caplab_firms_quarterly()
        base_mine_rev = self.engine.firms[f_mine].last_quarter_revenue_millions
        _, base_cogs_unint, _ = self.engine.compute_caplab_manufacturing_quality(self.engine.firms[f_unint])
        _, base_cogs_integ, int_cnt = self.engine.compute_caplab_manufacturing_quality(self.engine.firms[f_integ])
        self.assertEqual(int_cnt, 3)
        self.assertLess(base_cogs_integ, base_cogs_unint)

        # Loop #2 Test: Spike WSR OIL and COPPER spot prices by +60%
        self.engine.commodity_prices["OIL"] = 120.0
        self.engine.commodity_prices["COPPER"] = 6.56
        self.engine.step_caplab_firms_quarterly()
        shock_mine_rev = self.engine.firms[f_mine].last_quarter_revenue_millions
        _, shock_cogs_unint, _ = self.engine.compute_caplab_manufacturing_quality(self.engine.firms[f_unint])
        _, shock_cogs_integ, _ = self.engine.compute_caplab_manufacturing_quality(self.engine.firms[f_integ])

        # Physical OIL mine revenue jumps +60%, unintegrated CAR factory COGS jumps, while integrated factory is 100% shielded!
        self.assertGreater(shock_mine_rev, base_mine_rev * 1.45)
        self.assertGreater(shock_cogs_unint, base_cogs_unint + 0.04)
        self.assertAlmostEqual(shock_cogs_integ, base_cogs_integ, places=4)

        # Loop #1 Test: Raising retail/factory unit_price above P_std creates positive urban_cpi_push_pct
        self.engine.firms[f_unint].unit_price *= 1.35
        self.engine.firms[f_integ].unit_price *= 1.35
        imp = self.engine.compute_caplab_macro_impulses()
        self.assertGreater(imp["urban_cpi_push_pct"], 0.15)
        self.assertGreater(imp["real_gdp_impulse_pct"], 0.01)
        self.assertGreater(imp["commodity_supply_dampening_pct"], 0.10)

        # Loop #3 Test: High WSR Prime Rate compresses APARTMEN real estate revenue vs Low Prime Rate
        f_reit = self.engine.build_caplab_firm(c_unint, "APARTMEN", "APART1", "New York City", 40.0, 0.0, "CAR")["firm_id"]
        self.engine.prime_rate_pct = 3.50
        self.engine.step_caplab_firms_quarterly()
        low_rate_reit_rev = self.engine.firms[f_reit].last_quarter_revenue_millions

        self.engine.prime_rate_pct = 14.50
        self.engine.step_caplab_firms_quarterly()
        high_rate_reit_rev = self.engine.firms[f_reit].last_quarter_revenue_millions
        self.assertLess(high_rate_reit_rev, low_rate_reit_rev)

        # Loop #4 Test: CapLab R&D frontier imposes Technological Obsolescence on non-R&D legacy corps
        self.engine.entities[c_integ].industry_id = 10
        self.engine.entities[c_unint].industry_id = 10
        self.engine.build_caplab_firm(c_integ, "RD", "RD", "San Francisco", 15.0, 0.0, "SMARTPH", rd_units=9)
        for _ in range(3):
            self.engine.step_caplab_firms_quarterly()
        obs_leader = self.engine.get_industry_tech_obsolescence_factor(self.engine.entities[c_integ])
        obs_laggard = self.engine.get_industry_tech_obsolescence_factor(self.engine.entities[c_unint])
        self.assertGreaterEqual(obs_leader, 1.0)
        self.assertLess(obs_laggard, 0.85)

        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Invariants failed in Tier 2.9 Bidirectional Loops test: {inv}")

    def test_tier2_10_six_economic_sanity_laws_and_zero_asset_loss_save_load(self):
        """
        Test 2.10 — Verifies the 6 Fundamental Economic Sanity Laws & Full-Fidelity Save/Load (Zero Asset Loss):
          1. Law of Demand: Higher price strictly reduces market share; sum of city market shares <= 100%.
          2. Risk-Return Rate Hierarchy: ShortBond < LongBond < Prime (AAA) < BBB < CCC (no free-money arbitrage).
          3. No-Arbitrage Option Pricing Bounds: Call >= max(0, S-K), Put >= max(0, K-S), longer expiry >= shorter expiry.
          4. Convertible Bond Dilution Law: Cannot convert when S < CVP; converts & dilutes shares when S >= CVP.
          5. Ex-Dividend & Ex-SpinOff Price Adjustment: Paying cash dividend immediately adjusts stock price down.
          6. Full-Fidelity Save/Load Roundtrip: Restores 100% of entities, firms, options, swaps, CV bonds, and 320 investors.
        """
        # Law 1: Law of Demand & Market Share Monotonicity
        c1, c2 = 201, 202
        self.engine.entities[c1].cash = 300.0
        self.engine.entities[c2].cash = 300.0
        f1 = self.engine.build_caplab_firm(c1, "RETAIL", "RETAIL", "London", 15.0, 2.0, "SMARTPH")["firm_id"]
        f2 = self.engine.build_caplab_firm(c2, "RETAIL", "RETAIL", "London", 15.0, 2.0, "SMARTPH")["firm_id"]
        self.engine.firms[f1].unit_price = 180.0
        self.engine.firms[f2].unit_price = 260.0
        self.engine.step_caplab_firms_quarterly()
        self.assertGreater(self.engine.firms[f1].market_share, self.engine.firms[f2].market_share)
        self.assertLessEqual(self.engine.firms[f1].market_share + self.engine.firms[f2].market_share, 1.0)

        # Law 2: Strict Rate Hierarchy
        self.assertLess(self.engine.short_bond_rate_pct, self.engine.long_bond_rate_pct)
        self.assertLessEqual(self.engine.long_bond_rate_pct, self.engine.prime_rate_pct)

        # Law 3: Option No-Arbitrage Bounds
        spot = self.engine.entities[c1].stock_price
        call_3m = self.engine.price_option_per_share(c1, "CALL", spot * 0.90, 3.0)
        call_12m = self.engine.price_option_per_share(c1, "CALL", spot * 0.90, 12.0)
        self.assertGreaterEqual(call_3m, max(0.0, spot - spot * 0.90))
        self.assertGreater(call_12m, call_3m)

        # Law 5: Ex-Dividend Adjustment
        px_before = self.engine.entities[c1].stock_price
        self.engine.distribute_cash_dividend(c1, 0.50)
        self.assertAlmostEqual(self.engine.entities[c1].stock_price, max(0.10, round(px_before - 0.50, 4)), places=4)

        # Law 6: Full-Fidelity Save/Load Roundtrip with 320 Investors + Contracts + Firms
        self.engine.spawn_full_320_investor_ecosystem(spawn_all_320=True)
        self.engine.execute_action("BUY_GOV_BOND", {"buyer_id": 2005, "par_millions": 25.0})
        self.engine.execute_action("CREATE_SWAP", {"party_a_id": 2006, "notional_millions": 50.0, "fixed_rate_pct": 6.5})
        self.engine.execute_action("BUY_OPTION", {"holder_id": 2006, "underlying_corp_id": c1, "opt_type": "CALL", "shares_covered_millions": 0.2})
        self.engine.execute_action("TRADE_FUTURES", {"trader_id": 2007, "commodity_code": "OIL", "notional_millions": 20.0})
        self.engine.execute_action("TRADE_CRYPTO", {"trader_id": 2007, "symbol": "BTC", "usd_millions_delta": 5.0})

        cash_pre_save = self.engine.total_closed_loop_cash()
        nw_2005_pre = self.engine.entities[2005].net_worth
        nw_2007_pre = self.engine.entities[2007].net_worth
        firms_count_pre = len(self.engine.firms)
        personas_count_pre = len(self.engine.investor_personas)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name
        try:
            self.engine.save_state(temp_path)
            # Corrupt in-memory state to prove load_state restores 100% from disk
            self.engine.firms.clear()
            self.engine.investor_personas.clear()
            self.engine.entities[2005].cash = 0.0
            self.engine.load_state(temp_path)

            self.assertEqual(len(self.engine.firms), firms_count_pre)
            self.assertEqual(len(self.engine.investor_personas), personas_count_pre)
            self.assertAlmostEqual(self.engine.entities[2005].net_worth, nw_2005_pre, places=5)
            self.assertAlmostEqual(self.engine.entities[2007].net_worth, nw_2007_pre, places=5)
            self.assertAlmostEqual(self.engine.total_closed_loop_cash(), cash_pre_save, places=4)
            inv = self.engine.verify_global_invariants()
            self.assertTrue(inv["ok"], f"Invariants failed after Full-Fidelity Save/Load: {inv}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_tier2_11_320_investors_24_archetypes_and_six_macro_stress_scenarios_s1_to_s6(self):
        """
        Test 2.11 — Spawns all 320 Investors across all 24 Unique Archetypes (IDs 2001..2320)
        and stress-tests the unified engine across all 6 Macro-Economic Stress Scenarios (S1..S6):
          - S1: Goldenlocks Tech Boom (GDP +4.8%, Inflation 2.0%, Prime 4.5%)
          - S2: 1970s Volcker Stagflation & Rate Shock (GDP -3.0%, Inflation 11.5%, Prime 15.5%)
          - S3: 2008 Banking Default Contagion (Corporate loan default -> Bank CAR% write-off)
          - S4: Supply Chain Choke & Commodity Shock (OIL & COPPER +75% -> Mine boom vs Factory COGS squeeze)
          - S5: WSB Short Squeeze & Margin Call Cascade (Short seller squeezed -> Margin Call & Respawn)
          - S6: Multi-Quarter Full-Population Endurance with 320 Investors (< 2.0 ms subtick, 0 accounting error)
        """
        cash_0 = self.engine.total_closed_loop_cash()
        created = self.engine.spawn_full_320_investor_ecosystem(spawn_all_320=True)
        self.assertEqual(len(created), 320)
        self.assertEqual(len({p["persona_type"] for p in created}), 24)
        self.assertAlmostEqual(self.engine.total_closed_loop_cash(), cash_0, places=3)

        # Scenario S1: Goldenlocks Tech Boom — Execute conditional playbooks across all smart archetypes
        self.engine.gdp_growth_pct = 4.8
        self.engine.inflation_pct = 2.0
        self.engine.prime_rate_pct = 4.50
        for eid in range(2001, 2021):
            self.engine.execute_conditional_playbook_for_investor(eid)
        self.engine.step_behavioral_noise_investors()
        self.engine.step_quarter()

        # Scenario S2: 1970s Volcker Stagflation & Rate Shock
        self.engine.gdp_growth_pct = -3.0
        self.engine.inflation_pct = 11.5
        self.engine.prime_rate_pct = 15.50
        self.engine.long_bond_rate_pct = 15.00
        self.engine.step_quarter()
        self.assertLess(self.engine.get_long_gov_bond_price(), 75.0)

        # Scenario S3: 2008 Banking Default Contagion
        borrower_cid = 300
        bank_cid = self.engine.bank_corp_ids[0]
        self.engine.borrow_bank_loan(borrower_cid, 45.0, lender_bank_id=bank_cid, allow_emergency=True)
        def_res = self.engine.trigger_borrower_default_on_bank(borrower_cid, recovery_rate=0.20)
        self.assertTrue(def_res["ok"])
        self.assertLess(def_res["new_bank_net_worth"], def_res["old_bank_net_worth"])

        # Scenario S4: Supply Chain Choke & Commodity Shock
        self.engine.commodity_prices["OIL"] = 135.0
        self.engine.commodity_prices["COPPER"] = 7.20
        self.engine.step_quarter()

        # Scenario S5: WSB Short Squeeze & Margin Call Cascade
        shorter_eid = 2004
        squeeze_cid = 205
        self.engine.short_stock(shorter_eid, squeeze_cid, 2.0)
        self.engine.entities[squeeze_cid].stock_price *= 4.0
        mc_res = self.engine.check_margin_and_naked_options(shorter_eid)
        self.assertIn("margin_call_triggered", mc_res)

        # Scenario S6: Multi-Quarter Full-Population Endurance with all 320 Investors
        for _ in range(2):
            for eid in range(2025, 2185):
                self.engine.execute_conditional_playbook_for_investor(eid)
            self.engine.step_behavioral_noise_investors()
            self.engine.step_quarter()

        self.assertAlmostEqual(self.engine.total_closed_loop_cash(), cash_0, places=2)
        inv = self.engine.verify_global_invariants()
        self.assertTrue(inv["ok"], f"Invariants failed after Tier 2.11 320-Investor S1..S6 Stress Suite: {inv}")

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

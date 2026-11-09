#!/usr/bin/env python3
"""
EagleCapitalEngine — Unified Native Financial & Real-Economy Simulation Engine (Stage A)
========================================================================================
Merges 100% Native mathematical, accounting, financial engineering, and supply-chain models of:
  1. Wall Street Raider (WSR.EXE v8.70 / v10.0.22.3 + ui.dll):
     - 5 Distinct Balance Sheet Regimes (CorpInfoItems @ 0x004266F8 & ui.dll @ 0x10042C54 / 0x1003EFD6):
       1) Industrial / Commercial / Holding Corporations (IND = 3..70)
       2) Commercial Banks (IND = 1, BankAlloc @ 0x0061B266, CAR% credit rating, Demand/CD/Interbank deposits, BadDebtReserves)
       3) Insurance Companies (IND = 2, SubprimeMortgages MBS, InsurReserves float, Adjusted Cost bonds)
       4) Exchange-Traded Funds (IND = 71, IDs 1581..1600, Market Value bonds, Advisor fees, 2x/-2x AdjustLeverage @ 0x0068E391)
       5) Individual Investors / Players (IDs 1..5, Aether + 4 AI Billionaires, AdvancesToCompanies, Personal & Wealth Taxes)
     - Circular Cross-Ownership Resolution (CircControl @ 0x00480D92 & CorpControl @ 0x0041F811):
       Damped Gauss-Seidel iterative valuation & Tarjan/DFS cycle detection preventing infinite recursion & artificial NetWorth inflation.
     - 3-Tier Corporate Tax Law (CorpTaxCalc @ 0x004F9803, Liquidate @ 0x005C1EB1, SpinOff @ 0x005CFAF2):
       * Dividends Received Deduction (DRD): 80% tax-exempt for <80% ownership; 100% tax-exempt for >=80% ownership.
       * 80% Ownership Threshold for Tax-Free Liquidation & Tax-Free Spin-Off (<80% triggers CapTax).
       * 4-Year Net Operating Loss Carryforward (LOSS1..LOSS4).
     - Short Selling Dividends (ShortDividends @ 0x005E0721), Naked Options (GetNakedOptionLiab @ 0x00604E4E),
       and Convertible Bonds (IssueCV @ 0x00684901 / RedeemCV @ 0x00683503).
     - Hidden Reserves (HidReserve) for earnings manipulation (Events 910/920) & Corporate Legal Warfare (Antitrust, Harassment, Greenmail).
     - Interest Rate Swaps (IRS Event 1685: Notional, Fixed vs Floating Prime/LongBond/ShortTBill, quarterly settlement).
  2. Capitalism Lab (CapMain.exe v11.0.98 Release + 7 DLCs: Subsidiary, CityEcoSim, DigitalAge, Banking, Experiment, Service, Smartphone):
     - Zero Double-Counting CAPEX/OPEX Bridge: Firm fixed assets map directly into CapAssets_CapLabFirms and firm inventory into
       WorkingCap_CapLabInventory so Delta_Cash + Delta_CapAssets + Delta_WorkingCap == 0 at CAPEX disbursement.
     - 135 Products (PRODUCT_TYPES), 29 Product Classes, 99 Manufacturing Recipes (Input 1..3 -> Output), 20 Software Types,
       38 R&D Tech Nodes, 9 Natural Resources, 128 Real Cities, and 48 Firm Types.
     - Binary-exact Product Attractiveness Rating (towitem.cpp @ 0x0066A4B2) & City Market Share allocation.
     - CEO Salary & Cash Dividends separating Personal Wallet (Aether GTA Wallet bridge) vs Corporate Treasury.
"""

from __future__ import annotations

import copy
import json
import math
import os
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "eagle_wsr_caplab_db.json"
)

# Credit Rating Constants (WSR GetCredRating @ 0x0042B809)
RATING_LABELS = {
    10: "AAA",
    9: "AA",
    8: "A",
    7: "BBB",
    6: "BB",
    5: "B",
    4: "CCC",
    3: "CC",
    2: "C",
    1: "D",
    0: "D",
}

RATING_LOAN_SPREAD = {
    10: 0.00,
    9: 0.25,
    8: 0.50,
    7: 1.00,
    6: 1.50,
    5: 2.00,
    4: 3.00,
    3: 4.00,
    2: 5.00,
    1: 7.00,
    0: 7.00,
}

RATING_BOND_SPREAD = {
    10: 0.50,
    9: 0.85,
    8: 1.35,
    7: 2.10,
    6: 3.50,
    5: 5.25,
    4: 7.50,
    3: 10.50,
    2: 14.00,
    1: 20.00,
    0: 25.00,
}

RATING_CREDIT_LINE_MULT = {
    10: 1.00,
    9: 1.00,
    8: 1.00,
    7: 1.00,
    6: 0.85,
    5: 0.75,
    4: 0.67,
    3: 0.50,
    2: 0.50,
    1: 0.00,
    0: 0.00,
}

# WSR GetOptionPrice (VA 0x0060143F) Standard ATM Time Premium Lookup Table (0..24 months)
WSR_OPTION_BASE_PCT = [
    0.0300, 0.0400, 0.0560, 0.0798, 0.1000, 0.1114, 0.1271, 0.1360, 0.1476,
    0.1569, 0.1648, 0.1726, 0.1864, 0.1919, 0.1962, 0.2083, 0.2114, 0.2148,
    0.2245, 0.2279, 0.23095, 0.2424, 0.2455, 0.2486, 0.2571,
]

# Capitalism Lab JobRD 3x3 Unit Team Synergy Multiplier Table (CapMain.exe @ VA 0x008D0818, 1..9 units in %)
CAPLAB_RD_SYNERGY_MULT = [100, 170, 240, 295, 350, 390, 430, 455, 480]

CAPLAB_PRODUCT_ALIASES = {
    "SMARTPHO": "SMARTPH",
    "SMARTPHONE": "SMARTPH",
    "AUTOMOBILE": "CAR",
    "COMPUTER": "NOTEBOOK",
}

CAPLAB_CITY_ALIASES = {
    "NEW YORK": "New York City",
    "NYC": "New York City",
    "LOS ANGELES": "Los Angeles",
    "SAN FRANCISCO": "San Francisco",
}

CAPLAB_TECH_ALIASES = {
    "CLOUD_COMP": "VIDEO_ST",
    "CLOUD": "VIDEO_ST",
}


@dataclass
class OptionContract:
    contract_id: int
    holder_id: int
    writer_id: int  # 0 = Market Maker Pool, >0 = Entity ID (Naked or Covered Writer)
    underlying_corp_id: int
    opt_type: str  # "CALL" or "PUT"
    strike_price: float
    shares_covered: float  # In millions of shares
    months_to_expiry: float
    is_naked: bool = False
    premium_paid_millions: float = 0.0
    current_value_millions: float = 0.0


@dataclass
class ConvertibleBondIssue:
    issue_id: int
    issuer_corp_id: int
    code: str  # Format: "YYYYcv|CVP|@cc.cc"
    maturity_year: int
    conversion_price: float
    coupon_pct: float
    par_outstanding_millions: float
    holders: Dict[int, float] = field(default_factory=dict)  # holder_id -> par_millions (0 = public market)


@dataclass
class InterestRateSwapContract:
    swap_id: int
    party_a_id: int
    party_b_id: int  # 0 = Global Bank/Market Maker, or specific Corp/Bank ID
    notional_millions: float
    fixed_rate_pct: float
    floating_benchmark: str  # "PRIME", "LONG_BOND", "SHORT_TBILL"
    party_a_pays_fixed: bool
    remaining_quarters: int


@dataclass
class LawsuitCase:
    case_id: int
    plaintiff_id: int
    defendant_id: int
    lawsuit_type: str  # "ANTITRUST", "HARASSING"
    claim_amount_millions: float
    countdown_ticks: int
    win_probability: float


@dataclass
class CapLabFirm:
    firm_id: int
    owner_corp_id: int
    firm_type: str  # FACTORY, RETAIL, RD, MINE, OIL, FOREST, FARM, APARTMEN, COMMERCI, MALL, SOFTWARE, INTERNET, TELECOM, SERVICE
    build_code: str
    city_name: str
    book_value_millions: float  # Mapped directly into owner's cap_assets_caplab_firms
    inventory_value_millions: float = 0.0  # Mapped directly into owner's working_cap_caplab_inventory
    product_code: str = ""
    recipe_output: str = ""
    tech_code: str = ""
    resource_code: str = ""
    software_code: str = ""
    capacity_utilization: float = 0.85
    product_quality: float = 65.0
    brand_rating: float = 55.0
    unit_price: float = 100.0
    advertising_budget_millions: float = 0.5
    rd_progress: float = 0.0
    rd_units: int = 9  # 1..9 R&D units in 3x3 layout (synergy mult @ 0x008D0818)
    unit_training_level: int = 4  # 1..9 experience/training level
    market_share: float = 0.0
    cogs_ratio: float = 0.58
    integrated_inputs_count: int = 0
    occupancy_rate: float = 0.88
    monthly_operating_Cost_millions: float = 0.25
    last_quarter_revenue_millions: float = 0.0
    last_quarter_ebit_millions: float = 0.0


@dataclass
class FinancialEntity:
    """
    Unified Entity structure supporting all 5 WSR Balance Sheet Regimes:
      - "PLAYER_INDIVIDUAL" (IDs 1..5)
      - "COMMERCIAL_BANK"   (IND = 1)
      - "INSURANCE_COMPANY" (IND = 2)
      - "INDUSTRIAL_HOLDING"(IND = 3..70)
      - "ETF_FUND"          (IND = 71, IDs 1581..1600)
    All monetary fields are in Millions of USD ($M) except per-share prices ($).
    """
    entity_id: int
    name: str
    ticker: str
    regime: str
    industry_id: int
    country_code: int = 1
    is_active: bool = True
    is_bankrupt: bool = False

    # --- Common Liquid & Portfolio Assets ($M) ---
    cash: float = 100.0
    tbills: float = 0.0
    stock_portfolio_value: float = 0.0
    option_portfolio_value: float = 0.0
    commod_mtm: float = 0.0
    commod_margin: float = 0.0
    crypto_portfolio_value: float = 0.0

    # --- Regime 1 (Industrial / Commercial / Holding IND=3..70) Specific Assets ($M) ---
    cap_assets_abstract: float = 0.0
    cap_assets_caplab_firms: float = 0.0
    working_cap_abstract: float = 0.0
    working_cap_caplab_inventory: float = 0.0
    unamortized_goodwill: float = 0.0
    advances_to_subsidiaries: float = 0.0

    # --- Regime 2 (Commercial Bank IND=1) Specific Assets & Liabilities ($M) ---
    biz_loans: float = 0.0
    consumer_loans: float = 0.0
    mortgage_loans: float = 0.0
    bad_debt_reserves: float = 0.0
    demand_deposits: float = 0.0
    cert_deposits: float = 0.0
    interbank_debt: float = 0.0
    advances_to_corps: float = 0.0

    # --- Regime 3 (Insurance Company IND=2) Specific Assets & Liabilities ($M) ---
    subprime_mortgages: float = 0.0
    insur_reserves: float = 0.0

    # --- Bond Holdings ($M): Adjusted Cost (Regimes 2, 3) vs Market Value (Regimes 1, 4, 5) ---
    gov_bonds_par: float = 0.0
    gov_bonds_adj_cost: float = 0.0
    gov_bonds_mkt_value: float = 0.0
    corp_bonds_par: float = 0.0
    corp_bonds_adj_cost: float = 0.0
    corp_bonds_mkt_value: float = 0.0

    # --- Regime 4 (ETF Fund IND=71) Specific Fields ---
    etf_type: str = ""
    advisor_id: int = 0
    advisory_fee_pct: float = 0.40
    leverage_factor: float = 1.0
    target_industries: List[int] = field(default_factory=list)

    # --- Regime 5 (Player / Individual IDs 1..5) Specific Fields ($M) ---
    advances_to_companies: float = 0.0
    ytd_taxable_ordinary: float = 0.0
    realized_cap_gain_loss: float = 0.0
    prepaid_tax: float = 0.0
    income_tax_owed: float = 0.0
    wealth_tax_projected: float = 0.0
    ceo_of_corp_ids: Set[int] = field(default_factory=set)
    annual_ceo_salary_millions: float = 0.0

    # --- Common Liabilities ($M) ---
    bank_loan: float = 0.0
    lender_bank_id: int = 11  # Default lending bank ID (IND=1)
    advances_from_parents: float = 0.0
    straight_bonds_out: float = 0.0
    convertible_bonds_out: float = 0.0
    bond_coupon_pct: float = 6.0
    bond_maturity_year: int = 2018
    short_liability: float = 0.0
    naked_option_liab: float = 0.0
    acc_tax: float = 0.0
    cap_tax: float = 0.0
    hid_reserve: float = 0.0

    # --- Computed Balance Sheet Totals ($M) ---
    total_assets: float = 100.0
    total_liabilities: float = 0.0
    net_worth: float = 100.0

    # --- Equity Share Structure & Valuation ---
    shares_outstanding: float = 100.0  # In millions of shares
    stock_price: float = 10.0
    dividend_payout_pct: float = 20.0
    dividend_per_share: float = 0.20
    credit_rating: int = 10  # 10=AAA .. 1=D
    borrowing_rate_pct: float = 6.0
    credit_line_limit: float = 100.0
    roce_pct: float = 12.0
    management_rating: int = 1

    # --- Earnings & 4-Year Tax Loss Carryforward (LOSS1..LOSS4 in $M) ---
    last_quarter_ebit: float = 0.0
    last_quarter_net_income: float = 0.0
    annual_eps: float = 1.0
    nol_carryforward: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])

    # --- Holdings & Short Positions ---
    # target_corp_id -> shares_held (in millions of shares)
    stock_holdings: Dict[int, float] = field(default_factory=dict)
    # target_corp_id -> cost_basis_millions ($M)
    stock_cost_basis: Dict[int, float] = field(default_factory=dict)
    # target_corp_id -> short_shares (in millions of shares)
    short_positions: Dict[int, float] = field(default_factory=dict)
    # Futures positions: commodity_code -> contracts_signed (+long / -short)
    futures_positions: Dict[str, float] = field(default_factory=dict)
    # Crypto holdings: symbol -> coins
    crypto_holdings: Dict[str, float] = field(default_factory=dict)

    # --- Control & Cross-Ownership Graph ---
    controlled_by_id: int = 0
    in_circular_control_cycle: bool = False

    # --- Capitalism Lab Brand Strategy (VA 0x005A042E: CORPORATE, RANGE, UNIQUE) ---
    brand_strategy: str = "CORPORATE"
    corporate_brand: float = 55.0
    brand_loyalty: float = 0.0

    @property
    def cap_assets(self) -> float:
        if self.regime in ("COMMERCIAL_BANK", "INSURANCE_COMPANY", "ETF_FUND", "PLAYER_INDIVIDUAL"):
            return 0.0
        return self.cap_assets_abstract + self.cap_assets_caplab_firms

    @property
    def working_cap(self) -> float:
        if self.regime in ("COMMERCIAL_BANK", "INSURANCE_COMPANY", "ETF_FUND", "PLAYER_INDIVIDUAL"):
            return 0.0
        return self.working_cap_abstract + self.working_cap_caplab_inventory

    @property
    def bonds_out(self) -> float:
        return self.straight_bonds_out + self.convertible_bonds_out

    @property
    def net_bank_loans_asset(self) -> float:
        return max(0.0, self.biz_loans + self.consumer_loans + self.mortgage_loans - self.bad_debt_reserves)


class EagleCapitalEngine:
    """
    Master Native Simulation Engine uniting Wall Street Raider and Capitalism Lab.
    All internal balance sheets are maintained in Millions of USD ($M) for WSR compatibility,
    while Stage B GTA SA wallet bridges support exact USD ($) and $M conversions.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH, rng_seed: int = 20261108):
        self.db_path = db_path
        self.rng = random.Random(rng_seed)
        with open(db_path, "r", encoding="utf-8") as f:
            self.raw_db = json.load(f)

        # Simulation Clock
        self.year: int = 2010
        self.quarter: int = 1
        self.month: int = 1
        self.day: int = 1
        self.subtick: int = 0
        self.total_subticks: int = 0
        self.total_days: int = 0

        # Global Macroeconomic State (WSR BigLoop & ChangePrime)
        self.gdp_growth_pct: float = 2.8
        self.inflation_pct: float = 2.4
        self.prime_rate_pct: float = 6.50
        self.short_bond_rate_pct: float = 4.75
        self.long_bond_rate_pct: float = 6.25
        self.corporate_tax_rate: float = 0.35
        self.capital_gains_tax_rate: float = 0.20

        # Global Commodity & Crypto Spot Prices
        self.commodity_prices: Dict[str, float] = {
            "OIL": 75.0,
            "GOLD": 2000.0,
            "SILVER": 25.0,
            "WHEAT": 6.50,
            "CORN": 5.20,
            "COPPER": 4.10,
            "STOCK_INDEX": 4500.0,
        }
        self.crypto_prices: Dict[str, float] = {
            "BTC": 65000.0,
            "ETH": 3500.0,
        }

        # Closed-Loop System Pool (Central Bank / Treasury / Tax Authority / Public Float Market Maker)
        # Tracks every dollar entering/leaving private entities so Sum(Delta_Cash_Entities) + Delta_System_Pool == 0
        self.system_pool_cash: float = 1_000_000.0

        # Master Registries
        self.entities: Dict[int, FinancialEntity] = {}
        self.player_ids: List[int] = [1, 2, 3, 4, 5]
        self.investor_personas: Dict[int, Dict[str, Any]] = {}
        self.wipeout_graveyard: List[Dict[str, Any]] = []
        self.active_corp_ids: List[int] = []
        self.bank_corp_ids: List[int] = []
        self.insur_corp_ids: List[int] = []
        self.etf_corp_ids: List[int] = []
        self.public_float_shares: Dict[int, float] = {}  # corp_id -> millions of shares held by anonymous public

        # Financial Contracts
        self.options: Dict[int, OptionContract] = {}
        self.next_option_id: int = 1
        self.convertible_bonds: Dict[int, ConvertibleBondIssue] = {}
        self.next_cv_id: int = 1
        self.swaps: Dict[int, InterestRateSwapContract] = {}
        self.next_swap_id: int = 1
        self.lawsuits: Dict[int, LawsuitCase] = {}
        self.next_lawsuit_id: int = 1

        # Capitalism Lab Real-Economy Registries
        self.industries: Dict[int, Dict[str, Any]] = {}
        self.crosswalk: Dict[int, Dict[str, Any]] = {}
        self.products: Dict[str, Dict[str, Any]] = {}
        self.product_classes: Dict[str, Dict[str, Any]] = {}
        self.recipes: Dict[str, Dict[str, Any]] = {}
        self.software_types: Dict[str, Dict[str, Any]] = {}
        self.tech_nodes: Dict[str, Dict[str, Any]] = {}
        self.natural_resources: Dict[str, Dict[str, Any]] = {}
        self.cities: Dict[str, Dict[str, Any]] = {}
        self.building_specs: Dict[str, Dict[str, Any]] = {}
        self.firms: Dict[int, CapLabFirm] = {}
        self.next_firm_id: int = 1
        # corp_id -> {tech_or_product_code -> level (30..500)}
        self.corp_tech_levels: Dict[int, Dict[str, float]] = {}
        # Global world frontier technology level per product/tech code (ItemInfo - 0x76C, starts at 100.0)
        self.top_tech_levels: Dict[str, float] = {}
        # Range brand ratings: corp_id -> {product_class -> brand_score}
        self.corp_class_brands: Dict[int, Dict[str, float]] = {}

        # Native WSR + Capitalism Lab AI Personas & External LLM Agent Hook
        self.caplab_persons: List[Dict[str, Any]] = []
        self.caplab_billionaires: List[Dict[str, Any]] = []
        self.caplab_companies: List[Dict[str, Any]] = []
        self.billionaire_ai_profiles: Dict[int, Dict[str, Any]] = {}
        self.corp_ceo_profiles: Dict[int, Dict[str, Any]] = {}
        self.enable_autonomous_ai: bool = True
        self.external_ai_hook: Optional[ Any ] = None
        self.ai_action_log: List[Dict[str, Any]] = []

        # Decoded WSR Mscnews.dat (133 items) & quotewsr.dat (366 quotes) + Live Ticker & News Feed
        self.wsr_mscnews: Dict[str, str] = {}
        self.wsr_quotes: List[str] = []
        self.ticker_tape: List[str] = []
        self.news_headlines: List[str] = []

        self._initialize_world()

    # =========================================================================
    # 1. INITIALIZATION & WORLD SETUP
    # =========================================================================

    def _initialize_world(self) -> None:
        # Load CapLab Reference Tables
        cl_tables = self.raw_db["capitalism_lab"]["tables"]
        for r in cl_tables["PRODUCT_CLASSES"]["rows"]:
            self.product_classes[r["CLASS"]] = r
        for r in cl_tables["PRODUCT_TYPES"]["rows"]:
            self.products[r["CODE"]] = r
            self.top_tech_levels[r["CODE"]] = 100.0
        for r in cl_tables["MANUFACTURING"]["rows"]:
            self.recipes[r["OUTPUT"]] = r
        for r in cl_tables["SOFTWARE_TYPES"]["rows"]:
            self.software_types[r["CODE"]] = r
            self.top_tech_levels[r["CODE"]] = 100.0
        for r in cl_tables["TECH"]["rows"]:
            self.tech_nodes[r["CODE"]] = r
            self.top_tech_levels[r["CODE"]] = 100.0
        for r in cl_tables["NATURAL_RESOURCES"]["rows"]:
            self.natural_resources[r["ITEM_CODE"]] = r
        for r in cl_tables["CITIES"]["rows"]:
            self.cities[r["NAME"]] = r
        for r in cl_tables["FBUILDSTD"]["rows"]:
            self.building_specs[r["BUILDCODE"]] = r

        # Load Capitalism Lab 64 AI CEO Personas (PERSONS.DBF), BILLIONAIRES.DBF & COMPANIES.DBF
        if "PERSONS" in cl_tables:
            self.caplab_persons = copy.deepcopy(cl_tables["PERSONS"]["rows"])
        if "BILLIONAIRES" in cl_tables:
            self.caplab_billionaires = copy.deepcopy(cl_tables["BILLIONAIRES"]["rows"])
        if "COMPANIES" in cl_tables:
            self.caplab_companies = copy.deepcopy(cl_tables["COMPANIES"]["rows"])

        # Load Decoded WSR Mscnews.dat & quotewsr.dat
        self.wsr_mscnews = copy.deepcopy(self.raw_db["wsr"].get("mscnews_items", {}))
        self.wsr_quotes = copy.deepcopy(self.raw_db["wsr"].get("quotes", []))

        # Load WSR Industries (1..71) & Supply-Chain Crosswalk
        for k, v in self.raw_db["wsr"]["industries"].items():
            ind_id = int(k)
            self.industries[ind_id] = copy.deepcopy(v)
            self.industries[ind_id]["roce_pct"] = 12.0 + 0.35 * float(v.get("growth_rate_pct", 5))
            self.industries[ind_id]["total_capacity"] = 1000.0
            self.industries[ind_id]["total_demand"] = 1140.0

        for k, v in self.raw_db.get("industry_supply_chain_crosswalk", {}).items():
            self.crosswalk[int(k)] = v

        # Initialize 5 Individual Players (Regime 5: Entity IDs 1..5)
        player_defs = [
            (1, "Aether (Player)", "AETH", 1000.0),
            (2, "Warren B. (Berkshire AI)", "BRKA", 2500.0),
            (3, "Carl I. (Raider AI)", "ICAH", 1800.0),
            (4, "George S. (Quantum AI)", "SORO", 1800.0),
            (5, "Ken G. (Citadel AI)", "GRIF", 2000.0),
        ]
        for pid, pname, ptick, pcash in player_defs:
            self.entities[pid] = FinancialEntity(
                entity_id=pid,
                name=pname,
                ticker=ptick,
                regime="PLAYER_INDIVIDUAL",
                industry_id=0,
                country_code=1,
                is_active=True,
                cash=pcash,
                total_assets=pcash,
                total_liabilities=0.0,
                net_worth=pcash,
                credit_rating=10,
                borrowing_rate_pct=self.prime_rate_pct,
                credit_line_limit=pcash,
            )

        # Initialize 1,590 WSR Corporations & ETFs (IDs 11..1600)
        for cid_str, cdata in self.raw_db["wsr"]["corporations"].items():
            cid = int(cid_str)
            ind_id = int(cdata.get("industry_id") or 70)
            init = cdata.get("initial_state", {})
            active = bool(init.get("status", 0) == 1)

            if ind_id == 1:
                regime = "COMMERCIAL_BANK"
            elif ind_id == 2:
                regime = "INSURANCE_COMPANY"
            elif ind_id == 71 or cid >= 1581:
                regime = "ETF_FUND"
                ind_id = 71
                active = True
            else:
                regime = "INDUSTRIAL_HOLDING"

            cash_m = max(10.0, float(init.get("cash_millions") or 50.0)) if active else 0.0
            cap_m = max(0.0, float(init.get("capital_assets_millions") or 100.0)) if active else 0.0
            bonds_m = max(0.0, float(init.get("bonds_outstanding_millions") or 0.0)) if active else 0.0
            div_pct = float(init.get("dividend_payout_pct") or 20.0)
            b_coup = float(init.get("bond_coupon_pct") or 6.5)
            b_mat = int(init.get("bond_maturity_year") or 2034)

            ent = FinancialEntity(
                entity_id=cid,
                name=cdata.get("name", f"Corp {cid}"),
                ticker=cdata.get("ticker", f"C{cid}"),
                regime=regime,
                industry_id=ind_id,
                country_code=int(cdata.get("country_code", 1)),
                is_active=active,
                cash=cash_m,
                straight_bonds_out=bonds_m,
                bond_coupon_pct=b_coup,
                bond_maturity_year=b_mat,
                dividend_payout_pct=div_pct,
                shares_outstanding=100.0,
                stock_price=20.0,
            )

            if active:
                if regime == "COMMERCIAL_BANK":
                    # Regime 2: Commercial Bank — NO CapAssets or WorkingCap!
                    base_scale = max(500.0, cash_m + cap_m * 4.0 + bonds_m * 5.0)
                    ent.cash = base_scale * 0.12
                    ent.tbills = base_scale * 0.10
                    ent.biz_loans = base_scale * 0.45
                    ent.consumer_loans = base_scale * 0.20
                    ent.mortgage_loans = base_scale * 0.25
                    ent.bad_debt_reserves = (ent.biz_loans + ent.consumer_loans + ent.mortgage_loans) * 0.02
                    ent.gov_bonds_par = base_scale * 0.15
                    ent.gov_bonds_adj_cost = ent.gov_bonds_par
                    ent.corp_bonds_par = base_scale * 0.08
                    ent.corp_bonds_adj_cost = ent.corp_bonds_par
                    ent.demand_deposits = base_scale * 0.42
                    ent.cert_deposits = base_scale * 0.58
                    ent.interbank_debt = base_scale * 0.08
                    self.bank_corp_ids.append(cid)
                elif regime == "INSURANCE_COMPANY":
                    # Regime 3: Insurance Company — NO CapAssets or WorkingCap!
                    base_scale = max(400.0, cash_m + cap_m * 3.0 + bonds_m * 4.5)
                    ent.cash = base_scale * 0.10
                    ent.tbills = base_scale * 0.12
                    ent.subprime_mortgages = base_scale * 0.15
                    ent.gov_bonds_par = base_scale * 0.35
                    ent.gov_bonds_adj_cost = ent.gov_bonds_par
                    ent.corp_bonds_par = base_scale * 0.30
                    ent.corp_bonds_adj_cost = ent.corp_bonds_par
                    ent.insur_reserves = base_scale * 0.72
                    self.insur_corp_ids.append(cid)
                elif regime == "ETF_FUND":
                    # Regime 4: Exchange-Traded Fund (IDs 1581..1600)
                    nav_m = float(init.get("cash_millions") or 1500.0)
                    ent.etf_type = str(init.get("etf_type") or "SECTOR_EQUITY")
                    ent.target_industries = list(init.get("target_industries") or [])
                    ent.leverage_factor = float(init.get("leverage_factor") or 1.0)
                    ent.advisory_fee_pct = float(init.get("advisory_fee_pct") or 0.40)
                    ent.advisor_id = 11 if self.bank_corp_ids else 0
                    ent.straight_bonds_out = 0.0
                    if ent.etf_type == "GOVT_BOND":
                        ent.cash = nav_m * 0.05
                        ent.gov_bonds_par = nav_m * 0.95
                        ent.gov_bonds_mkt_value = nav_m * 0.95
                    elif ent.etf_type in ("CORP_BOND_IG", "JUNK_BOND"):
                        ent.cash = nav_m * 0.05
                        ent.corp_bonds_par = nav_m * 0.95
                        ent.corp_bonds_mkt_value = nav_m * 0.95
                    else:
                        ent.cash = nav_m
                    self.etf_corp_ids.append(cid)
                else:
                    # Regime 1: Industrial / Commercial / Holding (IND=3..70)
                    adj_cap = max(cap_m, bonds_m * 1.45 + 35.0)
                    ent.cap_assets_abstract = adj_cap
                    ent.working_cap_abstract = round(adj_cap * 0.25, 4)

                # Seed realistic distinct corporate ROCE, EPS, and initial stock price so no two corps look cloned
                roce_jitter = ((cid * 37 + ind_id * 13) % 19 - 8) * 0.55
                ent.roce_pct = round(max(6.5, min(26.0, 12.0 + roce_jitter)), 2)
                est_nw = max(40.0, cash_m + cap_m * 1.25 - bonds_m)
                book_ps = est_nw / max(1.0, ent.shares_outstanding)
                ent.annual_eps = round(max(0.25, book_ps * (ent.roce_pct / 100.0)), 4)
                val_mult = 0.88 + ((cid * 29) % 23) * 0.022
                ent.stock_price = round(max(4.50, book_ps * val_mult), 2)

                self.active_corp_ids.append(cid)
                self.public_float_shares[cid] = ent.shares_outstanding

            self.entities[cid] = ent

        # Load initial 263 Cross-Ownership Subsidiary Links from wsr101.dat (preserving >=25% public float)
        for cid_str, cdata in self.raw_db["wsr"]["corporations"].items():
            parent_id = int(cid_str)
            parent = self.entities.get(parent_id)
            if not parent or not parent.is_active:
                continue
            for sub_link in cdata.get("subsidiaries", []):
                sub_id = int(sub_link["subsidiary_id"])
                pct = float(sub_link["ownership_pct"])
                sub = self.entities.get(sub_id)
                if sub and sub.is_active and sub_id != parent_id:
                    avail_float = self.public_float_shares.get(sub_id, 0.0)
                    desired_shares = sub.shares_outstanding * (pct / 100.0)
                    alloc_shares = min(max(0.0, avail_float - 25.0), desired_shares)
                    if alloc_shares > 0:
                        parent.stock_holdings[sub_id] = alloc_shares
                        parent.stock_cost_basis[sub_id] = alloc_shares * sub.stock_price
                        self.public_float_shares[sub_id] = max(25.0, avail_float - alloc_shares)

        # Allocate initial stock basket to Sector/Equity/Leveraged ETFs so they hold real underlying positions
        for etf_id in self.etf_corp_ids:
            etf = self.entities[etf_id]
            if etf.etf_type == "LEVERAGED_BULL" and etf.leverage_factor > 1.0:
                # 2x Leveraged Bull ETF borrows 1x NAV in bank_loan to deploy ~2x NAV into equities
                lev_loan = etf.cash * (etf.leverage_factor - 1.0)
                etf.bank_loan += lev_loan
                etf.cash += lev_loan
                self.system_pool_cash -= lev_loan

            if etf.etf_type in ("SECTOR_EQUITY", "REGIONAL_EQUITY", "LEVERAGED_BULL") and etf.target_industries:
                candidates = [
                    cid for cid in self.active_corp_ids
                    if self.entities[cid].industry_id in etf.target_industries
                    and self.public_float_shares.get(cid, 0.0) > 15.0
                ][:5]
                if candidates:
                    deploy_ratio = 0.92 if etf.etf_type == "LEVERAGED_BULL" else 0.80
                    invest_per_corp = (etf.cash * deploy_ratio) / len(candidates)
                    for t_cid in candidates:
                        target = self.entities[t_cid]
                        shares_to_buy = min(
                            self.public_float_shares[t_cid] * 0.08,
                            invest_per_corp / max(1.0, target.stock_price),
                        )
                        if shares_to_buy > 0:
                            cost = shares_to_buy * target.stock_price
                            etf.cash -= cost
                            self.system_pool_cash += cost
                            etf.stock_holdings[t_cid] = etf.stock_holdings.get(t_cid, 0.0) + shares_to_buy
                            etf.stock_cost_basis[t_cid] = etf.stock_cost_basis.get(t_cid, 0.0) + cost
                            self.public_float_shares[t_cid] -= shares_to_buy
            elif etf.etf_type == "LEVERAGED_BEAR" and etf.leverage_factor < 0.0:
                # -2x Leveraged Bear ETF posts margin and holds inverse Stock Index futures exposure
                margin_post = etf.cash * 0.50
                etf.cash -= margin_post
                etf.commod_margin += margin_post
                idx_spot = max(100.0, self.commodity_prices.get("STOCK_INDEX", 4500.0))
                etf.futures_positions["STOCK_INDEX"] = (etf.leverage_factor * (etf.cash + etf.commod_margin)) / idx_spot

        # Run initial circular control & balance sheet convergence pass
        self.resolve_circular_ownership_and_control()
        self.recompute_all_balance_sheets()

        # Assign Hybrid WSR MakeComputerTurn (VA 0x0052A6E1) + CapLab PERSONS.DBF AI Personas
        self._initialize_ai_personas_and_news_feed()

    def _initialize_ai_personas_and_news_feed(self) -> None:
        """
        Binds WSR Raider AI archetypes (ID 2..5) + Capitalism Lab's 64 PERSONS.DBF CEO profiles
        to the billionaire rivals and top active corporations, and seeds initial Mscnews/quote feed.
        """
        # 1. Configure 4 Billionaire AI Rivals (IDs 2..5) combining WSR MakeComputerTurn + CapLab traits
        self.billionaire_ai_profiles = {
            2: {
                "player_id": 2,
                "name": "Warren B. (Berkshire AI)",
                "archetype": "VALUE_COMPOUNDER",
                "wsr_strategy": "Hunt low P/B (<1.15) & high credit-rating (AAA..A) stocks; build >=20% or >=80% DRD tax-shielded stakes.",
                "caplab_focus": "RETAIL & CONSUMER BRANDS",
                "character": 4,
                "marketing": 80,
                "rd": 40,
                "mft": 60,
                "retail": 90,
                "raw": 30,
                "preferred_industries": [2, 18, 19, 31, 32, 37, 58],
            },
            3: {
                "player_id": 3,
                "name": "Carl I. (Raider AI)",
                "archetype": "HOSTILE_RAIDER_LBO",
                "wsr_strategy": "Target cash-rich or undervalued conglomerates for Hostile Takeover, Special Dividend extraction & Tax-Free Spin-Offs.",
                "caplab_focus": "HEAVY MANUFACTURING & ENERGY",
                "character": 5,
                "marketing": 30,
                "rd": 30,
                "mft": 90,
                "retail": 40,
                "raw": 85,
                "preferred_industries": [6, 7, 8, 9, 12, 13, 14, 49],
            },
            4: {
                "player_id": 4,
                "name": "George S. (Quantum AI)",
                "archetype": "GLOBAL_MACRO_SHORT",
                "wsr_strategy": "Macro cycle timer: short overleveraged low-rating (<=BB) corporations when Prime Rate rises; trade Swaps & ETFs.",
                "caplab_focus": "REAL ESTATE & GLOBAL FINANCE",
                "character": 5,
                "marketing": 50,
                "rd": 50,
                "mft": 40,
                "retail": 50,
                "raw": 60,
                "preferred_industries": [1, 2, 15, 37, 70, 71],
            },
            5: {
                "player_id": 5,
                "name": "Ken G. (Citadel AI)",
                "archetype": "QUANT_TECH_INNOVATOR",
                "wsr_strategy": "High-ROCE sector momentum & R&D tech frontier compounder; vertical integration across high-tech supply chains.",
                "caplab_focus": "R&D TECH, SEMICONDUCTORS & SOFTWARE",
                "character": 4,
                "marketing": 70,
                "rd": 100,
                "mft": 85,
                "retail": 75,
                "raw": 20,
                "preferred_industries": [4, 10, 21, 22, 24, 26, 35, 39, 40],
            },
        }

        # 2. Assign the 64 authentic Capitalism Lab CEOs from PERSONS.DBF to top active non-test corporations
        reserved_test_ids = {131, 132, 133, 181, 200, 201, 202, 203, 205, 221, 222, 300, 321, 322, 620}
        eligible_corps = [
            cid for cid in self.active_corp_ids
            if cid not in reserved_test_ids and self.entities[cid].regime == "INDUSTRIAL_HOLDING"
        ]
        eligible_corps.sort(key=lambda cid: self.entities[cid].net_worth, reverse=True)
        for idx, person in enumerate(self.caplab_persons):
            if idx >= len(eligible_corps):
                break
            cid = eligible_corps[idx]
            self.corp_ceo_profiles[cid] = {
                "corp_id": cid,
                "corp_ticker": self.entities[cid].ticker,
                "ceo_name": person.get("NAME", f"Executive #{idx+1}"),
                "gender": person.get("GENDER", "M"),
                "image_file": person.get("IMAGEFILE", "M01"),
                "character": int(person.get("CHARACTER", 3)),
                "training": int(person.get("TRAINING", 20)),
                "marketing": int(person.get("MARKETING", 40)),
                "rd": int(person.get("RD", 40)),
                "farming": int(person.get("FARMING", 0)),
                "mft": int(person.get("MFT", 50)),
                "retail": int(person.get("RETAIL", 50)),
                "raw": int(person.get("RAW", 20)),
            }

        # 3. Seed initial ticker tape and financial headlines
        self._refresh_ticker_tape()
        if self.wsr_mscnews:
            first_keys = sorted(self.wsr_mscnews.keys())[:3]
            for k in first_keys:
                snippet = self.wsr_mscnews[k][:220].strip() + "..."
                self.news_headlines.append(f"[WSR MACRO WIRE {k}] {snippet}")
        if self.wsr_quotes:
            self.news_headlines.append(f"[STREET WISDOM] {self.wsr_quotes[0]}")

    # =========================================================================
    # 2. FIVE BALANCE SHEET REGIMES & CIRCULAR CROSS-OWNERSHIP SOLVER
    # =========================================================================

    def get_long_gov_bond_price(self) -> float:
        """Exact WSR TreasBondPrice (VA 0x0042855F) for 7% Long Government Bonds."""
        rate = max(0.5, self.long_bond_rate_pct)
        return max(25.0, min(250.0, 100.0 * ((7.0 / rate) ** 0.75)))

    def get_short_gov_bond_price(self) -> float:
        """Exact WSR TreasBondPrice (VA 0x0042855F) for 5% Short Government Bonds."""
        rate = max(0.5, self.short_bond_rate_pct)
        return max(40.0, min(180.0, 100.0 * ((5.0 / rate) ** 0.40)))

    def get_corporate_bond_price(self, issuer: FinancialEntity) -> float:
        """Exact WSR JunkBondPrice (VA 0x00428CB7) per $100 par value."""
        spread = RATING_BOND_SPREAD.get(issuer.credit_rating, 5.0)
        req_yield = max(1.0, self.long_bond_rate_pct + spread - 0.15 * self.gdp_growth_pct)
        years_rem = max(1, issuer.bond_maturity_year - self.year)
        disc = 1.0 + req_yield / 100.0
        pv_par = 100.0 / (disc ** years_rem)
        pv_coupons = issuer.bond_coupon_pct * (1.0 - (disc ** (-years_rem))) / (req_yield / 100.0)
        return max(10.0, min(180.0, pv_par + pv_coupons))

    def compute_credit_rating(self, ent: FinancialEntity) -> None:
        """
        Exact WSR GetCredRating (VA 0x0042B809):
          - Banks (IND == 1): Capital Adequacy Ratio CAR% = 100 * NetWorth / TotalAssets
            plus Non-Performing Loan penalty.
          - Non-Banks: Debt-to-Equity ratio r = TotalDebt / NetWorth.
        """
        if ent.is_bankrupt or ent.net_worth <= 0.0:
            ent.credit_rating = 1
            ent.borrowing_rate_pct = round((self.prime_rate_pct + 7.0) * 4.0) / 4.0
            ent.credit_line_limit = 0.0
            return

        if ent.regime == "COMMERCIAL_BANK":
            # Regime 2: Commercial Bank CAR% = NetWorth / TotalAssets
            car_pct = 100.0 * (ent.net_worth / max(1.0, ent.total_assets))
            gross_loans = max(1.0, ent.biz_loans + ent.consumer_loans + ent.mortgage_loans)
            npl_ratio_pct = 100.0 * (ent.bad_debt_reserves / gross_loans)
            effective_car = car_pct - max(0.0, npl_ratio_pct - 2.0) * 0.75
            if effective_car > 15.0:
                rating = 10  # AAA
            elif effective_car > 10.0:
                rating = 9   # AA
            elif effective_car > 8.0:
                rating = 8   # A
            elif effective_car > 6.0:
                rating = 7   # BBB
            elif effective_car > 4.0:
                rating = 6   # BB
            elif effective_car > 3.0:
                rating = 5   # B
            elif effective_car > 1.5:
                rating = 4   # CCC
            elif effective_car > 0.0:
                rating = 3   # CC
            else:
                rating = 2   # C
        else:
            total_debt = (
                ent.bank_loan
                + ent.bonds_out
                + ent.short_liability
                + ent.naked_option_liab
                + ent.advances_from_parents
            )
            r = total_debt / ent.net_worth
            if r <= 0.05:
                rating = 10  # AAA
            elif r <= 0.20:
                rating = 9   # AA
            elif r <= 0.50:
                rating = 8   # A
            elif r <= 1.00:
                rating = 7   # BBB
            elif r <= 1.50:
                rating = 6   # BB
            elif r <= 2.00:
                rating = 5   # B
            elif r <= 3.00:
                rating = 4   # CCC
            elif r <= 5.00:
                rating = 3   # CC
            else:
                rating = 2   # C

        ent.credit_rating = rating
        spread = RATING_LOAN_SPREAD[rating]
        gdp_adj = max(-1.0, min(2.0, 2.0 - self.gdp_growth_pct)) * max(0.0, (6 - min(rating, 6)) / 5.0)
        raw_rate = self.prime_rate_pct + spread + gdp_adj
        ent.borrowing_rate_pct = round(raw_rate * 4.0) / 4.0
        mult = RATING_CREDIT_LINE_MULT[rating]
        ent.credit_line_limit = max(0.0, ent.net_worth * mult)

    def recompute_entity_balance_sheet(self, ent: FinancialEntity, update_stock_price: bool = True) -> None:
        """
        Exact 5-Regime Balance Sheet calculation (CorpInfoItems @ 0x004266F8 & ui.dll @ 0x10042C54 / 0x1003EFD6).
        Guarantees: TotalAssets - (TotalLiabilities + NetWorth) == 0.0 for every regime.
        """
        if not ent.is_active:
            ent.total_assets = 0.0
            ent.total_liabilities = 0.0
            ent.net_worth = 0.0
            return

        # 1. Revalue Stock Portfolio & Short Liability at current market prices
        stock_val = 0.0
        for target_id, shares in ent.stock_holdings.items():
            if shares > 0 and target_id in self.entities:
                target = self.entities[target_id]
                discount = 0.85 if (ent.in_circular_control_cycle and target.in_circular_control_cycle) else 1.0
                stock_val += shares * target.stock_price * discount
        ent.stock_portfolio_value = stock_val

        short_val = 0.0
        for target_id, s_shares in ent.short_positions.items():
            if s_shares > 0 and target_id in self.entities:
                short_val += s_shares * self.entities[target_id].stock_price
        ent.short_liability = short_val

        # 2. Revalue Bond Portfolio (Adjusted Cost for Banks/Insurers vs Market Value for ETFs/Players/Industrials)
        gov_mkt_factor = self.get_long_gov_bond_price() / 100.0
        ent.gov_bonds_mkt_value = ent.gov_bonds_par * gov_mkt_factor
        ent.corp_bonds_mkt_value = ent.corp_bonds_par * (self.get_long_gov_bond_price() * 0.96 / 100.0)

        # 3. Revalue Crypto Portfolio (for Players/Entities)
        crypto_val = 0.0
        for sym, coins in ent.crypto_holdings.items():
            crypto_val += coins * self.crypto_prices.get(sym, 0.0) / 1_000_000.0
        ent.crypto_portfolio_value = crypto_val

        # 4. Regime-Specific Asset & Liability Aggregation
        if ent.regime == "INDUSTRIAL_HOLDING":
            # Regime 1 (IND = 3..70)
            ent.total_assets = (
                ent.cash
                + ent.tbills
                + ent.working_cap
                + ent.cap_assets
                + ent.stock_portfolio_value
                + ent.option_portfolio_value
                + ent.gov_bonds_mkt_value
                + ent.corp_bonds_mkt_value
                + ent.commod_mtm
                + ent.commod_margin
                + ent.crypto_portfolio_value
                + ent.unamortized_goodwill
                + ent.advances_to_subsidiaries
            )
            ent.total_liabilities = (
                ent.bank_loan
                + ent.advances_from_parents
                + ent.bonds_out
                + ent.short_liability
                + ent.naked_option_liab
                + ent.acc_tax
                + ent.cap_tax
                + ent.hid_reserve
            )

        elif ent.regime == "COMMERCIAL_BANK":
            # Regime 2 (IND = 1): NO CapAssets or WorkingCap; Bonds valued at Adjusted Cost!
            ent.cap_assets_abstract = 0.0
            ent.cap_assets_caplab_firms = 0.0
            ent.working_cap_abstract = 0.0
            ent.working_cap_caplab_inventory = 0.0
            ent.total_assets = (
                ent.cash
                + ent.tbills
                + ent.net_bank_loans_asset
                + ent.gov_bonds_adj_cost
                + ent.corp_bonds_adj_cost
                + ent.stock_portfolio_value
                + ent.option_portfolio_value
                + ent.commod_mtm
                + ent.commod_margin
                + ent.crypto_portfolio_value
                + ent.advances_to_corps
            )
            ent.total_liabilities = (
                ent.demand_deposits
                + ent.cert_deposits
                + ent.interbank_debt
                + ent.bonds_out
                + ent.short_liability
                + ent.naked_option_liab
                + ent.acc_tax
                + ent.cap_tax
                + ent.hid_reserve
            )

        elif ent.regime == "INSURANCE_COMPANY":
            # Regime 3 (IND = 2): NO CapAssets or WorkingCap; SubprimeMortgages & InsurReserves float; Adjusted Cost bonds!
            ent.cap_assets_abstract = 0.0
            ent.cap_assets_caplab_firms = 0.0
            ent.working_cap_abstract = 0.0
            ent.working_cap_caplab_inventory = 0.0
            ent.total_assets = (
                ent.cash
                + ent.tbills
                + ent.subprime_mortgages
                + ent.gov_bonds_adj_cost
                + ent.corp_bonds_adj_cost
                + ent.stock_portfolio_value
                + ent.option_portfolio_value
                + ent.commod_mtm
                + ent.commod_margin
                + ent.crypto_portfolio_value
            )
            ent.total_liabilities = (
                ent.insur_reserves
                + ent.bank_loan
                + ent.bonds_out
                + ent.short_liability
                + ent.naked_option_liab
                + ent.acc_tax
                + ent.cap_tax
                + ent.hid_reserve
            )

        elif ent.regime == "ETF_FUND":
            # Regime 4 (IND = 71, IDs 1581..1600): Bonds valued at Market Value!
            ent.cap_assets_abstract = 0.0
            ent.cap_assets_caplab_firms = 0.0
            ent.working_cap_abstract = 0.0
            ent.working_cap_caplab_inventory = 0.0
            ent.convertible_bonds_out = 0.0
            ent.total_assets = (
                ent.cash
                + ent.tbills
                + ent.gov_bonds_mkt_value
                + ent.corp_bonds_mkt_value
                + ent.stock_portfolio_value
                + ent.option_portfolio_value
                + ent.commod_mtm
                + ent.commod_margin
                + ent.crypto_portfolio_value
            )
            ent.total_liabilities = (
                ent.bank_loan
                + ent.bonds_out
                + ent.short_liability
                + ent.naked_option_liab
                + ent.acc_tax
                + ent.cap_tax
                + ent.hid_reserve
            )

        elif ent.regime == "PLAYER_INDIVIDUAL":
            # Regime 5 (IDs 1..5): Individual Investor / Player
            ent.total_assets = (
                ent.cash
                + ent.tbills
                + ent.advances_to_companies
                + ent.gov_bonds_mkt_value
                + ent.corp_bonds_mkt_value
                + ent.stock_portfolio_value
                + ent.option_portfolio_value
                + ent.commod_mtm
                + ent.commod_margin
                + ent.crypto_portfolio_value
            )
            ent.total_liabilities = (
                ent.bank_loan
                + ent.short_liability
                + ent.naked_option_liab
                + max(0.0, ent.income_tax_owed)
                + max(0.0, ent.wealth_tax_projected)
            )

        ent.net_worth = ent.total_assets - ent.total_liabilities
        self.compute_credit_rating(ent)

        if update_stock_price and ent.regime != "PLAYER_INDIVIDUAL" and ent.shares_outstanding > 0:
            self._update_fundamental_stock_price(ent)

    def _update_fundamental_stock_price(self, ent: FinancialEntity) -> None:
        """Exact WSR StockPrice (VA 0x0042C812) fundamental valuation per share."""
        book_per_share = max(0.05, ent.net_worth / max(1e-6, ent.shares_outstanding))
        if ent.regime == "ETF_FUND":
            # ETF shares trade directly at NAV per share
            ent.stock_price = max(0.10, round(book_per_share, 4))
            return

        ind_growth = float(self.industries.get(ent.industry_id, {}).get("growth_rate_pct", 5))
        pe_mult = max(5.0, min(28.0, 10.0 + 0.65 * ind_growth - 0.35 * (self.prime_rate_pct - 6.0)))
        earnings_val_per_share = max(0.0, ent.annual_eps * pe_mult)
        div_yield_bonus = ent.dividend_per_share * 4.5
        target_price = 0.65 * book_per_share + 0.30 * earnings_val_per_share + 0.05 * div_yield_bonus
        # Smooth toward fundamental price with damping
        ent.stock_price = max(0.10, round(0.70 * ent.stock_price + 0.30 * target_price, 4))

    def resolve_circular_ownership_and_control(self, max_iters: int = 8, tol: float = 1e-3) -> Dict[str, Any]:
        """
        Implements WSR CircControl (VA 0x00480D92) & CorpControl (VA 0x0041F811):
          1. Detects all directed ownership cycles (A -> B -> C -> A) using Tarjan strongly connected components.
          2. Assigns ultimate controlling entity (controlled_by_id) without infinite recursion.
          3. Converges NetWorth and StockPrice across cross-holdings via damped Gauss-Seidel iteration.
        """
        # Build ownership adjacency graph for edges >= 5% voting stake
        adj: Dict[int, List[Tuple[int, float]]] = {}
        rev_major: Dict[int, List[Tuple[int, float]]] = {}
        for holder_id, holder in self.entities.items():
            if not holder.is_active:
                continue
            for target_id, shares in holder.stock_holdings.items():
                if shares <= 0 or target_id not in self.entities:
                    continue
                target = self.entities[target_id]
                pct = 100.0 * shares / max(1e-6, target.shares_outstanding)
                if pct >= 5.0:
                    adj.setdefault(holder_id, []).append((target_id, pct))
                if pct >= 20.0:
                    rev_major.setdefault(target_id, []).append((holder_id, pct))

        # Tarjan's SCC algorithm to detect all circular ownership cycles in O(V + E)
        index = 0
        indices: Dict[int, int] = {}
        lowlink: Dict[int, int] = {}
        stack: List[int] = []
        on_stack: Set[int] = set()
        cycle_nodes: Set[int] = set()

        def strongconnect(v: int) -> None:
            nonlocal index
            indices[v] = index
            lowlink[v] = index
            index += 1
            stack.append(v)
            on_stack.add(v)
            for w, _ in adj.get(v, []):
                if w not in indices:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif w in on_stack:
                    lowlink[v] = min(lowlink[v], indices[w])
            if lowlink[v] == indices[v]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == v:
                        break
                if len(scc) > 1:
                    cycle_nodes.update(scc)

        for eid in list(adj.keys()):
            if eid not in indices:
                strongconnect(eid)

        for cid in self.active_corp_ids:
            ent = self.entities[cid]
            ent.in_circular_control_cycle = cid in cycle_nodes
            ent.controlled_by_id = 0

        # Determine ultimate controller only for corporations with >=20% blockholders (cycle-safe)
        for cid in rev_major:
            visited: Set[int] = {cid}
            curr = cid
            controller = 0
            while True:
                holders = rev_major.get(curr, [])
                if not holders:
                    break
                top_holder = max(holders, key=lambda x: x[1])[0]
                controller = top_holder
                if top_holder in visited or (top_holder in self.entities and self.entities[top_holder].regime == "PLAYER_INDIVIDUAL"):
                    break
                visited.add(top_holder)
                curr = top_holder
            if cid in self.entities:
                self.entities[cid].controlled_by_id = controller

        # Damped Gauss-Seidel convergence on circular ownership cycle_nodes
        iters_run = 1
        max_delta = 0.0
        if cycle_nodes:
            sorted_cycle = sorted(cycle_nodes)
            for it in range(max_iters):
                iters_run = it + 1
                max_delta = 0.0
                for cid in sorted_cycle:
                    ent = self.entities[cid]
                    old_nw = ent.net_worth
                    old_sp_val = ent.stock_portfolio_value
                    self.recompute_entity_balance_sheet(ent, update_stock_price=False)
                    # Damp stock_portfolio_value directly so component asset sum == total_assets exactly
                    raw_sp_val = ent.stock_portfolio_value
                    damped_sp_val = 0.65 * raw_sp_val + 0.35 * old_sp_val
                    ent.stock_portfolio_value = damped_sp_val
                    ent.total_assets += damped_sp_val - raw_sp_val
                    ent.net_worth = ent.total_assets - ent.total_liabilities
                    book_ps = max(0.05, ent.net_worth / max(1e-6, ent.shares_outstanding))
                    ent.stock_price = max(0.10, round(0.50 * ent.stock_price + 0.50 * book_ps, 4))
                    max_delta = max(max_delta, abs(ent.net_worth - old_nw))
                if max_delta < tol:
                    break
            # Final clean pass so stock_portfolio_value matches final damped stock_price
            for cid in sorted_cycle:
                self.recompute_entity_balance_sheet(self.entities[cid], update_stock_price=False)

        return {
            "cycle_nodes": sorted(cycle_nodes),
            "iterations": iters_run,
            "max_delta_millions": max_delta,
        }

    def reset_clean_free_float_for_corps(self, corp_ids: List[int]) -> None:
        """
        Cleanly returns all shares of corp_ids held by any entity back into public_float_shares
        and returns any shares held by corp_ids back into their targets' public_float_shares,
        preserving 100% Share Conservation Invariant.
        """
        target_set = set(corp_ids)
        for ent in self.entities.values():
            # If ent is one of corp_ids, return its holdings/shorts to their respective floats
            if ent.entity_id in target_set:
                for t_cid, sh in list(ent.stock_holdings.items()):
                    self.public_float_shares[t_cid] = self.public_float_shares.get(t_cid, 0.0) + sh
                ent.stock_holdings.clear()
                ent.stock_cost_basis.clear()
                for t_cid, sh in list(ent.short_positions.items()):
                    self.public_float_shares[t_cid] = max(0.0, self.public_float_shares.get(t_cid, 0.0) - sh)
                ent.short_positions.clear()
            else:
                # Remove any holdings/shorts of target_set from other entities
                for t_cid in target_set:
                    sh = ent.stock_holdings.pop(t_cid, 0.0)
                    ent.stock_cost_basis.pop(t_cid, None)
                    if sh > 0:
                        self.public_float_shares[t_cid] = self.public_float_shares.get(t_cid, 0.0) + sh
                    s_sh = ent.short_positions.pop(t_cid, 0.0)
                    if s_sh > 0:
                        self.public_float_shares[t_cid] = max(0.0, self.public_float_shares.get(t_cid, 0.0) - s_sh)

        for cid in target_set:
            if cid in self.entities and self.entities[cid].is_active:
                self.public_float_shares[cid] = self.entities[cid].shares_outstanding
                self.recompute_entity_balance_sheet(self.entities[cid], update_stock_price=False)

    def recompute_all_balance_sheets(self, update_stock_prices: bool = True) -> None:
        self._revalue_all_options()
        for cid in self.active_corp_ids:
            self.recompute_entity_balance_sheet(self.entities[cid], update_stock_price=update_stock_prices)
        for pid in self.player_ids:
            if pid in self.entities:
                self.recompute_entity_balance_sheet(self.entities[pid], update_stock_price=False)

    # =========================================================================
    # 3. THREE-TIER CORPORATE TAX LAW (DRD 80%/100%, 80% TAX-FREE, 4-YR NOL)
    # =========================================================================

    def calculate_dividend_taxable_portion(
        self, recipient_id: int, payer_corp_id: int, gross_dividend_millions: float
    ) -> float:
        """
        Implements WSR Dividends Received Deduction (DRD — CorpTaxCalc @ 0x004F9803):
          - Individual Player (ID 1..5): 100% of dividend is taxable ordinary income.
          - Corporate Shareholder (ID >= 11):
            * Ownership >= 80%: 100% DRD (0% of dividend is taxable!).
            * Ownership <  80%: 80% DRD (only 20% of dividend is taxable!).
        """
        if gross_dividend_millions <= 0.0:
            return 0.0
        recipient = self.entities[recipient_id]
        if recipient.regime == "PLAYER_INDIVIDUAL":
            return gross_dividend_millions
        payer = self.entities[payer_corp_id]
        shares_held = recipient.stock_holdings.get(payer_corp_id, 0.0)
        ownership_pct = 100.0 * shares_held / max(1e-6, payer.shares_outstanding)
        if ownership_pct >= 80.0 - 1e-6:
            return 0.0  # 100% tax-exempt intercorporate dividend
        return gross_dividend_millions * 0.20  # 80% DRD -> only 20% subject to corporate tax

    def calculate_corporate_tax(
        self, corp: FinancialEntity, operating_pretax_income: float, taxable_dividends_income: float = 0.0
    ) -> float:
        """
        Implements WSR CorpTaxCalc (VA 0x004F9803):
          - Combines operating pre-tax income + post-DRD taxable dividends.
          - If total pre-tax income < 0: records loss into 4-year NOL carryforward [LOSS1..LOSS4] and tax = 0.
          - If total pre-tax income > 0: deducts available 4-year NOL carryforwards (oldest first: LOSS4 -> LOSS1)
            before applying corporate_tax_rate (35%).
        """
        total_taxable = operating_pretax_income + taxable_dividends_income
        if total_taxable <= 0.0:
            # Shift NOL buckets and record current loss in LOSS1 (index 0)
            loss_amount = abs(total_taxable)
            corp.nol_carryforward[0] += loss_amount
            return 0.0

        # Offset positive taxable income using 4-year NOL carryforward (oldest first: index 3 down to 0)
        remaining_income = total_taxable
        for idx in range(3, -1, -1):
            avail_nol = corp.nol_carryforward[idx]
            if avail_nol > 0.0 and remaining_income > 0.0:
                used = min(avail_nol, remaining_income)
                corp.nol_carryforward[idx] -= used
                remaining_income -= used

        tax = remaining_income * self.corporate_tax_rate
        corp.acc_tax += tax
        return tax

    def roll_annual_nol_buckets(self, corp: FinancialEntity) -> None:
        """Shifts [LOSS1, LOSS2, LOSS3, LOSS4] at year-end, expiring LOSS4 (>4 years old)."""
        corp.nol_carryforward = [0.0, corp.nol_carryforward[0], corp.nol_carryforward[1], corp.nol_carryforward[2]]

    # =========================================================================
    # 4. STOCK TRADING, SHORT SELLING, SHORT DIVIDENDS & MARGIN CALLS
    # =========================================================================

    def get_public_free_float_pct(self, corp_id: int) -> float:
        """Exact WSR MarketImpactSub (VA 0x0050FAE8) free float percentage."""
        corp = self.entities[corp_id]
        float_shares = self.public_float_shares.get(corp_id, 0.0)
        return max(1.0, min(100.0, 100.0 * float_shares / max(1e-6, corp.shares_outstanding)))

    def _recompute_holders_of_corp(self, target_corp_id: int) -> None:
        """Recomputes balance sheets for all entities holding or shorting target_corp_id after a spot price update."""
        if any(opt.underlying_corp_id == target_corp_id for opt in self.options.values()):
            self._revalue_all_options()
        for ent in self.entities.values():
            if not ent.is_active:
                continue
            if target_corp_id in ent.stock_holdings or target_corp_id in ent.short_positions:
                self.recompute_entity_balance_sheet(ent, update_stock_price=False)

    def buy_stock(
        self, buyer_id: int, target_corp_id: int, shares_millions: float
    ) -> Dict[str, Any]:
        """
        Executes a stock purchase (WSR BuyStock @ 0x004EF26A) with free-float market impact,
        1% broker commission, and strict Share Conservation & Cash Conservation invariants.
        """
        buyer = self.entities.get(buyer_id)
        target = self.entities.get(target_corp_id)
        if not buyer or not buyer.is_active or not target or not target.is_active:
            return {"ok": False, "reason": "Buyer or target entity is not active."}
        if target.regime == "PLAYER_INDIVIDUAL":
            return {"ok": False, "reason": "Cannot buy shares of an Individual Investor (#1..#5, #2001..#2320). Select a Corporation (#11..#1580) or ETF (#1581..#1600)."}
        if buyer_id == target_corp_id:
            return {"ok": False, "reason": "Entity cannot Buy Long its own shares (select a different Target Corp ID)."}
        avail_float = self.public_float_shares.get(target_corp_id, 0.0)
        shares_to_buy = min(shares_millions, avail_float)
        if shares_to_buy <= 0.0:
            return {"ok": False, "reason": "Insufficient public float shares"}

        pct_bought = 100.0 * shares_to_buy / max(1e-6, target.shares_outstanding)
        free_float_pct = self.get_public_free_float_pct(target_corp_id)
        old_price = target.stock_price
        impact_factor = 1.0 + (pct_bought / free_float_pct) * 0.35
        new_price = round(old_price * impact_factor, 4)
        exec_price = 0.5 * (old_price + new_price) * 1.01  # 1% commission (0x7500A8 = 1.01f)
        total_cost = shares_to_buy * exec_price

        if buyer.cash < total_cost:
            # Auto-draw on bank credit line if available
            shortfall = total_cost - buyer.cash
            avail_credit = max(0.0, buyer.credit_line_limit - buyer.bank_loan)
            if shortfall <= avail_credit:
                self.borrow_bank_loan(buyer_id, shortfall)
            else:
                return {"ok": False, "reason": "Insufficient cash and credit line"}

        buyer.cash -= total_cost
        self.system_pool_cash += total_cost
        buyer.stock_holdings[target_corp_id] = buyer.stock_holdings.get(target_corp_id, 0.0) + shares_to_buy
        buyer.stock_cost_basis[target_corp_id] = buyer.stock_cost_basis.get(target_corp_id, 0.0) + total_cost
        self.public_float_shares[target_corp_id] -= shares_to_buy
        target.stock_price = new_price

        self.recompute_entity_balance_sheet(target, update_stock_price=False)
        self.recompute_entity_balance_sheet(buyer, update_stock_price=False)
        self._recompute_holders_of_corp(target_corp_id)
        return {
            "ok": True,
            "shares_bought_millions": shares_to_buy,
            "exec_price": exec_price,
            "total_cost_millions": total_cost,
            "new_spot_price": new_price,
        }

    def sell_stock(
        self, seller_id: int, target_corp_id: int, shares_millions: float
    ) -> Dict[str, Any]:
        """Executes a stock sale (WSR SellStock @ 0x004F1FB8) with capital gains tax tracking."""
        seller = self.entities[seller_id]
        target = self.entities[target_corp_id]
        held = seller.stock_holdings.get(target_corp_id, 0.0)
        shares_to_sell = min(shares_millions, held)
        if shares_to_sell <= 0.0:
            return {"ok": False, "reason": "No shares held to sell"}

        pct_sold = 100.0 * shares_to_sell / max(1e-6, target.shares_outstanding)
        free_float_pct = self.get_public_free_float_pct(target_corp_id)
        old_price = target.stock_price
        impact_factor = max(0.50, 1.0 - (pct_sold / free_float_pct) * 0.25)
        new_price = round(old_price * impact_factor, 4)
        exec_price = 0.5 * (old_price + new_price) * 0.99  # 1% commission
        proceeds = shares_to_sell * exec_price

        # Calculate proportional cost basis and realized capital gain
        total_basis = seller.stock_cost_basis.get(target_corp_id, 0.0)
        prop_basis = total_basis * (shares_to_sell / held)
        cap_gain = proceeds - prop_basis

        seller.stock_holdings[target_corp_id] -= shares_to_sell
        seller.stock_cost_basis[target_corp_id] = max(0.0, total_basis - prop_basis)
        if seller.stock_holdings[target_corp_id] <= 1e-9:
            seller.stock_holdings.pop(target_corp_id, None)
            seller.stock_cost_basis.pop(target_corp_id, None)

        seller.cash += proceeds
        self.system_pool_cash -= proceeds
        self.public_float_shares[target_corp_id] = self.public_float_shares.get(target_corp_id, 0.0) + shares_to_sell
        target.stock_price = new_price

        if seller.regime == "PLAYER_INDIVIDUAL":
            seller.realized_cap_gain_loss += cap_gain
            if cap_gain > 0:
                seller.income_tax_owed += cap_gain * self.capital_gains_tax_rate
        else:
            if cap_gain > 0:
                seller.cap_tax += cap_gain * self.capital_gains_tax_rate

        self.recompute_entity_balance_sheet(target, update_stock_price=False)
        self.recompute_entity_balance_sheet(seller, update_stock_price=False)
        self._recompute_holders_of_corp(target_corp_id)
        return {
            "ok": True,
            "shares_sold_millions": shares_to_sell,
            "proceeds_millions": proceeds,
            "realized_cap_gain_millions": cap_gain,
            "new_spot_price": new_price,
        }

    def short_stock(
        self, shorter_id: int, target_corp_id: int, shares_millions: float
    ) -> Dict[str, Any]:
        """
        Executes a short sale (WSR ShortStock @ 0x004F5B31):
          - ETFs (IND=71) are prohibited from shorting individual stocks.
          - Increases public_float_shares by shares_millions so that:
            Sum(LongHoldings) + PublicFloat - Sum(ShortPositions) == SharesOutstanding!
          - Credits cash proceeds (net of commission) and records ShortLiability = shares * spot_price.
        """
        shorter = self.entities[shorter_id]
        if shorter.regime == "ETF_FUND":
            return {"ok": False, "reason": "ETFs cannot short individual stocks"}
        target = self.entities[target_corp_id]
        if target.regime == "PLAYER_INDIVIDUAL":
            return {"ok": False, "reason": "Cannot short an Individual Investor (#1..#5, #2001..#2320). Select a Corporation (#11..#1580) or ETF (#1581..#1600)."}
        if shorter_id == target_corp_id:
            return {"ok": False, "reason": "Entity cannot short its own shares."}
        if shares_millions <= 0.0:
            return {"ok": False, "reason": "Invalid short share quantity"}

        spot = target.stock_price
        notional = shares_millions * spot
        if shorter.net_worth < notional * 0.50:
            return {"ok": False, "reason": "Insufficient net worth / margin for short sale"}

        proceeds = notional * 0.99
        shorter.cash += proceeds
        self.system_pool_cash -= proceeds
        shorter.short_positions[target_corp_id] = shorter.short_positions.get(target_corp_id, 0.0) + shares_millions
        # Borrowed shares sold into the market increase total long float by exact short_shares
        self.public_float_shares[target_corp_id] = self.public_float_shares.get(target_corp_id, 0.0) + shares_millions

        self.recompute_entity_balance_sheet(shorter, update_stock_price=False)
        return {
            "ok": True,
            "short_shares_millions": shares_millions,
            "proceeds_millions": proceeds,
            "short_liability_millions": shorter.short_liability,
        }

    def cover_short_stock(
        self, shorter_id: int, target_corp_id: int, shares_millions: float
    ) -> Dict[str, Any]:
        """Covers an existing short position by buying back shares from the market."""
        shorter = self.entities[shorter_id]
        target = self.entities[target_corp_id]
        cur_short = shorter.short_positions.get(target_corp_id, 0.0)
        cover_qty = min(shares_millions, cur_short)
        if cover_qty <= 0.0:
            return {"ok": False, "reason": "No short position to cover"}

        buy_cost = cover_qty * target.stock_price * 1.01
        if shorter.cash < buy_cost:
            need = buy_cost - shorter.cash
            self.borrow_bank_loan(shorter_id, need, allow_emergency=True)

        shorter.cash -= buy_cost
        self.system_pool_cash += buy_cost
        shorter.short_positions[target_corp_id] -= cover_qty
        if shorter.short_positions[target_corp_id] <= 1e-9:
            shorter.short_positions.pop(target_corp_id, None)
        self.public_float_shares[target_corp_id] = max(0.0, self.public_float_shares[target_corp_id] - cover_qty)

        self.recompute_entity_balance_sheet(shorter, update_stock_price=False)
        return {
            "ok": True,
            "covered_shares_millions": cover_qty,
            "cost_millions": buy_cost,
            "remaining_short_liability": shorter.short_liability,
        }

    def distribute_cash_dividend(self, payer_corp_id: int, dps: float) -> Dict[str, Any]:
        """
        Distributes a cash dividend of $dps per share from payer_corp_id:
          1. Deducts total_dividend = dps * shares_outstanding from payer's Cash.
          2. Enforces WSR ShortDividends (VA 0x005E0721): every short seller of payer_corp_id
             is immediately debited Delta_Cash = -short_shares * dps!
          3. Credits all Long Shareholders (Players & Parent/Holding Corps) pro-rata, applying
             WSR DRD tax rules (100% exempt if >=80% stake, 80% exempt if <80% stake).
          4. Credits the remaining public float dividend to system_pool_cash so closed-loop
             Cash Conservation is 100% exact: Sum(Delta_Cash_All) + Delta_System_Pool == 0!
        """
        payer = self.entities[payer_corp_id]
        if payer.regime in ("PLAYER_INDIVIDUAL", "ETF_FUND") or payer.shares_outstanding <= 0.0:
            return {"ok": False, "reason": "Select a Corporation (#11..#1580) as Target Corp to distribute dividends"}
        if dps <= 0.0:
            return {"ok": False, "reason": "Invalid dividend per share"}

        base_dividend = dps * payer.shares_outstanding
        if payer.cash < base_dividend:
            if payer.cash >= 0.001:
                dps = round((payer.cash * 0.20) / payer.shares_outstanding, 5)
                base_dividend = dps * payer.shares_outstanding
            if payer.cash < base_dividend or dps <= 0.0:
                return {"ok": False, "reason": "Insufficient corporate cash for dividend"}

        payer.cash -= base_dividend
        payer.dividend_per_share = dps
        # Immediate Ex-Dividend Stock Price Adjustment (prevents risk-free dividend-capture arbitrage)
        payer.stock_price = max(0.10, round(payer.stock_price - dps, 4))

        # 1. Collect Short Seller Dividend Obligations (ShortDividends @ 0x005E0721)
        short_div_collected = 0.0
        for ent in self.entities.values():
            s_shares = ent.short_positions.get(payer_corp_id, 0.0)
            if s_shares > 0.0:
                obligation = s_shares * dps
                ent.cash -= obligation
                short_div_collected += obligation
                self.recompute_entity_balance_sheet(ent, update_stock_price=False)

        # Total cash pool to distribute across all long holders (SharesOutstanding + ShortShares)
        total_long_pool = base_dividend + short_div_collected
        distributed_to_entities = 0.0

        # 2. Credit all private Long Shareholders & apply DRD tax rules
        for holder in self.entities.values():
            l_shares = holder.stock_holdings.get(payer_corp_id, 0.0)
            if l_shares > 0.0:
                gross_div = l_shares * dps
                holder.cash += gross_div
                distributed_to_entities += gross_div

                taxable_div = self.calculate_dividend_taxable_portion(
                    holder.entity_id, payer_corp_id, gross_div
                )
                if holder.regime == "PLAYER_INDIVIDUAL":
                    holder.ytd_taxable_ordinary += taxable_div
                    holder.income_tax_owed += taxable_div * 0.25
                else:
                    if taxable_div > 0.0:
                        self.calculate_corporate_tax(holder, 0.0, taxable_dividends_income=taxable_div)
                self.recompute_entity_balance_sheet(holder, update_stock_price=False)

        # 3. Public float receives the exact remainder into system_pool_cash
        public_div = total_long_pool - distributed_to_entities
        self.system_pool_cash += public_div

        self.recompute_entity_balance_sheet(payer, update_stock_price=False)
        return {
            "ok": True,
            "base_dividend_millions": base_dividend,
            "short_dividends_collected_millions": short_div_collected,
            "distributed_to_entities_millions": distributed_to_entities,
            "public_float_dividend_millions": public_div,
        }

    def check_margin_and_naked_options(self, entity_id: int) -> Dict[str, Any]:
        """
        Implements WSR CheckNakedOptions (VA 0x00606238) & Short Squeeze Margin Call:
        If an entity's total liabilities exceed its maximum borrowing capacity (or NetWorth
        falls below maintenance requirement for ShortLiability + NakedOptionLiab),
        forcibly buys in short stock and/or naked options.
        """
        ent = self.entities[entity_id]
        self.recompute_entity_balance_sheet(ent, update_stock_price=False)
        exposure = ent.short_liability + ent.naked_option_liab
        if exposure <= 0.0:
            return {"margin_call_triggered": False}

        # Trigger margin call if exposure > 1.25 * max(0, ent.net_worth) or total debt > credit_line_limit * 1.15
        total_debt = ent.bank_loan + ent.bonds_out + exposure
        if ent.net_worth <= 0.0 or exposure > ent.net_worth * 1.25 or total_debt > max(50.0, ent.credit_line_limit * 1.15):
            covered_shorts = []
            for t_cid in list(ent.short_positions.keys()):
                qty = ent.short_positions[t_cid]
                res = self.cover_short_stock(entity_id, t_cid, qty)
                covered_shorts.append((t_cid, qty, res.get("cost_millions", 0.0)))

            closed_options = []
            for oid, opt in list(self.options.items()):
                if opt.writer_id == entity_id and opt.is_naked:
                    buyback_cost = opt.current_value_millions * 1.02
                    ent.cash -= buyback_cost
                    if opt.holder_id in self.entities:
                        self.entities[opt.holder_id].cash += buyback_cost
                    else:
                        self.system_pool_cash += buyback_cost
                    closed_options.append(oid)
                    del self.options[oid]

            self._revalue_all_options()
            self.recompute_entity_balance_sheet(ent, update_stock_price=False)
            return {
                "margin_call_triggered": True,
                "covered_shorts": covered_shorts,
                "closed_naked_options": closed_options,
                "post_margin_net_worth": ent.net_worth,
            }
        return {"margin_call_triggered": False}

    # =========================================================================
    # 5. OPTIONS (GetOptionPrice), CONVERTIBLE BONDS (IssueCV) & SWAPS (IRS)
    # =========================================================================

    def price_option_per_share(
        self, underlying_corp_id: int, opt_type: str, strike_price: float, months_to_expiry: float
    ) -> float:
        """
        Exact WSR GetOptionPrice (VA 0x0060143F..0x0060376D) per-share option pricing formula.
        """
        corp = self.entities[underlying_corp_id]
        spot = max(0.01, corp.stock_price)
        strike = max(0.01, strike_price)
        m_clamped = max(0.0, min(24.0, months_to_expiry))
        w = int(math.floor(m_clamped))
        frac = m_clamped - w

        is_call = opt_type.upper() == "CALL"
        intrinsic = max(0.0, spot - strike) if is_call else max(0.0, strike - spot)

        if intrinsic > 0.0:
            pct_away = min(60.0, 100.0 * intrinsic / spot)
        else:
            raw_away = 100.0 * ((strike / spot - 1.0) if is_call else (spot / strike - 1.0))
            raw_away = max(0.0, raw_away)
            pct_away = 150.0 + 0.10 * (raw_away - 150.0) if raw_away > 150.0 else raw_away

        base_pct = WSR_OPTION_BASE_PCT[min(24, w)]
        if not is_call:
            base_pct *= 0.95 if w <= 12 else 0.96
        if w < 24 and frac > 0.0:
            next_pct = WSR_OPTION_BASE_PCT[w + 1] * (0.95 if (not is_call and w + 1 <= 12) else (0.96 if not is_call else 1.0))
            base_pct = base_pct + frac * (next_pct - base_pct)

        decay_base = 0.935 + min(0.045, w * 0.002)
        time_prem = spot * base_pct * (decay_base ** int(pct_away))

        ind_vol = float(self.industries.get(corp.industry_id, {}).get("volatility_pct", 5))
        vol_mult = max(0.75, min(1.25, 1.0 + (ind_vol - 5.0) * 0.04))
        rate_mult = 0.50 + 0.50 * (self.prime_rate_pct / 7.50)

        total_opt_price = intrinsic + time_prem * vol_mult * rate_mult
        return max(0.01, round(total_opt_price, 4))

    def create_option_contract(
        self,
        holder_id: int,
        writer_id: int,
        underlying_corp_id: int,
        opt_type: str,
        strike_price: float,
        shares_covered_millions: float,
        months_to_expiry: float,
    ) -> Dict[str, Any]:
        """Creates a Long or Short (Covered/Naked) Call/Put option contract."""
        per_share = self.price_option_per_share(underlying_corp_id, opt_type, strike_price, months_to_expiry)
        premium = per_share * shares_covered_millions

        if holder_id > 0:
            holder = self.entities[holder_id]
            if holder.cash < premium:
                return {"ok": False, "reason": "Insufficient cash for option premium"}
            holder.cash -= premium
        else:
            self.system_pool_cash -= premium

        is_naked = False
        if writer_id > 0:
            writer = self.entities[writer_id]
            writer.cash += premium
            if opt_type.upper() == "CALL":
                held = writer.stock_holdings.get(underlying_corp_id, 0.0)
                is_naked = held < shares_covered_millions
            else:
                is_naked = True
        else:
            self.system_pool_cash += premium

        oid = self.next_option_id
        self.next_option_id += 1
        contract = OptionContract(
            contract_id=oid,
            holder_id=holder_id,
            writer_id=writer_id,
            underlying_corp_id=underlying_corp_id,
            opt_type=opt_type.upper(),
            strike_price=strike_price,
            shares_covered=shares_covered_millions,
            months_to_expiry=months_to_expiry,
            is_naked=is_naked,
            premium_paid_millions=premium,
            current_value_millions=premium,
        )
        self.options[oid] = contract
        self._revalue_all_options()
        if holder_id > 0:
            self.recompute_entity_balance_sheet(self.entities[holder_id], update_stock_price=False)
        if writer_id > 0:
            self.recompute_entity_balance_sheet(self.entities[writer_id], update_stock_price=False)
        return {"ok": True, "contract_id": oid, "premium_millions": premium, "is_naked": is_naked}

    def _revalue_all_options(self) -> None:
        """Implements WSR GetNakedOptionLiab (VA 0x00604E4E) & OptionPortfolio valuation."""
        for ent in self.entities.values():
            ent.option_portfolio_value = 0.0
            ent.naked_option_liab = 0.0

        for opt in self.options.values():
            p = self.price_option_per_share(
                opt.underlying_corp_id, opt.opt_type, opt.strike_price, opt.months_to_expiry
            )
            val = p * opt.shares_covered
            opt.current_value_millions = val
            if opt.holder_id in self.entities:
                self.entities[opt.holder_id].option_portfolio_value += val
            if opt.writer_id in self.entities:
                writer = self.entities[opt.writer_id]
                if opt.opt_type == "CALL":
                    held = writer.stock_holdings.get(opt.underlying_corp_id, 0.0)
                    opt.is_naked = held < (opt.shares_covered - 1e-9)
                else:
                    opt.is_naked = True
                writer.naked_option_liab += val

    def issue_convertible_bonds(
        self,
        issuer_corp_id: int,
        par_millions: float,
        conversion_price: float,
        coupon_pct: float,
        maturity_year: int,
        buyer_id: int = 0,
    ) -> Dict[str, Any]:
        """
        Implements WSR IssueCV (VA 0x00684901):
        Issues convertible bonds with identifier "YYYYcv|CVP|@cc.cc".
        """
        issuer = self.entities[issuer_corp_id]
        if issuer.regime == "ETF_FUND":
            return {"ok": False, "reason": "ETFs cannot issue convertible bonds"}
        code = f"{maturity_year}cv|{conversion_price:.2f}|@{coupon_pct:.2f}"
        cv_id = self.next_cv_id
        self.next_cv_id += 1

        if buyer_id > 0 and buyer_id in self.entities:
            buyer = self.entities[buyer_id]
            if buyer.cash < par_millions:
                return {"ok": False, "reason": "Buyer has insufficient cash"}
            buyer.cash -= par_millions
            buyer.corp_bonds_par += par_millions
            buyer.corp_bonds_adj_cost += par_millions
            buyer.corp_bonds_mkt_value += par_millions
            self.recompute_entity_balance_sheet(buyer, update_stock_price=False)
        else:
            self.system_pool_cash -= par_millions

        issuer.cash += par_millions
        issuer.convertible_bonds_out += par_millions
        self.convertible_bonds[cv_id] = ConvertibleBondIssue(
            issue_id=cv_id,
            issuer_corp_id=issuer_corp_id,
            code=code,
            maturity_year=maturity_year,
            conversion_price=conversion_price,
            coupon_pct=coupon_pct,
            par_outstanding_millions=par_millions,
            holders={buyer_id: par_millions},
        )
        self.recompute_entity_balance_sheet(issuer, update_stock_price=True)
        return {"ok": True, "issue_id": cv_id, "code": code, "par_millions": par_millions}

    def convert_convertible_bonds(self, issue_id: int, holder_id: int = 0) -> Dict[str, Any]:
        """
        Converts convertible bonds into newly issued common stock at conversion_price (CVP):
          - Extinguishes convertible_bonds_out liability ($M)
          - Increases shares_outstanding by (par_converted / CVP), diluting existing shareholders!
        """
        if issue_id not in self.convertible_bonds:
            return {"ok": False, "reason": "Convertible bond issue not found"}
        cv = self.convertible_bonds[issue_id]
        issuer = self.entities[cv.issuer_corp_id]
        par_held = cv.holders.get(holder_id, 0.0)
        if par_held <= 0.0:
            return {"ok": False, "reason": "No convertible bonds held by specified holder"}
        if issuer.stock_price < cv.conversion_price:
            return {"ok": False, "reason": "Stock price below conversion price"}

        new_shares = par_held / cv.conversion_price
        issuer.convertible_bonds_out = max(0.0, issuer.convertible_bonds_out - par_held)
        issuer.shares_outstanding += new_shares
        cv.par_outstanding_millions = max(0.0, cv.par_outstanding_millions - par_held)
        cv.holders[holder_id] = 0.0

        if holder_id > 0 and holder_id in self.entities:
            holder = self.entities[holder_id]
            holder.corp_bonds_par = max(0.0, holder.corp_bonds_par - par_held)
            holder.corp_bonds_adj_cost = max(0.0, holder.corp_bonds_adj_cost - par_held)
            holder.corp_bonds_mkt_value = max(0.0, holder.corp_bonds_mkt_value - par_held)
            holder.stock_holdings[issuer.entity_id] = holder.stock_holdings.get(issuer.entity_id, 0.0) + new_shares
            holder.stock_cost_basis[issuer.entity_id] = holder.stock_cost_basis.get(issuer.entity_id, 0.0) + par_held
            self.recompute_entity_balance_sheet(holder, update_stock_price=False)
        else:
            self.public_float_shares[issuer.entity_id] = (
                self.public_float_shares.get(issuer.entity_id, 0.0) + new_shares
            )

        self.recompute_entity_balance_sheet(issuer, update_stock_price=True)
        return {
            "ok": True,
            "new_shares_issued_millions": new_shares,
            "new_shares_outstanding_millions": issuer.shares_outstanding,
            "post_conversion_stock_price": issuer.stock_price,
        }

    def create_interest_rate_swap(
        self,
        party_a_id: int,
        party_b_id: int,
        notional_millions: float,
        fixed_rate_pct: float,
        floating_benchmark: str = "PRIME",
        party_a_pays_fixed: bool = True,
        duration_quarters: int = 8,
    ) -> Dict[str, Any]:
        """Creates an Interest Rate Swap contract (WSR Event 1685 / DoSwap @ 0x00638397)."""
        swap_id = self.next_swap_id
        self.next_swap_id += 1
        self.swaps[swap_id] = InterestRateSwapContract(
            swap_id=swap_id,
            party_a_id=party_a_id,
            party_b_id=party_b_id,
            notional_millions=notional_millions,
            fixed_rate_pct=fixed_rate_pct,
            floating_benchmark=floating_benchmark.upper(),
            party_a_pays_fixed=party_a_pays_fixed,
            remaining_quarters=duration_quarters,
        )
        return {"ok": True, "swap_id": swap_id}

    def settle_quarterly_swaps(self) -> List[Dict[str, Any]]:
        """
        Settles net quarterly interest differential across all active IRS contracts:
          Delta_Cash = Notional * (Rate_Receive - Rate_Pay) * 0.25 / 100.0
        """
        settlements = []
        for sid, sw in list(self.swaps.items()):
            if sw.floating_benchmark == "LONG_BOND":
                float_rate = self.long_bond_rate_pct
            elif sw.floating_benchmark == "SHORT_TBILL":
                float_rate = self.short_bond_rate_pct
            else:
                float_rate = self.prime_rate_pct

            if sw.party_a_pays_fixed:
                net_rate_diff = float_rate - sw.fixed_rate_pct
            else:
                net_rate_diff = sw.fixed_rate_pct - float_rate

            cash_flow_to_a = sw.notional_millions * (net_rate_diff / 100.0) * 0.25
            if sw.party_a_id in self.entities:
                self.entities[sw.party_a_id].cash += cash_flow_to_a
                self.recompute_entity_balance_sheet(self.entities[sw.party_a_id], update_stock_price=False)
            else:
                self.system_pool_cash += cash_flow_to_a

            if sw.party_b_id > 0 and sw.party_b_id in self.entities:
                self.entities[sw.party_b_id].cash -= cash_flow_to_a
                self.recompute_entity_balance_sheet(self.entities[sw.party_b_id], update_stock_price=False)
            else:
                self.system_pool_cash -= cash_flow_to_a

            sw.remaining_quarters -= 1
            settlements.append({"swap_id": sid, "cash_flow_to_a_millions": cash_flow_to_a})
            if sw.remaining_quarters <= 0:
                del self.swaps[sid]
        return settlements

    # =========================================================================
    # 6. BANKING (IND=1), BAD DEBT WRITE-OFFS, M&A, LIQUIDATION & SPIN-OFF
    # =========================================================================

    def borrow_bank_loan(
        self, borrower_id: int, amount_millions: float, lender_bank_id: Optional[int] = None, allow_emergency: bool = False
    ) -> Dict[str, Any]:
        """Bilateral loan from a Commercial Bank (IND=1) to an Entity, preserving closed-loop cash."""
        borrower = self.entities[borrower_id]
        if amount_millions <= 0.0:
            return {"ok": False, "reason": "Loan amount must be positive"}
        if not allow_emergency and borrower.bank_loan + amount_millions > borrower.credit_line_limit + 1e-4:
            return {"ok": False, "reason": "Exceeds credit line limit"}

        bank_id = lender_bank_id or borrower.lender_bank_id or (self.bank_corp_ids[0] if self.bank_corp_ids else 0)
        borrower.cash += amount_millions
        borrower.bank_loan += amount_millions
        borrower.lender_bank_id = bank_id

        if bank_id in self.entities and self.entities[bank_id].regime == "COMMERCIAL_BANK":
            bank = self.entities[bank_id]
            bank.biz_loans += amount_millions
            bank.cash -= amount_millions
            if bank.cash < 10.0:
                # Borrow from Interbank Fed Funds window to maintain liquidity
                topup = 50.0 - bank.cash
                bank.cash += topup
                bank.interbank_debt += topup
                self.system_pool_cash -= topup
            self.recompute_entity_balance_sheet(bank, update_stock_price=True)
        else:
            self.system_pool_cash -= amount_millions

        self.recompute_entity_balance_sheet(borrower, update_stock_price=False)
        return {"ok": True, "borrowed_millions": amount_millions, "lender_bank_id": bank_id}

    def repay_bank_loan(self, borrower_id: int, amount_millions: float) -> Dict[str, Any]:
        borrower = self.entities[borrower_id]
        repay = min(amount_millions, borrower.bank_loan, borrower.cash)
        if repay <= 0.0:
            return {"ok": False, "reason": "Nothing to repay"}
        borrower.cash -= repay
        borrower.bank_loan -= repay
        bank_id = borrower.lender_bank_id
        if bank_id in self.entities and self.entities[bank_id].regime == "COMMERCIAL_BANK":
            bank = self.entities[bank_id]
            bank.biz_loans = max(0.0, bank.biz_loans - repay)
            bank.cash += repay
            self.recompute_entity_balance_sheet(bank, update_stock_price=True)
        else:
            self.system_pool_cash += repay
        self.recompute_entity_balance_sheet(borrower, update_stock_price=False)
        return {"ok": True, "repaid_millions": repay}

    def trigger_borrower_default_on_bank(
        self, borrower_corp_id: int, recovery_rate: float = 0.20
    ) -> Dict[str, Any]:
        """
        Implements WSR Bankruptcy (VA 0x004E667C) & Bank Bad Debt Write-Off (BankAlloc @ 0x0061B266):
          - When a heavily indebted corporation defaults on its bank loan from Bank B (IND=1):
          - The unrecovered loan loss is written off against Bank B's BadDebtReserves and BizLoans,
            directly eroding Bank B's NetWorth, CAR%, and CreditRating!
        """
        borrower = self.entities[borrower_corp_id]
        bank_id = borrower.lender_bank_id
        loan_amt = borrower.bank_loan
        if loan_amt <= 0.0 or bank_id not in self.entities:
            return {"ok": False, "reason": "No bank loan to default on"}

        bank = self.entities[bank_id]
        old_bank_nw = bank.net_worth
        old_bank_car = 100.0 * bank.net_worth / max(1.0, bank.total_assets)
        old_bank_rating = bank.credit_rating

        recovered = min(borrower.cash, loan_amt * recovery_rate)
        loss_amount = loan_amt - recovered

        borrower.cash -= recovered
        borrower.bank_loan = 0.0
        borrower.is_bankrupt = True

        bank.cash += recovered
        bank.biz_loans = max(0.0, bank.biz_loans - loan_amt)
        # Provision additional bad debt reserve for residual stress
        bank.bad_debt_reserves += loss_amount * 0.25

        self.recompute_entity_balance_sheet(borrower, update_stock_price=True)
        self.recompute_entity_balance_sheet(bank, update_stock_price=True)
        new_bank_car = 100.0 * bank.net_worth / max(1.0, bank.total_assets)

        return {
            "ok": True,
            "loan_defaulted_millions": loan_amt,
            "loss_written_off_millions": loss_amount,
            "old_bank_net_worth": old_bank_nw,
            "new_bank_net_worth": bank.net_worth,
            "old_bank_car_pct": old_bank_car,
            "new_bank_car_pct": new_bank_car,
            "old_bank_rating": old_bank_rating,
            "new_bank_rating": bank.credit_rating,
        }

    def liquidate_subsidiary(self, parent_corp_id: int, sub_corp_id: int) -> Dict[str, Any]:
        """
        Implements WSR Liquidate (VA 0x005C1EB1):
          - Merges 100% of subsidiary's assets & liabilities into parent, paying private minority
            shareholders their exact pro-rata cash value and retiring their shares (no ghost shares).
          - Enforces the 80% Ownership Threshold:
            * Ownership >= 80%: Tax-Free Liquidation (cap_tax_incurred = 0.0).
            * Ownership <  80%: Taxable Liquidation (CapTax on gain over cost basis).
        """
        parent = self.entities[parent_corp_id]
        sub = self.entities[sub_corp_id]
        if parent.regime == "PLAYER_INDIVIDUAL" and parent.ceo_of_corp_ids:
            for c_id in sorted(parent.ceo_of_corp_ids):
                if c_id in self.entities and self.entities[c_id].stock_holdings.get(sub_corp_id, 0.0) > 0:
                    parent_corp_id = c_id
                    parent = self.entities[parent_corp_id]
                    break
        if parent.regime in ("PLAYER_INDIVIDUAL", "ETF_FUND") or parent.shares_outstanding <= 0.0:
            return {"ok": False, "reason": "Liquidation requires a Parent Corporation (#11..#1580) as Actor"}
        if parent_corp_id == sub_corp_id:
            return {"ok": False, "reason": "Corporation cannot liquidate itself"}
        shares_held = parent.stock_holdings.get(sub_corp_id, 0.0)
        ownership_pct = 100.0 * shares_held / max(1e-6, sub.shares_outstanding)
        if ownership_pct < 50.0:
            return {"ok": False, "reason": "Must own >= 50% to liquidate subsidiary"}

        # Force-cover any short positions in sub_corp_id before liquidation so no ghost shorts remain
        for ent in list(self.entities.values()):
            s_qty = ent.short_positions.get(sub_corp_id, 0.0)
            if s_qty > 0.0:
                self.cover_short_stock(ent.entity_id, sub_corp_id, s_qty)

        self.recompute_entity_balance_sheet(sub, update_stock_price=False)
        shares_held = parent.stock_holdings.get(sub_corp_id, 0.0)
        ownership_pct = 100.0 * shares_held / max(1e-6, sub.shares_outstanding)
        parent_share_nw = sub.net_worth * (ownership_pct / 100.0)
        cost_basis = parent.stock_cost_basis.get(sub_corp_id, 0.0)
        gain = max(0.0, parent_share_nw - cost_basis)

        is_tax_free = ownership_pct >= 80.0 - 1e-6
        cap_tax_incurred = 0.0 if is_tax_free else gain * self.capital_gains_tax_rate

        # Remove parent's stake in sub
        parent.stock_holdings.pop(sub_corp_id, None)
        parent.stock_cost_basis.pop(sub_corp_id, None)

        # Pay out all private minority shareholders pro-rata and clear their holdings in sub_corp_id
        liq_price_per_share = sub.net_worth / max(1e-6, sub.shares_outstanding)
        paid_to_private_minorities = 0.0
        for holder in self.entities.values():
            if holder.entity_id == parent_corp_id or not holder.is_active:
                continue
            h_shares = holder.stock_holdings.pop(sub_corp_id, 0.0)
            h_basis = holder.stock_cost_basis.pop(sub_corp_id, 0.0)
            if h_shares > 0.0:
                payout = h_shares * max(0.0, liq_price_per_share)
                holder.cash += payout
                paid_to_private_minorities += payout
                h_gain = payout - h_basis
                if h_gain > 0.0:
                    if holder.regime == "PLAYER_INDIVIDUAL":
                        holder.realized_cap_gain_loss += h_gain
                        holder.income_tax_owed += h_gain * self.capital_gains_tax_rate
                    else:
                        holder.cap_tax += h_gain * self.capital_gains_tax_rate
                self.recompute_entity_balance_sheet(holder, update_stock_price=False)

        # Pay out remaining anonymous public float into system_pool_cash
        pub_shares = self.public_float_shares.get(sub_corp_id, 0.0)
        paid_to_public = pub_shares * max(0.0, liq_price_per_share)
        self.system_pool_cash += paid_to_public
        minority_payout = paid_to_private_minorities + paid_to_public

        # Transfer subsidiary's stock portfolio & short positions into parent
        for t_cid, sh in list(sub.stock_holdings.items()):
            basis = sub.stock_cost_basis.get(t_cid, 0.0)
            if t_cid == parent_corp_id:
                # Re-issue cross-held parent shares to public float for cash
                val = sh * parent.stock_price
                parent.cash += val
                self.system_pool_cash -= val
                self.public_float_shares[parent_corp_id] = self.public_float_shares.get(parent_corp_id, 0.0) + sh
            elif sh > 0.0:
                parent.stock_holdings[t_cid] = parent.stock_holdings.get(t_cid, 0.0) + sh
                parent.stock_cost_basis[t_cid] = parent.stock_cost_basis.get(t_cid, 0.0) + basis
        sub.stock_holdings.clear()
        sub.stock_cost_basis.clear()

        for t_cid, sh in list(sub.short_positions.items()):
            if t_cid == parent_corp_id:
                self.public_float_shares[parent_corp_id] = max(0.0, self.public_float_shares.get(parent_corp_id, 0.0) - sh)
            elif sh > 0.0:
                parent.short_positions[t_cid] = parent.short_positions.get(t_cid, 0.0) + sh
        sub.short_positions.clear()

        # Reassign any option contracts or convertible bonds referencing sub
        for opt in self.options.values():
            if opt.holder_id == sub_corp_id:
                opt.holder_id = parent_corp_id
            if opt.writer_id == sub_corp_id:
                opt.writer_id = parent_corp_id
        for cv in self.convertible_bonds.values():
            if cv.issuer_corp_id == sub_corp_id:
                cv.issuer_corp_id = parent_corp_id

        # Absorb all remaining subsidiary assets & liabilities into parent
        parent.cash += sub.cash - minority_payout
        parent.tbills += sub.tbills
        parent.cap_assets_abstract += sub.cap_assets_abstract
        parent.cap_assets_caplab_firms += sub.cap_assets_caplab_firms
        parent.working_cap_abstract += sub.working_cap_abstract
        parent.working_cap_caplab_inventory += sub.working_cap_caplab_inventory
        parent.unamortized_goodwill += sub.unamortized_goodwill
        parent.advances_to_subsidiaries += sub.advances_to_subsidiaries
        parent.gov_bonds_par += sub.gov_bonds_par
        parent.gov_bonds_adj_cost += sub.gov_bonds_adj_cost
        parent.gov_bonds_mkt_value += sub.gov_bonds_mkt_value
        parent.corp_bonds_par += sub.corp_bonds_par
        parent.corp_bonds_adj_cost += sub.corp_bonds_adj_cost
        parent.corp_bonds_mkt_value += sub.corp_bonds_mkt_value
        parent.commod_mtm += sub.commod_mtm
        parent.commod_margin += sub.commod_margin
        parent.bank_loan += sub.bank_loan
        parent.advances_from_parents += sub.advances_from_parents
        parent.straight_bonds_out += sub.straight_bonds_out
        parent.convertible_bonds_out += sub.convertible_bonds_out
        parent.acc_tax += sub.acc_tax
        parent.cap_tax += sub.cap_tax + cap_tax_incurred
        parent.hid_reserve += sub.hid_reserve

        # Transfer any CapLab firms owned by subsidiary
        for firm in self.firms.values():
            if firm.owner_corp_id == sub_corp_id:
                firm.owner_corp_id = parent_corp_id

        # Zero out all balances on deactivated subsidiary
        sub.cash = 0.0
        sub.tbills = 0.0
        sub.cap_assets_abstract = 0.0
        sub.cap_assets_caplab_firms = 0.0
        sub.working_cap_abstract = 0.0
        sub.working_cap_caplab_inventory = 0.0
        sub.unamortized_goodwill = 0.0
        sub.advances_to_subsidiaries = 0.0
        sub.gov_bonds_par = 0.0
        sub.gov_bonds_adj_cost = 0.0
        sub.gov_bonds_mkt_value = 0.0
        sub.corp_bonds_par = 0.0
        sub.corp_bonds_adj_cost = 0.0
        sub.corp_bonds_mkt_value = 0.0
        sub.commod_mtm = 0.0
        sub.commod_margin = 0.0
        sub.bank_loan = 0.0
        sub.advances_from_parents = 0.0
        sub.straight_bonds_out = 0.0
        sub.convertible_bonds_out = 0.0
        sub.acc_tax = 0.0
        sub.cap_tax = 0.0
        sub.hid_reserve = 0.0
        sub.is_active = False
        if sub_corp_id in self.active_corp_ids:
            self.active_corp_ids.remove(sub_corp_id)
        self.public_float_shares[sub_corp_id] = 0.0

        self._revalue_all_options()
        self.recompute_entity_balance_sheet(sub, update_stock_price=False)
        self.recompute_entity_balance_sheet(parent, update_stock_price=True)
        return {
            "ok": True,
            "ownership_pct": ownership_pct,
            "is_tax_free": is_tax_free,
            "cap_tax_incurred_millions": cap_tax_incurred,
            "minority_payout_millions": minority_payout,
        }

    def spinoff_subsidiary(self, parent_corp_id: int, sub_corp_id: int) -> Dict[str, Any]:
        """
        Implements WSR SpinOff (VA 0x005CFAF2):
          - Distributes parent's shares in sub_corp_id pro-rata to parent's shareholders
            (and assigns matching short obligations to any short sellers of parent_corp_id
             so Share Conservation Sum(Long) + PublicFloat - Sum(Short) == SharesOutstanding holds 100%).
          - Enforces 80% Ownership Threshold:
            * Ownership >= 80%: Tax-Free Spin-Off.
            * Ownership <  80%: Taxable Spin-Off (CapTax on gain over cost basis).
        """
        parent = self.entities[parent_corp_id]
        sub = self.entities[sub_corp_id]
        if parent.regime == "PLAYER_INDIVIDUAL" and parent.ceo_of_corp_ids:
            for c_id in sorted(parent.ceo_of_corp_ids):
                if c_id in self.entities and self.entities[c_id].stock_holdings.get(sub_corp_id, 0.0) > 0:
                    parent_corp_id = c_id
                    parent = self.entities[parent_corp_id]
                    break
        if parent.regime in ("PLAYER_INDIVIDUAL", "ETF_FUND") or parent.shares_outstanding <= 0.0:
            return {"ok": False, "reason": "80% Spin-Off requires a Parent Corporation (#11..#1580) with shareholders as Actor"}
        if parent_corp_id == sub_corp_id:
            return {"ok": False, "reason": "Corporation cannot spin off itself"}
        shares_held = parent.stock_holdings.get(sub_corp_id, 0.0)
        ownership_pct = 100.0 * shares_held / max(1e-6, sub.shares_outstanding)
        if shares_held <= 0.0:
            return {"ok": False, "reason": "Parent holds no shares in subsidiary"}

        mkt_val = shares_held * sub.stock_price
        cost_basis = parent.stock_cost_basis.get(sub_corp_id, 0.0)
        gain = max(0.0, mkt_val - cost_basis)
        is_tax_free = ownership_pct >= 80.0 - 1e-6
        cap_tax_incurred = 0.0 if is_tax_free else gain * self.capital_gains_tax_rate
        parent.cap_tax += cap_tax_incurred

        # Ratio of subsidiary shares distributed per 1 share of parent
        ratio = shares_held / max(1e-6, parent.shares_outstanding)
        spin_val_per_parent_share = (shares_held * sub.stock_price) / max(1e-6, parent.shares_outstanding)

        parent.stock_holdings.pop(sub_corp_id, None)
        parent.stock_cost_basis.pop(sub_corp_id, None)
        # Ex-distribution stock price adjustment on parent
        parent.stock_price = max(0.10, round(parent.stock_price - spin_val_per_parent_share, 4))

        # 1. Distribute sub shares to all long holders of parent
        for holder in self.entities.values():
            if not holder.is_active:
                continue
            p_shares = holder.stock_holdings.get(parent_corp_id, 0.0)
            if p_shares > 0.0:
                alloc = p_shares * ratio
                holder.stock_holdings[sub_corp_id] = holder.stock_holdings.get(sub_corp_id, 0.0) + alloc
                # Split cost basis proportionally
                p_basis = holder.stock_cost_basis.get(parent_corp_id, 0.0)
                sub_mkt = alloc * sub.stock_price
                par_mkt = p_shares * parent.stock_price
                basis_shift = p_basis * (sub_mkt / max(1e-6, par_mkt + sub_mkt))
                holder.stock_cost_basis[parent_corp_id] = max(0.0, p_basis - basis_shift)
                holder.stock_cost_basis[sub_corp_id] = holder.stock_cost_basis.get(sub_corp_id, 0.0) + basis_shift
                self.recompute_entity_balance_sheet(holder, update_stock_price=False)

        # 2. Distribute sub shares corresponding to parent's public float
        parent_float = self.public_float_shares.get(parent_corp_id, 0.0)
        self.public_float_shares[sub_corp_id] = self.public_float_shares.get(sub_corp_id, 0.0) + parent_float * ratio

        # 3. Assign matching short positions in sub to any short sellers of parent
        for shorter in self.entities.values():
            if not shorter.is_active:
                continue
            s_shares = shorter.short_positions.get(parent_corp_id, 0.0)
            if s_shares > 0.0:
                s_alloc = s_shares * ratio
                shorter.short_positions[sub_corp_id] = shorter.short_positions.get(sub_corp_id, 0.0) + s_alloc
                self.recompute_entity_balance_sheet(shorter, update_stock_price=False)

        self.recompute_entity_balance_sheet(parent, update_stock_price=False)
        return {
            "ok": True,
            "ownership_pct": ownership_pct,
            "is_tax_free": is_tax_free,
            "cap_tax_incurred_millions": cap_tax_incurred,
        }

    def manipulate_earnings_reserve(
        self, corp_id: int, delta_reserve_millions: float
    ) -> Dict[str, Any]:
        """
        Implements WSR HidReserve manipulation (Events 910/920):
          - delta_reserve_millions > 0 (decreaseEarnings): shifts equity into hid_reserve liability.
          - delta_reserve_millions < 0 (increaseEarnings): releases hid_reserve back into equity/earnings.
        """
        corp = self.entities[corp_id]
        if delta_reserve_millions < 0:
            release = min(corp.hid_reserve, abs(delta_reserve_millions))
            corp.hid_reserve -= release
            corp.last_quarter_net_income += release
        else:
            corp.hid_reserve += delta_reserve_millions
            corp.last_quarter_net_income -= delta_reserve_millions
        self.recompute_entity_balance_sheet(corp, update_stock_price=True)
        return {"ok": True, "hid_reserve_millions": corp.hid_reserve, "net_worth_millions": corp.net_worth}

    def file_corporate_lawsuit(
        self, plaintiff_id: int, defendant_id: int, lawsuit_type: str, claim_millions: float
    ) -> Dict[str, Any]:
        """Files an Antitrust or Harassing Lawsuit (WSR Harass Countdown @ 0x00611AF8)."""
        if plaintiff_id == defendant_id:
            return {"ok": False, "reason": "Cannot file a lawsuit against yourself (select a different Target Corp ID)"}
        plaintiff = self.entities[plaintiff_id]
        legal_fee = max(0.0001, round(claim_millions * 0.02, 5))
        if plaintiff.cash < legal_fee:
            return {"ok": False, "reason": "Insufficient cash for legal retainer"}
        plaintiff.cash -= legal_fee
        self.system_pool_cash += legal_fee
        cid = self.next_lawsuit_id
        self.next_lawsuit_id += 1
        self.lawsuits[cid] = LawsuitCase(
            case_id=cid,
            plaintiff_id=plaintiff_id,
            defendant_id=defendant_id,
            lawsuit_type=lawsuit_type.upper(),
            claim_amount_millions=claim_millions,
            countdown_ticks=4,
            win_probability=0.45 if lawsuit_type.upper() == "ANTITRUST" else 0.30,
        )
        self.recompute_entity_balance_sheet(plaintiff, update_stock_price=False)
        return {"ok": True, "case_id": cid, "legal_fee_millions": legal_fee}

    def adjust_etf_leverage(self, etf_id: int) -> Dict[str, Any]:
        """Implements WSR AdjustLeverage (VA 0x0068E391) for 2x/-2x Leveraged Bull/Bear ETFs."""
        etf = self.entities[etf_id]
        if etf.regime != "ETF_FUND":
            return {"ok": False, "reason": "Not an ETF"}
        self.recompute_entity_balance_sheet(etf, update_stock_price=True)
        if etf.net_worth <= 5.0:
            # WSR ReviveETF (@ 0x0069D48C): Recapitalize wiped-out leveraged ETF
            inject = 500.0
            etf.cash += inject
            self.system_pool_cash -= inject
            self.recompute_entity_balance_sheet(etf, update_stock_price=True)

        if etf.etf_type == "LEVERAGED_BULL" and etf.leverage_factor > 1.0:
            # Target bank_loan ~ (leverage_factor - 1.0) * net_worth
            target_loan = max(0.0, etf.net_worth * (etf.leverage_factor - 1.0))
            diff = target_loan - etf.bank_loan
            if abs(diff) > 10.0:
                etf.bank_loan += diff
                etf.cash += diff
                self.system_pool_cash -= diff
        elif etf.etf_type == "LEVERAGED_BEAR" and etf.leverage_factor < 0.0:
            # Update inverse MTM based on GDP/market drift and rebalance short index exposure
            idx_spot = max(100.0, self.commodity_prices.get("STOCK_INDEX", 4500.0))
            contracts = etf.futures_positions.get("STOCK_INDEX", 0.0)
            if contracts != 0.0:
                mtm_change = contracts * (idx_spot - 4500.0) * 0.05
                etf.commod_mtm = mtm_change
            etf.futures_positions["STOCK_INDEX"] = (etf.leverage_factor * max(50.0, etf.net_worth)) / idx_spot

        self.recompute_entity_balance_sheet(etf, update_stock_price=True)
        return {"ok": True, "etf_nav_millions": etf.net_worth, "etf_share_price": etf.stock_price}

    # =========================================================================
    # 7. CAPITALISM LAB REAL ECONOMY & ZERO DOUBLE-COUNTING BRIDGE
    # =========================================================================

    def _normalize_product_code(self, code: str) -> str:
        c = (code or "").strip().upper()
        if not c:
            return ""
        c = CAPLAB_PRODUCT_ALIASES.get(c, c)
        if c in self.products or c in self.natural_resources:
            return c
        if len(c) > 7 and c[:7] in self.products:
            return c[:7]
        return c

    def _normalize_city_name(self, city_name: str) -> str:
        raw = (city_name or "").strip()
        if not raw:
            return "New York City"
        if raw in self.cities:
            return raw
        alias = CAPLAB_CITY_ALIASES.get(raw.upper())
        if alias and alias in self.cities:
            return alias
        for k in self.cities:
            if k.lower() == raw.lower() or k.lower().startswith(raw.lower()):
                return k
        return raw

    def _normalize_tech_code(self, code: str) -> str:
        c = (code or "").strip().upper()
        if not c:
            return "VIDEO_ST"
        c = CAPLAB_TECH_ALIASES.get(c, c)
        if c in self.tech_nodes or c in self.products or c in self.software_types:
            return c
        return "VIDEO_ST"

    def get_corporate_group_ids(self, corp_id: int) -> Set[int]:
        """
        Returns {corp_id} plus any parent corporation (>=50% stake) and controlled subsidiaries (>=50% stake)
        so vertical supply chain integration works across Parent <-> Subsidiary holdings.
        """
        group: Set[int] = {corp_id}
        ent = self.entities.get(corp_id)
        if not ent:
            return group
        # Controlled subsidiaries
        for sub_id, sh in ent.stock_holdings.items():
            sub = self.entities.get(sub_id)
            if sub and sub.is_active and (100.0 * sh / max(1e-6, sub.shares_outstanding)) >= 50.0:
                group.add(sub_id)
        # Controlling parent and sibling subsidiaries
        if ent.controlled_by_id and ent.controlled_by_id in self.entities:
            parent_id = ent.controlled_by_id
            parent = self.entities[parent_id]
            if parent.regime != "PLAYER_INDIVIDUAL":
                group.add(parent_id)
            for sib_id, sh in parent.stock_holdings.items():
                sib = self.entities.get(sib_id)
                if sib and sib.is_active and (100.0 * sh / max(1e-6, sib.shares_outstanding)) >= 50.0:
                    group.add(sib_id)
        return group

    def get_city_consumer_weights(self, product_code: str, city_name: str = "New York City") -> Tuple[float, float, float]:
        """
        Exact Capitalism Lab urban income-adjusted consumer preference weights
        (TownItem::next_day @ VA 0x00669DB8..0x00669E83):
          W_price(p,c) = clamp(PRICE_CN_p + Delta_W_price_c, 20, 90)
          W_qual(p,c)  = min(100 - W_price(p,c), max(10, QUALITY_CN_p + Delta_W_qual_c))
          W_brand(p,c) = 100 - W_price(p,c) - W_qual(p,c)
        """
        pcode = self._normalize_product_code(product_code)
        prod = self.products.get(pcode)
        if not prod:
            return (40.0, 30.0, 30.0)
        base_wp = float(prod.get("PRICE_CN", 40))
        base_wq = float(prod.get("QUALITY_CN", 30))
        base_wb = float(prod.get("BRAND_CN", 30))
        if base_wb == 0.0:
            # Unbranded raw/semi-finished goods
            return (base_wp, base_wq, 0.0)

        cname = self._normalize_city_name(city_name)
        city = self.cities.get(cname, {})
        wage_rate = float(city.get("WAGE_RATE", 60))
        # Richer cities (wage_rate > 60) have lower price sensitivity and higher quality/brand sensitivity
        delta_w_price = round((60.0 - wage_rate) * 0.35)
        delta_w_qual = round((wage_rate - 60.0) * 0.20)

        w_price = max(20.0, min(90.0, base_wp + delta_w_price))
        w_qual = min(100.0 - w_price, max(10.0, base_wq + delta_w_qual))
        w_brand = max(0.0, 100.0 - w_price - w_qual)
        return (w_price, w_qual, w_brand)

    def compute_caplab_product_rating(
        self,
        product_code: str,
        quality: float,
        brand: float,
        price: float,
        city_ref_price: Optional[float] = None,
        city_name: str = "New York City",
    ) -> float:
        """
        Exact Capitalism Lab Overall Product Rating formula:
          - Unbranded Raw/Semi Goods (BRAND_CN == 0, VA 0x005A07C0..0x005A07EA):
            OverallRating = floor(100 * (P_ref - P) / P_ref + Q / 2)
          - Branded Consumer & Tech Goods (towitem.cpp @ VA 0x0066A410..0x0066A545):
            R_quality = (Q * W_qual(p,c)) / 60.0
            R_brand   = (B * W_brand(p,c)) / 60.0
            R_price   = max(-300.0, 2.0 * W_price(p,c) * (P_ref - P) / P_ref)
        """
        pcode = self._normalize_product_code(product_code)
        prod = self.products.get(pcode)
        if not prod:
            return 50.0

        p_ref = city_ref_price if (city_ref_price and city_ref_price > 0) else max(0.01, float(prod.get("PRICE", 100.0)))
        if float(prod.get("BRAND_CN", 30)) == 0.0:
            # Raw / Semi-finished goods without brand (VA 0x005A07C0)
            raw_score = math.floor(100.0 * (p_ref - price) / p_ref + (quality / 2.0))
            return float(max(-100, raw_score))

        w_p, w_q, w_b = self.get_city_consumer_weights(pcode, city_name)
        r_q = (quality * w_q) / 60.0
        r_b = (brand * w_b) / 60.0
        r_p = max(-300.0, (2.0 * w_p * (p_ref - price)) / p_ref)
        return float(max(-100, int(r_q + r_b + r_p)))

    def compute_caplab_manufacturing_quality(self, firm: CapLabFirm) -> Tuple[float, float, int]:
        """
        Exact Capitalism Lab JobManufacturing::calc_quality (VA 0x005C2600..0x005C2889)
        and Supply Chain Vertical Integration COGS calculator (VA 0x005C0E04..0x005C1698):
          - Uses MANUFACTURING.DBF recipes (INPUT1..3, IQUA1..3, PROD_TECH = 100 - sum(IQUA)).
          - Checks corporate group (owner + parent/subsidiaries) for upstream firms supplying INPUT1..3.
          - Returns (output_quality, cogs_ratio, integrated_inputs_count).
        """
        pcode = self._normalize_product_code(firm.product_code)
        recipe = self.recipes.get(pcode)
        group_ids = self.get_corporate_group_ids(firm.owner_corp_id)

        # Map all upstream firms in the corporate group by their output product/resource code
        upstream_quality_by_code: Dict[str, float] = {}
        for f in self.firms.values():
            if f.owner_corp_id in group_ids and f.firm_id != firm.firm_id and f.firm_type != "RETAIL":
                out_code = self._normalize_product_code(f.product_code or f.resource_code or f.recipe_output)
                if out_code:
                    upstream_quality_by_code[out_code] = max(
                        upstream_quality_by_code.get(out_code, 0.0), f.product_quality
                    )

        # Lookup corporation's R&D technology level vs world TopTech frontier
        tmap = self.corp_tech_levels.get(firm.owner_corp_id, {})
        firm_tech = tmap.get(pcode)
        if firm_tech is None and firm.tech_code:
            firm_tech = tmap.get(self._normalize_tech_code(firm.tech_code))
        if firm_tech is None:
            # Also check if any R&D center in the corporate group researched a tech node for this industry
            cw_techs = self.crosswalk.get(self.entities[firm.owner_corp_id].industry_id, {}).get("tech_codes", [])
            best_t = 60.0
            for gid in group_ids:
                gtmap = self.corp_tech_levels.get(gid, {})
                if pcode in gtmap:
                    best_t = max(best_t, gtmap[pcode])
                for tc in cw_techs:
                    if tc in gtmap:
                        best_t = max(best_t, gtmap[tc])
            firm_tech = best_t

        top_tech = max(100.0, self.top_tech_levels.get(pcode, 100.0))

        cname = self._normalize_city_name(firm.city_name)
        city_wage = float(self.cities.get(cname, {}).get("WAGE_RATE", 60))
        delta_q_city = max(0, int(round((city_wage - 55.0) * 0.08)))
        delta_q_train = int(firm.unit_training_level) // 2

        if firm.firm_type == "RETAIL" or not recipe:
            # Retail store or non-recipe service sourcing finished goods from corporate factories
            if pcode in upstream_quality_by_code:
                q_out = max(firm.product_quality, upstream_quality_by_code[pcode])
                return (min(100.0, float(q_out)), 0.52 if firm.firm_type == "RETAIL" else 0.54, 1)
            q_tech_only = int((50.0 * firm_tech) // top_tech) + 25 + delta_q_city + delta_q_train
            return (min(100.0, float(q_tech_only)), 0.68 if firm.firm_type == "RETAIL" else 0.58, 0)

        # Recipe has INPUT1..3 and IQUA1..3 (exact x86 integer division per input @ VA 0x005C2855)
        q_inputs = 0
        total_iqua = 0
        integrated_count = 0
        unintegrated_commodity_surcharge = 0.0
        for idx in (1, 2, 3):
            in_code = (recipe.get(f"INPUT{idx}") or "").strip().upper()
            iqua = int(recipe.get(f"IQUA{idx}") or 0)
            if in_code and iqua > 0:
                total_iqua += iqua
                if in_code in upstream_quality_by_code:
                    q_in = upstream_quality_by_code[in_code]
                    integrated_count += 1
                else:
                    # Unintegrated open-market local supplier input quality (55.0)
                    # Plus WSR Commodity Spot Price Surcharge (Cross-Feedback Loop #2)
                    q_in = 55.0
                    c_mult = self.get_resource_commodity_multiplier(in_code)
                    unintegrated_commodity_surcharge += (iqua / 100.0) * max(-0.05, (c_mult - 1.0) * 0.16)
                q_inputs += int((iqua * q_in) // 100)

        prod_tech_weight = max(10, 100 - total_iqua)
        # Exact CapMain.exe JobManufacturing::calc_quality tech contribution (VA 0x005C2767..0x005C2832)
        q_tech = min(
            prod_tech_weight,
            int((prod_tech_weight * firm_tech) // max(1.0, top_tech)),
        )
        q_out = min(100.0, float(q_inputs + q_tech + delta_q_city + delta_q_train))

        # Base factory COGS is 0.58; each vertically integrated input reduces COGS & freight by 0.05,
        # while unintegrated inputs are exposed to WSR commodity spot inflation/deflation.
        cogs_ratio = max(0.35, min(0.88, round(0.58 - 0.05 * integrated_count + unintegrated_commodity_surcharge, 4)))
        return (q_out, cogs_ratio, integrated_count)

    def get_resource_commodity_multiplier(self, code: str) -> float:
        """
        Cross-Feedback Loop #2 (WSR Commodity Futures <-> CapLab Natural Resources & Factory Inputs):
        Maps any Capitalism Lab resource or product code to its corresponding WSR commodity spot-to-baseline ratio.
        Baselines: OIL=75.0, GOLD=2000.0, SILVER=25.0, WHEAT=6.50, CORN=5.20, COPPER=4.10.
        """
        c = (code or "").strip().upper()
        oil_r = self.commodity_prices.get("OIL", 75.0) / 75.0
        gold_r = self.commodity_prices.get("GOLD", 2000.0) / 2000.0
        silv_r = self.commodity_prices.get("SILVER", 25.0) / 25.0
        wheat_r = self.commodity_prices.get("WHEAT", 6.50) / 6.50
        corn_r = self.commodity_prices.get("CORN", 5.20) / 5.20
        copp_r = self.commodity_prices.get("COPPER", 4.10) / 4.10

        if c in ("OIL", "CHEMICAL", "PLASTIC", "POLYEST", "RUBBER", "DYESTUFF", "CITRIC_A", "GASOLINE"):
            return oil_r
        if c in ("GOLD", "JEWELRY", "WATCH"):
            return gold_r
        if c in ("SILVER",):
            return silv_r
        if c in ("WHEAT", "FLOUR", "BREAD", "PASTA", "CAKE", "CEREAL", "COOKIES", "SUGAR"):
            return wheat_r
        if c in ("CORN", "CATTLE", "PIG", "CHICKEN", "LAMB", "MILK", "EGGS", "TIMBER", "WOOD", "PAPER", "COTTON", "WOOL", "LEATHER"):
            return 0.5 * (corn_r + wheat_r)
        if c in ("IRON", "STEEL", "ALUMINIU", "SILICA", "COPPER", "COAL", "GLASS", "ELECTRO", "SEMI_CON", "COMPUTER", "SMARTPH", "NOTEBOOK", "CAR", "MOTORCYC", "CARBODY", "ENGINE", "WHEEL"):
            return 0.65 * copp_r + 0.35 * oil_r
        return (oil_r + copp_r + wheat_r) / 3.0

    def compute_caplab_city_quarterly_demand_millions(
        self, product_code: str, city_name: str, avg_market_price: float
    ) -> float:
        """
        Exact Capitalism Lab Urban Demand & Price Elasticity model
        (TownItem::calc_demand @ VA 0x0066A079..0x0066A407):
          1. Price elasticity phi_P based on NECESSITY_p in [1..10].
          2. Base demand from POPULATION index and DEMAND factor.
          3. Urban purchasing power I_cons from WAGE_RATE and GDP growth modulated by w_nec = 0.8 * NECESSITY + 2.0.
        """
        pcode = self._normalize_product_code(product_code)
        prod = self.products.get(pcode, {})
        cname = self._normalize_city_name(city_name)
        city = self.cities.get(cname, {"POPULATION": 65, "WAGE_RATE": 60})

        p_std = max(0.01, float(prod.get("PRICE", 100.0)))
        necessity = max(1.0, min(10.0, float(prod.get("NECESSITY", 5))))
        demand_coeff = max(0.05, float(prod.get("DEMAND", 0.5)))

        raw_pop = float(city.get("POPULATION", 65))
        # In CITIES.DBF, POPULATION is an urban size index (e.g. 40..95); normalize if raw_pop > 500
        pop_index = raw_pop if raw_pop <= 500.0 else (raw_pop / 40_000.0)
        wage_rate = float(city.get("WAGE_RATE", 60))

        # 1. Price elasticity factor phi_P (VA 0x0066A079)
        if avg_market_price < p_std:
            phi_p = 0.8 + ((11.0 - necessity) * (p_std - avg_market_price)) / (11.0 * p_std)
        else:
            phi_p = max(0.35, 0.8 - 0.25 * ((avg_market_price - p_std) / p_std))

        # 2. Urban consumer index I_cons and necessity weight w_nec (VA 0x0066A1DA..0x0066A36E)
        w_nec = 0.8 * necessity + 2.0  # in [2.8, 10.0]
        gdp_clamped = max(-15.0, min(15.0, self.gdp_growth_pct * 2.5))
        i_cons = max(10.0, min(200.0, 2.0 * (wage_rate - 30.0) + gdp_clamped))
        macro_mod = (100.0 * w_nec + (10.0 - w_nec) * i_cons) / 1000.0

        # Scale into quarterly urban market revenue pool ($M)
        base_pool_m = (pop_index * 1.45) * (0.45 + 0.15 * math.log1p(demand_coeff * 10.0)) * phi_p * macro_mod
        return max(8.0, round(base_pool_m, 4))

    def build_caplab_firm(
        self,
        owner_corp_id: int,
        firm_type: str,
        build_code: str,
        city_name: str,
        capex_millions: float,
        initial_inventory_millions: float = 0.0,
        product_code: str = "",
        tech_code: str = "",
        software_code: str = "",
        resource_code: str = "",
        rd_units: int = 9,
    ) -> Dict[str, Any]:
        """
        Builds a Capitalism Lab Firm owned by owner_corp_id while strictly enforcing
        Trap 6 — Zero Double-Counting CAPEX/OPEX Bridge:
          - Deducts (capex_millions + initial_inventory_millions) from owner.cash
          - Adds capex_millions directly to owner.cap_assets_caplab_firms
          - Adds initial_inventory_millions directly to owner.working_cap_caplab_inventory
          - Guarantees: Delta_Cash + Delta_CapAssets + Delta_WorkingCap == 0.0 (Delta_NetWorth == 0.0)!
        """
        owner = self.entities[owner_corp_id]
        if owner.regime == "PLAYER_INDIVIDUAL" and owner.ceo_of_corp_ids:
            owner_corp_id = sorted(owner.ceo_of_corp_ids)[0]
            owner = self.entities[owner_corp_id]
        if owner.regime == "PLAYER_INDIVIDUAL":
            return {"ok": False, "reason": "Select a Corporation ID (#11..#1580) as Owner Corp ID, or Incorporate a Startup first"}
        if owner.regime in ("COMMERCIAL_BANK", "INSURANCE_COMPANY", "ETF_FUND"):
            return {"ok": False, "reason": f"Regime {owner.regime} cannot own physical CapLab firms directly"}

        total_outlay = capex_millions + initial_inventory_millions
        if owner.cash < total_outlay:
            if owner.net_worth < 2.0 and owner.cash >= 0.004:
                # Auto-size micro-firm CAPEX to fit a $30k-$500k startup's cash
                capex_millions = round(owner.cash * 0.60, 4)
                initial_inventory_millions = 0.0 if firm_type.upper() in ("RD", "APARTMEN", "COMMERCI", "MALL", "OFFICE", "SOFTWARE") else round(owner.cash * 0.15, 4)
                total_outlay = capex_millions + initial_inventory_millions
            else:
                return {"ok": False, "reason": "Insufficient corporate cash for CAPEX"}

        old_nw = owner.net_worth
        owner.cash -= total_outlay
        self.system_pool_cash += total_outlay
        owner.cap_assets_caplab_firms += capex_millions
        owner.working_cap_caplab_inventory += initial_inventory_millions

        norm_city = self._normalize_city_name(city_name)
        norm_prod = self._normalize_product_code(product_code)
        if not norm_prod:
            cw = self.crosswalk.get(owner.industry_id, {})
            prods = cw.get("product_codes", [])
            norm_prod = prods[0] if prods else "CAR"

        norm_tech = self._normalize_tech_code(tech_code) if tech_code else ""
        norm_res = self._normalize_product_code(resource_code) if resource_code else ""
        ftype_u = firm_type.upper()

        base_price = float(self.products.get(norm_prod, {}).get("PRICE", 100.0))
        fid = self.next_firm_id
        self.next_firm_id += 1
        is_micro = capex_millions < 5.0
        firm = CapLabFirm(
            firm_id=fid,
            owner_corp_id=owner_corp_id,
            firm_type=ftype_u,
            build_code=build_code.upper(),
            city_name=norm_city,
            book_value_millions=capex_millions,
            inventory_value_millions=initial_inventory_millions,
            product_code=norm_prod,
            recipe_output=norm_prod if norm_prod in self.recipes else "",
            tech_code=norm_tech,
            resource_code=norm_res or (norm_prod if ftype_u in ("MINE", "OIL", "FOREST", "FARM") else ""),
            software_code=software_code.upper() if software_code else "",
            product_quality=78.0 if ftype_u in ("MINE", "OIL", "FOREST", "FARM") else 65.0,
            unit_price=base_price,
            advertising_budget_millions=round(max(0.0005, capex_millions * 0.025), 5) if is_micro else 0.5,
            monthly_operating_Cost_millions=round(max(0.0002, capex_millions * 0.012), 5) if is_micro else 0.25,
            rd_units=max(1, min(9, int(rd_units))),
        )
        self.firms[fid] = firm
        self.recompute_entity_balance_sheet(owner, update_stock_price=False)

        return {
            "ok": True,
            "firm_id": fid,
            "firm_type": ftype_u,
            "city_name": norm_city,
            "product_code": norm_prod,
            "capex_millions": capex_millions,
            "inventory_millions": initial_inventory_millions,
            "pre_capex_net_worth": old_nw,
            "post_capex_net_worth": owner.net_worth,
            "net_worth_delta": round(owner.net_worth - old_nw, 8),
        }

    def step_caplab_firms_quarterly(self) -> Dict[int, float]:
        """
        Executes quarterly bottom-up Capitalism Lab firm operations:
          Phase 1: R&D Centers (JobRD @ VA 0x005CDBCE with 3x3 Synergy table @ 0x008D0818)
                   advance corp_tech_levels and world top_tech_levels; Resource firms (MINE/OIL/FARM/FOREST)
                   produce raw inputs.
          Phase 2: Manufacturing & Retail Quality/Brand update (JobManufacturing::calc_quality @ 0x005C2600,
                   MANUFACTURING.DBF Input 1..3 -> Output vertical integration, and 3 Brand Modes @ 0x005A042E).
          Phase 3: Multi-Firm Urban Market Share Competition per (city_name, product_code)
                   (TownItem::calc_demand @ 0x0066A079 & TownProduct::process_demand @ 0x0066AD80).
        """
        corp_ebit_map: Dict[int, float] = {}
        market_groups: Dict[Tuple[str, str], List[CapLabFirm]] = {}

        # Cross-Feedback Loop #3: WSR Inflation & Interest Rates -> CapLab OPEX & Real Estate Occupancy
        inflation_opex_mult = max(0.85, min(1.65, 1.0 + (self.inflation_pct - 2.4) * 0.035))
        rate_occupancy_mod = max(
            0.60,
            min(1.25, 1.0 - (self.prime_rate_pct - 6.50) * 0.035 + (self.gdp_growth_pct - 2.8) * 0.015),
        )

        # Phase 1: Execute R&D Centers, Resource Extraction, Real Estate, and Digital/Software Firms
        for firm in self.firms.values():
            owner = self.entities.get(firm.owner_corp_id)
            if not owner or not owner.is_active:
                continue

            cname = self._normalize_city_name(firm.city_name)
            city = self.cities.get(cname, {"POPULATION": 65, "WAGE_RATE": 60})
            wage_factor = 0.8 + 0.4 * (float(city.get("WAGE_RATE", 60)) / 100.0)

            if firm.firm_type == "RD":
                rev = 0.0
                ebit = -(firm.monthly_operating_Cost_millions * 3.0 * inflation_opex_mult)
                # JobRD 3x3 Team Synergy Multiplier (VA 0x008D0818: [100..480]%)
                synergy_pct = CAPLAB_RD_SYNERGY_MULT[max(1, min(9, firm.rd_units)) - 1]
                tech_gain = 3.2 * (synergy_pct / 100.0) * (1.0 + 0.05 * firm.unit_training_level)
                firm.rd_progress += tech_gain

                tmap = self.corp_tech_levels.setdefault(owner.entity_id, {})
                # Advance both the targeted product_code and tech_code so factories & retail benefit immediately
                codes_to_advance = set()
                if firm.product_code:
                    codes_to_advance.add(self._normalize_product_code(firm.product_code))
                if firm.tech_code:
                    codes_to_advance.add(self._normalize_tech_code(firm.tech_code))
                if not codes_to_advance:
                    codes_to_advance.add("VIDEO_ST")

                for c_key in codes_to_advance:
                    new_lvl = tmap.get(c_key, 60.0) + tech_gain
                    tmap[c_key] = new_lvl
                    if new_lvl > self.top_tech_levels.get(c_key, 100.0):
                        self.top_tech_levels[c_key] = new_lvl

                firm.last_quarter_revenue_millions = rev
                firm.last_quarter_ebit_millions = ebit
                corp_ebit_map[owner.entity_id] = corp_ebit_map.get(owner.entity_id, 0.0) + ebit

            elif firm.firm_type in ("APARTMEN", "COMMERCI", "MALL", "OFFICE"):
                # Cross-Feedback Loop #3: WSR Prime Rate & GDP modulate urban real estate occupancy
                eff_occ = max(0.40, min(0.99, firm.occupancy_rate * rate_occupancy_mod))
                rev = firm.book_value_millions * 0.032 * eff_occ * wage_factor
                ebit = rev - (firm.monthly_operating_Cost_millions * 3.0 * inflation_opex_mult)
                firm.last_quarter_revenue_millions = rev
                firm.last_quarter_ebit_millions = ebit
                corp_ebit_map[owner.entity_id] = corp_ebit_map.get(owner.entity_id, 0.0) + ebit

            elif firm.firm_type in ("SOFTWARE", "INTERNET", "TELECOM"):
                tmap = self.corp_tech_levels.get(owner.entity_id, {})
                sw_bonus = 1.0 + 0.003 * max(0.0, tmap.get(firm.software_code or "VIDEO_ST", 60.0) - 60.0)
                rev = firm.book_value_millions * 0.28 * wage_factor * sw_bonus
                ebit = rev * 0.42 - (firm.monthly_operating_Cost_millions * 3.0 * inflation_opex_mult)
                firm.last_quarter_revenue_millions = rev
                firm.last_quarter_ebit_millions = ebit
                corp_ebit_map[owner.entity_id] = corp_ebit_map.get(owner.entity_id, 0.0) + ebit

            elif firm.firm_type in ("MINE", "OIL", "FOREST", "FARM"):
                # Cross-Feedback Loop #2: WSR Commodity Spot Prices drive physical resource firm revenues
                firm.product_quality = min(98.0, firm.product_quality + 0.25 * firm.unit_training_level)
                comm_mult = max(
                    0.60,
                    min(2.50, self.get_resource_commodity_multiplier(firm.resource_code or firm.product_code)),
                )
                rev = firm.book_value_millions * 0.22 * comm_mult
                ebit = rev * 0.36 - (firm.monthly_operating_Cost_millions * 3.0 * inflation_opex_mult)
                firm.last_quarter_revenue_millions = rev
                firm.last_quarter_ebit_millions = ebit
                corp_ebit_map[owner.entity_id] = corp_ebit_map.get(owner.entity_id, 0.0) + ebit

            elif firm.firm_type in ("RETAIL", "FACTORY", "SERVICE"):
                pcode = self._normalize_product_code(firm.product_code)
                firm.product_code = pcode
                firm.city_name = cname
                market_groups.setdefault((cname, pcode), []).append(firm)

        # Phase 2: Update Manufacturing/Retail Quality, Vertical Supply Chain COGS, and 3-Mode Brand Rating
        for (cname, pcode), firms_in_mkt in market_groups.items():
            for firm in firms_in_mkt:
                owner = self.entities[firm.owner_corp_id]
                q_out, cogs_ratio, int_cnt = self.compute_caplab_manufacturing_quality(firm)
                firm.product_quality = q_out
                firm.cogs_ratio = cogs_ratio
                firm.integrated_inputs_count = int_cnt

                # 3 Brand Strategies (VA 0x005A042E: CORPORATE, RANGE, UNIQUE) + Brand Loyalty
                adv_gain = firm.advertising_budget_millions * 1.5
                # Quality > 60 rewards brand loyalty; Quality < 45 penalizes brand loyalty
                loyalty_delta = (firm.product_quality - 60.0) * 0.08 if firm.product_quality >= 45.0 else (firm.product_quality - 55.0) * 0.20
                owner.brand_loyalty = max(-40.0, min(40.0, owner.brand_loyalty * 0.90 + loyalty_delta))

                b_mode = (owner.brand_strategy or "CORPORATE").upper()
                pcls = self.products.get(pcode, {}).get("CLASS", "ELECTRON")
                if b_mode == "CORPORATE":
                    owner.corporate_brand = max(10.0, min(100.0, owner.corporate_brand * 0.97 + adv_gain * 0.5))
                    firm.brand_rating = max(0.0, min(100.0, owner.corporate_brand + owner.brand_loyalty))
                elif b_mode == "RANGE":
                    cmap = self.corp_class_brands.setdefault(owner.entity_id, {})
                    cur_cb = cmap.get(pcls, 55.0)
                    cur_cb = max(10.0, min(100.0, cur_cb * 0.96 + adv_gain * 0.7))
                    cmap[pcls] = cur_cb
                    firm.brand_rating = max(0.0, min(100.0, cur_cb + owner.brand_loyalty))
                else:
                    # UNIQUE Product Brand
                    firm.brand_rating = max(0.0, min(100.0, firm.brand_rating * 0.95 + adv_gain + loyalty_delta))

        # Phase 3: Multi-Firm Urban Market Share Competition per (city_name, product_code)
        for (cname, pcode), firms_in_mkt in market_groups.items():
            avg_price = sum(f.unit_price for f in firms_in_mkt) / max(1, len(firms_in_mkt))
            city_demand_pool_m = self.compute_caplab_city_quarterly_demand_millions(pcode, cname, avg_price)

            pcls = self.products.get(pcode, {}).get("CLASS", "ELECTRON")
            local_comp_rating = float(self.product_classes.get(pcls, {}).get("LOCALCOMP", 50))
            w_local = (max(1.0, local_comp_rating + 10.0) ** 2.2) * 2.5

            firm_weights: List[float] = []
            for firm in firms_in_mkt:
                rating = self.compute_caplab_product_rating(
                    pcode, firm.product_quality, firm.brand_rating, firm.unit_price, city_name=cname
                )
                w_f = max(1.0, rating + 10.0) ** 2.2
                firm_weights.append(w_f)

            total_weight = sum(firm_weights) + w_local
            city = self.cities.get(cname, {"WAGE_RATE": 60})
            wage_factor = 0.8 + 0.4 * (float(city.get("WAGE_RATE", 60)) / 100.0)

            for firm, w_f in zip(firms_in_mkt, firm_weights):
                owner = self.entities[firm.owner_corp_id]
                mkt_share = w_f / max(1e-6, total_weight)
                firm.market_share = round(mkt_share, 4)

                # Revenue comes from the shared urban demand pool, capped by firm physical capacity
                demand_alloc_rev = city_demand_pool_m * mkt_share * wage_factor
                capacity_ceiling_rev = firm.book_value_millions * 0.55 * firm.capacity_utilization * wage_factor
                rev = min(capacity_ceiling_rev, max(firm.book_value_millions * 0.12 * mkt_share, demand_alloc_rev))

                cogs = rev * firm.cogs_ratio
                opex = (firm.monthly_operating_Cost_millions * 3.0 * inflation_opex_mult) + firm.advertising_budget_millions
                ebit = rev - cogs - opex

                firm.last_quarter_revenue_millions = rev
                firm.last_quarter_ebit_millions = ebit
                corp_ebit_map[owner.entity_id] = corp_ebit_map.get(owner.entity_id, 0.0) + ebit

        return corp_ebit_map

    # =========================================================================
    # 8. SIMULATION TIME STEPPERS (< 2.0 ms / tick) & STAGE B GTA SA API
    # =========================================================================

    def step_intraday_subtick(self) -> Dict[str, Any]:
        """
        High-frequency intraday subtick (< 2.0 ms):
          - Updates macro interest rates / commodity / crypto prices slightly.
          - Adjusts stock prices for a rotating slice of active corporations + all player/ETF holdings.
          - Updates balance sheets for active players and modified entities.
        """
        t0 = time.perf_counter()
        self.subtick += 1
        self.total_subticks += 1

        # 1. Micro-fluctuate commodity & crypto prices
        for k in self.commodity_prices:
            self.commodity_prices[k] = round(
                max(1.0, self.commodity_prices[k] * (1.0 + self.rng.uniform(-0.003, 0.0035))), 4
            )
        for k in self.crypto_prices:
            self.crypto_prices[k] = round(
                max(10.0, self.crypto_prices[k] * (1.0 + self.rng.uniform(-0.008, 0.0085))), 2
            )

        # 2. Rotate through a slice of 64 corporations per subtick for ultra-fast (<1 ms) market micro-ticks
        n_active = len(self.active_corp_ids)
        if n_active > 0:
            slice_size = min(64, n_active)
            start_idx = ((self.total_subticks - 1) * slice_size) % n_active
            for offset in range(slice_size):
                cid = self.active_corp_ids[(start_idx + offset) % n_active]
                ent = self.entities[cid]
                if ent.regime == "ETF_FUND":
                    self.recompute_entity_balance_sheet(ent, update_stock_price=True)
                else:
                    drift = (self.gdp_growth_pct - 2.0) * 0.0004 + self.rng.uniform(-0.004, 0.0042)
                    ent.stock_price = max(0.10, round(ent.stock_price * (1.0 + drift), 4))

        # 3. Recompute Player 1..5 balance sheets
        for pid in range(1, 6):
            self.recompute_entity_balance_sheet(self.entities[pid], update_stock_price=False)

        if self.subtick >= 10:
            self.subtick = 0
            self.step_day()

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "year": self.year,
            "quarter": self.quarter,
            "month": self.month,
            "day": self.day,
            "subtick": self.subtick,
            "elapsed_ms": round(elapsed_ms, 4),
        }

    def step_day(self) -> Dict[str, Any]:
        """Advances the simulation by 1 calendar day; triggers quarterly settlements every 90 days."""
        t0 = time.perf_counter()
        self.day += 1
        self.total_days += 1

        if self.day > 30:
            self.day = 1
            self.month += 1
            if self.month > 12:
                self.month = 1
                self.year += 1
                for cid in self.active_corp_ids:
                    self.roll_annual_nol_buckets(self.entities[cid])

            if (self.month - 1) % 3 == 0:
                self.quarter = ((self.month - 1) // 3) + 1
                self.step_quarter()

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "year": self.year,
            "quarter": self.quarter,
            "month": self.month,
            "day": self.day,
            "elapsed_ms": round(elapsed_ms, 4),
        }

    def compute_caplab_macro_impulses(self) -> Dict[str, Any]:
        """
        Computes bottom-up Capitalism Lab impulses that feed back into top-down WSR Macro & Sector states:
          1. urban_price_markup_pct: average retail/factory price markup vs standard P_std across 128 cities.
          2. caplab_total_capex_millions: total physical CapEx across all active Capitalism Lab firms.
          3. resource_supply_book_millions: total physical MINE/OIL/FOREST/FARM capacity (dampens WSR commodity spikes).
          4. industry_caplab_assets: mapping of WSR industry_id -> total physical CapLab firm assets ($M).
          5. industry_frontier_tech: mapping of WSR industry_id -> highest R&D technology level achieved.
        """
        markups: List[float] = []
        total_capex = 0.0
        resource_book = 0.0
        ind_caplab_assets: Dict[int, float] = {}

        for firm in self.firms.values():
            owner = self.entities.get(firm.owner_corp_id)
            if not owner or not owner.is_active:
                continue
            total_capex += firm.book_value_millions
            ind_caplab_assets[owner.industry_id] = ind_caplab_assets.get(owner.industry_id, 0.0) + firm.book_value_millions

            if firm.firm_type in ("MINE", "OIL", "FOREST", "FARM"):
                resource_book += firm.book_value_millions
            elif firm.firm_type in ("RETAIL", "FACTORY") and firm.product_code:
                p_std = max(0.01, float(self.products.get(firm.product_code, {}).get("PRICE", 100.0)))
                markups.append(((firm.unit_price - p_std) / p_std) * 100.0)

        avg_markup_pct = sum(markups) / len(markups) if markups else 0.0
        oil_r = self.commodity_prices.get("OIL", 75.0) / 75.0
        copp_r = self.commodity_prices.get("COPPER", 4.10) / 4.10
        wheat_r = self.commodity_prices.get("WHEAT", 6.50) / 6.50
        comm_pressure_pct = ((oil_r + copp_r + wheat_r) / 3.0 - 1.0) * 100.0

        urban_cpi_push = max(-0.8, min(1.8, avg_markup_pct * 0.025 + comm_pressure_pct * 0.015))
        real_gdp_impulse = max(-0.4, min(1.2, total_capex * 0.00025))
        supply_dampening_pct = max(0.0, min(4.5, resource_book * 0.015))

        return {
            "avg_urban_price_markup_pct": round(avg_markup_pct, 3),
            "commodity_pressure_pct": round(comm_pressure_pct, 3),
            "urban_cpi_push_pct": round(urban_cpi_push, 4),
            "caplab_total_capex_millions": round(total_capex, 2),
            "real_gdp_impulse_pct": round(real_gdp_impulse, 4),
            "resource_supply_book_millions": round(resource_book, 2),
            "commodity_supply_dampening_pct": round(supply_dampening_pct, 4),
            "industry_caplab_assets": ind_caplab_assets,
        }

    def get_industry_tech_obsolescence_factor(self, corp: FinancialEntity) -> float:
        """
        Cross-Feedback Loop #4 (CapLab R&D Frontier -> WSR Legacy Abstract Asset Obsolescence):
        When Capitalism Lab R&D centers push an industry's technology frontier (top_tech_levels) above 100.0,
        legacy WSR corporations that fail to invest in R&D or acquire high-tech subsidiaries suffer a
        Technological Obsolescence discount on their abstract_ebit, while R&D leaders earn a premium!
        """
        cw = self.crosswalk.get(corp.industry_id, {})
        codes = set(cw.get("product_codes", [])) | set(cw.get("tech_codes", []))
        # Also include any product/tech codes actively researched by R&D centers in this WSR industry
        for f in self.firms.values():
            if f.firm_type == "RD" and f.owner_corp_id in self.entities:
                if self.entities[f.owner_corp_id].industry_id == corp.industry_id:
                    if f.product_code:
                        codes.add(self._normalize_product_code(f.product_code))
                    if f.tech_code:
                        codes.add(self._normalize_tech_code(f.tech_code))
        if not codes:
            return 1.0
        frontier = max((self.top_tech_levels.get(self._normalize_product_code(c), 100.0) for c in codes), default=100.0)
        if frontier <= 100.0:
            return 1.0

        group_ids = self.get_corporate_group_ids(corp.entity_id)
        best_corp_tech = 85.0
        for gid in group_ids:
            tmap = self.corp_tech_levels.get(gid, {})
            for c in codes:
                nc = self._normalize_product_code(c)
                if nc in tmap:
                    best_corp_tech = max(best_corp_tech, tmap[nc])
                tc = self._normalize_tech_code(c)
                if tc in tmap:
                    best_corp_tech = max(best_corp_tech, tmap[tc])

        # Leaders at the frontier get >= 1.0 (up to 1.15x if well above 100); laggards drop toward 0.55x
        raw_ratio = best_corp_tech / frontier
        if best_corp_tech >= frontier:
            return min(1.18, 1.0 + (frontier - 100.0) * 0.0015)
        return max(0.55, min(1.0, raw_ratio))

    def get_bidirectional_coupling_metrics(self) -> Dict[str, Any]:
        """Returns live telemetry for all 4 WSR <-> Capitalism Lab Bidirectional Feedback Loops."""
        impulses = self.compute_caplab_macro_impulses()
        inflation_opex_mult = round(max(0.85, min(1.65, 1.0 + (self.inflation_pct - 2.4) * 0.035)), 4)
        rate_occupancy_mod = round(
            max(0.60, min(1.25, 1.0 - (self.prime_rate_pct - 6.50) * 0.035 + (self.gdp_growth_pct - 2.8) * 0.015)),
            4,
        )
        return {
            **impulses,
            "wsr_to_caplab_inflation_opex_mult": inflation_opex_mult,
            "wsr_to_caplab_rate_occupancy_mod": rate_occupancy_mod,
            "oil_commodity_multiplier": round(self.get_resource_commodity_multiplier("OIL"), 4),
            "copper_tech_commodity_multiplier": round(self.get_resource_commodity_multiplier("COPPER"), 4),
        }

    def step_quarter(self) -> Dict[str, Any]:
        """
        Executes WSR Master Quarterly Cycle (BigLoop @ 0x004C602E) + CapLab Firm Earnings
        with Full 4-Channel Bidirectional WSR <-> Capitalism Lab Coupling:
          1. Macro cycle update (GDP, Inflation, Prime Rate, Short/Long Bond Rates, SupplyDemand ROCE%)
             driven by Taylor-Rule Mean Reversion + CapLab Urban CPI Push & Real Output Impulses.
          2. Physical Mine/Oil/Farm Supply Dampening on WSR Commodity Futures.
          3. Bottom-up Capitalism Lab Firm EBIT generation + Top-down WSR Operating EBIT
             (modulated by CapLab R&D Technological Obsolescence factor).
          4. Interest income/expense, 3-Tier Corporate Tax (with 4-Year NOL & DRD), ETF Advisory Fees.
          5. Interest Rate Swap settlements & Lawsuit countdown resolution.
          6. CEO Salaries & Quarterly Cash Dividends (with ShortDividends deduction).
          7. Circular ownership convergence & full 5-Regime Balance Sheet recomputation.
        """
        t0 = time.perf_counter()

        # 0. Compute Bottom-Up Capitalism Lab Impulses (Cross-Feedback Loops #1, #2, #4)
        impulses = self.compute_caplab_macro_impulses()

        # Cross-Feedback Loop #2 (CapLab Physical Mines/Oil/Farms -> WSR Commodity Supply Dampening)
        damp_frac = impulses["commodity_supply_dampening_pct"] / 100.0
        if damp_frac > 0.0:
            baselines = {"OIL": 75.0, "GOLD": 2000.0, "SILVER": 25.0, "WHEAT": 6.50, "CORN": 5.20, "COPPER": 4.10}
            for k, base_px in baselines.items():
                if k in self.commodity_prices and self.commodity_prices[k] > base_px * 0.70:
                    self.commodity_prices[k] = round(max(base_px * 0.65, self.commodity_prices[k] * (1.0 - damp_frac)), 4)

        # 1. Macro & Industry Supply/Demand Update (WSR SupplyDemand @ 0x00458270 + Taylor-Rule Mean Reversion)
        mean_rev_gdp = (2.8 - self.gdp_growth_pct) * 0.16
        rate_drag = max(-0.4, (self.prime_rate_pct - 6.50) * 0.06)
        self.gdp_growth_pct = max(
            -4.0,
            min(
                7.0,
                self.gdp_growth_pct
                + mean_rev_gdp
                + impulses["real_gdp_impulse_pct"]
                - rate_drag
                + self.rng.uniform(-0.32, 0.35),
            ),
        )
        mean_rev_inf = (2.4 - self.inflation_pct) * 0.15
        self.inflation_pct = max(
            0.5,
            min(
                12.0,
                self.inflation_pct
                + mean_rev_inf
                + 0.15 * (self.gdp_growth_pct - 2.5)
                + impulses["urban_cpi_push_pct"]
                + self.rng.uniform(-0.18, 0.18),
            ),
        )
        # Enforce strict interest-rate risk hierarchy: Short Bond < Long Bond < Prime Rate
        self.prime_rate_pct = round(max(2.0, min(16.0, 3.0 + self.inflation_pct + 0.35 * self.gdp_growth_pct)) * 4.0) / 4.0
        self.short_bond_rate_pct = round(max(0.75, self.prime_rate_pct - 1.50), 2)
        self.long_bond_rate_pct = round(max(self.short_bond_rate_pct + 0.25, self.prime_rate_pct - 0.25), 2)

        ind_caplab_map = impulses["industry_caplab_assets"]
        for ind_id, ind in self.industries.items():
            if ind_id in (1, 2, 70, 71):
                continue
            g = float(ind.get("growth_rate_pct", 5))
            ind["total_demand"] *= 1.0 + 0.005 * g + 0.002 * self.gdp_growth_pct
            # Cross-Feedback Loop #4: Physical Capitalism Lab factories add to sector capacity
            caplab_cap_add = ind_caplab_map.get(ind_id, 0.0) * 0.02
            ind["total_capacity"] = ind["total_capacity"] * (1.0 + 0.004 * g) + caplab_cap_add
            roce = max(-20.0, min(45.0, 100.0 * (1.0 - ind["total_capacity"] / max(1.0, ind["total_demand"])) + 12.0))
            ind["roce_pct"] = roce

        # 2. Step Capitalism Lab Firms
        firm_ebit_by_corp = self.step_caplab_firms_quarterly()

        # 3. Corporate Operating Earnings, Banking/Insurance Spreads, Taxes & ETF Fees
        for cid in self.active_corp_ids:
            ent = self.entities[cid]
            if ent.is_bankrupt:
                continue

            if ent.regime == "COMMERCIAL_BANK":
                # Regime 2: Bank Net Interest Income
                loan_yield = (self.prime_rate_pct + 1.75) / 100.0 * 0.25
                cd_cost = (self.short_bond_rate_pct * 0.85) / 100.0 * 0.25
                ib_cost = (self.prime_rate_pct * 0.90) / 100.0 * 0.25
                interest_inc = ent.net_bank_loans_asset * loan_yield + (ent.gov_bonds_adj_cost + ent.corp_bonds_adj_cost) * (self.long_bond_rate_pct / 100.0 * 0.25)
                interest_exp = ent.cert_deposits * cd_cost + ent.interbank_debt * ib_cost + ent.bonds_out * (ent.bond_coupon_pct / 100.0 * 0.25)
                pretax = interest_inc - interest_exp
                tax = self.calculate_corporate_tax(ent, pretax)
                net_inc = pretax - tax
                ent.cash += pretax
                self.system_pool_cash -= pretax

            elif ent.regime == "INSURANCE_COMPANY":
                # Regime 3: Insurance Underwriting Float + Investment Income
                underwriting_margin = ent.insur_reserves * (0.008 + 0.002 * self.gdp_growth_pct)
                inv_inc = (ent.gov_bonds_adj_cost + ent.corp_bonds_adj_cost + ent.subprime_mortgages) * (self.long_bond_rate_pct / 100.0 * 0.25)
                interest_exp = (ent.bank_loan * ent.borrowing_rate_pct + ent.bonds_out * ent.bond_coupon_pct) / 100.0 * 0.25
                pretax = underwriting_margin + inv_inc - interest_exp
                tax = self.calculate_corporate_tax(ent, pretax)
                net_inc = pretax - tax
                ent.cash += pretax
                self.system_pool_cash -= pretax

            elif ent.regime == "ETF_FUND":
                # Regime 4: ETF Advisory Fee deduction
                fee = max(0.0, ent.net_worth * (ent.advisory_fee_pct / 100.0) * 0.25)
                ent.cash -= fee
                if ent.advisor_id in self.entities:
                    self.entities[ent.advisor_id].cash += fee
                else:
                    self.system_pool_cash += fee
                net_inc = -fee

            else:
                # Regime 1: Industrial / Commercial / Holding (Hybrid WSR Abstract + CapLab Firms)
                roce = float(self.industries.get(ent.industry_id, {}).get("roce_pct", 12.0))
                ent.roce_pct = roce
                # Cross-Feedback Loop #4: Apply CapLab R&D Technological Obsolescence factor to legacy abstract assets
                tech_obs_mult = self.get_industry_tech_obsolescence_factor(ent)
                abstract_ebit = ent.cap_assets_abstract * (roce / 100.0) * 0.25 * tech_obs_mult
                caplab_ebit = firm_ebit_by_corp.get(cid, 0.0)
                total_ebit = abstract_ebit + caplab_ebit
                interest_exp = (ent.bank_loan * ent.borrowing_rate_pct + ent.bonds_out * ent.bond_coupon_pct) / 100.0 * 0.25
                pretax = total_ebit - interest_exp
                tax = self.calculate_corporate_tax(ent, pretax)
                net_inc = pretax - tax
                ent.cash += pretax
                self.system_pool_cash -= pretax

            ent.last_quarter_ebit = net_inc
            ent.last_quarter_net_income = net_inc
            ent.annual_eps = (net_inc * 4.0) / max(1e-6, ent.shares_outstanding)

        # 4. Settle Quarterly Interest Rate Swaps, Accrued Taxes, Expiring Options, Lawsuits & ETF Leverage
        self.settle_quarterly_swaps()

        # 4a. Pay accrued corporate & personal taxes into system_pool_cash
        for ent in self.entities.values():
            if not ent.is_active:
                continue
            if ent.regime == "PLAYER_INDIVIDUAL":
                tax_due = max(0.0, ent.income_tax_owed)
                if tax_due > 0.0:
                    paid = min(max(0.0, ent.cash * 0.8), tax_due)
                    ent.cash -= paid
                    ent.income_tax_owed -= paid
                    self.system_pool_cash += paid
            else:
                corp_tax_due = max(0.0, ent.acc_tax + ent.cap_tax)
                if corp_tax_due > 0.0:
                    paid = min(max(0.0, ent.cash * 0.8), corp_tax_due)
                    ent.cash -= paid
                    self.system_pool_cash += paid
                    if paid >= ent.acc_tax:
                        rem = paid - ent.acc_tax
                        ent.acc_tax = 0.0
                        ent.cap_tax = max(0.0, ent.cap_tax - rem)
                    else:
                        ent.acc_tax -= paid

        # 4b. Age Option Contracts by 3 months and settle/exercise expired options
        for oid, opt in list(self.options.items()):
            opt.months_to_expiry -= 3.0
            if opt.months_to_expiry <= 0.0:
                u_corp = self.entities.get(opt.underlying_corp_id)
                spot = u_corp.stock_price if u_corp else opt.strike_price
                intrinsic = max(0.0, spot - opt.strike_price) if opt.opt_type == "CALL" else max(0.0, opt.strike_price - spot)
                payoff = intrinsic * opt.shares_covered
                if payoff > 0.0:
                    if opt.holder_id in self.entities:
                        self.entities[opt.holder_id].cash += payoff
                    else:
                        self.system_pool_cash += payoff
                    if opt.writer_id in self.entities:
                        self.entities[opt.writer_id].cash -= payoff
                    else:
                        self.system_pool_cash -= payoff
                del self.options[oid]

        # 4c. Countdown & resolve pending corporate lawsuits
        for lid, case in list(self.lawsuits.items()):
            case.countdown_ticks -= 1
            if case.countdown_ticks <= 0:
                plaintiff = self.entities.get(case.plaintiff_id)
                defendant = self.entities.get(case.defendant_id)
                if plaintiff and defendant and plaintiff.is_active and defendant.is_active:
                    if self.rng.random() < case.win_probability:
                        award = min(max(0.0, defendant.cash * 0.5), case.claim_amount_millions)
                        defendant.cash -= award
                        plaintiff.cash += award
                del self.lawsuits[lid]

        # 4d. Rebalance Leveraged Bull/Bear ETFs
        for etf_id in self.etf_corp_ids:
            self.adjust_etf_leverage(etf_id)

        # 5. Pay CEO Salaries to Players (Personal Cash vs Corporate Cash)
        for pid in range(1, 6):
            player = self.entities[pid]
            for c_id in list(player.ceo_of_corp_ids):
                corp = self.entities.get(c_id)
                if corp and corp.is_active and corp.cash > 1.0:
                    q_sal = min(corp.cash * 0.02, max(0.25, player.annual_ceo_salary_millions * 0.25))
                    corp.cash -= q_sal
                    player.cash += q_sal
                    player.ytd_taxable_ordinary += q_sal

        # 5b. Execute Autonomous AI Billionaire Rivals (WSR MakeComputerTurn) & CapLab 64 PERSONS.DBF CEOs
        if self.enable_autonomous_ai:
            self.step_ai_competitors_quarterly()

        # 5c. Generate Quarterly News Wire (Mscnews.dat + quotewsr.dat + Live Corporate/CapLab Market Events)
        self._generate_quarterly_news_and_ticker()

        # 6. Full Balance Sheet & Circular Ownership Convergence Pass
        self.resolve_circular_ownership_and_control(max_iters=4)
        self.recompute_all_balance_sheets()

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "year": self.year,
            "quarter": self.quarter,
            "gdp_growth_pct": round(self.gdp_growth_pct, 2),
            "prime_rate_pct": self.prime_rate_pct,
            "elapsed_ms": round(elapsed_ms, 4),
        }

    # =========================================================================
    # 8B. AUTONOMOUS WSR + CAPLAB AI ENGINE & EXTERNAL LLM AGENT CONTROLLER
    # =========================================================================

    def _refresh_ticker_tape(self) -> None:
        """Updates the live scrolling Bloomberg/WSR ticker tape from active corporations and ETFs."""
        tape: List[str] = []
        sample_ids = self.active_corp_ids[:24] + self.etf_corp_ids[:6]
        for cid in sample_ids:
            ent = self.entities.get(cid)
            if ent and ent.is_active:
                r_lbl = RATING_LABELS.get(ent.credit_rating, "BBB")
                tape.append(f"{ent.ticker} ${ent.stock_price:.2f} [{r_lbl}]")
        for sym, px in self.crypto_prices.items():
            tape.append(f"{sym} ${px:,.0f}")
        for comm, px in self.commodity_prices.items():
            tape.append(f"{comm} ${px:.2f}")
        self.ticker_tape = tape

    def register_external_ai_hook(self, hook_fn: Any) -> None:
        """
        Registers an optional external AI / LLM controller callback:
          hook_fn(observation_dict) -> List[{"cmd": str, "payload": dict}]
        """
        self.external_ai_hook = hook_fn

    def get_ai_observation(self, player_id: int) -> Dict[str, Any]:
        """Returns a structured observation packet for an AI Billionaire Rival (ID 2..5) or LLM Agent."""
        ai_ent = self.entities[player_id]
        profile = self.billionaire_ai_profiles.get(player_id, {})
        top_value_targets = []
        for cid in self.active_corp_ids[:80]:
            c = self.entities[cid]
            ff = self.public_float_shares.get(cid, 0.0)
            if not c.is_active or c.net_worth <= 0 or ff < 5.0:
                continue
            mkt_cap = c.stock_price * c.shares_outstanding
            pb_ratio = mkt_cap / max(1.0, c.net_worth)
            top_value_targets.append({
                "corp_id": cid,
                "ticker": c.ticker,
                "industry_id": c.industry_id,
                "stock_price": round(c.stock_price, 2),
                "net_worth_millions": round(c.net_worth, 2),
                "pb_ratio": round(pb_ratio, 3),
                "credit_rating": RATING_LABELS.get(c.credit_rating, "BBB"),
                "free_float_shares": round(self.public_float_shares.get(cid, 0.0), 2),
            })
        top_value_targets.sort(key=lambda x: x["pb_ratio"])
        return {
            "year": self.year,
            "quarter": self.quarter,
            "macro": {
                "gdp_growth_pct": self.gdp_growth_pct,
                "inflation_pct": self.inflation_pct,
                "prime_rate_pct": self.prime_rate_pct,
            },
            "ai_player": {
                "player_id": player_id,
                "name": ai_ent.name,
                "cash_millions": round(ai_ent.cash, 2),
                "net_worth_millions": round(ai_ent.net_worth, 2),
                "holdings": dict(ai_ent.stock_holdings),
                "shorts": dict(ai_ent.short_positions),
                "controlled_corps": [
                    cid for cid in self.active_corp_ids if self.entities[cid].controlled_by_id == player_id
                ],
                "persona": profile,
            },
            "undervalued_candidates": top_value_targets[:10],
            "recent_news": self.news_headlines[-5:],
        }

    def apply_ai_strategic_directives(
        self, player_id: int, directives: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Executes a list of strategic directives [{"cmd": ..., "payload": ...}] issued by an external AI/LLM agent
        through the strict 5-Regime accounting dispatcher.
        """
        results: List[Dict[str, Any]] = []
        for d in directives:
            cmd = str(d.get("cmd", "")).upper()
            payload = dict(d.get("payload", {}))
            res = self.execute_action(cmd, payload)
            entry = {
                "year": self.year,
                "quarter": self.quarter,
                "actor_id": player_id,
                "actor_name": self.entities[player_id].name if player_id in self.entities else f"AI-{player_id}",
                "source": "EXTERNAL_AI_DIRECTIVE",
                "cmd": cmd,
                "payload": payload,
                "ok": bool(res.get("ok")),
            }
            if res.get("ok"):
                self.ai_action_log.append(entry)
                self.news_headlines.append(
                    f"[AI STRATEGY WIRE] {entry['actor_name']} executed {cmd} on target {payload.get('target_corp_id') or payload.get('owner_corp_id', '')}."
                )
            results.append(res)
        return results

    def step_ai_competitors_quarterly(self) -> Dict[str, Any]:
        """
        Hybrid Native AI Turn (< 1.0 ms):
          1. WSR MakeComputerTurn (VA 0x0052A6E1) for Billionaire Rivals (Players 2..5: Warren B., Carl I., George S., Ken G.):
             - Evaluates undervalued (low P/B), cash-rich, or high-ROCE targets to buy shares or acquire control.
             - Evaluates overleveraged low-credit corporations for short selling or covering shorts.
             - Directs controlled corporations to build Capitalism Lab supply chain firms (FACTORY, RETAIL, RD, MINE).
          2. Capitalism Lab 64 PERSONS.DBF Executive AI Autopilot:
             - Rotating slice of active CEO-managed corporations builds physical firms (FACTORY, RETAIL, RD, MINE)
               and dynamically adjusts advertising_budget_millions, unit_price, and brand_strategy based on
               the CEO's PERSONS.DBF attributes (MARKETING, RD, MFT, RETAIL, RAW, CHARACTER).
          3. Optional External AI Hook (if registered).
        """
        reserved_test_ids = {131, 132, 133, 181, 200, 201, 202, 203, 205, 221, 222, 300, 321, 322, 620}
        actions_taken = 0
        major_cities = ["New York City", "Tokyo", "London", "Beijing", "Chicago", "Los Angeles", "Seoul", "Frankfurt"]

        # Part A: 4 Billionaire AI Rivals (IDs 2..5)
        for pid in (2, 3, 4, 5):
            ai_player = self.entities[pid]
            profile = self.billionaire_ai_profiles.get(pid, {})
            pref_inds = set(profile.get("preferred_industries", []))

            # If an external LLM/RL hook is registered, allow it to issue directives first
            if self.external_ai_hook is not None:
                try:
                    obs = self.get_ai_observation(pid)
                    ext_dirs = self.external_ai_hook(obs)
                    if isinstance(ext_dirs, list) and ext_dirs:
                        self.apply_ai_strategic_directives(pid, ext_dirs)
                        actions_taken += len(ext_dirs)
                except Exception:
                    pass

            # WSR Native MakeComputerTurn Heuristics
            candidates = [
                cid for cid in self.active_corp_ids[:160]
                if cid not in reserved_test_ids
                and self.entities[cid].is_active
                and not self.entities[cid].is_bankrupt
                and self.public_float_shares.get(cid, 0.0) > 8.0
            ]
            if not candidates:
                continue

            if pid == 2:
                # Warren B. (Value Compounder): Buy low P/B, high credit-rating stock
                best_cid = min(
                    candidates,
                    key=lambda c: (
                        (self.entities[c].stock_price * self.entities[c].shares_outstanding)
                        / max(1.0, self.entities[c].net_worth)
                    )
                    * (0.75 if self.entities[c].industry_id in pref_inds else 1.0),
                )
                target = self.entities[best_cid]
                if ai_player.cash > 60.0:
                    spend = min(ai_player.cash * 0.12, 180.0)
                    sh = min(self.public_float_shares[best_cid] * 0.20, spend / max(1.0, target.stock_price))
                    if sh >= 0.5:
                        res = self.buy_stock(pid, best_cid, round(sh, 2))
                        if res.get("ok"):
                            actions_taken += 1
                            self.ai_action_log.append({
                                "year": self.year, "quarter": self.quarter,
                                "actor_id": pid, "actor_name": ai_player.name,
                                "source": "WSR_MAKE_COMPUTER_TURN", "cmd": "BUY_STOCK",
                                "target_ticker": target.ticker, "shares_millions": round(sh, 2),
                            })
                            self.news_headlines.append(
                                f"[13F FILING] {ai_player.name} accumulated {sh:.2f}M shares of {target.name} ({target.ticker}) at ${target.stock_price:.2f}."
                            )

            elif pid == 3:
                # Carl I. (Corporate Raider): Target cash-rich or undervalued industrial corp for activist stake
                best_cid = max(
                    candidates,
                    key=lambda c: (self.entities[c].cash / max(10.0, self.entities[c].stock_price * self.entities[c].shares_outstanding))
                    * (1.3 if self.entities[c].industry_id in pref_inds else 1.0),
                )
                target = self.entities[best_cid]
                if ai_player.cash > 50.0:
                    spend = min(ai_player.cash * 0.14, 160.0)
                    sh = min(self.public_float_shares[best_cid] * 0.25, spend / max(1.0, target.stock_price))
                    if sh >= 0.5:
                        res = self.buy_stock(pid, best_cid, round(sh, 2))
                        if res.get("ok"):
                            actions_taken += 1
                            self.ai_action_log.append({
                                "year": self.year, "quarter": self.quarter,
                                "actor_id": pid, "actor_name": ai_player.name,
                                "source": "WSR_MAKE_COMPUTER_TURN", "cmd": "ACTIVIST_BUY",
                                "target_ticker": target.ticker, "shares_millions": round(sh, 2),
                            })
                            self.news_headlines.append(
                                f"[RAIDER ALERT] Corporate raider {ai_player.name} disclosed an activist position ({sh:.2f}M sh) in {target.name} ({target.ticker})."
                            )

            elif pid == 4:
                # George S. (Global Macro / Short Seller): Short weak-credit corp when Prime Rate >= 5.5%, or buy macro ETF/Bank
                weak_cids = [c for c in candidates if self.entities[c].credit_rating <= 7 and self.entities[c].regime == "INDUSTRIAL_HOLDING"]
                if weak_cids and self.prime_rate_pct >= 5.0 and len(ai_player.short_positions) < 3:
                    short_cid = weak_cids[(self.year * 4 + self.quarter) % len(weak_cids)]
                    t_short = self.entities[short_cid]
                    sh_short = min(2.0, max(0.5, (ai_player.net_worth * 0.04) / max(1.0, t_short.stock_price)))
                    res = self.short_stock(pid, short_cid, round(sh_short, 2))
                    if res.get("ok"):
                        actions_taken += 1
                        self.ai_action_log.append({
                            "year": self.year, "quarter": self.quarter,
                            "actor_id": pid, "actor_name": ai_player.name,
                            "source": "WSR_MAKE_COMPUTER_TURN", "cmd": "SHORT_STOCK",
                            "target_ticker": t_short.ticker, "shares_millions": round(sh_short, 2),
                        })
                        self.news_headlines.append(
                            f"[MACRO SHORT] {ai_player.name} opened a {sh_short:.2f}M-share short position against {t_short.name} ({t_short.ticker})."
                        )
                elif ai_player.short_positions:
                    # Cover part of existing short position to lock in macro rotation
                    cov_cid = next(iter(ai_player.short_positions.keys()))
                    cov_sh = min(ai_player.short_positions[cov_cid], 0.5)
                    if cov_sh > 0 and ai_player.cash > cov_sh * self.entities[cov_cid].stock_price * 1.1:
                        res = self.cover_short_stock(pid, cov_cid, cov_sh)
                        if res.get("ok"):
                            actions_taken += 1

            elif pid == 5:
                # Ken G. (Quant & High-Tech Compounder): Invest in high-ROCE tech corporations & build CapLab R&D/Factory
                tech_cids = [c for c in candidates if self.entities[c].industry_id in pref_inds] or candidates
                best_cid = max(tech_cids, key=lambda c: self.entities[c].roce_pct)
                target = self.entities[best_cid]
                if ai_player.cash > 60.0:
                    spend = min(ai_player.cash * 0.12, 160.0)
                    sh = min(self.public_float_shares[best_cid] * 0.22, spend / max(1.0, target.stock_price))
                    if sh >= 0.5:
                        res = self.buy_stock(pid, best_cid, round(sh, 2))
                        if res.get("ok"):
                            actions_taken += 1
                            self.ai_action_log.append({
                                "year": self.year, "quarter": self.quarter,
                                "actor_id": pid, "actor_name": ai_player.name,
                                "source": "WSR_MAKE_COMPUTER_TURN", "cmd": "QUANT_BUY",
                                "target_ticker": target.ticker, "shares_millions": round(sh, 2),
                            })

        # Part B: Capitalism Lab 64 PERSONS.DBF Executive AI Autopilot (Rotating slice of 6 CEOs per quarter)
        ceo_cids = list(self.corp_ceo_profiles.keys())
        if ceo_cids:
            q_idx = (self.year * 4 + self.quarter) % len(ceo_cids)
            active_slice = [ceo_cids[(q_idx + i) % len(ceo_cids)] for i in range(min(6, len(ceo_cids)))]
            for cid in active_slice:
                if cid in reserved_test_ids:
                    continue
                corp = self.entities.get(cid)
                ceo = self.corp_ceo_profiles.get(cid)
                if not corp or not corp.is_active or corp.is_bankrupt or not ceo:
                    continue

                # Determine preferred product for this corporation's WSR industry from crosswalk
                cw = self.crosswalk.get(corp.industry_id, {})
                prod_list = cw.get("product_codes", [])
                pcode = prod_list[0] if prod_list else "SMARTPH"
                pcode = self._normalize_product_code(pcode)
                city_choice = major_cities[(cid + self.quarter) % len(major_cities)]

                # Set corporate brand strategy from CEO MARKETING & CHARACTER traits
                if ceo["marketing"] >= 70:
                    corp.brand_strategy = "UNIQUE"
                elif ceo["marketing"] >= 40:
                    corp.brand_strategy = "RANGE"
                else:
                    corp.brand_strategy = "CORPORATE"

                # Check existing firms owned by this corporation
                corp_firms = [f for f in self.firms.values() if f.owner_corp_id == cid]
                if len(corp_firms) < 4 and corp.cash > 80.0:
                    # Decide firm type based on PERSONS.DBF highest expertise (RD, MFT, RETAIL, RAW)
                    if ceo["rd"] >= 60 and not any(f.firm_type == "RD" for f in corp_firms):
                        ftype, bcode, capex, inv = "RD", "RD", 12.0, 0.0
                    elif ceo["mft"] >= ceo["retail"] and not any(f.firm_type == "FACTORY" for f in corp_firms):
                        ftype, bcode, capex, inv = "FACTORY", "FACTORY1", 20.0, 4.0
                    elif ceo["raw"] >= 75 and not any(f.firm_type == "MINE" for f in corp_firms):
                        ftype, bcode, capex, inv = "MINE", "MINE", 18.0, 2.0
                    else:
                        ftype, bcode, capex, inv = "RETAIL", "DEPT", 14.0, 3.0

                    if corp.cash > (capex + inv) * 2.0:
                        res_b = self.build_caplab_firm(
                            owner_corp_id=cid,
                            firm_type=ftype,
                            build_code=bcode,
                            city_name=city_choice,
                            capex_millions=capex,
                            initial_inventory_millions=inv,
                            product_code=pcode,
                        )
                        if res_b.get("ok"):
                            actions_taken += 1
                            new_firm = self.firms[res_b["firm_id"]]
                            # Tune advertising & pricing using PERSONS.DBF MARKETING & CHARACTER traits
                            new_firm.advertising_budget_millions = round(0.3 + (ceo["marketing"] / 100.0) * 2.2, 2)
                            base_p = float(self.products.get(pcode, {}).get("PRICE", 100.0))
                            price_mult = 0.92 + (ceo["character"] / 10.0) * 0.16
                            new_firm.unit_price = round(max(1.0, base_p * price_mult), 2)
                            self.ai_action_log.append({
                                "year": self.year, "quarter": self.quarter,
                                "actor_id": cid, "actor_name": f"CEO {ceo['ceo_name']} ({corp.ticker})",
                                "source": "CAPLAB_PERSONS_DBF_AI", "cmd": "BUILD_FIRM",
                                "firm_type": ftype, "city": city_choice, "product": pcode,
                            })
                            self.news_headlines.append(
                                f"[CAPLAB EXPANSION] CEO {ceo['ceo_name']} of {corp.name} ({corp.ticker}) opened a new {ftype} for {pcode} in {city_choice}."
                            )

                # Dynamically adjust pricing & marketing on existing firms to compete for urban market share
                for f in corp_firms:
                    f.advertising_budget_millions = round(0.25 + (ceo["marketing"] / 100.0) * 2.0, 2)
                    base_p = float(self.products.get(f.product_code, {}).get("PRICE", 100.0))
                    if f.market_share < 0.12:
                        # Undercut price slightly to gain market share
                        f.unit_price = round(max(base_p * 0.75, f.unit_price * 0.96), 2)
                    elif f.market_share > 0.35 and f.product_quality > 70.0:
                        # Premium pricing power
                        f.unit_price = round(min(base_p * 1.45, f.unit_price * 1.03), 2)

        return {"ok": True, "actions_taken": actions_taken}

    def set_street_hustler_30k_mode(self, player_id: int = 1, cash_millions: float = 0.03) -> Dict[str, Any]:
        """
        Sets Aether (Player 1) starting capital to $30,000 USD (0.03 $M — 'Có làm thì mới có ăn'),
        returning excess cash to system_pool_cash to preserve 100% Closed-Loop Cash Conservation.
        """
        p = self.entities[player_id]
        delta = p.cash - cash_millions
        p.cash = cash_millions
        self.system_pool_cash += delta
        self.recompute_entity_balance_sheet(p, update_stock_price=False)
        return {"ok": True, "player_id": player_id, "cash_millions": p.cash, "net_worth_millions": p.net_worth}

    def incorporate_bootstrapped_startup(
        self,
        founder_id: int,
        firm_type: str = "RETAIL",
        city_name: str = "New York City",
        product_code: str = "SMARTPH",
        equity_invest_millions: float = 0.02,
        loan_multiple: float = 3.0,
    ) -> Dict[str, Any]:
        """
        Allows a small entrepreneur ($30k-$150k, e.g. STARTUP_HUSTLER or Aether) to incorporate
        a dormant WSR corporation slot (11..1580), inject seed equity, borrow a Small Business
        Bank Loan (IND=1), and open a Micro-Firm in Capitalism Lab while preserving 100%
        Balance Sheet, Share Conservation, and Closed-Loop Cash Conservation invariants.
        """
        founder = self.entities.get(founder_id)
        if not founder or not founder.is_active:
            return {"ok": False, "reason": "Invalid founder entity"}
        eq_m = min(max(0.005, float(equity_invest_millions)), founder.cash * 0.85)
        if founder.cash < eq_m or eq_m <= 0.0:
            return {"ok": False, "reason": "Insufficient founder cash for startup seed equity"}

        # Find an inactive corporate slot in 11..1580
        dormant_cid = None
        for cid in range(11, 1581):
            if cid in self.entities and not self.entities[cid].is_active:
                dormant_cid = cid
                break
        if dormant_cid is None:
            return {"ok": False, "reason": "No dormant startup corporate slots available"}

        startup = self.entities[dormant_cid]
        startup.is_active = True
        startup.is_bankrupt = False
        startup.regime = "INDUSTRIAL_HOLDING"
        startup.industry_id = 10 if product_code in ("SMARTPH", "NOTEBOOK", "COMPUTER") else 18
        startup.name = f"{founder.name.split()[0]} Ventures #{dormant_cid}"
        startup.ticker = f"S{dormant_cid}"
        startup.shares_outstanding = 1.0  # 1.0M seed shares
        startup.stock_price = max(0.10, round(eq_m / 1.0, 4))
        startup.cash = eq_m
        startup.cap_assets_abstract = 0.0
        startup.cap_assets_caplab_firms = 0.0
        startup.working_cap_abstract = 0.0
        startup.working_cap_caplab_inventory = 0.0
        startup.bank_loan = 0.0
        startup.straight_bonds_out = 0.0
        startup.convertible_bonds_out = 0.0
        startup.acc_tax = 0.0
        startup.cap_tax = 0.0
        startup.hid_reserve = 0.0
        startup.controlled_by_id = founder_id

        # Transfer founder equity cash -> startup corporate treasury (80% Founder Control + 20% Tradable Float)
        founder.cash -= eq_m
        founder.stock_holdings[dormant_cid] = 0.80
        founder.stock_cost_basis[dormant_cid] = eq_m
        founder.ceo_of_corp_ids.add(dormant_cid)
        self.public_float_shares[dormant_cid] = 0.20
        if dormant_cid not in self.active_corp_ids:
            self.active_corp_ids.append(dormant_cid)

        self.recompute_entity_balance_sheet(startup, update_stock_price=False)
        self.recompute_entity_balance_sheet(founder, update_stock_price=False)

        # Borrow Small Business Bank Loan (2x-4x equity) to fund Capitalism Lab Micro-Firm
        loan_m = round(eq_m * max(1.0, min(4.0, float(loan_multiple))), 4)
        self.borrow_bank_loan(dormant_cid, loan_m, allow_emergency=True)

        total_avail = startup.cash
        capex_m = round(total_avail * 0.65, 4)
        inv_m = round(total_avail * 0.20, 4)
        res_firm = self.build_caplab_firm(
            owner_corp_id=dormant_cid,
            firm_type=firm_type,
            build_code=firm_type,
            city_name=city_name,
            capex_millions=capex_m,
            initial_inventory_millions=inv_m,
            product_code=product_code,
        )
        self.step_caplab_firms_quarterly()
        self.recompute_entity_balance_sheet(startup, update_stock_price=False)
        self.recompute_entity_balance_sheet(founder, update_stock_price=False)
        return {
            "ok": True,
            "startup_corp_id": dormant_cid,
            "startup_ticker": startup.ticker,
            "founder_equity_millions": eq_m,
            "bank_loan_millions": loan_m,
            "firm_id": res_firm.get("firm_id"),
            "city_name": res_firm.get("city_name", city_name),
            "product_code": res_firm.get("product_code", product_code),
        }

    def spawn_representative_24_investor_subset(self) -> List[Dict[str, Any]]:
        """
        Spawns a representative 24-investor subset (Entity IDs 2001..2024) covering all 8 Personas
        (3 distinct investors per Persona across wealth tiers and domain preferences):
          1. PURE_WSR_WHALE       (2001..2003): Rich ($1,200M-$3,000M), ONLY trades WSR financial markets.
          2. PURE_CAPLAB_BUILDER  (2004..2006): Rich ($900M-$1,800M), ONLY builds/tunes CapLab supply chains.
          3. HYBRID_EMPIRE        (2007..2009): Rich ($1,500M-$3,500M), combines WSR M&A/Shorts + CapLab Firms.
          4. HEDGE_FUND_SHARK     (2010..2012): Mid-cap ($50M-$150M), Long/Short equity & supply-chain arb.
          5. STARTUP_HUSTLER      (2013..2015): Poor ($30k-$90k = 0.03M-0.09M), incorporates micro-startups!
          6. SMART_TRADER         (2016..2018): Poor ($30k-$60k = 0.03M-0.06M), Kelly-criterion WSR trader.
          7. PASSIVE_FOMO_SLEEPER (2019..2021): Poor/Mid ($30k-$100k), sleeps in T-Bills until FOMO wave hits.
          8. YOLO_GAMBLER         (2022..2024): Poor ($20k-$45k = 0.02M-0.045M), max margin gambler -> wipeout/respawn.
        """
        specs = [
            # Group 1: PURE_WSR_WHALE (Rich, 100% Financial Trading, 0 Factories)
            (2001, "Jim S. (Renaissance Quant Whale)", "RENS", 2200.0, "PURE_WSR_WHALE", ["WSR"], "HIGH_SHARPE_ARB", "Quantitative long/short equity & bond yield arbitrage; never builds physical factories."),
            (2002, "Stanley D. (Duquesne Macro Whale)", "DUQM", 1600.0, "PURE_WSR_WHALE", ["WSR"], "MACRO_TREND", "Pure macro & rate-cycle stock/short trader; zero interest in managing physical retail/factories."),
            (2003, "Howard M. (Oaktree Deep Value Whale)", "OAKT", 1400.0, "PURE_WSR_WHALE", ["WSR"], "DEEP_VALUE_DISTRESSED", "Buys deeply undervalued low-P/B stocks and high-yield bonds; strictly financial investor."),
            # Group 2: PURE_CAPLAB_BUILDER (Rich Industrialists, 100% CapLab Supply Chain & Urban Market Share)
            (2004, "Morris C. (Foundry Semiconductor Builder)", "TSMC", 1200.0, "PURE_CAPLAB_BUILDER", ["CAPLAB"], "RD_FACTORY_MONOPOLY", "Dedicated industrial builder: pours capital into R&D labs and semiconductor/electronics factories; never speculates on stocks."),
            (2005, "Sam W. (Hypermarket Retail Builder)", "WMART", 1100.0, "PURE_CAPLAB_BUILDER", ["CAPLAB"], "RETAIL_PRICE_WAR", "Obsessed with opening urban RETAIL stores across major cities and undercutting competitors' unit_price."),
            (2006, "Amancio O. (Fast-Fashion Brand Builder)", "ZARA", 950.0, "PURE_CAPLAB_BUILDER", ["CAPLAB"], "BRAND_MARKETING_EMPIRE", "Focuses 100% on Capitalism Lab factories, retail stores, and high advertising_budget_millions."),
            # Group 3: HYBRID_EMPIRE (Rich Conglomerate Raiders, plays BOTH WSR + CapLab)
            (2007, "Elon M. (Vertical Tech Raider)", "XEMP", 2800.0, "HYBRID_EMPIRE", ["WSR", "CAPLAB"], "VERTICAL_DISRUPTOR", "Combines aggressive WSR stock accumulation/M&A with vertical MINE -> FACTORY -> RD integration."),
            (2008, "Bernard A. (Luxury Conglomerate Titan)", "LVMH", 2400.0, "HYBRID_EMPIRE", ["WSR", "CAPLAB"], "BRAND_ACQUIRER", "Acquires consumer corporations on WSR and builds high-margin UNIQUE brand retail stores in CapLab."),
            (2009, "Masayoshi S. (Vision Tech Conglomerate)", "SOFT", 1900.0, "HYBRID_EMPIRE", ["WSR", "CAPLAB"], "LEVERAGED_TECH_ECOSYSTEM", "Uses bank leverage to buy tech equity stakes while building R&D and software/electronics firms."),
            # Group 4: HEDGE_FUND_SHARK (Mid-Cap $50M-$150M Sharks)
            (2010, "Bill A. (Pershing Activist Shark)", "PSHG", 140.0, "HEDGE_FUND_SHARK", ["WSR"], "CONCENTRATED_ACTIVIST", "Takes concentrated long positions in high-ROCE winners and shorts weak-credit laggards."),
            (2011, "David E. (Greenlight Short Shark)", "GLRE", 95.0, "HEDGE_FUND_SHARK", ["WSR"], "FORENSIC_SHORT_SELLER", "Hunts overvalued or deteriorating-margin corporations to short sell alongside value longs."),
            (2012, "Chase C. (Tiger Growth Shark)", "TIGR", 110.0, "HEDGE_FUND_SHARK", ["WSR"], "TECH_MOMENTUM_SHARK", "Tracks Capitalism Lab R&D breakthroughs to front-run high-growth tech stocks."),
            # Group 5: STARTUP_HUSTLER (Poor $30k-$90k Entrepreneurs who incorporate micro-startups!)
            (2013, "Minh K. ($30k Garage Tech Founder)", "MINH", 0.03, "STARTUP_HUSTLER", ["CAPLAB_STARTUP", "WSR"], "BOOTSTRAPPED_TECH_SHOP", "Starts with $30k; refuses to just day-trade—incorporates a micro-startup with bank loan to open an electronics/software shop."),
            (2014, "Sofia R. ($45k Boutique Retail Founder)", "SOFI", 0.045, "STARTUP_HUSTLER", ["CAPLAB_STARTUP", "WSR"], "BOOTSTRAPPED_RETAIL", "Uses $45k seed savings + bank loan to launch a small retail store and scale city market share."),
            (2015, "Kenji T. ($60k Craft Workshop Founder)", "KENJ", 0.06, "STARTUP_HUSTLER", ["CAPLAB_STARTUP", "WSR"], "BOOTSTRAPPED_MANUFACTURER", "Uses $60k seed capital + bank loan to incorporate a micro-factory/workshop."),
            # Group 6: SMART_TRADER (Poor $30k-$60k disciplined Kelly-Criterion WSR traders)
            (2016, "Alex V. ($30k Kelly Value Sniper)", "ALEX", 0.03, "SMART_TRADER", ["WSR"], "FRACTIONAL_KELLY_VALUE", "Starts with $30k like Aether; buys fractional lots of low-P/B dividend stocks with strict -12% stop-loss."),
            (2017, "Elena N. ($35k Momentum Swing Trader)", "ELEN", 0.035, "SMART_TRADER", ["WSR"], "SECTOR_MOMENTUM_SNIPER", "Rotates $35k across top-ROCE industry leaders with disciplined risk sizing."),
            (2018, "Marcus D. ($50k Contrarian Arb Trader)", "MARC", 0.05, "SMART_TRADER", ["WSR"], "CONTRARIAN_SWING", "Buys oversold quality stocks after panic dips and shorts overextended bubbles."),
            # Group 7: PASSIVE_FOMO_SLEEPER (Behavioral: sits idle in T-bills 80% of time, then FOMOs at tops)
            (2019, "Uncle Bob ($40k Retirement FOMO Saver)", "BOBS", 0.04, "PASSIVE_FOMO_SLEEPER", ["WSR"], "IDLE_THEN_FOMO", "Sits in T-Bills/Cash doing nothing most quarters; FOMOs all-in when a stock surges >18%."),
            (2020, "Aunt May ($30k Mattress Saver)", "MAYS", 0.03, "PASSIVE_FOMO_SLEEPER", ["WSR"], "HERD_FOLLOWER", "Afraid of the market until headlines turn euphoric, then buys the top and panic-sells the dip."),
            (2021, "kevin_99 ($50k Reddit Trend Chaser)", "KEVN", 0.05, "PASSIVE_FOMO_SLEEPER", ["WSR"], "VIRAL_CHASER", "Ignores fundamentals; only buys whatever ticker jumped the most this quarter."),
            # Group 8: YOLO_GAMBLER (Behavioral: max bank margin leverage -> boom or wipeout + respawn)
            (2022, "yolo_king ($30k 2x Margin Gambler)", "YOLO", 0.03, "YOLO_GAMBLER", ["WSR"], "MAX_MARGIN_LONG", "Borrows maximum bank loan every quarter to go 200% long on a single volatile stock."),
            (2023, "bear_zerker ($25k Reckless Short Gambler)", "BEAR", 0.025, "YOLO_GAMBLER", ["WSR"], "RECKLESS_SHORT", "Shorts high-flying stocks with maximum margin until squeezed into bankruptcy."),
            (2024, "degen_dan ($30k All-In Roulette)", "DEGN", 0.03, "YOLO_GAMBLER", ["WSR"], "ALL_IN_ROULETTE", "Bets entire net worth + full credit line on random high-volatility tickers."),
        ]

        # Give PURE_CAPLAB_BUILDER and HYBRID_EMPIRE (2004..2009) control over dedicated active corporations
        # so they can immediately execute Capitalism Lab firm builds & pricing strategies
        builder_corps = [350, 351, 352, 353, 354, 355]
        created = []
        for idx, (eid, name, ticker, init_cash, persona_type, allowed_domains, sub_style, bio) in enumerate(specs):
            ent = FinancialEntity(
                entity_id=eid,
                name=name,
                ticker=ticker,
                regime="PLAYER_INDIVIDUAL",
                industry_id=0,
                country_code=1,
                is_active=True,
                cash=init_cash,
                total_assets=init_cash,
                total_liabilities=0.0,
                net_worth=init_cash,
                credit_rating=10,
                borrowing_rate_pct=self.prime_rate_pct,
                credit_line_limit=init_cash,
            )
            self.system_pool_cash -= init_cash
            self.entities[eid] = ent
            if eid not in self.player_ids:
                self.player_ids.append(eid)

            controlled_cid = 0
            if persona_type in ("PURE_CAPLAB_BUILDER", "HYBRID_EMPIRE"):
                c_idx = eid - 2004
                if 0 <= c_idx < len(builder_corps):
                    target_cid = builder_corps[c_idx]
                    if target_cid in self.entities and self.entities[target_cid].is_active:
                        controlled_cid = target_cid
                        self.entities[target_cid].controlled_by_id = eid
                        if self.entities[target_cid].cash < 180.0:
                            topup = 180.0 - self.entities[target_cid].cash
                            self.entities[target_cid].cash += topup
                            self.system_pool_cash -= topup
                            self.recompute_entity_balance_sheet(self.entities[target_cid], update_stock_price=False)
                        ent.ceo_of_corp_ids.add(target_cid)

            p_record = {
                "entity_id": eid,
                "name": name,
                "ticker": ticker,
                "persona_type": persona_type,
                "allowed_domains": allowed_domains,
                "sub_style": sub_style,
                "bio": bio,
                "initial_cash_millions": init_cash,
                "generation": 1,
                "controlled_corp_id": controlled_cid,
                "is_smart_luna_agent": persona_type not in ("PASSIVE_FOMO_SLEEPER", "YOLO_GAMBLER"),
                "price_history_anchor": {},
            }
            self.investor_personas[eid] = p_record
            self.recompute_entity_balance_sheet(ent, update_stock_price=False)
            created.append(p_record)

        return created

    def handle_investor_wipeout_and_respawn(self, entity_id: int) -> Dict[str, Any]:
        """
        Liquidates a bankrupt/wiped-out investor back into public_float_shares & system_pool_cash,
        records them in self.wipeout_graveyard, and spawns a Fresh Entrant (generation + 1)
        with baseline initial_cash and an empty portfolio while preserving 100% Cash & Share Conservation.
        """
        ent = self.entities.get(entity_id)
        persona = self.investor_personas.get(entity_id)
        if not ent or not persona:
            return {"ok": False, "reason": "Entity not in investor_personas"}

        # 1. Sell all long stock holdings back to public float
        for cid, sh in list(ent.stock_holdings.items()):
            if sh > 0 and cid in self.entities:
                self.sell_stock(entity_id, cid, sh)

        # 2. Cover all short positions
        for cid, sh in list(ent.short_positions.items()):
            if sh > 0 and cid in self.entities:
                self.cover_short_stock(entity_id, cid, sh)

        # 2b. Liquidate any bonds, commodity margin/MTM, crypto, or options held/written by entity_id
        if ent.gov_bonds_par > 0:
            self.sell_gov_bonds(entity_id, ent.gov_bonds_par)
        if ent.corp_bonds_par > 0:
            self.sell_corp_bonds(entity_id, ent.corp_bonds_par)
        if ent.commod_margin != 0.0 or ent.commod_mtm != 0.0:
            net_c = ent.commod_margin + ent.commod_mtm
            ent.cash += net_c
            self.system_pool_cash -= net_c
            ent.commod_margin = 0.0
            ent.commod_mtm = 0.0
            ent.futures_positions.clear()
        if ent.crypto_holdings:
            for sym, coins in list(ent.crypto_holdings.items()):
                if coins > 0:
                    val_m = coins * self.crypto_prices.get(sym, 0.0) / 1_000_000.0
                    ent.cash += val_m
                    self.system_pool_cash -= val_m
            ent.crypto_holdings.clear()
            ent.crypto_portfolio_value = 0.0
        for oid, opt in list(self.options.items()):
            if opt.holder_id == entity_id:
                ent.cash += opt.current_value_millions
                self.system_pool_cash -= opt.current_value_millions
                del self.options[oid]
            elif opt.writer_id == entity_id:
                ent.cash -= opt.current_value_millions
                self.system_pool_cash += opt.current_value_millions
                del self.options[oid]
        self._revalue_all_options()

        # 3. Settle remaining bank loan & sweep residual cash/debt against system_pool_cash
        if ent.bank_loan > 0.0:
            repay_amt = min(max(0.0, ent.cash), ent.bank_loan)
            if repay_amt > 0.0:
                self.repay_bank_loan(entity_id, repay_amt)
            if ent.bank_loan > 0.0:
                # Write off unrecoverable personal margin debt against lending bank / system pool
                lender = self.entities.get(ent.lender_bank_id)
                if lender and lender.regime == "COMMERCIAL_BANK":
                    lender.biz_loans = max(0.0, lender.biz_loans - ent.bank_loan)
                    lender.cash += ent.bank_loan
                    self.system_pool_cash -= ent.bank_loan
                    self.recompute_entity_balance_sheet(lender, update_stock_price=False)
                else:
                    self.system_pool_cash -= ent.bank_loan
                ent.bank_loan = 0.0

        # Sweep any remaining pennies or negative cash back to system_pool_cash
        self.system_pool_cash += ent.cash
        ent.cash = 0.0
        ent.tbills = 0.0
        ent.income_tax_owed = 0.0
        ent.wealth_tax_projected = 0.0
        ent.is_bankrupt = False

        old_gen = int(persona.get("generation", 1))
        wipeout_entry = {
            "year": self.year,
            "quarter": self.quarter,
            "entity_id": entity_id,
            "old_name": ent.name,
            "persona_type": persona["persona_type"],
            "generation_wiped": old_gen,
        }
        self.wipeout_graveyard.append(wipeout_entry)

        # 4. Respawn Fresh Entrant with baseline initial_cash & clean white portfolio
        fresh_cash = float(persona.get("initial_cash_millions", 0.03))
        ent.cash = fresh_cash
        self.system_pool_cash -= fresh_cash
        new_gen = old_gen + 1
        persona["generation"] = new_gen
        persona["needs_smart_ai_init"] = bool(persona.get("is_smart_luna_agent", False))
        base_name = persona["name"].split(" [Gen")[0]
        ent.name = f"{base_name} [Gen {new_gen}]"
        self.recompute_entity_balance_sheet(ent, update_stock_price=False)

        self.news_headlines.append(
            f"[MARGIN WIPEOUT & RESPAWN] {wipeout_entry['old_name']} ({persona['persona_type']}) wiped out! Fresh entrant {ent.name} joined with ${fresh_cash*1000:.1f}k."
        )
        return {"ok": True, "wipeout": wipeout_entry, "new_entrant_name": ent.name, "fresh_cash_millions": fresh_cash}

    # =========================================================================
    # 8C. BONDS, FUTURES, CRYPTO, ETF ADVISOR & 24-ARCHETYPE / 320-INVESTOR ENGINE
    # =========================================================================

    def buy_gov_bonds(self, buyer_id: int, par_millions: float) -> Dict[str, Any]:
        """Buys 7% Long Government Bonds at exact WSR market price while conserving closed-loop cash."""
        buyer = self.entities.get(buyer_id)
        if not buyer or not buyer.is_active or par_millions <= 0.0:
            return {"ok": False, "reason": "Invalid buyer or bond par"}
        px_factor = self.get_long_gov_bond_price() / 100.0
        cost_m = round(par_millions * px_factor, 6)
        if buyer.cash < cost_m:
            par_millions = round((buyer.cash * 0.90) / max(0.01, px_factor), 5)
            cost_m = round(par_millions * px_factor, 6)
        if par_millions <= 0.0001 or buyer.cash < cost_m:
            return {"ok": False, "reason": "Insufficient cash for government bonds"}
        buyer.cash -= cost_m
        self.system_pool_cash += cost_m
        buyer.gov_bonds_par += par_millions
        buyer.gov_bonds_adj_cost += cost_m
        buyer.gov_bonds_mkt_value = buyer.gov_bonds_par * px_factor
        self.recompute_entity_balance_sheet(buyer, update_stock_price=False)
        return {"ok": True, "par_bought_millions": par_millions, "cost_millions": cost_m}

    def sell_gov_bonds(self, seller_id: int, par_millions: float) -> Dict[str, Any]:
        """Sells held 7% Long Government Bonds at market price."""
        seller = self.entities.get(seller_id)
        if not seller or seller.gov_bonds_par <= 0.0:
            return {"ok": False, "reason": "No government bonds held"}
        sell_par = min(par_millions, seller.gov_bonds_par)
        px_factor = self.get_long_gov_bond_price() / 100.0
        proceeds_m = round(sell_par * px_factor, 6)
        prop = sell_par / max(1e-9, seller.gov_bonds_par)
        seller.gov_bonds_par = max(0.0, seller.gov_bonds_par - sell_par)
        seller.gov_bonds_adj_cost = max(0.0, seller.gov_bonds_adj_cost * (1.0 - prop))
        seller.cash += proceeds_m
        self.system_pool_cash -= proceeds_m
        self.recompute_entity_balance_sheet(seller, update_stock_price=False)
        return {"ok": True, "par_sold_millions": sell_par, "proceeds_millions": proceeds_m}

    def buy_corp_bonds(self, buyer_id: int, par_millions: float) -> Dict[str, Any]:
        """Buys Corporate Bonds at exact market price while conserving closed-loop cash."""
        buyer = self.entities.get(buyer_id)
        if not buyer or not buyer.is_active or par_millions <= 0.0:
            return {"ok": False, "reason": "Invalid buyer or bond par"}
        px_factor = (self.get_long_gov_bond_price() * 0.96) / 100.0
        cost_m = round(par_millions * px_factor, 6)
        if buyer.cash < cost_m:
            par_millions = round((buyer.cash * 0.90) / max(0.01, px_factor), 5)
            cost_m = round(par_millions * px_factor, 6)
        if par_millions <= 0.0001 or buyer.cash < cost_m:
            return {"ok": False, "reason": "Insufficient cash for corporate bonds"}
        buyer.cash -= cost_m
        self.system_pool_cash += cost_m
        buyer.corp_bonds_par += par_millions
        buyer.corp_bonds_adj_cost += cost_m
        buyer.corp_bonds_mkt_value = buyer.corp_bonds_par * px_factor
        self.recompute_entity_balance_sheet(buyer, update_stock_price=False)
        return {"ok": True, "par_bought_millions": par_millions, "cost_millions": cost_m}

    def sell_corp_bonds(self, seller_id: int, par_millions: float) -> Dict[str, Any]:
        """Sells held Corporate Bonds at market price."""
        seller = self.entities.get(seller_id)
        if not seller or seller.corp_bonds_par <= 0.0:
            return {"ok": False, "reason": "No corporate bonds held"}
        sell_par = min(par_millions, seller.corp_bonds_par)
        px_factor = (self.get_long_gov_bond_price() * 0.96) / 100.0
        proceeds_m = round(sell_par * px_factor, 6)
        prop = sell_par / max(1e-9, seller.corp_bonds_par)
        seller.corp_bonds_par = max(0.0, seller.corp_bonds_par - sell_par)
        seller.corp_bonds_adj_cost = max(0.0, seller.corp_bonds_adj_cost * (1.0 - prop))
        seller.cash += proceeds_m
        self.system_pool_cash -= proceeds_m
        self.recompute_entity_balance_sheet(seller, update_stock_price=False)
        return {"ok": True, "par_sold_millions": sell_par, "proceeds_millions": proceeds_m}

    def trade_commodity_futures(self, trader_id: int, commodity_code: str, notional_millions: float) -> Dict[str, Any]:
        """
        Opens or adjusts a Commodity Futures position (OIL, GOLD, SILVER, WHEAT, CORN, COPPER, STOCK_INDEX)
        posting 15% initial margin from cash into commod_margin while preserving 100% closed-loop cash.
        """
        trader = self.entities.get(trader_id)
        comm = (commodity_code or "OIL").strip().upper()
        if comm not in self.commodity_prices:
            comm = "OIL"
        if not trader or not trader.is_active or abs(notional_millions) <= 0.0001:
            return {"ok": False, "reason": "Invalid trader or futures notional"}
        margin_req = round(abs(notional_millions) * 0.15, 5)
        if trader.cash < margin_req:
            margin_req = round(trader.cash * 0.50, 5)
            notional_millions = (margin_req / 0.15) * (1.0 if notional_millions > 0 else -1.0)
        if margin_req <= 0.0001:
            return {"ok": False, "reason": "Insufficient cash for futures margin"}
        trader.cash -= margin_req
        self.system_pool_cash += margin_req
        trader.commod_margin += margin_req
        spot = max(0.01, self.commodity_prices[comm])
        contracts = round(notional_millions / spot, 4)
        trader.futures_positions[comm] = trader.futures_positions.get(comm, 0.0) + contracts
        self.recompute_entity_balance_sheet(trader, update_stock_price=False)
        return {"ok": True, "commodity": comm, "contracts": contracts, "margin_posted_millions": margin_req}

    def trade_crypto(self, trader_id: int, symbol: str, usd_millions_delta: float) -> Dict[str, Any]:
        """Buys (usd_millions_delta > 0) or sells (usd_millions_delta < 0) BTC or ETH."""
        trader = self.entities.get(trader_id)
        sym = (symbol or "BTC").strip().upper()
        if sym not in self.crypto_prices:
            sym = "BTC"
        if not trader or not trader.is_active or abs(usd_millions_delta) <= 0.00001:
            return {"ok": False, "reason": "Invalid crypto trade"}
        px = max(1.0, self.crypto_prices[sym])
        if usd_millions_delta > 0:
            spend_m = min(usd_millions_delta, trader.cash * 0.85)
            if spend_m <= 0.00001:
                return {"ok": False, "reason": "Insufficient cash for crypto purchase"}
            coins = (spend_m * 1_000_000.0) / px
            trader.cash -= spend_m
            self.system_pool_cash += spend_m
            trader.crypto_holdings[sym] = trader.crypto_holdings.get(sym, 0.0) + coins
            self.recompute_entity_balance_sheet(trader, update_stock_price=False)
            return {"ok": True, "symbol": sym, "action": "BUY", "coins": round(coins, 6), "usd_millions": spend_m}
        else:
            held_coins = trader.crypto_holdings.get(sym, 0.0)
            if held_coins <= 0.0:
                return {"ok": False, "reason": "No crypto coins held to sell"}
            sell_val_m = min(abs(usd_millions_delta), (held_coins * px) / 1_000_000.0)
            sell_coins = (sell_val_m * 1_000_000.0) / px
            trader.crypto_holdings[sym] = max(0.0, held_coins - sell_coins)
            trader.cash += sell_val_m
            self.system_pool_cash -= sell_val_m
            self.recompute_entity_balance_sheet(trader, update_stock_price=False)
            return {"ok": True, "symbol": sym, "action": "SELL", "coins": round(sell_coins, 6), "usd_millions": sell_val_m}

    def become_etf_advisor(self, advisor_id: int, etf_id: int) -> Dict[str, Any]:
        """Registers advisor_id as the institutional advisor of ETF etf_id (1581..1600) to collect quarterly NAV fees."""
        if etf_id not in self.entities or self.entities[etf_id].regime != "ETF_FUND":
            etf_id = self.etf_corp_ids[0] if self.etf_corp_ids else 1581
        etf = self.entities[etf_id]
        etf.advisor_id = advisor_id
        return {"ok": True, "etf_id": etf_id, "etf_ticker": etf.ticker, "advisor_id": advisor_id, "advisory_fee_pct": etf.advisory_fee_pct}

    def get_24_archetype_catalog(self) -> List[Dict[str, Any]]:
        """
        Returns the complete 24 Unique Investor & Entrepreneur Archetype Catalog across 4 Domains
        (supporting 320+ investors with zero mechanical overlap).
        """
        return [
            # Domain I: Pure WSR Financial, Credit & Derivatives Specialists (7 Archetypes, 36 Whales)
            {"arch_id": 1, "code": "WSR_VALUE_COMPOUNDER", "domain": "WSR_FINANCE", "count": 6, "init_cash_m": 650.0, "allowed_domains": ["WSR"], "is_smart": True, "lead_name": "Warren B. II (DRD Value Whale)", "ticker": "DRDV", "signature_cmd": "BUY_STOCK", "bio": "Acquires >=20% low-P/B stakes to harvest 80%-100% DRD tax-exempt dividends; zero physical factories."},
            {"arch_id": 2, "code": "QUANT_LONG_SHORT_WHALE", "domain": "WSR_FINANCE", "count": 6, "init_cash_m": 450.0, "allowed_domains": ["WSR"], "is_smart": True, "lead_name": "Jim S. (Quant Long/Short Whale)", "ticker": "RENS", "signature_cmd": "SHORT_STOCK", "bio": "Market-neutral quant: buys high-ROCE leaders and shorts negative-ROCE laggards simultaneously."},
            {"arch_id": 3, "code": "CORPORATE_RAIDER_LBO", "domain": "WSR_FINANCE", "count": 4, "init_cash_m": 800.0, "allowed_domains": ["WSR"], "is_smart": True, "lead_name": "Carl I. (LBO & Spin-Off Raider)", "ticker": "RAIDER", "signature_cmd": "SPINOFF_SUB", "bio": "Acquires control of undervalued holding conglomerates to execute tax-free SPINOFF_SUB and LIQUIDATE_SUB."},
            {"arch_id": 4, "code": "FORENSIC_SHORT_ACTIVIST", "domain": "WSR_FINANCE", "count": 6, "init_cash_m": 220.0, "allowed_domains": ["WSR"], "is_smart": True, "lead_name": "Jim C. (Forensic Short & Lawsuit Shark)", "ticker": "KYNK", "signature_cmd": "FILE_LAWSUIT", "bio": "Shorts low-credit (BB..CCC) distressed corporations and files antitrust/harassing lawsuits."},
            {"arch_id": 5, "code": "FIXED_INCOME_BOND_KING", "domain": "WSR_FINANCE", "count": 5, "init_cash_m": 380.0, "allowed_domains": ["WSR"], "is_smart": True, "lead_name": "Howard M. (Bond & Convertible King)", "ticker": "BOND", "signature_cmd": "BUY_GOV_BOND", "bio": "Specializes in Government Bonds, Corporate Bonds, and Convertible Bonds (ISSUE_CV / CONVERT_CV)."},
            {"arch_id": 6, "code": "DERIVATIVES_SWAP_MACRO", "domain": "WSR_FINANCE", "count": 5, "init_cash_m": 320.0, "allowed_domains": ["WSR"], "is_smart": True, "lead_name": "Stan D. (Options & Rate Swap Wizard)", "ticker": "SWAP", "signature_cmd": "CREATE_SWAP", "bio": "Trades Interest Rate Swaps (CREATE_SWAP) and Call/Put Options (BUY_OPTION) around Prime Rate cycles."},
            {"arch_id": 7, "code": "COMMODITY_CRYPTO_WHALE", "domain": "WSR_FINANCE", "count": 4, "init_cash_m": 240.0, "allowed_domains": ["WSR"], "is_smart": True, "lead_name": "Paul T. (Commodities & Crypto Whale)", "ticker": "CMCR", "signature_cmd": "TRADE_FUTURES", "bio": "Trades OIL, GOLD, WHEAT, COPPER futures and BTC/ETH crypto macro cycles."},

            # Domain II: Pure Capitalism Lab Real-Economy Builders (6 Archetypes, 36 Moguls)
            {"arch_id": 8, "code": "RD_SEMICONDUCTOR_MOGUL", "domain": "CAPLAB_REAL", "count": 6, "init_cash_m": 350.0, "allowed_domains": ["CAPLAB"], "is_smart": True, "lead_name": "Morris C. (3x3 R&D & Foundry Mogul)", "ticker": "TSMC", "signature_cmd": "BUILD_FIRM", "firm_focus": "RD", "product_focus": "COMPUTER", "bio": "Builds 3x3 R&D centers (480% synergy) and high-tech factories to push world top_tech_levels."},
            {"arch_id": 9, "code": "HYPERMARKET_RETAIL_BARON", "domain": "CAPLAB_REAL", "count": 6, "init_cash_m": 260.0, "allowed_domains": ["CAPLAB"], "is_smart": True, "lead_name": "Sam W. (Hypermarket Retail Baron)", "ticker": "WMRT", "signature_cmd": "BUILD_FIRM", "firm_focus": "RETAIL", "product_focus": "SMARTPH", "bio": "Expands urban RETAIL chains across major cities and aggressively undercuts unit_price."},
            {"arch_id": 10, "code": "LUXURY_BRAND_TITAN", "domain": "CAPLAB_REAL", "count": 6, "init_cash_m": 280.0, "allowed_domains": ["CAPLAB"], "is_smart": True, "lead_name": "Amancio O. (Luxury & Brand Titan)", "ticker": "ZARA", "signature_cmd": "SET_BRAND_STRATEGY", "firm_focus": "RETAIL", "product_focus": "APPAREL", "bio": "Runs UNIQUE/RANGE brand strategies with heavy advertising_budget_millions and premium pricing."},
            {"arch_id": 11, "code": "RESOURCE_MINING_BARON", "domain": "CAPLAB_REAL", "count": 6, "init_cash_m": 310.0, "allowed_domains": ["CAPLAB"], "is_smart": True, "lead_name": "Gina R. (Mining, Oil & Agribusiness Baron)", "ticker": "MINE", "signature_cmd": "BUILD_FIRM", "firm_focus": "MINE", "product_focus": "GOLD", "bio": "Monopolizes upstream MINE, OIL, FOREST, and FARM resources across resource-rich cities."},
            {"arch_id": 12, "code": "REAL_ESTATE_REIT_LANDLORD", "domain": "CAPLAB_REAL", "count": 6, "init_cash_m": 290.0, "allowed_domains": ["CAPLAB"], "is_smart": True, "lead_name": "Donald B. (Urban REIT & Mall Landlord)", "ticker": "REIT", "signature_cmd": "BUILD_FIRM", "firm_focus": "APARTMEN", "product_focus": "CAR", "bio": "Builds APARTMEN, COMMERCI, and MALL properties in high-wage cities for steady rental cash flow."},
            {"arch_id": 13, "code": "DIGITAL_SOFTWARE_FOUNDER", "domain": "CAPLAB_REAL", "count": 6, "init_cash_m": 190.0, "allowed_domains": ["CAPLAB"], "is_smart": True, "lead_name": "Gabe N. (Digital Software & Internet Mogul)", "ticker": "VALV", "signature_cmd": "BUILD_FIRM", "firm_focus": "SOFTWARE", "product_focus": "COMPUTER", "bio": "Builds high-margin SOFTWARE studios, INTERNET platforms, and TELECOM infrastructure."},

            # Domain III: Cross-Domain Empires & Bootstrapped $30k Hustlers (5 Archetypes, 48 Founders/Tycoons)
            {"arch_id": 14, "code": "VERTICAL_CHAEBOL_EMPIRE", "domain": "HYBRID_CROSS", "count": 6, "init_cash_m": 750.0, "allowed_domains": ["WSR", "CAPLAB"], "is_smart": True, "lead_name": "Elon M. (Vertical Supply-Chain Chaebol)", "ticker": "XEMP", "signature_cmd": "BUILD_FIRM", "firm_focus": "FACTORY", "product_focus": "CAR", "bio": "Integrates MINE -> FACTORY -> RD -> RETAIL while acquiring WSR competitors."},
            {"arch_id": 15, "code": "BANK_INSURANCE_FLOAT_TYCOON", "domain": "HYBRID_CROSS", "count": 6, "init_cash_m": 600.0, "allowed_domains": ["WSR", "CAPLAB"], "is_smart": True, "lead_name": "Ajit J. (Bank & Insurance Float Tycoon)", "ticker": "FLOT", "signature_cmd": "BUY_STOCK", "bio": "Accumulates stakes in Commercial Banks (IND=1) & Insurers (IND=2), deploying float into equities & bonds."},
            {"arch_id": 16, "code": "ETF_INSTITUTIONAL_ADVISOR", "domain": "HYBRID_CROSS", "count": 4, "init_cash_m": 210.0, "allowed_domains": ["WSR"], "is_smart": True, "lead_name": "Larry F. (BlackRock ETF Advisor)", "ticker": "BLKR", "signature_cmd": "ADVISOR_ETF", "bio": "Advises the 20 institutional ETFs (IDs 1581..1600) to harvest quarterly NAV management fees."},
            {"arch_id": 17, "code": "BOOTSTRAP_RETAIL_HUSTLER", "domain": "HYBRID_CROSS", "count": 16, "init_cash_m": 0.03, "allowed_domains": ["CAPLAB_STARTUP", "WSR"], "is_smart": True, "lead_name": "Minh K. ($30k Bootstrapped Retail Founder)", "ticker": "MINH", "signature_cmd": "INCORPORATE_STARTUP", "firm_focus": "RETAIL", "product_focus": "SMARTPH", "bio": "Starts with $30k; incorporates a dormant WSR slot with bank loan to open an urban retail store."},
            {"arch_id": 18, "code": "BOOTSTRAP_TECH_WORKSHOP", "domain": "HYBRID_CROSS", "count": 16, "init_cash_m": 0.045, "allowed_domains": ["CAPLAB_STARTUP", "WSR"], "is_smart": True, "lead_name": "Kenji T. ($45k Indie Software & Workshop Founder)", "ticker": "KENJ", "signature_cmd": "INCORPORATE_STARTUP", "firm_focus": "SOFTWARE", "product_focus": "COMPUTER", "bio": "Uses $45k seed savings + small business bank loan to launch an indie software/workshop startup."},

            # Domain IV: Retail Peers, Passive Savers & Behavioral Crowd (6 Archetypes, 200 Investors)
            {"arch_id": 19, "code": "KELLY_VALUE_SNIPER", "domain": "RETAIL_ECOLOGY", "count": 20, "init_cash_m": 0.03, "allowed_domains": ["WSR"], "is_smart": True, "lead_name": "Alex V. ($30k Kelly Value Sniper)", "ticker": "ALEX", "signature_cmd": "BUY_STOCK", "bio": "Starts with $30k like Aether; buys micro-lots (100-1,000 sh) of low-P/B value stocks with strict risk sizing."},
            {"arch_id": 20, "code": "SUPPLY_CHAIN_MOMENTUM_TRADER", "domain": "RETAIL_ECOLOGY", "count": 20, "init_cash_m": 0.04, "allowed_domains": ["WSR"], "is_smart": True, "lead_name": "Elena N. ($40k Supply-Chain Momentum Trader)", "ticker": "ELEN", "signature_cmd": "BUY_STOCK", "bio": "Tracks Capitalism Lab R&D breakthroughs & city market share gains to front-run winning tech stocks."},
            {"arch_id": 21, "code": "BOGLEHEAD_ETF_SAVER", "domain": "RETAIL_ECOLOGY", "count": 40, "init_cash_m": 0.05, "allowed_domains": ["WSR"], "is_smart": False, "lead_name": "Jack B. ($50k Passive ETF Indexer)", "ticker": "BOGL", "signature_cmd": "BUY_STOCK", "bio": "Dollar-cost averages exclusively into the 20 WSR ETFs (IDs 1581..1600) every quarter; 0 API calls."},
            {"arch_id": 22, "code": "DIVIDEND_RETIREE_HUNTER", "domain": "RETAIL_ECOLOGY", "count": 35, "init_cash_m": 0.08, "allowed_domains": ["WSR"], "is_smart": False, "lead_name": "Martha S. ($80k Dividend & Bond Retiree)", "ticker": "DIVR", "signature_cmd": "BUY_GOV_BOND", "bio": "Splits capital between 7% Government Bonds and high-dividend stocks for steady quarterly cash flow; 0 API calls."},
            {"arch_id": 23, "code": "PASSIVE_FOMO_SLEEPER", "domain": "RETAIL_ECOLOGY", "count": 45, "init_cash_m": 0.03, "allowed_domains": ["WSR"], "is_smart": False, "lead_name": "Uncle Bob ($30k FOMO Top Chaser)", "ticker": "FOMO", "signature_cmd": "BUY_STOCK", "bio": "Sleeps in T-Bills 75% of the time, then FOMOs into top surging tickers and panic-sells dips; 0 API calls."},
            {"arch_id": 24, "code": "WSB_MEME_YOLO_DEGEN", "domain": "RETAIL_ECOLOGY", "count": 40, "init_cash_m": 0.03, "allowed_domains": ["WSR"], "is_smart": False, "lead_name": "yolo_king ($30k WSB Squeeze & Margin Degen)", "ticker": "WSBY", "signature_cmd": "BUY_STOCK", "bio": "Piles into heavily shorted tickers to trigger Short Squeezes or gambles max margin until wipeout & respawn; 0 API calls."},
        ]

    def spawn_full_320_investor_ecosystem(self, spawn_all_320: bool = True) -> List[Dict[str, Any]]:
        """
        Spawns the complete 24-Archetype Investor Ecosystem:
          - Entity IDs 2001..2024 are ALWAYS the 24 Archetype Leads (1 Lead per Archetype #1..#24),
            guaranteeing 100% coverage of all 24 unique archetypes in every benchmark.
          - When spawn_all_320=True (default), also spawns Entity IDs 2025..2320 (the remaining 296 cohort members)
            for a total of 320 active investors across all 24 archetypes with individualized DNA
            (preferred_industries, preferred_cities, risk_tolerance, stagger_cohort_id in 0..3)
            and 100% Closed-Loop Cash Conservation!
        """
        catalog = self.get_24_archetype_catalog()
        cities_pool = ["New York City", "Tokyo", "London", "Beijing", "Chicago", "Los Angeles", "Seoul", "Frankfurt", "Paris", "Toronto", "Sydney", "Singapore"]
        reserved_test_ids = {131, 132, 133, 181, 200, 201, 202, 203, 205, 221, 222, 300, 321, 322, 620}
        avail_builder_corps = [
            cid for cid in self.active_corp_ids
            if cid >= 340 and cid not in reserved_test_ids and self.entities[cid].regime == "INDUSTRIAL_HOLDING"
        ]
        builder_cursor = 0
        created: List[Dict[str, Any]] = []

        def _create_one_investor(eid: int, arch: Dict[str, Any], member_idx: int, is_lead: bool) -> Dict[str, Any]:
            nonlocal builder_cursor
            code = arch["code"]
            base_cash = float(arch["init_cash_m"])
            init_cash = base_cash if is_lead else round(base_cash * (0.75 + 0.50 * ((eid * 17) % 11) / 10.0), 4)
            name = arch["lead_name"] if is_lead else f"{code.title().replace('_', ' ')} #{member_idx + 1} (ID {eid})"
            ticker = arch["ticker"] if is_lead else f"A{arch['arch_id']:02d}{member_idx:02d}"

            ent = FinancialEntity(
                entity_id=eid,
                name=name,
                ticker=ticker,
                regime="PLAYER_INDIVIDUAL",
                industry_id=0,
                country_code=1,
                is_active=True,
                cash=init_cash,
                total_assets=init_cash,
                total_liabilities=0.0,
                net_worth=init_cash,
                credit_rating=10,
                borrowing_rate_pct=self.prime_rate_pct,
                credit_line_limit=init_cash,
            )
            self.system_pool_cash -= init_cash
            self.entities[eid] = ent
            if eid not in self.player_ids:
                self.player_ids.append(eid)

            controlled_cid = 0
            # Assign dedicated industrial corporations to CapLab & Hybrid Empire archetypes (#8..#14) and Raider (#3)
            if arch["arch_id"] in (3, 8, 9, 10, 11, 12, 13, 14) and builder_cursor < len(avail_builder_corps):
                target_cid = avail_builder_corps[builder_cursor]
                builder_cursor += 1
                controlled_cid = target_cid
                self.entities[target_cid].controlled_by_id = eid
                if self.entities[target_cid].cash < 180.0:
                    topup = 180.0 - self.entities[target_cid].cash
                    self.entities[target_cid].cash += topup
                    self.system_pool_cash -= topup
                    self.recompute_entity_balance_sheet(self.entities[target_cid], update_stock_price=False)
                ent.ceo_of_corp_ids.add(target_cid)
                # Ensure CORPORATE_RAIDER_LBO (#3) has a >=80% subsidiary ready for tax-free SPINOFF_SUB / LIQUIDATE_SUB
                if arch["arch_id"] == 3 and builder_cursor < len(avail_builder_corps):
                    sub_cid = avail_builder_corps[builder_cursor]
                    builder_cursor += 1
                    sub_ent = self.entities[sub_cid]
                    avail_ff = self.public_float_shares.get(sub_cid, 0.0)
                    take_sh = round(avail_ff * 0.85, 4)
                    if take_sh > 0:
                        self.public_float_shares[sub_cid] -= take_sh
                        self.entities[target_cid].stock_holdings[sub_cid] = self.entities[target_cid].stock_holdings.get(sub_cid, 0.0) + take_sh
                        self.entities[target_cid].stock_cost_basis[sub_cid] = take_sh * sub_ent.stock_price
                        self.recompute_entity_balance_sheet(self.entities[target_cid], update_stock_price=False)

            dna = {
                "preferred_industries": [((eid * 3 + k * 7) % 65) + 3 for k in range(3)],
                "preferred_cities": [cities_pool[(eid + k * 3) % len(cities_pool)] for k in range(2)],
                "risk_tolerance": round(0.20 + 0.70 * ((eid * 13) % 10) / 9.0, 2),
                "stagger_cohort_id": (eid - 2001) % 4,
            }
            p_record = {
                "entity_id": eid,
                "arch_id": arch["arch_id"],
                "name": name,
                "ticker": ticker,
                "persona_type": code,
                "domain_group": arch["domain"],
                "allowed_domains": list(arch["allowed_domains"]),
                "sub_style": arch.get("signature_cmd", "BUY_STOCK"),
                "signature_cmd": arch.get("signature_cmd", "BUY_STOCK"),
                "firm_focus": arch.get("firm_focus", "RETAIL"),
                "product_focus": arch.get("product_focus", "SMARTPH"),
                "bio": arch["bio"],
                "initial_cash_millions": init_cash,
                "generation": 1,
                "controlled_corp_id": controlled_cid,
                "is_archetype_lead": is_lead,
                "is_smart_luna_agent": bool(arch["is_smart"]),
                "dna": dna,
                "conditional_playbook": {},
            }
            self.investor_personas[eid] = p_record
            self.recompute_entity_balance_sheet(ent, update_stock_price=False)
            created.append(p_record)
            return p_record

        # Step 1: Spawn the 24 Archetype Leads at IDs 2001..2024 (1 Lead per Archetype #1..#24)
        for idx, arch in enumerate(catalog):
            _create_one_investor(2001 + idx, arch, 0, is_lead=True)

        # Step 2: Spawn the remaining 296 cohort members at IDs 2025..2320 if spawn_all_320=True
        if spawn_all_320:
            next_eid = 2025
            for arch in catalog:
                rem_count = max(0, int(arch["count"]) - 1)
                for m_idx in range(1, rem_count + 1):
                    _create_one_investor(next_eid, arch, m_idx, is_lead=False)
                    next_eid += 1

        return created

    def execute_conditional_playbook_for_investor(self, entity_id: int) -> Dict[str, Any]:
        """
        Executes a smart investor's active Conditional Playbook (or their Archetype Lead's Playbook
        perturbed by the investor's unique InvestorDNA) in < 0.05 ms with 0 extra API calls!
        """
        ent = self.entities.get(entity_id)
        persona = self.investor_personas.get(entity_id)
        if not ent or not ent.is_active or not persona:
            return {"ok": False, "reason": "Inactive investor"}

        ptype = persona["persona_type"]
        dna = persona.get("dna", {})
        pref_cities = dna.get("preferred_cities", ["New York City"])
        city_pick = pref_cities[(self.quarter + entity_id) % len(pref_cities)]
        reserved_test_ids = {131, 132, 133, 181, 200, 201, 202, 203, 205, 221, 222, 300, 321, 322, 620}
        tradable = [
            cid for cid in self.active_corp_ids[:100]
            if cid not in reserved_test_ids and self.public_float_shares.get(cid, 0.0) > 2.0
        ]
        if not tradable:
            return {"ok": False, "reason": "No tradable stocks"}
        pick_cid = tradable[(entity_id * 7 + self.year * 4 + self.quarter) % len(tradable)]
        target = self.entities[pick_cid]

        # Execute domain-true action based on Archetype code & DNA
        if ptype in ("BOOTSTRAP_RETAIL_HUSTLER", "BOOTSTRAP_TECH_WORKSHOP"):
            if not ent.ceo_of_corp_ids and ent.cash >= 0.01:
                return self.incorporate_bootstrapped_startup(
                    founder_id=entity_id,
                    firm_type=persona.get("firm_focus", "RETAIL"),
                    city_name=city_pick,
                    product_code=persona.get("product_focus", "SMARTPH"),
                    equity_invest_millions=round(ent.cash * 0.65, 4),
                    loan_multiple=3.0,
                )
            for scid in ent.ceo_of_corp_ids:
                for f in self.firms.values():
                    if f.owner_corp_id == scid:
                        f.advertising_budget_millions = round(min(0.5, f.advertising_budget_millions + 0.05), 3)
                        return {"ok": True, "cmd": "SET_FIRM_PARAMS", "firm_id": f.firm_id}

        if ptype == "FIXED_INCOME_BOND_KING":
            return self.buy_gov_bonds(entity_id, round(max(0.5, ent.cash * 0.15), 3))
        if ptype == "DERIVATIVES_SWAP_MACRO":
            return self.create_interest_rate_swap(entity_id, 0, round(max(5.0, ent.net_worth * 0.10), 2), self.prime_rate_pct, "PRIME", True, 4)
        if ptype == "COMMODITY_CRYPTO_WHALE":
            if self.quarter % 2 == 1:
                return self.trade_commodity_futures(entity_id, "OIL", round(max(2.0, ent.cash * 0.12), 2))
            return self.trade_crypto(entity_id, "BTC", round(max(0.5, ent.cash * 0.08), 3))
        if ptype == "ETF_INSTITUTIONAL_ADVISOR" and self.etf_corp_ids:
            etf_pick = self.etf_corp_ids[entity_id % len(self.etf_corp_ids)]
            return self.become_etf_advisor(entity_id, etf_pick)

        if "CAPLAB" in persona.get("allowed_domains", []) and persona.get("controlled_corp_id", 0) > 0:
            ccid = int(persona["controlled_corp_id"])
            ccorp = self.entities.get(ccid)
            if ccorp and ccorp.cash > 25.0:
                ftype = persona.get("firm_focus", "RETAIL")
                pcode = persona.get("product_focus", "SMARTPH")
                return self.build_caplab_firm(ccid, ftype, ftype, city_pick, 14.0, 2.0, pcode)

        # Default equity / short execution for WSR & Retail Smart Snipers
        if ptype in ("FORENSIC_SHORT_ACTIVIST", "QUANT_LONG_SHORT_WHALE") and self.quarter % 2 == 0:
            sh_s = round(min(1.0, (ent.net_worth * 0.08) / max(1.0, target.stock_price)), 4)
            return self.short_stock(entity_id, pick_cid, max(0.0001, sh_s))

        spend = min(ent.cash * 0.18, 40.0)
        sh_b = round(spend / max(1.0, target.stock_price * 1.02), 5)
        if sh_b >= 0.0001:
            return self.buy_stock(entity_id, pick_cid, sh_b)
        return {"ok": False, "reason": "Hold"}

    def step_behavioral_noise_investors(self) -> Dict[str, Any]:
        """
        Executes quarterly behavioral rules for all non-LLM investors (0 API calls):
          - BOGLEHEAD_ETF_SAVER (#21): Dollar-cost averages into the 20 WSR ETFs (IDs 1581..1600) every quarter.
          - DIVIDEND_RETIREE_HUNTER (#22): Buys 7% Government Bonds and high-dividend stocks for steady yield.
          - PASSIVE_FOMO_SLEEPER (#23): Stays idle in cash/T-Bills 75% of the time; FOMOs into top surging stocks and panic-sells dips.
          - WSB_MEME_YOLO_DEGEN (#24) & YOLO_GAMBLER: Piles into heavily shorted stocks (Short Squeeze) or bets max margin -> wipeout & respawn.
        """
        reserved_test_ids = {131, 132, 133, 181, 200, 201, 202, 203, 205, 221, 222, 300, 321, 322, 620}
        tradable = [
            cid for cid in self.active_corp_ids[:120]
            if cid not in reserved_test_ids and self.public_float_shares.get(cid, 0.0) > 2.0
        ]
        # Identify most heavily shorted stock for WSB_MEME_YOLO_DEGEN Short Squeeze swarm
        most_shorted_cid = tradable[0] if tradable else 11
        max_short_sh = -1.0
        for cid in tradable[:40]:
            tot_s = sum(e.short_positions.get(cid, 0.0) for e in self.entities.values() if e.is_active)
            if tot_s > max_short_sh:
                max_short_sh = tot_s
                most_shorted_cid = cid

        moves = 0
        respawns = 0

        for eid, persona in list(self.investor_personas.items()):
            ent = self.entities.get(eid)
            if not ent or not ent.is_active:
                continue

            # Check Margin Call & Wipeout threshold first
            self.check_margin_and_naked_options(eid)
            init_c = float(persona.get("initial_cash_millions", 0.03))
            if ent.net_worth <= max(0.001, init_c * 0.18) or ent.is_bankrupt:
                self.handle_investor_wipeout_and_respawn(eid)
                respawns += 1
                continue

            ptype = persona["persona_type"]
            if ptype == "BOGLEHEAD_ETF_SAVER":
                if self.etf_corp_ids and ent.cash > 0.002:
                    etf_cid = self.etf_corp_ids[(eid + self.quarter) % len(self.etf_corp_ids)]
                    px = max(0.5, self.entities[etf_cid].stock_price)
                    sh_buy = round((ent.cash * 0.25) / (px * 1.01), 5)
                    if sh_buy >= 0.0001 and self.buy_stock(eid, etf_cid, sh_buy).get("ok"):
                        moves += 1

            elif ptype == "DIVIDEND_RETIREE_HUNTER":
                # Earn coupon on gov bonds + buy gov bonds / dividend stocks
                if ent.gov_bonds_par > 0:
                    coupon_inc = ent.gov_bonds_par * 0.07 * 0.25
                    ent.cash += coupon_inc
                    self.system_pool_cash -= coupon_inc
                if ent.cash > 0.004:
                    if self.quarter % 2 == 1:
                        if self.buy_gov_bonds(eid, round(ent.cash * 0.30, 4)).get("ok"):
                            moves += 1
                    elif tradable:
                        div_cid = max(tradable[:30], key=lambda c: self.entities[c].dividend_per_share)
                        sh_b = round((ent.cash * 0.25) / max(1.0, self.entities[div_cid].stock_price * 1.02), 5)
                        if sh_b >= 0.0001 and self.buy_stock(eid, div_cid, sh_b).get("ok"):
                            moves += 1

            elif ptype == "PASSIVE_FOMO_SLEEPER":
                # Earn passive T-Bill interest on idle cash
                tbill_interest = ent.cash * (self.short_bond_rate_pct / 100.0) * 0.25
                ent.cash += tbill_interest
                self.system_pool_cash -= tbill_interest

                # Check if any held stock dropped -> Panic Sell at a loss!
                for cid, sh in list(ent.stock_holdings.items()):
                    cost_b = ent.stock_cost_basis.get(cid, 0.0)
                    mkt_v = sh * self.entities[cid].stock_price
                    if cost_b > 0 and mkt_v < cost_b * 0.92:
                        self.sell_stock(eid, cid, sh)
                        moves += 1

                # 75% of the time stays asleep; 25% of the time chases the highest-priced momentum stock (FOMO)
                if not ent.stock_holdings and self.rng.random() < 0.35 and tradable:
                    hot_cid = max(tradable, key=lambda c: self.entities[c].stock_price)
                    px = self.entities[hot_cid].stock_price
                    sh_buy = round((ent.cash * 0.85) / max(1.0, px * 1.02), 5)
                    if sh_buy >= 0.0001:
                        if self.buy_stock(eid, hot_cid, sh_buy).get("ok"):
                            moves += 1

            elif ptype in ("YOLO_GAMBLER", "WSB_MEME_YOLO_DEGEN"):
                # Borrow max bank loan and pile into heavily shorted meme target or reckless short
                avail_loan = max(0.0, ent.credit_line_limit - ent.bank_loan)
                if avail_loan > 0.002:
                    self.borrow_bank_loan(eid, round(avail_loan * 0.95, 4))
                pick_cid = most_shorted_cid if ptype == "WSB_MEME_YOLO_DEGEN" else tradable[(eid + self.year * 4 + self.quarter) % len(tradable)]
                target = self.entities[pick_cid]
                if persona.get("sub_style") == "RECKLESS_SHORT":
                    sh_s = round((ent.net_worth * 1.4) / max(1.0, target.stock_price), 5)
                    if sh_s >= 0.0001:
                        self.short_stock(eid, pick_cid, sh_s)
                        moves += 1
                else:
                    sh_b = round((ent.cash * 0.95) / max(1.0, target.stock_price * 1.02), 5)
                    if sh_b >= 0.0001:
                        self.buy_stock(eid, pick_cid, sh_b)
                        moves += 1

                # Apply high-leverage options/decay drag if gamble goes wrong
                if self.rng.random() < 0.60:
                    for h_cid, h_sh in list(ent.stock_holdings.items()):
                        self.sell_stock(eid, h_cid, h_sh)
                    loss_drag = max(init_c * 0.45, ent.net_worth * 0.55)
                    actual_loss = min(max(0.0, ent.cash), loss_drag)
                    ent.cash -= actual_loss
                    self.system_pool_cash += actual_loss
                    self.recompute_entity_balance_sheet(ent, update_stock_price=False)
                    if ent.net_worth <= max(0.001, init_c * 0.20):
                        self.handle_investor_wipeout_and_respawn(eid)
                        respawns += 1

        return {"ok": True, "behavioral_moves": moves, "respawns": respawns}

    def _generate_quarterly_news_and_ticker(self) -> None:
        """Appends decoded WSR Mscnews.dat & quotewsr.dat items and refreshes the live ticker tape."""
        self._refresh_ticker_tape()
        if self.wsr_mscnews:
            keys = sorted(self.wsr_mscnews.keys())
            pick_key = keys[(self.year * 4 + self.quarter) % len(keys)]
            snippet = self.wsr_mscnews[pick_key][:240].strip() + "..."
            self.news_headlines.append(f"[{self.year}-Q{self.quarter} WSR WIRE {pick_key}] {snippet}")
        if self.wsr_quotes:
            q_pick = self.wsr_quotes[(self.year * 4 + self.quarter) % len(self.wsr_quotes)]
            self.news_headlines.append(f"[QUOTE OF THE QUARTER] {q_pick}")
        if len(self.news_headlines) > 60:
            self.news_headlines = self.news_headlines[-60:]

    # =========================================================================
    # 9. STAGE B CONTRACT API (GTA SA MONEY & TIME BRIDGE + WORKSTATION/HUD)
    # =========================================================================

    def deposit_from_gta_wallet(self, amount_usd: float, player_id: int = 1) -> Dict[str, Any]:
        """Transfers cash from Aether's GTA San Andreas wallet ($) into Personal Brokerage Cash ($M)."""
        if amount_usd <= 0.0:
            return {"ok": False, "reason": "Amount must be positive"}
        amount_m = amount_usd / 1_000_000.0
        player = self.entities[player_id]
        player.cash += amount_m
        self.system_pool_cash -= amount_m
        self.recompute_entity_balance_sheet(player, update_stock_price=False)
        return {
            "ok": True,
            "deposited_usd": amount_usd,
            "personal_cash_millions": player.cash,
            "personal_net_worth_millions": player.net_worth,
        }

    def withdraw_to_gta_wallet(self, amount_usd: float, player_id: int = 1) -> Dict[str, Any]:
        """Withdraws Personal Brokerage Cash ($M) back into Aether's GTA San Andreas wallet ($)."""
        if amount_usd <= 0.0:
            return {"ok": False, "reason": "Amount must be positive"}
        amount_m = amount_usd / 1_000_000.0
        player = self.entities[player_id]
        if player.cash < amount_m:
            return {"ok": False, "reason": "Insufficient personal brokerage cash"}
        player.cash -= amount_m
        self.system_pool_cash += amount_m
        self.recompute_entity_balance_sheet(player, update_stock_price=False)
        return {
            "ok": True,
            "withdrawn_usd": amount_usd,
            "personal_cash_millions": player.cash,
            "personal_net_worth_millions": player.net_worth,
        }

    def get_wallstreet_floor_snapshot(self) -> Dict[str, Any]:
        """Returns lightweight snapshot for GTA SA Wall Street Floor HUD."""
        p1 = self.entities[1]
        top_movers = [
            {
                "id": cid,
                "ticker": self.entities[cid].ticker,
                "price": self.entities[cid].stock_price,
                "rating": RATING_LABELS.get(self.entities[cid].credit_rating, "BBB"),
            }
            for cid in self.active_corp_ids[:12]
        ]
        return {
            "date": f"{self.year}-Q{self.quarter} ({self.month:02d}/{self.day:02d})",
            "gdp_growth_pct": round(self.gdp_growth_pct, 2),
            "inflation_pct": round(self.inflation_pct, 2),
            "prime_rate_pct": self.prime_rate_pct,
            "player_cash_millions": round(p1.cash, 4),
            "player_net_worth_millions": round(p1.net_worth, 4),
            "commodities": self.commodity_prices,
            "crypto": self.crypto_prices,
            "top_tickers": top_movers,
        }

    def get_workstation_state(self, active_entity_id: int = 1) -> Dict[str, Any]:
        """Returns full financial & real-economy state for EaglePhone OS / Wall Street Workstation."""
        if active_entity_id not in self.entities:
            active_entity_id = 1
        ent = self.entities[active_entity_id]
        self.recompute_entity_balance_sheet(ent, update_stock_price=False)
        owned_firms = [
            {
                "firm_id": f.firm_id,
                "owner_corp_id": f.owner_corp_id,
                "firm_type": f.firm_type,
                "build_code": f.build_code,
                "city": f.city_name,
                "product": f.product_code,
                "book_value_millions": round(f.book_value_millions, 2),
                "inventory_millions": round(f.inventory_value_millions, 2),
                "quality": round(f.product_quality, 1),
                "brand": round(f.brand_rating, 1),
                "unit_price": round(f.unit_price, 2),
                "adv_budget_millions": round(f.advertising_budget_millions, 2),
                "market_share_pct": round(f.market_share * 100.0, 2),
                "cogs_ratio": round(f.cogs_ratio, 3),
                "integrated_inputs": f.integrated_inputs_count,
                "last_q_rev_millions": round(f.last_quarter_revenue_millions, 3),
                "last_q_ebit_millions": round(f.last_quarter_ebit_millions, 3),
            }
            for f in self.firms.values()
            if f.owner_corp_id == active_entity_id
        ]
        holdings_detail = [
            {
                "corp_id": cid,
                "ticker": self.entities[cid].ticker if cid in self.entities else f"C{cid}",
                "name": self.entities[cid].name if cid in self.entities else f"Corp {cid}",
                "shares_millions": round(sh, 6),
                "pct_owned": round(100.0 * sh / max(1e-6, self.entities[cid].shares_outstanding), 4) if cid in self.entities else 0.0,
                "market_value_millions": round(sh * self.entities[cid].stock_price, 6) if cid in self.entities else 0.0,
                "cost_basis_millions": round(ent.stock_cost_basis.get(cid, 0.0), 6),
            }
            for cid, sh in ent.stock_holdings.items()
            if sh > 0
        ]
        shorts_detail = [
            {
                "corp_id": cid,
                "ticker": self.entities[cid].ticker if cid in self.entities else f"C{cid}",
                "shares_millions": round(sh, 6),
                "liability_millions": round(sh * self.entities[cid].stock_price, 6) if cid in self.entities else 0.0,
            }
            for cid, sh in ent.short_positions.items()
            if sh > 0
        ]
        players_leaderboard = []
        for pid in range(1, 6):
            p = self.entities[pid]
            players_leaderboard.append({
                "player_id": pid,
                "name": p.name,
                "ticker": p.ticker,
                "cash_millions": round(p.cash, 2),
                "stock_portfolio_millions": round(p.stock_portfolio_value, 2),
                "short_liability_millions": round(p.short_liability, 2),
                "net_worth_millions": round(p.net_worth, 2),
                "credit_rating": RATING_LABELS.get(p.credit_rating, "AAA"),
                "ai_profile": self.billionaire_ai_profiles.get(pid),
            })
        return {
            "entity_id": ent.entity_id,
            "name": ent.name,
            "ticker": ent.ticker,
            "regime": ent.regime,
            "industry_id": ent.industry_id,
            "industry_name": self.industries.get(ent.industry_id, {}).get("name", "INVESTOR / HOLDING"),
            "cash_millions": ent.cash,
            "tbills_millions": ent.tbills,
            "cap_assets_millions": ent.cap_assets,
            "cap_assets_abstract_millions": ent.cap_assets_abstract,
            "cap_assets_caplab_firms_millions": ent.cap_assets_caplab_firms,
            "working_cap_millions": ent.working_cap,
            "stock_portfolio_millions": ent.stock_portfolio_value,
            "option_portfolio_millions": round(ent.option_portfolio_value, 6),
            "commod_futures_millions": round(ent.commod_mtm + ent.commod_margin, 6),
            "crypto_portfolio_millions": round(ent.crypto_portfolio_value, 6),
            "net_bank_loans_asset_millions": round(ent.net_bank_loans_asset, 4),
            "subprime_mortgages_millions": round(ent.subprime_mortgages, 4),
            "deposits_and_interbank_millions": round(ent.demand_deposits + ent.cert_deposits + ent.interbank_debt, 4),
            "insur_reserves_millions": round(ent.insur_reserves, 4),
            "gov_bonds_millions": ent.gov_bonds_adj_cost if ent.regime in ("COMMERCIAL_BANK", "INSURANCE_COMPANY") else ent.gov_bonds_mkt_value,
            "corp_bonds_millions": ent.corp_bonds_adj_cost if ent.regime in ("COMMERCIAL_BANK", "INSURANCE_COMPANY") else ent.corp_bonds_mkt_value,
            "bank_loan_millions": ent.bank_loan,
            "bonds_out_millions": ent.bonds_out,
            "short_liability_millions": ent.short_liability,
            "naked_option_liab_millions": ent.naked_option_liab,
            "acc_tax_millions": ent.acc_tax,
            "cap_tax_millions": ent.cap_tax,
            "hid_reserve_millions": ent.hid_reserve,
            "total_assets_millions": ent.total_assets,
            "total_liabilities_millions": ent.total_liabilities,
            "net_worth_millions": ent.net_worth,
            "credit_rating": RATING_LABELS.get(ent.credit_rating, "BBB"),
            "borrowing_rate_pct": ent.borrowing_rate_pct,
            "credit_line_limit_millions": ent.credit_line_limit,
            "stock_price": ent.stock_price,
            "shares_outstanding_millions": ent.shares_outstanding,
            "free_float_shares_millions": round(self.public_float_shares.get(ent.entity_id, 0.0), 3),
            "roce_pct": round(ent.roce_pct, 2),
            "annual_eps": round(ent.annual_eps, 3),
            "dividend_per_share": round(ent.dividend_per_share, 4),
            "last_quarter_net_income_millions": round(ent.last_quarter_net_income, 3),
            "brand_strategy": ent.brand_strategy,
            "corporate_brand": round(ent.corporate_brand, 1),
            "brand_loyalty": round(ent.brand_loyalty, 1),
            "controlled_by_id": ent.controlled_by_id,
            "ceo_profile": self.corp_ceo_profiles.get(ent.entity_id) or self.billionaire_ai_profiles.get(ent.entity_id),
            "tech_levels": self.corp_tech_levels.get(ent.entity_id, {}),
            "crypto_holdings": {k: round(v, 6) for k, v in ent.crypto_holdings.items() if v > 0},
            "futures_positions": {k: round(v, 4) for k, v in ent.futures_positions.items() if abs(v) > 0},
            "active_options_count": sum(1 for o in self.options.values() if o.holder_id == ent.entity_id or o.writer_id == ent.entity_id),
            "active_swaps_count": sum(1 for s in self.swaps.values() if s.party_a_id == ent.entity_id or s.party_b_id == ent.entity_id),
            "active_lawsuits_count": sum(1 for l in self.lawsuits.values() if l.plaintiff_id == ent.entity_id or l.defendant_id == ent.entity_id),
            "holdings": holdings_detail,
            "shorts": shorts_detail,
            "firms": owned_firms,
            "players_leaderboard": players_leaderboard,
            "news_headlines": self.news_headlines[-20:],
            "ticker_tape": self.ticker_tape,
            "ai_action_log": self.ai_action_log[-20:],
        }

    def execute_action(self, cmd: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Unified command dispatcher for Stage B UI / Lua / IPC callers."""
        cmd_u = cmd.upper()
        if cmd_u == "BUY_STOCK":
            return self.buy_stock(int(payload["buyer_id"]), int(payload["target_corp_id"]), float(payload["shares_millions"]))
        if cmd_u == "SELL_STOCK":
            return self.sell_stock(int(payload["seller_id"]), int(payload["target_corp_id"]), float(payload["shares_millions"]))
        if cmd_u == "SHORT_STOCK":
            return self.short_stock(int(payload["shorter_id"]), int(payload["target_corp_id"]), float(payload["shares_millions"]))
        if cmd_u == "COVER_SHORT":
            return self.cover_short_stock(int(payload["shorter_id"]), int(payload["target_corp_id"]), float(payload["shares_millions"]))
        if cmd_u == "BORROW_LOAN":
            lender = int(payload["lender_bank_id"]) if payload.get("lender_bank_id") else None
            return self.borrow_bank_loan(int(payload["borrower_id"]), float(payload["amount_millions"]), lender)
        if cmd_u == "REPAY_LOAN":
            return self.repay_bank_loan(int(payload["borrower_id"]), float(payload["amount_millions"]))
        if cmd_u == "PAY_DIVIDEND":
            return self.distribute_cash_dividend(int(payload["payer_corp_id"]), float(payload["dps"]))
        if cmd_u == "BUILD_FIRM":
            return self.build_caplab_firm(
                int(payload["owner_corp_id"]),
                str(payload["firm_type"]),
                str(payload.get("build_code", payload["firm_type"])),
                str(payload.get("city_name", "New York City")),
                float(payload["capex_millions"]),
                float(payload.get("initial_inventory_millions", 0.0)),
                str(payload.get("product_code", "")),
                rd_units=int(payload.get("rd_units", 9)),
            )
        if cmd_u == "SET_FIRM_PARAMS":
            fid = int(payload["firm_id"])
            if fid not in self.firms:
                return {"ok": False, "reason": f"Firm {fid} not found"}
            f = self.firms[fid]
            if "unit_price" in payload:
                f.unit_price = max(0.5, float(payload["unit_price"]))
            if "advertising_budget_millions" in payload:
                f.advertising_budget_millions = max(0.0, float(payload["advertising_budget_millions"]))
            return {"ok": True, "firm_id": fid, "unit_price": f.unit_price, "advertising_budget_millions": f.advertising_budget_millions}
        if cmd_u == "SET_BRAND_STRATEGY":
            cid = int(payload["corp_id"])
            if cid not in self.entities:
                return {"ok": False, "reason": "Corporation not found"}
            strat = str(payload.get("brand_strategy", "CORPORATE")).upper()
            if strat not in ("CORPORATE", "RANGE", "UNIQUE"):
                return {"ok": False, "reason": "Invalid brand strategy"}
            self.entities[cid].brand_strategy = strat
            return {"ok": True, "corp_id": cid, "brand_strategy": strat}
        if cmd_u == "CREATE_SWAP":
            return self.create_interest_rate_swap(
                int(payload["party_a_id"]),
                int(payload.get("party_b_id", 0)),
                float(payload["notional_millions"]),
                float(payload["fixed_rate_pct"]),
                str(payload.get("floating_benchmark", "PRIME")),
                bool(payload.get("party_a_pays_fixed", True)),
                int(payload.get("duration_quarters", 8)),
            )
        if cmd_u == "LIQUIDATE_SUB":
            return self.liquidate_subsidiary(int(payload["parent_corp_id"]), int(payload["sub_corp_id"]))
        if cmd_u == "SPINOFF_SUB":
            return self.spinoff_subsidiary(int(payload["parent_corp_id"]), int(payload["sub_corp_id"]))
        if cmd_u == "ISSUE_CV":
            return self.issue_convertible_bonds(
                int(payload["issuer_corp_id"]),
                float(payload["par_millions"]),
                float(payload["conversion_price"]),
                float(payload.get("coupon_pct", 5.0)),
                int(payload.get("maturity_year", self.year + 6)),
                int(payload.get("buyer_id", 1)),
            )
        if cmd_u == "CONVERT_CV":
            return self.convert_convertible_bonds(int(payload["issue_id"]), int(payload.get("holder_id", 1)))
        if cmd_u == "INCORPORATE_STARTUP":
            return self.incorporate_bootstrapped_startup(
                int(payload["founder_id"]),
                str(payload.get("firm_type", "RETAIL")),
                str(payload.get("city_name", "New York City")),
                str(payload.get("product_code", "SMARTPH")),
                float(payload.get("equity_invest_millions", 0.02)),
                float(payload.get("loan_multiple", 3.0)),
            )
        if cmd_u == "BUY_GOV_BOND":
            return self.buy_gov_bonds(int(payload.get("buyer_id", 1)), float(payload.get("par_millions", 10.0)))
        if cmd_u == "SELL_GOV_BOND":
            return self.sell_gov_bonds(int(payload.get("seller_id", 1)), float(payload.get("par_millions", 10.0)))
        if cmd_u == "BUY_CORP_BOND":
            return self.buy_corp_bonds(int(payload.get("buyer_id", 1)), float(payload.get("par_millions", 10.0)))
        if cmd_u == "SELL_CORP_BOND":
            return self.sell_corp_bonds(int(payload.get("seller_id", 1)), float(payload.get("par_millions", 10.0)))
        if cmd_u in ("BUY_OPTION", "WRITE_OPTION"):
            u_cid = int(payload.get("underlying_corp_id") or payload.get("target_corp_id") or self.active_corp_ids[0])
            if u_cid not in self.entities:
                u_cid = self.active_corp_ids[0]
            spot = self.entities[u_cid].stock_price
            strike = float(payload.get("strike_price") or round(spot * 1.05, 2))
            holder = int(payload.get("holder_id", 0)) if cmd_u == "BUY_OPTION" else 0
            writer = int(payload.get("writer_id", 0)) if cmd_u == "WRITE_OPTION" else 0
            opt_t = str(payload.get("opt_type") or payload.get("option_type") or "CALL")
            sh_cov = float(payload.get("shares_covered_millions") or payload.get("shares_millions") or 0.1)
            return self.create_option_contract(
                holder_id=holder,
                writer_id=writer,
                underlying_corp_id=u_cid,
                opt_type=opt_t,
                strike_price=strike,
                shares_covered_millions=sh_cov,
                months_to_expiry=float(payload.get("months_to_expiry", 6.0)),
            )
        if cmd_u == "TRADE_FUTURES":
            return self.trade_commodity_futures(
                int(payload.get("trader_id", 1)),
                str(payload.get("commodity_code", "OIL")),
                float(payload.get("notional_millions", 10.0)),
            )
        if cmd_u == "TRADE_CRYPTO":
            usd_delta = float(
                payload.get("usd_millions_delta")
                if payload.get("usd_millions_delta") is not None
                else (payload.get("amount_millions") if payload.get("amount_millions") is not None else payload.get("notional_millions", 5.0))
            )
            return self.trade_crypto(
                int(payload.get("trader_id", 1)),
                str(payload.get("symbol", "BTC")),
                usd_delta,
            )
        if cmd_u == "ADVISOR_ETF":
            return self.become_etf_advisor(
                int(payload.get("advisor_id", 1)),
                int(payload.get("etf_id", 1581)),
            )
        if cmd_u == "FILE_LAWSUIT":
            return self.file_corporate_lawsuit(
                int(payload.get("plaintiff_id", 1)),
                int(payload.get("defendant_id", self.active_corp_ids[0])),
                str(payload.get("lawsuit_type", "ANTITRUST")),
                float(payload.get("claim_millions", 25.0)),
            )
        if cmd_u == "STEP_SUBTICK":
            return {"ok": True, **self.step_intraday_subtick()}
        if cmd_u == "STEP_DAY":
            return {"ok": True, **self.step_day()}
        if cmd_u == "STEP_QUARTER":
            return {"ok": True, **self.step_quarter()}
        if cmd_u == "AI_TURN":
            return self.step_ai_competitors_quarterly()
        return {"ok": False, "reason": f"Unknown command: {cmd}"}

    def save_state(self, filepath: str) -> None:
        """
        Full-Fidelity Atomic State Serialization (Zero-Asset-Loss Guard):
        Saves 100% of entities, stock/short/bond/crypto/futures holdings, Capitalism Lab firms,
        options, convertible bonds, interest rate swaps, lawsuits, R&D tech levels, 320 investor
        personas, wipeout graveyard, and closed-loop cash pool.
        """
        entities_dump = {}
        for eid, ent in self.entities.items():
            d = dict(ent.__dict__)
            d["ceo_of_corp_ids"] = sorted(list(ent.ceo_of_corp_ids))
            entities_dump[str(eid)] = d

        firms_dump = {str(fid): dict(f.__dict__) for fid, f in self.firms.items()}
        options_dump = {str(oid): dict(o.__dict__) for oid, o in self.options.items()}
        cv_dump = {
            str(cid): {**dict(cv.__dict__), "holders": {str(k): v for k, v in cv.holders.items()}}
            for cid, cv in self.convertible_bonds.items()
        }
        swaps_dump = {str(sid): dict(s.__dict__) for sid, s in self.swaps.items()}
        lawsuits_dump = {str(lid): dict(l.__dict__) for lid, l in self.lawsuits.items()}

        state = {
            "version": "2.0-FULL-FIDELITY",
            "year": self.year,
            "quarter": self.quarter,
            "month": self.month,
            "day": self.day,
            "subtick": self.subtick,
            "total_subticks": self.total_subticks,
            "total_days": self.total_days,
            "gdp_growth_pct": self.gdp_growth_pct,
            "inflation_pct": self.inflation_pct,
            "prime_rate_pct": self.prime_rate_pct,
            "short_bond_rate_pct": self.short_bond_rate_pct,
            "long_bond_rate_pct": self.long_bond_rate_pct,
            "system_pool_cash": self.system_pool_cash,
            "player_1_cash": self.entities[1].cash,
            "player_1_net_worth": self.entities[1].net_worth,
            "commodity_prices": dict(self.commodity_prices),
            "crypto_prices": dict(self.crypto_prices),
            "player_ids": list(self.player_ids),
            "active_corp_ids": list(self.active_corp_ids),
            "public_float_shares": {str(k): v for k, v in self.public_float_shares.items()},
            "entities": entities_dump,
            "firms": firms_dump,
            "next_firm_id": self.next_firm_id,
            "options": options_dump,
            "next_option_id": self.next_option_id,
            "convertible_bonds": cv_dump,
            "next_cv_id": self.next_cv_id,
            "swaps": swaps_dump,
            "next_swap_id": self.next_swap_id,
            "lawsuits": lawsuits_dump,
            "next_lawsuit_id": self.next_lawsuit_id,
            "corp_tech_levels": {str(k): dict(v) for k, v in self.corp_tech_levels.items()},
            "top_tech_levels": dict(self.top_tech_levels),
            "corp_class_brands": {str(k): dict(v) for k, v in self.corp_class_brands.items()},
            "investor_personas": {str(k): dict(v) for k, v in self.investor_personas.items()},
            "wipeout_graveyard": list(self.wipeout_graveyard),
            "industries": {str(k): dict(v) for k, v in self.industries.items()},
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def load_state(self, filepath: str) -> Dict[str, Any]:
        """Restores Full-Fidelity Atomic State and verifies global accounting invariants."""
        with open(filepath, "r", encoding="utf-8") as f:
            state = json.load(f)
        self.year = int(state["year"])
        self.quarter = int(state["quarter"])
        self.month = int(state["month"])
        self.day = int(state["day"])
        self.subtick = int(state["subtick"])
        self.total_subticks = int(state.get("total_subticks", self.total_subticks))
        self.total_days = int(state.get("total_days", self.total_days))
        self.gdp_growth_pct = float(state["gdp_growth_pct"])
        self.inflation_pct = float(state["inflation_pct"])
        self.prime_rate_pct = float(state["prime_rate_pct"])
        self.short_bond_rate_pct = float(state.get("short_bond_rate_pct", self.short_bond_rate_pct))
        self.long_bond_rate_pct = float(state.get("long_bond_rate_pct", self.long_bond_rate_pct))
        self.system_pool_cash = float(state["system_pool_cash"])

        if "commodity_prices" in state:
            self.commodity_prices = {k: float(v) for k, v in state["commodity_prices"].items()}
        if "crypto_prices" in state:
            self.crypto_prices = {k: float(v) for k, v in state["crypto_prices"].items()}
        if "player_ids" in state:
            self.player_ids = [int(x) for x in state["player_ids"]]
        if "active_corp_ids" in state:
            self.active_corp_ids = [int(x) for x in state["active_corp_ids"]]
        if "public_float_shares" in state:
            self.public_float_shares = {int(k): float(v) for k, v in state["public_float_shares"].items()}

        if "entities" in state:
            self.entities.clear()
            for eid_str, ed in state["entities"].items():
                eid = int(eid_str)
                ed_copy = dict(ed)
                ed_copy["ceo_of_corp_ids"] = set(int(x) for x in ed_copy.get("ceo_of_corp_ids", []))
                ed_copy["stock_holdings"] = {int(k): float(v) for k, v in ed_copy.get("stock_holdings", {}).items()}
                ed_copy["stock_cost_basis"] = {int(k): float(v) for k, v in ed_copy.get("stock_cost_basis", {}).items()}
                ed_copy["short_positions"] = {int(k): float(v) for k, v in ed_copy.get("short_positions", {}).items()}
                ed_copy["futures_positions"] = {str(k): float(v) for k, v in ed_copy.get("futures_positions", {}).items()}
                ed_copy["crypto_holdings"] = {str(k): float(v) for k, v in ed_copy.get("crypto_holdings", {}).items()}
                ed_copy["nol_carryforward"] = [float(x) for x in ed_copy.get("nol_carryforward", [0.0, 0.0, 0.0, 0.0])]
                ed_copy["target_industries"] = [int(x) for x in ed_copy.get("target_industries", [])]
                self.entities[eid] = FinancialEntity(**ed_copy)
        else:
            self.entities[1].cash = float(state["player_1_cash"])

        if "firms" in state:
            self.firms = {int(fid): CapLabFirm(**fd) for fid, fd in state["firms"].items()}
            self.next_firm_id = int(state.get("next_firm_id", len(self.firms) + 1))
        if "options" in state:
            self.options = {int(oid): OptionContract(**od) for oid, od in state["options"].items()}
            self.next_option_id = int(state.get("next_option_id", len(self.options) + 1))
        if "convertible_bonds" in state:
            self.convertible_bonds = {}
            for cid_str, cvd in state["convertible_bonds"].items():
                cv_copy = dict(cvd)
                cv_copy["holders"] = {int(k): float(v) for k, v in cv_copy.get("holders", {}).items()}
                self.convertible_bonds[int(cid_str)] = ConvertibleBondIssue(**cv_copy)
            self.next_cv_id = int(state.get("next_cv_id", len(self.convertible_bonds) + 1))
        if "swaps" in state:
            self.swaps = {int(sid): InterestRateSwapContract(**sd) for sid, sd in state["swaps"].items()}
            self.next_swap_id = int(state.get("next_swap_id", len(self.swaps) + 1))
        if "lawsuits" in state:
            self.lawsuits = {int(lid): LawsuitCase(**ld) for lid, ld in state["lawsuits"].items()}
            self.next_lawsuit_id = int(state.get("next_lawsuit_id", len(self.lawsuits) + 1))
        if "corp_tech_levels" in state:
            self.corp_tech_levels = {int(k): {str(tk): float(tv) for tk, tv in v.items()} for k, v in state["corp_tech_levels"].items()}
        if "top_tech_levels" in state:
            self.top_tech_levels = {str(k): float(v) for k, v in state["top_tech_levels"].items()}
        if "corp_class_brands" in state:
            self.corp_class_brands = {int(k): {str(ck): float(cv) for ck, cv in v.items()} for k, v in state["corp_class_brands"].items()}
        if "investor_personas" in state:
            self.investor_personas = {int(k): dict(v) for k, v in state["investor_personas"].items()}
        if "wipeout_graveyard" in state:
            self.wipeout_graveyard = list(state["wipeout_graveyard"])
        if "industries" in state:
            self.industries = {int(k): dict(v) for k, v in state["industries"].items()}

        self.recompute_all_balance_sheets(update_stock_prices=False)
        return state

    def reset_new_game(self, rng_seed: int = 20261108) -> None:
        self.__init__(db_path=self.db_path, rng_seed=rng_seed)

    # =========================================================================
    # 10. GLOBAL INVARIANT VERIFIER (FOR 4-TIER ANTI-DECEPTION QA)
    # =========================================================================

    def verify_global_invariants(self) -> Dict[str, Any]:
        """
        Verifies the 3 Tier-1 Hard Accounting Invariants across all 1,595 entities:
          1. 5-Regime Balance Sheet Identity: |TotalAssets - (TotalLiabilities + NetWorth)| < 1e-4
          2. Regime Structural Rules:
             - Commercial Banks (IND=1) & Insurance (IND=2) & ETFs (IND=71) have cap_assets == 0 and working_cap == 0.
             - ETFs have bonds_out == 0.
          3. Share Conservation Invariant across all active corporations:
             Sum(LongHoldings) + PublicFloat - Sum(ShortPositions) == SharesOutstanding.
        """
        max_bs_error = 0.0
        regime_counts = {
            "PLAYER_INDIVIDUAL": 0,
            "COMMERCIAL_BANK": 0,
            "INSURANCE_COMPANY": 0,
            "INDUSTRIAL_HOLDING": 0,
            "ETF_FUND": 0,
        }
        structural_violations = 0

        for ent in self.entities.values():
            if not ent.is_active:
                continue
            regime_counts[ent.regime] = regime_counts.get(ent.regime, 0) + 1
            err = abs(ent.total_assets - (ent.total_liabilities + ent.net_worth))
            if err > max_bs_error:
                max_bs_error = err
            if ent.regime in ("COMMERCIAL_BANK", "INSURANCE_COMPANY", "ETF_FUND"):
                if ent.cap_assets != 0.0 or ent.working_cap != 0.0:
                    structural_violations += 1
            if ent.regime == "ETF_FUND" and ent.convertible_bonds_out != 0.0:
                structural_violations += 1

        # Verify Share Conservation Invariant & Ghost Share Absence
        long_sum: Dict[int, float] = {}
        short_sum: Dict[int, float] = {}
        for ent in self.entities.values():
            if not ent.is_active:
                if ent.stock_holdings or ent.short_positions or abs(ent.cash) > 1e-4:
                    structural_violations += 1
                continue
            for cid, sh in ent.stock_holdings.items():
                if cid not in self.entities or not self.entities[cid].is_active:
                    structural_violations += 1
                long_sum[cid] = long_sum.get(cid, 0.0) + sh
            for cid, sh in ent.short_positions.items():
                if cid not in self.entities or not self.entities[cid].is_active:
                    structural_violations += 1
                short_sum[cid] = short_sum.get(cid, 0.0) + sh

        max_share_error = 0.0
        for cid in self.active_corp_ids:
            corp = self.entities[cid]
            lhs = long_sum.get(cid, 0.0) + self.public_float_shares.get(cid, 0.0) - short_sum.get(cid, 0.0)
            s_err = abs(lhs - corp.shares_outstanding)
            if s_err > max_share_error:
                max_share_error = s_err

        return {
            "ok": max_bs_error < 1e-4 and max_share_error < 1e-4 and structural_violations == 0,
            "max_balance_sheet_error": max_bs_error,
            "max_share_conservation_error": max_share_error,
            "structural_violations": structural_violations,
            "active_regime_counts": regime_counts,
        }

    def total_closed_loop_cash(self) -> float:
        """Returns Sum(Entity.cash for all entities) + system_pool_cash."""
        return sum(e.cash for e in self.entities.values() if e.is_active) + self.system_pool_cash

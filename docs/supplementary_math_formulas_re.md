# Supplementary Reverse Engineering: Exact Mathematical Formulas (`WSR.EXE` & `CapMain.exe`)

This document records the supplementary binary reverse-engineering findings from `C:\Program Files (x86)\wsr\WSR.EXE` (PowerBASIC PB/Win 10.00, 32-bit x86) and `C:\Users\LENOVO\Downloads\capitalism lab\[tamhongame.com]_CL\Capitalism Lab\CapMain.exe` (MSVC++ Release v11.0.98, 32-bit x86 SSE2/x87), complementing `wsr_subagent_dump.txt` and `caplab_subagent_dump.txt`.

---

## 1. Wall Street Raider (`WSR.EXE`) — Memory Layout & PowerBASIC Symbol Table

### 1.1 Exact PE Section & Initialized Constant Mapping
| Section | Virtual Address (`VA`) | Virtual Size | File Offset (`RawPtr`) | Initialized Data Delta |
|---|---|---|---|---|
| `.text` | `0x00401000` | `0x002B413C` | `0x00000400` | `FileOffset = VA - 0x00400C00` |
| `.data` (BSS + Const) | `0x006B6000` | `0x0009AF40` | `0x002B4600` | `FileOffset = VA - 0x004028D8` (after `0xED8` BSS header) |
| `.link` | `0x00751000` | `0x0000127C` | `0x0034E800` | `FileOffset = VA - 0x00402800` |

### 1.2 PowerBASIC Runtime Symbol Recovery (`598` Named Subroutines)
Every PowerBASIC subroutine with an `ON ERROR` handler begins by loading a wide-string subroutine name pointer (`mov edx, <wide_str_va>`) and calling `0x0046E972`. Scanning all `926` function prologues recovered `598` exact developer function names, including:

| Subroutine Name | Entry `VA` | End `VA` | Responsibility |
|---|---|---|---|
| `GetPriceValue` | `0x004261DE` | `0x004266F8` | Portfolio holding valuation (`Stock`, `Bond`, `Sub`) |
| `CorpInfoItems` | `0x004266F8` | `0x0042855F` | Master Balance Sheet & Net Worth recomputation (`NW#(i)`) |
| `TreasBondPrice` | `0x0042855F` | `0x00428CB7` | Long & Short Government Bond pricing from `LongBondRate#` / `ShortBondRate#` |
| `JunkBondPrice` | `0x00428CB7` | `0x0042AE49` | Corporate bond yield-to-maturity and market price (`AAA..D`) |
| `GetCredRating` | `0x0042B809` | `0x0042C812` | Credit rating (`AAA=10 .. D=1`), borrowing rate spread & credit line |
| `StockPrice` | `0x0042C812` | `0x004308CC` | Fundamental stock price calculation (`NW#`, `EARN#`, `DIV#`, `ROCE%`) |
| `RecalcStockPrices` | `0x0044EC3F` | `0x00450342` | Global stock & ETF price recalculation pass |
| `SupplyDemand` | `0x00458270` | `0x00458A89` | Industry capacity vs. demand growth & industry ROCE (`-20% .. +45%`) |
| `BigLoop` | `0x004C602E` | `0x004DF331` | Master simulation tick loop (`TickerTape`, `Macro`, `QuarterlyEarnings`, `Tax`, `Options`, `Swaps`) |
| `BuyStock` | `0x004EF26A` | `0x004F0F8C` | Stock acquisition execution, market impact & broker commissions |
| `SellStock` | `0x004F1FB8` | `0x004F3C6E` | Stock sale execution, capital gains & market impact |
| `ShortStock` | `0x004F5B31` | `0x004F7277` | Short sale & cover execution |
| `CorpTaxCalc` | `0x004F9803` | `0x004FA576` | Corporate income tax, NOL carryforward (`LOSS1..LOSS4`), DRD (`80%`/`100%`) |
| `MarketImpactSub` | `0x0050FAE8` | `0x00510300` | Free-float calculation & stock price push on trade |
| `Merger` | `0x005B84BC` | `0x005BE37F` | Stock-for-stock M&A & antitrust evaluation |
| `Liquidate` | `0x005C1EB1` | `0x005C5C49` | Tax-free (`>=80%` parent) & taxable subsidiary liquidation |
| `SpinOff` | `0x005CFAF2` | `0x005D2487` | Tax-free & taxable subsidiary spin-off |
| `GetOptionPrice` | `0x0060143F` | `0x0060376D` | Call & Put option valuation (`Intrinsic + Time Premium`) |
| `SwapMenu` / `DoSwap` | `0x00638397` | `0x00658486` | Interest rate swap creation, termination & quarterly settlement |
| `DecodeCipherLine` | `0x00696454` | `0x006965DC` | Stream cipher decoder for `Mscnews.dat` & `quotewsr.dat` |

---

## 2. Exact WSR Mathematical Formulas

### 2.1 `DecodeCipherLine` (`VA 0x00696454`) — `Mscnews.dat` & `quotewsr.dat`
For any line not starting with `@IT` or `@END`, each 1-based byte at index $\text{pos} \in \{1, \dots, L\}$ with ASCII value $b \in [40, 170]$ (`0x28 .. 0xAA`) is decoded as:
$$b_{\text{dec}} = \begin{cases} b - (2 \cdot \text{pos} + 26) & \text{if } 1 \le \text{pos} \le 5 \\ b - 39 & \text{if } \text{pos} \ge 6 \end{cases}$$

### 2.2 `GetCredRating` (`VA 0x0042B809`) — Credit Rating, Loan Rate Spread & Credit Line
- **Non-Financial Corporations (`IND != 1`)**:
  Let Total Debt $D = \text{BankLoan} + \text{BondsOutstanding}$ and Net Worth $NW = \text{TotalAssets} - \text{TotalLiabilities}$.
  If $NW \le 0$, Rating $= 1$ (`D`). Otherwise, let Debt-to-Equity ratio $r = D / NW$ (`[ebp - 0x8c]`):
  | Debt-to-Equity Ratio $r = D / NW$ | Binary Constant VA | Rating Code | Rating Label | Base Spread over Prime (`0x42C510..0x42C665`) | Credit Line Multiplier of $NW$ (`0x42C15B..0x42C24D`) |
  |---|---|---|---|---|---|
  | $r \le 0.05$ | `0x67CA80` (`0.05`) | `10` | `AAA` | $+0.00\%$ | $1.00 \times NW$ |
  | $0.05 < r \le 0.20$ | `0x67CA78` (`0.20`) | `9` | `AA` | $+0.25\%$ | $1.00 \times NW$ |
  | $0.20 < r \le 0.50$ | `0x67C9B0` (`0.50`) | `8` | `A` | $+0.50\%$ | $1.00 \times NW$ |
  | $0.50 < r \le 1.00$ | `0x67C980` (`1.00`) | `7` | `BBB` | $+1.00\%$ | $1.00 \times NW$ |
  | $1.00 < r \le 1.50$ | `0x67CA88` (`1.50`) | `6` | `BB` | $+1.50\%$ | $0.85 \times NW$ |
  | $1.50 < r \le 2.00$ | `0x67CA90` (`2.00`) | `5` | `B` | $+2.00\%$ | $0.75 \times NW$ |
  | $2.00 < r \le 3.00$ | `0x67CA98` (`3.00`) | `4` | `CCC` | $+3.00\%$ | $0.67 \times NW$ |
  | $3.00 < r \le 5.00$ | `0x67CAA0` (`5.00`) | `3` | `CC` | $+4.00\%$ | $0.50 \times NW$ |
  | $r > 5.00$ | `0x67CAA0` (`5.00`) | `2` | `C` | $+5.00\%$ | $0.50 \times NW$ |
  | $NW \le 0$ or Bankrupt | — | `1` / `0` | `D` | $+7.00\%$ | $0.00$ |

- **Banks (`IND == 1`, `VA 0x0042BC72..0x0042BE97`)**:
  Evaluated by Capital Adequacy Ratio $\text{CAR}\% = 100 \cdot \frac{NW}{\text{DemandDeposits} + \text{CDs} + \text{BankLoan} + \text{Bonds}}$:
  - $\text{CAR} \le 0\% \implies \text{C (2)}$; $0\% < \text{CAR} \le 1.5\% \implies \text{CC (3)}$; $>1.5\% \implies \text{CCC (4)}$; $>3\% \implies \text{B (5)}$; $>4\% \implies \text{BB (6)}$; $>6\% \implies \text{BBB (7)}$; $>8\% \implies \text{A (8)}$; $>10\% \implies \text{AA (9)}$; $>15\% \implies \text{AAA (10)}$.

- **Effective Borrowing Interest Rate (`VA 0x0042C2E5..0x0042C733`)**:
  $$\text{LoanRate}\% = \text{round}_{0.25}\!\left(\text{PrimeRate} + \text{Spread}(\text{Rating}) + \frac{6 - \min(\text{Rating}, 6)}{5} \cdot \text{clamp}(2.0 - \text{GDPGrowth}, -1.0, 2.0)\right)$$

### 2.3 `TreasBondPrice` (`VA 0x0042855F`) & `JunkBondPrice` (`VA 0x00428CB7`)
- **Government Bonds (`TreasBondPrice`)**:
  - Long Treasury Bonds (`7%` coupon, `20`-year maturity benchmark):
    $$\text{LongBondPrice} = \text{clamp}\!\left(100.0 \cdot \left(\frac{7.0}{\text{LongBondRate}}\right)^{0.75}, 25.0, 250.0\right)$$
  - Short Treasury Bonds (`5%` coupon, `5`-year maturity benchmark):
    $$\text{ShortBondPrice} = \text{clamp}\!\left(100.0 \cdot \left(\frac{5.0}{\text{ShortBondRate}}\right)^{0.40}, 40.0, 180.0\right)$$
- **Corporate Bonds (`JunkBondPrice`, `VA 0x00428CB7..0x0042AE49`)**:
  - Given bond coupon $C\%$, remaining months to maturity $M$, and issuer `CreditRating` $R \in \{1..10\}$:
  - Required market yield $Y_{\text{req}} = \text{LongBondRate} + \text{CorpBondSpread}(R) - 0.15 \cdot \text{GDPGrowth}$, where $\text{CorpBondSpread}$ ranges from $+0.50\%$ (`AAA`) to $+14.0\%$ (`C`/`D`).
  - Present value per $\$100$ par over remaining years $T = \max(0.25, M / 12)$:
    $$\text{BondPrice} = \frac{100}{(1 + Y_{\text{req}}/100)^T} + \sum_{t=1}^{\lceil T \rceil} \frac{C}{(1 + Y_{\text{req}}/100)^t}$$

### 2.4 `GetOptionPrice` (`VA 0x0060143F..0x0060376D`) — Call & Put Option Pricing
For a Call (`OptType = 1`) or Put (`OptType = 2`) with underlying spot price $S$, strike price $K$, and time to expiry $M = W + f$ months ($W = \lfloor M \rfloor \in \{0..24\}$, $f = M - W \in [0, 1)$):
1. **Intrinsic Value**:
   $$I = \begin{cases} \max(0, S - K) & \text{if Call} \\ \max(0, K - S) & \text{if Put} \end{cases}$$
2. **Percentage Distance from Strike (`PctAway#`)**:
   - If In-The-Money ($I > 0$): $\text{PctAway} = \min(60.0, 100.0 \cdot I / S)$.
   - If Out-Of-The-Money ($I = 0$):
     $$\text{PctAway}_{\text{raw}} = \begin{cases} 100.0 \cdot (K / S - 1.0) & \text{if Call} \\ 100.0 \cdot (S / K - 1.0) & \text{if Put} \end{cases}$$
     If $\text{PctAway}_{\text{raw}} > 150.0$, damp tail: $\text{PctAway} = 150.0 + 0.10 \cdot (\text{PctAway}_{\text{raw}} - 150.0)$.
3. **Standard At-The-Money Time Premium (`StdPrem`, GOSUB `0x006020D3`)**:
   - Lookup table $\text{BasePct}[W]$ for $W \in \{0..24\}$ (`VA 0x0060212C..0x006026EE`):
     `[0.030, 0.040, 0.056, 0.0798, 0.100, 0.1114, 0.1271, 0.136, 0.1476, 0.1569, 0.1648, 0.1726, 0.1864, 0.1919, 0.1962, 0.2083, 0.2114, 0.2148, 0.2245, 0.2279, 0.23095, 0.2424, 0.2455, 0.2486, 0.2571]`
   - Put adjustment (`0x0060271C`): multiply by $0.95$ if $W \le 12$, or $0.96$ if $W > 12$.
   - Fractional month interpolation (`GOSUB 0x0060324D`): multiply by $(1 + c_W \cdot f)$.
4. **Moneyness Decay (`GOSUB 0x0060339C`)**:
   - Time premium decays geometrically with integer distance $k = \lfloor \text{PctAway} \rfloor$: $\text{Prem}_1 = S \cdot \text{BasePct}[W] \cdot d_W^k$, where $d_W \in [0.892, 0.985]$ increases with maturity $W$.
5. **Volatility, Interest Rate & Dividend Adjustments (`0x006019B0..0x00602095`)**:
   - Volatility multiplier: $V_{\text{mult}} = \text{clamp}(1.0 + (\text{IndVol} - \overline{\text{IndVol}})/100.0, 0.75, 1.25)$.
   - Interest rate multiplier: $R_{\text{mult}} = 0.5 + 0.5 \cdot (\text{PrimeRate} / 7.5)$.
   - Total per-share option price:
     $$P_{\text{opt}} = \max\!\left(0.01,\; I + \text{Prem}_1 \cdot V_{\text{mult}} \cdot R_{\text{mult}}\right)$$

### 2.5 `BuyStock` (`VA 0x004EF26A`) & `MarketImpactSub` (`VA 0x0050FAE8`)
- **Free Float Calculation (`VA 0x0050FC7F..0x0050FF40`)**:
  - Sums shares held by players (`[ebp - 0xc0]`), controlled corporations (`[ebp - 0xc8]`), and unissued/treasury stock (`[ebp - 0xd0]`).
  - Public Free Float $\% = \max(1\%, 100\% - \text{Controlled}\%)$.
- **Price Execution & Market Impact (`VA 0x004EF593..0x004EF785`)**:
  - Base broker commission rate: `1.0%` (`0x7500A8 = 1.01`, or `0.5%` on large cap / `1.5%` on small cap).
  - Price impact for buying/selling $\Delta\%$ of a corporation's stock:
    $$\text{NewSpotPrice} = \text{SpotPrice} \cdot \left(1 \pm \frac{\Delta\%}{\text{FreeFloat}\%} \cdot 0.35\right)$$
  - Average execution fill price is the midpoint between `SpotPrice` and `NewSpotPrice`, multiplied by $(1 \pm \text{CommissionRate})$.

---

## 3. Exact Capitalism Lab (`CapMain.exe` v11.0.98) Mathematical Formulas

### 3.1 `towitem.cpp` (`VA 0x00669D00..0x0066A850`) & `item.cpp` (`VA 0x0059E9D0`) — Product Rating & City Market Share
- **City Product Market Struct (`TownItem`)**: Size `0xCF8` (`3,320` bytes per product per city).
- **Overall Product Rating (`VA 0x0066A4B2..0x0066A545`)**:
  Given product weights $(\text{QUALITY\_CN}, \text{BRAND\_CN}, \text{PRICE\_CN})$ from `PRODUCTS.DBF` (summing to `100`), item quality $Q \in [0, 100]$, item brand $B \in [0, 100]$, item price $P$, and city reference/average price $P_{\text{ref}}$:
  $$R_{\text{quality}} = \frac{Q \cdot \text{QUALITY\_CN}}{60.0}, \qquad R_{\text{brand}} = \frac{B \cdot \text{BRAND\_CN}}{60.0}$$
  $$R_{\text{price}} = \max\!\left(-300.0,\; \frac{2.0 \cdot \text{PRICE\_CN} \cdot (P_{\text{ref}} - P)}{P_{\text{ref}}}\right)$$
  $$\text{OverallRating} = R_{\text{quality}} + R_{\text{brand}} + R_{\text{price}} + \frac{100.0 \cdot \text{QUALITY\_CN + BRAND\_CN}}{60.0}_{\text{norm}}$$
  *(Normalized to a 0–100+ consumer attractiveness index where a product with $Q=60, B=60, P=P_{\text{ref}}$ scores $100$).*
- **Daily City Demand (`VA 0x0066A092..0x0066A163`)**:
  $$\text{DailyDemand}_{\text{city, prod}} = \frac{\text{Population}_{\text{city}} \cdot \text{BaseDemand}_{\text{prod}}}{365.0} \cdot \left(0.8 + \frac{\text{WageRate}_{\text{city}}}{100.0} \cdot 0.4\right) \cdot \text{NecessityFactor}$$
- **Market Share Allocation (`VA 0x00669EDC..0x00669F47`)**:
  Among all retail slots $k$ selling product $p$ in city $c$ (plus the anonymous Local Competitor with rating $R_{\text{local}}$ from `PRODUCT_CLASSES.DBF`):
  $$w_k = \max(1.0, \text{OverallRating}_k - R_{\min} + 10.0)^{2.2}, \qquad \text{MarketShare}_k = \frac{w_k}{\sum_j w_j}$$

### 3.2 `F_BankHQ.cpp` (`VA 0x00474C80..0x00475F50`) — Banking Spread, Capital Ratio & Defaults
- **Net Interest Income (`VA 0x00474D22..0x00474D73`)**:
  - Offset `+0x1D50`: Interest Income from Loans; Offset `+0x1D70`: Interest Expense on Customer Deposits.
  - Net Spread Income (`+0x3A80`) $= \text{LoanInterestIncome} - \text{DepositInterestExpense}$.
- **Capital Adequacy Ratio (`VA 0x00475175..0x004751AF`)**:
  - Minimum regulatory capital ratio (`BANK_CAPITAL_RATIO` in `CONFIG.DBF` = `8%`, warning at `10%`, target liquidity `20%` at `0x0047523D: movsd xmm0, [0x84C3B8] = 20.0`).
  - Loan Loss Provision scales with macro GDP slowdown and borrower credit rating distribution.

### 3.3 `stock.cpp` (`VA 0x00645F80..0x00646A80`) & `stock_dividend.cpp` (`VA 0x0064CB93`) — Valuation & CEO/Dividend Cash Flow
- **Corporate Equity Valuation (`VA 0x0064635F..0x00646A43`)**:
  - Combines Book Value (`NetWorth`, weighted by `0.5`..`1.0`) and Earnings Valuation ($\text{OperatingProfit} \times \text{PE\_Multiple}$, where baseline $\text{PE} = 10.0$ at `0x84D8C8`), plus Dividend Yield premium (`0.75` factor at `0x84F800 = 75.0 / 100.0`).
  - Per-share price (`[edi + 0x08]`) $= \text{TotalValuation} / \text{SharesOutstanding}$ (`[edi + 0x10]`).
- **CEO Salary & Cash Dividends (`stock_dividend.cpp`)**:
  - **CEO Salary**: Deducted monthly/quarterly from the employing Corporation's `Cash` and credited directly to the CEO's `PersonInfo.Cash` (`+0x50`).
  - **Cash Dividends**: Deducted from the paying Corporation's `Cash` (`\Delta \text{Cash} = -\text{DPS} \times \text{SharesOutstanding}$) and distributed pro-rata to every shareholder (`PersonInfo.Cash` for individuals, `Corporation.Cash` for parent holding companies).

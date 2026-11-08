# EagleCapitalEngine — Đặc Tả Kỹ Thuật, Bản Đồ Dịch Ngược & Công Thức Hợp Nhất (`WSR` + `Capitalism Lab`)

## 1. Mục Tiêu Của Dự Án Độc Lập (`Stage A`)
Xây dựng và kiểm thử hoàn chỉnh khối **`EagleCapitalEngine` (`eagle_capital_engine.py`)** — một Engine Tài chính Vĩ mô, Ngân hàng Đầu tư & Quản trị Tập đoàn/Chuỗi cung ứng **100% Native Python** hợp nhất từ:
1. **Wall Street Raider (`C:\Program Files (x86)\wsr\WSR.EXE` v8.70/9.0):**
   - Tầng Thượng tầng Tài chính (`Top-Down Macro & Financial Engineering`):
   - `1,590` tập đoàn (`ID 11..1600`), `70` ngành công nghiệp (`IND 1..70`), `20` quỹ ETF (`1581..1600`), `54` quốc gia (`00..53`), `263` liên kết sở hữu chéo (`Holding / Subsidiary < >`).
   - Vĩ mô: `GDP Growth`, `Prime Rate`, `Short/Long Bond Yields`, `Inflation`, giá `Crude Oil`, `Gold`, `Silver`, `Wheat`, `Corn`, `BTC`, `ETH`, `Stock Index`.
   - Công cụ tài chính & Nghiệp vụ: Cổ phiếu (`Long / Short / Margin`), Trái phiếu Chính phủ & Doanh nghiệp (`AAA..D`), Quyền chọn (`Call/Put Options`), Hợp đồng tương lai (`Futures`), Hoán đổi lãi suất (`Interest Rate Swaps`), Vay ngân hàng (`Bank Loans` & `Credit Line`), Thâu tóm & Tái cấu trúc (`M&A`, `Tender Offer`, `Hostile Takeover`, `LBO`, `Spin-Off`, `Tax-Free Liquidation`, `Stock Buyback / Issuance`, `Antitrust Lawsuits`).
2. **Capitalism Lab (`C:\Users\LENOVO\Downloads\capitalism lab\[tamhongame.com]_CL\Capitalism Lab\CapMain.exe` v11.0.98 — 7 DLCs):**
   - Tầng Hạ tầng Kinh tế Thực (`Bottom-Up Real Economy & Supply Chain`):
   - `56` bảng cơ sở dữ liệu chuẩn dBase III (`.DBF`) trong `gameset/1STD.SET`:
     - `135` sản phẩm (`PRODUCT_TYPES`) với trọng số cạnh tranh người tiêu dùng chuẩn (`PRICE_CN`, `QUALITY_CN`, `BRAND_CN`, `NECESSITY`, `DEMAND`, `RD_PREMIUM`).
     - `99` công thức chế tạo nhà máy (`MANUFACTURING`: tối đa 3 nguyên liệu đầu vào `INPUT1..3` $\rightarrow$ `OUTPUT`).
     - `48` loại cơ sở (`FIRM`), `142` quy cách tòa nhà (`FBUILDSTD`), `33` bộ phận chức năng (`JOB`), `86` cấu hình cửa hàng bán lẻ (`RETAIL_STORE_PRODUCTS`).
     - `9` loại tài nguyên khoáng sản (`NATURAL_RESOURCES`), `12` cây trồng (`FARM_CROPS`), `4` vật nuôi (`FARM_LIVESTOCK`).
     - `20` loại phần mềm (`SOFTWARE_TYPES` — Digital Age DLC), `38` công nghệ R&D (`TECH`), `128` thành phố (`CITIES`), `64` CEO AI (`PERSONS`).
   - Toàn bộ 7 DLC (`Subsidiary`, `CityEcoSim`, `DigitalAge`, `Banking`, `Experiment`, `Service`, `Smartphone`): Tách biệt `Personal Cash` (nhận Lương CEO + Cổ tức, mua biệt thự/cổ phiếu cá nhân) và `Corporate Cash` (kho bạc tập đoàn).

---

## 2. Cơ Sở Dữ Liệu Hợp Nhất Đã Trích Xuất (`data/eagle_wsr_caplab_db.json`)
File `data/eagle_wsr_caplab_db.json` (`1,771,764` bytes, tạo bởi `extract_wsr_caplab_db.py`) đã trích xuất sạch 100% dữ liệu gốc của cả 2 game:
- `wsr.countries`: `54` quốc gia (`00 = UNITED STATES / WALL STREET` .. `53 = VIETNAM / HANOI`).
- `wsr.industries`: `70` ngành công nghiệp (`IND 1 = BANKING`, `IND 2 = INSURANCE`, `IND 3..69 = Sản xuất/Công nghệ/Dịch vụ/Tài nguyên`, `IND 70 = HOLDING / TRADING COS.`).
- `wsr.corporations`: `1,590` tập đoàn (`ID 11..1600`), trong đó `1,058` tập đoàn đang hoạt động từ đầu (`status = 1`) và `532` slot dự phòng cho Startup / IPO mới (`status = 0`), kèm đầy đủ `cash_millions`, `capital_assets_millions` (`PL1`), `dividend_payout_pct` (`DV%`), `bonds_outstanding_millions` (`JBOS`), `bond_maturity_year` + `bond_coupon_pct` (`BCOUP`), và đồ thị sở hữu chéo 2 chiều `parents` / `subsidiaries` (`263` liên kết).
- `capitalism_lab.tables`: Toàn bộ `56` bảng `.DBF` từ `1STD.SET` (`PRODUCT_TYPES`, `MANUFACTURING`, `FIRM`, `FBUILDSTD`, `JOB`, `FIRMJOB`, `RETAIL_STORE_PRODUCTS`, `NATURAL_RESOURCES`, `FARM_CROPS`, `FARM_LIVESTOCK_PRODUCTS`, `SOFTWARE_TYPES`, `TECH`, `CITIES`, `PERSONS`, `STOCKS`, `BILLIONAIRES`, v.v.).

---

## 3. Bản Đồ Địa Chỉ & Công Thức Dịch Ngược Từ `WSR.EXE` (Tham Chiếu Chuẩn Hóa Toán Học)
- **PE Image:** 32-bit PowerBASIC (`ImageBase = 0x00400000`, no ASLR). Startup (`0x006AA2FE`) dịch `.data + 0x28` lên `0xED8` bytes (`FileOffset_Const = VA - 0x004028D8`, `FileOffset_Code = VA - 0x00400C00`).
- **Biến Thời Gian & Vĩ Mô (`Global Scalars`):**
  - `YEAR&` (`0x006B6CC8`), `QTR&` (`0x006B6BE8`, `1..4`), `SUBTICK&` (`0x006B6AA8`, `1..1600` mỗi quý; `500` sub-ticks/tháng; `~16.67` sub-ticks/ngày).
  - `GDP` (`0x006B6AFC` float), `Prime Rate` (`0x006B6BDC` float), `Long Bond` (`0x006B6C9C`), `Short Bond` (`0x006B6C0C`), `Oil` (`0x006B6BB0`), `Gold` (`0x006B6B00`), `Silver` (`0x006B6C38`), `Wheat` (`0x006B6CC0`), `Corn` (`0x006B6AB4`), `BTC` (`0x006B6CF8` int32), `ETH` (`0x006B6D00` int32), `Stock Index` (`0x006B6C40` 10B EXT).
- **Mảng Thực Thể `1..1600` (`20-byte PowerBASIC Array Descriptors`, phần tử `i` tại `*(uint32_t*)Desc + i * ElemSize`):**
  - `CASH##(1..1600)`: `0x006B71B8` (`10B EXT`, đơn vị `$ Millions`).
  - `TBILLS##(1..1600)`: `0x006BB0B4` (`10B EXT`).
  - `BANKLOAN##(1..1600)`: `0x006BA478` (`10B EXT`).
  - `NETWORTH##(1..1600)`: `0x006BA4EC` (`10B EXT`).
  - `PRICE##(1..1600)`: `0x006B7388` (`10B EXT`, `$/share`).
  - `SHARES##(1..1600)`: `0x006B9014` (`10B EXT`, triệu CP).
  - `CONTROLLED_BY&(1..1600)`: `0x006B722C` (`4B int32`).
  - `CREDIT_RATING&(1..1600)`: `0x006B9754` (`4B int32`, `10=AAA .. 1=D`).
  - `SYMBOL$(1..1600)`: `0x006B70D0` (`4B BSTR`).
- **Các Subroutine Toán Học Trọng Tâm trong `WSR.EXE` (để đối chiếu/dịch ngược thêm nếu cần):**
  - `VA 0x004C602E`: `MasterSimulationStep` (vòng lặp kinh tế vĩ mô, ngành, báo cáo quý, thuế, lãi vay).
  - `VA 0x004266F8`: `CalculateEntityBalanceSheet` (`TotalAssets = Cash + TBills + OperatingAssets + StockPortfolio + BondPortfolio + Derivatives`; `NetWorth = TotalAssets - TotalDebt`).
  - `VA 0x0042B809`: `CalculateCreditRatingAndCreditLine`.
  - `VA 0x004112C1` / `0x004113BE`: Mua / Bán / Bán khống cổ phiếu & Tác động giá (`Market Impact`).
  - `VA 0x00411934`: Trái phiếu, Options, Futures, Commodities, Crypto.
  - `VA 0x004119D8`: Vay ngân hàng, Phát hành Cổ phiếu / Trái phiếu.
  - `VA 0x00411A7C`: Quản trị Tập đoàn (Cổ tức, R&D/Capex, M&A, Tender Offer, LBO, Spin-off, Liquidation, Lawsuits).
  - `VA 0x00411B20`: Interest Rate Swaps.

---

## 4. Bản Đồ Địa Chỉ & Công Thức Dịch Ngược Từ `CapMain.exe` (`v11.0.98`)
- **PE Image:** 32-bit MSVC (`ImageBase = 0x00400000`), `218` C++ RTTI classes, `453` đường dẫn file nguồn `E:\CLsrc\*.cpp`.
- **Đối tượng Toàn cục:**
  - `Info` (`RVA 0x00645BA0` / `VA 0x00A45BA0`): `game_date` (`+0x18`), `game_day` (`+0x1C`), `game_month` (`+0x24`), `game_year` (`+0x28`), hàm bước ngày `Info::next_day()` (`VA 0x004E3EA0`).
  - `PersonRes` (`RVA 0x0051C0E0` / `VA 0x0091C0E0`) & `PersonInfo` (`sizeof = 0x5A8`):
    - `Personal Cash`: `*(double*)(pInfo + 0x50)` (`$1` units).
    - `CEO Salary`: `*(double*)(pInfo + 0xD0)` (`$1` units).
    - `PersonInfo::get_net_worth`: `VA 0x00619320` (`Personal Cash` + `Stock Value 0x00619670` + `Financial Assets 0x0061A330` + `Mansion Value 0x006197A0`).
  - `GroupArray` (`RVA 0x00646DF0` / `VA 0x00A46DF0`) & `Group`:
    - `Corporate Cash`: `*(double*)(pGroup + 0xCC0)` (`Group::add_cash` @ `VA 0x0051BC70`).
    - `ceo_person_id`: `+0xDC`.
  - **Hệ thống `Firm` (`FirmFactory`, `FirmRetail`, `FirmRD`, `FirmMine`, `FirmFarm`, `FirmBank`, `FirmInsurance`, `FirmApartment`, `FirmCommercial`, `FirmSoftware`, `FirmInternet`, `FirmTelecom`, `FirmMedia`):**
    - Điểm cạnh tranh sản phẩm tại từng Đô thị (`Overall Product Rating`):
      $$\text{Rating}_{p, c} = \frac{\text{QUALITY\_CN}_p \cdot Q + \text{BRAND\_CN}_p \cdot B + \text{PRICE\_CN}_p \cdot P_{\text{score}}}{100}$$
      trong đó $Q$ phụ thuộc vào trình độ công nghệ `TECH` của công ty + chất lượng nguyên liệu đầu vào `INPUT1..3`, và $B$ phụ thuộc vào chi phí quảng cáo (`Advertising`) + độ trung thành thương hiệu.

---

## 5. Kiến Trúc Hợp Nhất Của `EagleCapitalEngine` & Giao Thức Tích Hợp Sang GTA SA (`Stage B Contract`)
Khi hoàn thiện `EagleCapitalEngine`, module này chỉ cần cung cấp một API Python sạch (`EagleCapitalEngine`) với:
1. **Trục Thời Gian (`Time Axis`):**
   - `step_intraday_subtick(count=1)`: Chạy biến động giá nội ngày, khớp lệnh, tin tức, phái sinh.
   - `step_day(days=1)`: Chạy sản xuất nhà máy, bán lẻ, R&D, thu tiền thuê BĐS, và tự động kích hoạt chốt Tháng (trả Lương CEO) / chốt Quý (BCTC Quý, Lãi vay, Coupon Trái phiếu, Cổ tức, Thuế).
2. **Trục Tiền Tệ (`Money Axis`):**
   - `deposit_from_gta_wallet(amount_usd)` / `withdraw_to_gta_wallet(amount_usd)`: Liên thông 2 chiều với `NeoBank` / `GTA Cash` của Aether.
   - Tự động đẩy sự kiện `CEO Salary Paid` và `Cash Dividend Paid` vào `Personal Cash` của Aether.
3. **Trục Lưu Trữ & Giao Diện (`State & UI Snapshot API`):**
   - `save_state(slot_path)` / `load_state(slot_path)` / `reset_new_game()`: Gắn 1:1 với 8 slot save của GTA SA (`GTAPEsf1..8.b`).
   - `get_wallstreet_floor_snapshot()`: Cấp dữ liệu cho 5 bảng LED 3D (`EagleWallStreet.asi`) và 8 Nữ Broker AI.
   - `get_workstation_state()` / `execute_action(cmd, payload)`: Cấp dữ liệu và thực thi mọi lệnh giao dịch Phố Wall (WSR) & Quản trị Đế chế (Capitalism Lab) cho `EagleWallStreetHud.lua` và `EaglePhone OS`.

---

## 5. Năm Chế Độ Bảng Cân Đối Kế Toán (`5 Balance Sheet Regimes`) & 7 Cơ Chế Hạch Toán Cốt Tử Của WSR

Dựa trên kết quả giải phẫu nhị phân `WSR.EXE` (`v8.70` & `v10.0.22.3` + `ui.dll` tại [`docs/re_dumps/wsr_architecture_and_qa_guide.md`](docs/re_dumps/wsr_architecture_and_qa_guide.md) và [`docs/re_dumps/supplementary_math_formulas_re.md`](docs/re_dumps/supplementary_math_formulas_re.md)), `EagleCapitalEngine` bắt buộc thực thi đầy đủ **5 chế độ Bảng cân đối kế toán** và **7 quy tắc hạch toán ngầm**:

### 5.1. Năm Chế Độ Bảng Cân Đối Kế Toán (`CorpInfoItems` `@ 0x004266F8` & `ui.dll` `@ 0x10042C54`)
1. **Chế độ 1 — Tập đoàn Sản xuất / Thương mại / Holding (`IND = 3..70`):**
   - $\text{Assets} = \text{Cash} + \text{TBills} + \text{WorkingCap} + \text{CapAssets} + \text{StockPortfolio} + \text{OptionPortfolio} + \text{CommodMTM} + \text{CommodMargin} + \text{UnamortizedGoodwill}$
   - $\text{Liabilities} = \text{BankLoan} + \text{BondsOut (Straight + Convertible)} + \text{ShortLiability} + \text{NakedOptionLiab} + \text{AccTax} + \text{CapTax} + \text{HidReserve}$
2. **Chế độ 2 — Ngân hàng Thương mại (`IND = 1` — `BankAlloc` `@ 0x0061B266`):**
   - Không có `CapAssets` hay `WorkingCap`.
   - $\text{Assets} = \text{Cash} + \text{TBills} + (\text{BizLoans} + \text{ConsumerLoans} + \text{MortgageLoans} - \text{BadDebtReserves}) + \text{GovBonds}_{\text{AdjCost}} + \text{CorpBonds}_{\text{AdjCost}} + \text{StockPortfolio} + \text{AdvancesToCorps}$
   - $\text{Liabilities} = \text{DemandDeposits (0\%)} + \text{CertDeposits (CDs)} + \text{InterbankDebt (Fed Funds)} + \text{BondsOut} + \text{AccTax} + \text{CapTax} + \text{HidReserve}$
   - Xếp hạng tín nhiệm (`GetCredRating`): Tính theo **Tỷ lệ An toàn Vốn ($\text{CAR} = \text{NetWorth} / \text{TotalAssets}$)** và tỷ lệ nợ xấu chứ không dùng `D/E`.
3. **Chế độ 3 — Công ty Bảo hiểm (`IND = 2`):**
   - Không có `CapAssets` hay `WorkingCap`.
   - $\text{Assets} = \text{Cash} + \text{TBills} + \text{SubprimeMortgages (MBS)} + \text{GovBonds}_{\text{AdjCost}} + \text{CorpBonds}_{\text{AdjCost}} + \text{StockPortfolio} + \text{OptionPortfolio} + \text{CommodMTM} + \text{CommodMargin}$
   - $\text{Liabilities} = \text{InsurReserves (Insurance Float)} + \text{BankLoan} + \text{BondsOut} + \text{AccTax} + \text{CapTax} + \text{HidReserve}$
4. **Chế độ 4 — 20 Quỹ ETF (`IND = 71`, Entity ID `1581..1600`):**
   - Quản lý bởi `advisorId` thu phí quản lý (`0.2%..2.0%` NAV) + `ETFBonus`.
   - Trái phiếu (`GovBonds`, `CorpBonds`) trong ETF được định giá theo **Market Value** (khác với Adjusted Cost của Ngân hàng/Bảo hiểm).
   - Hỗ trợ tự cân bằng đòn bẩy (`AdjustLeverage` cho 2x/3x Bull/Bear ETF), không bán khống cổ phiếu đơn lẻ hay phát hành trái phiếu.
5. **Chế độ 5 — Người chơi / Nhà đầu tư Cá nhân (`Entity ID 1..5`, `ui.dll` `@ 0x1003EFD6`):**
   - $\text{Assets} = \text{Cash} + \text{TBills} + \text{AdvancesToCompanies} + \text{GovBonds}_{\text{Mkt}} + \text{CorpBonds}_{\text{Mkt}} + \text{StockPortfolio} + \text{OptionPortfolio} + \text{CommodMTM} + \text{CommodMargin}$
   - $\text{Liabilities} = \text{BankLoan} + \text{ShortLiability} + \text{NakedOptionLiab} + \text{IncomeTaxOwed} + \text{WealthTaxProjected}$

### 5.2. Bảy Cơ Chế & Quy Tắc Chống Sai Lệch Bắt Buộc
1. **Sở hữu Chéo Vòng tròn (`CircControl` `@ 0x00480D92` & `CorpControl` `@ 0x0041F811`):** Định giá hội tụ giảm chấn (damped iterative Gauss–Seidel/Jacobi valuation) và phát hiện chu trình kiểm soát để chống bơm thổi `NetWorth` ảo.
2. **Luật Thuế Doanh nghiệp 3 Tầng (`CorpTaxCalc` `@ 0x004F9803`):**
   - **DRD (`Dividends Received Deduction`):** Miễn thuế **80%** cổ tức nhận từ công ty con nếu sở hữu $< 80\%$; miễn thuế **100%** nếu sở hữu $\ge 80\%$.
   - **Ngưỡng `80%` Tax-Free:** `Liquidate` và `SpinOff` công ty con được miễn thuế `CapTax` khi nắm giữ $\ge 80\%$; dưới $80\%$ chịu thuế Capital Gains.
   - **Chuyển lỗ 4 năm (`LOSS1..LOSS4`):** Lưu lỗ ròng 4 năm gần nhất và tự động khấu trừ vào thu nhập chịu thuế.
3. **Nghĩa vụ Cổ tức Bán khống (`ShortDividends` `@ 0x005E0721`), `NakedOptionLiab` & `ConvertibleBonds` (`IssueCV` `@ 0x00684901`):**
   - Người bán khống bị trừ tiền mặt trực tiếp $\Delta \text{Cash} = -\text{ShortShares} \times \text{DPS}$ mỗi khi công ty trả cổ tức; tổng cổ phiếu Long trên thị trường $= \text{SharesOutstanding} + \text{TotalShortShares}$.
   - Quyền chọn bán khống (`Naked Options`) ghi nhận vào `NakedOptionLiab` và bị cưỡng chế mua đóng (`CheckNakedOptions`) khi vượt hạn mức vay.
   - Trái phiếu chuyển đổi (`Convertible Bonds`) cho phép đổi sang cổ phiếu mới tại giá `CVP`, pha loãng `SharesOutstanding`.
4. **Quỹ Dự phòng Ẩn (`HidReserve`) & Chiến tranh Pháp lý:** Hỗ trợ `increaseEarnings`/`decreaseEarnings` qua `HidReserve` và các vụ kiện `antitrustLawsuit`, `harrassingLawsuit`, `greenmail`.
5. **Chống Hạch toán Kép (`Zero Double-Counting`) tại Cầu nối WSR $\leftrightarrow$ Capitalism Lab:** Khi giải ngân `Cash` xây dựng `Firm` Capitalism Lab, tài sản cố định của `Firm` ánh xạ trực tiếp vào `CapAssets` (`CapAssets = CapAssets_Abstract + CapAssets_CapLabFirms`) và tồn kho ánh xạ vào `WorkingCap`, bảo toàn tuyệt đối $\Delta \text{Cash} + \Delta \text{CapAssets} + \Delta \text{WorkingCap} \equiv 0$ tại thời điểm CAPEX.
6. **Hoán đổi Lãi suất (`Interest Rate Swaps` — Event `1685`):** Hợp đồng IRS (`Notional`, `FixedRate` vs `FloatingRate` neo theo `PrimeRate`/`LongBondRate`/`ShortBondRate`) thanh toán chênh lệch mỗi quý.
7. **Khung Kiểm Thử Chống Đánh Lừa 4 Tầng (`4-Tier Anti-Deception QA`):** Kiểm tra bất biến kế toán trên toàn bộ `1,595+` thực thể thuộc cả 5 chế độ, kiểm thử 5 bẫy tài chính đối kháng (Circular Ownership, 3-Tier DRD, Short Dividend & Squeeze, Bank Run & Bad Debt, Zero Double-Counting CAPEX), kiểm thử đối chiếu Oracle, và benchmark 40–80 quý đạt $< 2.0\text{ ms/tick}$.


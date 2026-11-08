# Wall Street Raider (v8.70 & v10.0.22.3) — Giải Phẫu Kiến Trúc 180.000 Dòng Code PowerBASIC, Điểm Mù Mô Phỏng & Khung Kiểm Thử Chống Đánh Lừa (QA Guide)

> **Mục đích tài liệu:** Tài liệu này tổng hợp kết quả dịch ngược nhị phân trực tiếp từ bản Legacy (`C:\Program Files (x86)\wsr\WSR.EXE` v8.70/9.0) và bản Steam Remaster mới nhất (`C:\Users\LENOVO\Downloads\Wall.Street.Raider.v10.0.22.3\...\WSR.EXE` v10.0.22.3 + `ui.dll`), kết hợp phân tích mã nguồn từ hai kho lưu trữ của tác giả bản Remaster Ben Ward (`benstopics/powerbasilisk` và `benstopics/wallstreetraider-electron`).
>
> Tài liệu dùng làm **chuẩn đối chiếu (Ground Truth)** để:
> 1. Đánh giá chính xác độ bao phủ của [`EAGLE_CAPITAL_ENGINE_SPEC.md`](../../EAGLE_CAPITAL_ENGINE_SPEC.md) và `eagle_capital_engine.py`.
> 2. Chỉ ra các **"cạm bẫy kế toán / tài chính ngầm"** trong WSR mà một bản port rút gọn rất dễ bỏ sót hoặc tính sai.
> 3. Cung cấp **Khung Kiểm Thử Đối Chiếu (Differential & Invariant QA Framework)** để đảm bảo hệ thống test không bị "đánh lừa" bởi các bài test bề nổi.

---

## 1. Giải Mã "180.000 Dòng Code PowerBASIC" — Thực Tế Bên Trong `WSR.EXE` Có Gì?

Qua quét toàn bộ prologue hàm PowerBASIC (`55 8b ec 53 56 57 83 ec 64 68 <func_va>`) và bảng đăng ký tên hàm tại `ErrorSub` (`VA 0x0046E972` trên bản v8.70; `VA 0x004A3F32` trên bản v10.0.22.3):
- Bản Legacy `WSR.EXE` (`4,028,416` bytes) có **926 hàm PowerBASIC** (`3.09 MB` mã máy `.text`).
- Bản Steam Remaster `WSR.EXE` v10.0.22.3 (`5,088,768` bytes) có **995 hàm PowerBASIC** (`4.13 MB` mã máy `.text`), cộng thêm `ui.dll` (`1,275,392` bytes, C++ MSVC 32-bit).

Tại sao một trình mô phỏng tài chính lại lên tới ~180.000 dòng code? Khi phân loại toàn bộ 926–995 hàm theo kích thước mã máy và chức năng, cấu trúc thực sự chia làm **4 khối rõ rệt**:

| Khối kiến trúc | Tỷ trọng code | Các hàm tiêu biểu trong `WSR.EXE` (v8.70 / v10.0.22.3) | Bản chất & Ý nghĩa đối với `EagleCapitalEngine` |
| :--- | :---: | :--- | :--- |
| **1. Giao diện Win32/DDT cũ, Đồ thị GDI & Trình tạo Báo cáo Văn bản (`BSTR` Concatenation)** | **~45%** | `Research Report` (`62,337 B` @ `0x448eef`), `EarnReport` (`36,968 B` @ `0x462f2d`), `Profiles` (`36,838 B` @ `0x4308cc`), `FrontBuyStock` (`31,796 B`), `FrontSellOptions` (`28,048 B`), `PersProfile` (`26,699 B`), `CashFlowProj` (`26,229 B`), `Portfolio` (`16,857 B`), `ChartStock` (`7,537 B`) | Trong PowerBASIC, mọi báo cáo tài chính, bản tin ticker, bảng biểu và hộp thoại đều được nối chuỗi thủ công dòng-theo-dòng bằng hàm runtime `BSTR`. **Không phải là toán học mô phỏng** — có thể thay thế hoàn toàn bằng JSON/UI hiện đại. |
| **2. Vòng lặp Thời gian Vĩ mô & AI Tự trị / Market Maker (`BigLoop` + `AutoPlay` + `Random*`)** | **~25%** | `BigLoop` (`103,171 B` @ `0x4c602e` v8.70; **`181,540 B` @ `0x6bfe04` v10.0.22.3**), `AutoPlay` (`59,892 B` @ `0x5c0ab9`), `Good/Bad Events` (`37,608 B` @ `0x62ed00`), `RandomMerger` (`18,892 B` @ `0x521d46`), `ChangePrime` (`15,623 B` @ `0x534bd5`), `SupplyDemand` (`2,073 B` @ `0x53a7aa`) | **Trái tim của sự sống động trong WSR.** Chạy từng sub-tick: cập nhật GDP, lạm phát, lãi suất, cung cầu 70 ngành, sự kiện thiên tai/đột phá, và cho 1.000+ tập đoàn AI tự động M&A, LBO, phát hành/mua lại cổ phiếu, đảo nợ trái phiếu, giao dịch phái sinh. |
| **3. Toán học Tài chính, Kế toán 5 Chế độ, Thuế, Phái sinh & Tái cấu trúc Doanh nghiệp** | **~20%** | `Bankruptcy` (`26,329 B` @ `0x4e667c`), `StockPrice` (`16,570 B` @ `0x42c812`), `BankAlloc` (`12,090 B` @ `0x61b266`), `HedgeFutures` (`11,971 B`), `ExerciseOption` (`11,032 B`), `AdvancedOptions` (`10,422 B`), `GetOptionPrice` (`9,006 B`), `JunkBondPrice` (`8,594 B`), `CorpInfoItems` (`7,783 B` @ `0x4266f8`), `CircControl` (`5,301 B` @ `0x480d92`), `GetNakedOptionLiab` (`4,998 B`), `RedeemCV` (`4,690 B`), `IssueCV` (`4,273 B`), `GetCredRating` (`4,105 B` @ `0x42b809`), `CorpTaxCalc` (`3,443 B` @ `0x4f9803`) | **Lõi nghiệp vụ khắt khe nhất.** Chứa toàn bộ công thức định giá, kiểm soát sở hữu chéo, luật thuế (DRD, NOL, Tax-Free Spin-off/Liquidation), ngân hàng/bảo hiểm/ETF, bán khống, quyền chọn, hợp đồng tương lai và hoán đổi lãi suất (IRS). |
| **4. Lưu/Đọc Savefile & Cầu nối FFI (`WriteAll`/`ReadAll` & `SyncGameData`/`EventDispatch`)** | **~10%** | `WriteAll` (`18,864 B` @ `0x4854ad`), `ReadAll` (`18,880 B` @ `0x489e5d`), `EventDispatch` (`26,912 B` @ `0x40652c` v10), `SyncGameData` (`0x708f1d` & `0x70bb1e` v10) | Đóng gói toàn bộ biến toàn cục PowerBASIC ra đĩa (`.SAV`) hoặc đồng bộ sang struct `GameData` (`VA 0x0091F7B0`) cho `ui.dll`. |

---

## 2. Giải Phẫu 3 Nguồn Tư Liệu Mới (`powerbasilisk`, `wallstreetraider-electron`, và Bản `v10.0.22.3`)

### 2.1. `benstopics/powerbasilisk` — Dự án Compiler PowerBASIC sang 64-bit LLVM
- Tác giả Ben Ward xây dựng `powerbasilisk` (gồm `pbcompiler` biên dịch sang LLVM IR 64-bit và `pbinterp` thông dịch AST) với mục tiêu duy nhất là biên dịch bộ mã nguồn 180.000 dòng của Wall Street Raider thoát khỏi giới hạn 32-bit của trình biên dịch `PB/Win` cổ điển.
- **Giá trị trực tiếp:** Thư mục `pbinterp/tests/fixtures/` và `pbcompiler/tests/` chứa các đoạn code `.bas` trích nguyên bản từ mã nguồn WSR. Ví dụ tiêu biểu là `pbinterp/tests/fixtures/loanrate_test.bas` — hàm `GetLoanRate` tính lãi suất vay ngân hàng theo xếp hạng tín nhiệm `CredRat(N)` từ `0..9` (`AAA..D`) cộng với phần bù rủi ro thu nhập (`IncomeToInt`) của người chơi (`N <= 5`) và tập đoàn (`N > 5`).

### 2.2. `benstopics/wallstreetraider-electron` & Bản cài `Wall.Street.Raider.v10.0.22.3` — "Hòn Đá Rosetta"
Bản `Wall.Street.Raider.v10.0.22.3` giải quyết bài toán khó nhất của việc dịch ngược WSR: **Ánh xạ tên biến và cấu trúc dữ liệu.**
- Thay vì viết lại game bằng JS/C++, bản v10.0.22.3 giữ nguyên `WSR.EXE` biên dịch từ PowerBASIC nhưng nhúng thêm 2 file include:
  - `ui.inc`: Khai báo struct `GameData` khổng lồ (`Descriptor @ VA 0x0091F7B0`) và gọi `ui.dll!InitUI(ByVal VarPtr(GameData))` tại `VA 0x0040570A`.
  - `SYNCGAMEDATA.INC`: Chứa các hàm `SyncGameData` (`VA 0x00708F1D`, `11,265 B` và `VA 0x0070BB1E`, `11,310 B`, gọi từ `VA 0x004027B9`) chép toàn bộ mảng toàn cục của PowerBASIC vào struct `GameData`, sau đó gọi `ui.dll!UpdateUI`.
- Phía `ui.dll` (`C++`) đọc trực tiếp struct `GameData` từ bộ nhớ của `WSR.EXE` (hàm `SerializeEntityFinancials` tại `VA 0x10042C54` và `SerializePlayerFinancials` tại `VA 0x1003EFD6`) rồi phát ra JSON chuẩn qua cổng HTTP nội bộ (`/gamestate`) và WebSocket (`/game_state_patch`).
- Ngược lại, mọi thao tác của người chơi trên giao diện Preact/Electron (`js/api.js`) được gửi qua `ui.dll!PollEvent` về hàm `EventDispatch` (`VA 0x0040652C..0x0040CE4C` trong `WSR.EXE` v10.0.22.3) dưới dạng mã `GameEventType` (`5..4201`).

> [!IMPORTANT]
> **Ý nghĩa chiến lược cho việc Kiểm thử (Testing):**
> Vì `WSR.EXE` v10.0.22.3 + `ui.dll` xuất toàn bộ trạng thái kế toán ra JSON qua HTTP `/gamestate` và nhận lệnh qua `/event`, chúng ta có một **Oracle (Máy chuẩn đối chiếu sống)**: có thể nạp cùng một kịch bản giao dịch vào `WSR.EXE` v10.0.22.3 và `eagle_capital_engine.py` để so sánh kết quả từng đồng đô-la!

---

## 3. Chẩn Đoán Kiến Trúc Hiện Tại (`EAGLE_CAPITAL_ENGINE_SPEC.md`) — 7 "Điểm Mù & Cạm Bẫy Ngầm" Của WSR

Đối chiếu [`EAGLE_CAPITAL_ENGINE_SPEC.md`](../../EAGLE_CAPITAL_ENGINE_SPEC.md) với mã máy của `WSR.EXE` (`v8.70` & `v10.0.22.3`) và `FinancialsTab.js`, kiến trúc hiện tại đã nắm bắt đúng khung xương sống (Bảng cân đối kế toán, `StockPrice`, `GetCredRating`, `TreasBondPrice`, `JunkBondPrice`, `SupplyDemand`, cầu nối Capitalism Lab). Tuy nhiên, nếu chỉ dừng ở các công thức trong Spec hiện tại, mô phỏng sẽ gặp **7 điểm mù lớn** dưới đây (và các bài test đơn giản sẽ không phát hiện ra):

### Cạm bẫy 1: WSR có tới 5 Chế độ Bảng Cân đối Kế toán (5 Balance Sheet Regimes), KHÔNG PHẢI 1
Trong `CorpInfoItems` (`VA 0x004266F8`) và serializer `VA 0x10042C54` (`FinancialsTab.js`), WSR tách biệt hoàn toàn cấu trúc Tài sản & Nợ phải trả của 5 nhóm thực thể:

1. **Tập đoàn Công nghiệp / Thương mại / Holding (`IND = 3..70`):**
   - **Tài sản (`Assets`):** `Cash` + `T-Bills` + `WorkingCap` ($25\%$ `CapAssets` khi hoạt động) + `CapAssets` (`FLOW` / Thiết bị nhà máy) + `StockPortfolio` (Long stocks) + `OptionPortfolio` (Long options) + `CommodMTM` (Lãi/lỗ ròng hợp đồng Futures) + `CommodMargin` (Ký quỹ Futures) + `UnamortizedGoodwill` (Lợi thế thương mại chưa phân bổ khi M&A giá cao hơn Book Value).
   - **Nợ phải trả (`Liabilities`):** `BankLoan` + `BondsOut` (Trái phiếu thường + Trái phiếu chuyển đổi) + `ShortLiability` (Giá trị thị trường cổ phiếu bán khống) + `NakedOptionLiab` (Nghĩa vụ quyền chọn bán khống) + `AccTax` (Thuế thu nhập tích lũy) + `CapTax` (Thuế thanh lý/tách công ty) + `HidReserve` (Quỹ dự phòng ẩn).
2. **Ngân hàng Thương mại (`IND = 1` — `BankAlloc` `@ 0x0061B266`):**
   - **Không có `CapAssets` hay `WorkingCap`!**
   - **Tài sản:** `Cash` + `T-Bills` + `BizLoans` (Cho các tập đoàn vay) + `ConsumerLoans` (Vay tiêu dùng) + `MortgageLoans` (Vay thế chấp) $-$ `BadDebtReserves` (Dự phòng nợ xấu) + `GovBonds` (**Định giá theo Adjusted Cost**, không phải Market Value!) + `CorpBonds` (**Adjusted Cost**) + `StockPortfolio` + `AdvancesToCorps`.
   - **Nợ phải trả:** `DemandDeposits` (Tiền gửi không kỳ hạn, lãi suất = $0$) + `CertDeposits` (Chứng chỉ tiền gửi CD, có lãi suất) + `InterbankDebt` (Vay liên ngân hàng / Fed Funds từ NHTW hoặc ngân hàng khác) + `BondsOut` + `AccTax` + `CapTax` + `HidReserve`.
   - **Xếp hạng tín nhiệm (`GetCredRating`):** Ngân hàng **không dùng hệ số `D/E`** mà dùng **Tỷ lệ An toàn Vốn (`CAR = NetWorth / TotalAssets`)** và tỷ lệ Nợ xấu để xếp hạng `AAA..D` và kiểm tra phá sản ngân hàng (`BankCapital` / `BankLiq`).
3. **Công ty Bảo hiểm (`IND = 2`):**
   - **Không có `CapAssets` hay `WorkingCap`.**
   - **Tài sản đặc thù:** `SubprimeMortgages` (Chứng khoán thế chấp dưới chuẩn MBS — nguồn gây khủng hoảng tài chính khi lãi suất/vỡ nợ tăng), `GovBonds` (Adjusted Cost), `CorpBonds` (Adjusted Cost), `StockPortfolio`, `OptionPortfolio`, `IndexFuturesMTM` & `CommodMargin`.
   - **Nợ phải trả đặc thù:** `InsurReserves` (Dự phòng nghiệp vụ bảo hiểm — nguồn vốn float khổng lồ giống Berkshire Hathaway, sinh lời hoặc lỗ tùy theo chu kỳ bồi thường bảo hiểm ` Good/Bad Events`) + `BankLoan` + `BondsOut` + `AccTax` + `CapTax` + `HidReserve`.
4. **20 Quỹ ETF (`IND = 71`, Entity ID `1581..1600`):**
   - Được quản lý bởi một Tập đoàn đóng vai trò **Investment Advisor (`advisorId`)**, thu phí quản lý hàng năm (`setAdvisoryFee`: $0.2\% - 2.0\%$ NAV + thưởng hiệu suất `ETFBonus`).
   - **Khác biệt định giá quan trọng:** Trái phiếu Chính phủ và Trái phiếu Doanh nghiệp trong danh mục ETF được định giá theo **Market Value (Giá thị trường)** chứ không phải Adjusted Cost như Ngân hàng/Bảo hiểm!
   - Có cơ chế tự cân bằng đòn bẩy (`AdjustLeverage` `@ 0x0068E391` cho các quỹ 2x/3x Bull/Bear ETF), quản lý danh mục trái phiếu tự động (`BondFundMgr` `@ 0x006901C4`), xả bớt tiền mặt dư (`TooLiquidETF` `@ 0x0068D374`) và tái cấp vốn khi ETF cháy tài khoản (`ReviveETF` `@ 0x0069D48C`).
5. **Người chơi / Nhà đầu tư Cá nhân (`Entity ID 1..5`, serialize tại `VA 0x1003EFD6`):**
   - Có `AdvancesToCompanies` (Tiền cá nhân ứng trước cho công ty mình kiểm soát vay, hưởng lãi suất riêng), `ShortLiability`, `NakedOptionLiab`, `CommodMTM`, `CommodMargin`, và 4 khoản mục thuế cá nhân: `ytdTaxableOrdinary`, `realizedCapGainLoss`, `prepaidTax`, `incomeTaxOwed` (+hoàn thuế / -nợ thuế) và `wealthTaxProjected` (Thuế tài sản ròng lũy tiến).

### Cạm bẫy 2: Vòng lặp Sở hữu Chéo (`CircControl` `@ 0x00480D92` & `CorpControl` `@ 0x0041F811`)
- Trong WSR, Tập đoàn A có thể mua $45\%$ cổ phần Tập đoàn B, Tập đoàn B mua $45\%$ Tập đoàn C, và Tập đoàn C mua ngược lại $45\%$ Tập đoàn A (hoặc A $\leftrightarrow$ B trực tiếp).
- **Nguy cơ đánh lừa:**
  - Nếu tính `NetWorth` và `StockPrice` chỉ bằng 1 lượt (single-pass) không xét kiểm soát vòng tròn, người chơi có thể dùng A bơm tiền mua B rồi dùng B mua lại A để thổi phồng `NetWorth` ảo lên vô hạn mà không tốn tiền thật!
  - Trong `WSR.EXE`, hàm `CircControl` (`5,301 B` `@ 0x00480D92`) và `CorpControl` (`@ 0x0041F811`) duyệt đồ thị sở hữu có hướng (`263` liên kết khởi tạo trong `wsr101.dat`) để chặn quyền biểu quyết vòng tròn và chiết khấu giá trị cổ phần chéo.

### Cạm bẫy 3: Luật Thuế Doanh nghiệp 3 Tầng (DRD, Ngưỡng 80% Tax-Free, và 4-Year NOL Carryforward)
Hàm `CorpTaxCalc` (`VA 0x004F9803`), `Liquidate` (`VA 0x005C1EB1`) và `SpinOff` (`VA 0x005CFAF2`) thực thi luật thuế Mỹ cực kỳ chi tiết:
1. **DRD (Dividends Received Deduction — Khấu trừ Cổ tức Nhận được giữa các Tập đoàn):**
   - Khi Công ty Mẹ nhận cổ tức từ Công ty Con:
     - Nếu sở hữu $< 80\%$: Được miễn thuế **$80\%$** khoản cổ tức đó (chỉ chịu thuế thu nhập doanh nghiệp trên $20\%$ cổ tức).
     - Nếu sở hữu $\ge 80\%$: Được miễn thuế **$100\%$** cổ tức nội bộ!
   - **Hậu quả nếu thiếu:** Nếu đánh thuế thu nhập doanh nghiệp $35\%$ trên toàn bộ cổ tức nhận được ở mỗi tầng Holding Company, một tập đoàn 3 tầng sẽ mất $1 - 0.65^3 = 72.5\%$ dòng tiền cổ tức trước khi tới tay cổ đông!
2. **Ngưỡng sở hữu $80\%$ cho Thanh lý (`Liquidate`) và Tách công ty (`Spin-Off`):**
   - Nếu Công ty Mẹ nắm $\ge 80\%$ cổ phần Công ty Con, việc thanh lý (`Liquidate` gộp tài sản về mẹ) hoặc chia tách (`SpinOff` cổ phần cho cổ đông) là **Tax-Free (Miễn thuế Capital Gains)**.
   - Nếu nắm $< 80\%$, giao dịch bị đánh thuế `CapTax` nặng nề. Đây là lý do trong WSR luôn có cuộc chiến gom đủ $80\%$ cổ phần trước khi tái cấu trúc.
3. **Chuyển lỗ 4 năm (`LOSS1..LOSS4` — Net Operating Loss Carryforward):**
   - Khoản lỗ ròng của 4 năm trước (`LOSS1, LOSS2, LOSS3, LOSS4`) được lưu riêng và tự động khấu trừ vào thu nhập chịu thuế của các quý có lãi tiếp theo. Đây là cơ sở của chiến thuật thâu tóm "Tax-Loss Shell" (`mostTaxLossReport`).

### Cạm bẫy 4: Nghĩa vụ Cổ tức Bán khống (`ShortDividends`), Naked Options (`GetNakedOptionLiab`) & Trái phiếu Chuyển đổi (`IssueCV`)
1. **Bán khống Cổ phiếu (`Short Stock` — `GetShortData` `@ 0x004AD14E`, `ShortDividends` `@ 0x005E0721`):**
   - Khi thực thể bán khống $N$ cổ phiếu của công ty X:
     - Tiền bán khống bị khóa vào yêu cầu ký quỹ / giảm hạn mức tín dụng (`Line of Credit`).
     - Trên Bảng cân đối kế toán xuất hiện khoản nợ phải trả `ShortLiability` $= N \times \text{MarketPrice}(X)$ cập nhật mỗi tick.
     - **Quan trọng nhất:** Mỗi quý khi công ty X trả cổ tức $\text{DPS}$, người bán khống **bị trừ tiền mặt trực tiếp** $\Delta \text{Cash} = -N \times \text{DPS}$ (`ShortDividends` `@ 0x005E0721`).
2. **Quyền chọn Bán khống (`Naked Options` — `GetNakedOptionLiab` `@ 0x00604E4E`, `CheckNakedOptions` `@ 0x00606238`):**
   - Viết (Sell/Write) Call hoặc Put mà không có cổ phiếu/tiền đảm bảo tạo ra khoản nợ phải trả biến động theo công thức Black-Scholes + In-the-money intrinsic value (`GetNakedOptionLiab`). Nếu vượt quá tài sản thế chấp, `CheckNakedOptions` sẽ cưỡng chế mua đóng vị thế (Forced Buy-In / Margin Call).
3. **Trái phiếu Chuyển đổi (`Convertible Bonds` — `IssueCV` `@ 0x00684901`, `RedeemCV` `@ 0x00683503`):**
   - Khác với trái phiếu thường (`Straight Bonds`), trái phiếu chuyển đổi (mã định danh `"YYYYcv|CVP|@cc.cc"`) có lãi suất coupon thấp hơn nhưng cho phép trái chủ đổi thành cổ phiếu mới phát hành tại mức giá `CVP` (Conversion Price), làm tăng tổng số cổ phiếu lưu hành (`SharesOutstanding`) và pha loãng (`Dilution`) cổ đông hiện hữu.

### Cạm bẫy 5: Quỹ Dự phòng Ẩn (`HidReserve`) & Vũ khí Pháp lý / Thao túng (`LawFirm`, `Harass`, `Greenmail`)
- Mỗi tập đoàn có khoản mục nợ `Reserve for Contingencies` (`hidReserve`). Người điều hành có thể dùng lệnh `decreaseEarnings` (trích lập dự phòng ảo để giấu lãi, giảm thuế tạm thời hoặc dìm giá cổ phiếu trước khi mua gom/LBO) hoặc `increaseEarnings` (xả dự phòng để bơm lợi nhuận quý trước khi xả cổ phiếu/phát hành thêm).
- Các hành động chiến tranh doanh nghiệp (`antitrustLawsuit`, `harrassingLawsuit`, `spreadRumors`, `greenmail`) có bộ đếm thời gian (`Harass Countdown` `@ 0x00611AF8`) và xác suất thắng/thua gây thiệt hại hàng trăm triệu tới hàng tỷ USD tiền phạt pháp lý.

### Cạm bẫy 6: Hạch toán Kép (Double-Counting Risk) tại Cầu nối WSR $\leftrightarrow$ Capitalism Lab
- Trong [`EAGLE_CAPITAL_ENGINE_SPEC.md`](../../EAGLE_CAPITAL_ENGINE_SPEC.md), khi một Tập đoàn WSR sở hữu các `Firm` (Nhà máy, Cửa hàng, R&D, Trang trại) của Capitalism Lab:
  - Trong WSR gốc, tài sản sản xuất của tập đoàn nằm ở 2 biến tổng hợp: `CapAssets` (Capital Assets / `FLOW`) và `WorkingCap` ($25\%$ `CapAssets`).
  - Khi tích hợp Capitalism Lab, nếu chúng ta vừa giữ nguyên `CapAssets` + `WorkingCap` trừu tượng của WSR, vừa cộng thêm giá trị tài sản của các `Firm` Capitalism Lab vào `TotalAssets`, phương trình kế toán sẽ bị **tính trùng (Double-Count)** hoặc sinh tiền từ hư không khi xây dựng `Firm`!
  - **Quy tắc chuẩn bắt buộc:** Khi một Tập đoàn chuyển tiền mặt `Cash` sang xây dựng `Firm` trong Capitalism Lab ($\Delta \text{Cash} = -\text{BuildCost}$), giá trị sổ sách của `Firm` đó phải được cộng trực tiếp vào `CapAssets` (hoặc tách thành `CapAssets_Abstract` + `CapAssets_CapLabFirms`), và tồn kho hàng hóa thực tế của `Firm` phải ánh xạ vào `WorkingCap`, đảm bảo:
    $$\Delta \text{Cash} + \Delta \text{CapAssets} + \Delta \text{WorkingCap} \equiv 0 \quad (\text{tại thời điểm giải ngân vốn đầu tư CAPEX})$$

### Cạm bẫy 7: Hoán đổi Lãi suất (`Interest Rate Swaps` — `SwapMenu` / `DoSwap` / `InterestRateSwapsModal.js`)
- Trong WSR (`InterestRateSwapsModal.js` & `api.js` Event `1685`), hợp đồng Interest Rate Swap không chỉ là cá cược đơn giản mà có cấu trúc đầy đủ:
  - Gồm: `Notional Principal` (Vốn danh nghĩa), `Fixed Rate` vs `Floating Rate` (neo theo `Prime Rate`, `Long Bond Yield`, hoặc `Short T-Bill Yield`), kỳ hạn (`Duration` theo quý/năm), và kiểm tra hạn mức tín nhiệm đối tác (`Counterparty Credit Limit`).
  - Thanh toán chênh lệch lãi suất ròng diễn ra vào cuối mỗi quý: $\Delta \text{Cash} = \text{Notional} \times (\text{Rate}_{\text{Receive}} - \text{Rate}_{\text{Pay}}) \times 0.25$.

---

## 4. Khung Kiểm Thử Chống Đánh Lừa (4-Tier Anti-Deception QA Framework)

Để đảm bảo quá trình kiểm thử `eagle_capital_engine.py` thực sự chứng minh được độ chính xác toán học và kế toán (không bị đánh lừa bởi các bài test chỉ kiểm tra "code chạy không văng lỗi"), bộ test bắt buộc phải vượt qua **4 tầng kiểm định** sau:

### Tầng 1: Bất biến Kế toán Tuyệt đối trên cả 5 Chế độ Thực thể (5-Regime Balance Sheet Invariants)
Không chỉ kiểm tra $\text{Assets} == \text{Liabilities} + \text{Equity}$ trên một công ty mẫu, bài test phải chạy sau **mọi tick** và **mọi lệnh giao dịch** trên toàn bộ `1,605` thực thể (`5` Players + `1,580` Tập đoàn thuộc đủ các ngành `IND=1` Bank, `IND=2` Insurance, `IND=3..70` Industrial/Holding + `20` ETFs `IND=71`):
1. **Bất biến Cân đối Nội bộ Thực thể ($i \in [1..1600]$):**
   $$\left| \text{TotalAssets}_i(t) - \left(\text{TotalLiabilities}_i(t) + \text{NetWorth}_i(t)\right) \right| < 10^{-4}$$
2. **Bất biến Bảo toàn Cổ phần Lưu hành (Share Conservation Invariant):**
   Với mọi tập đoàn $c \in [6..1600]$:
   $$\sum_{holder \in \text{Players} \cup \text{Corps}} \text{SharesHeld}(holder, c) + \text{PublicFloatShares}(c) - \sum_{shorter} \text{ShortShares}(shorter, c) \equiv \text{TotalSharesOutstanding}(c)$$
   *(Lưu ý: Khi có người bán khống $\text{ShortShares}$, tổng số cổ phiếu Long trên thị trường sẽ lớn hơn $\text{TotalSharesOutstanding}$ đúng bằng lượng $\text{ShortShares}$!)*
3. **Bất biến Bảo toàn Tiền tệ Hệ thống (Closed-Loop Cash Flow Conservation):**
   Trong mọi giao dịch song phương (Mua/bán cổ phiếu, Trả cổ tức, Mua lại trái phiếu, Thanh toán phái sinh, Vay/trả nợ ngân hàng, Chuyển vốn sang `Firm` Capitalism Lab):
   $$\sum_{i \in \text{AllEntities}} \Delta \text{Cash}_i + \Delta \text{CentralBank\_Govt\_MarketMaker\_Pool} \equiv 0$$

### Tầng 2: Bộ Test Các Cạm Bẫy Tài Chính Đặc Thù (Adversarial Financial Trap Tests)
Phải có các bài test chuyên biệt nhằm thẳng vào các góc khuất dễ sai nhất:
- **Test 2.1 — Đồ thị Sở hữu Chéo Vòng tròn (`Circular Ownership Stress Test`):**
  - Tạo chuỗi sở hữu vòng tròn $A \xrightarrow{45\%} B \xrightarrow{45\%} C \xrightarrow{45\%} A$. Chạy `StockPrice` và `CorpInfoItems` qua 50 ticks.
  - **Kỳ vọng:** Hàm định giá hội tụ trong $< 1\text{ ms}$, không bị đệ quy vô tận (`RecursionError`), không làm nổ `NetWorth` lên $\infty$, và `CircControl` nhận diện đúng thực thể kiểm soát thực sự.
- **Test 2.2 — Chuỗi Cổ tức Holding Company 3 Tầng & Luật Thuế DRD (`Triple-Tier Holding Dividend & DRD Test`):**
  - Cho Công ty $C$ chia cổ tức $\$100\text{M}$ cho Công ty $B$ (sở hữu $85\%$ $C$ $\rightarrow$ miễn thuế $100\%$ DRD), và Công ty $B$ chia cổ tức cho Công ty $A$ (sở hữu $50\%$ $B$ $\rightarrow$ miễn thuế $80\%$ DRD).
  - **Kỳ vọng:** Thuế thu nhập phát sinh tại $B$ bằng $\$0$; thuế thu nhập phát sinh tại $A$ chỉ tính trên $20\%$ khoản cổ tức nhận được.
- **Test 2.3 — Nghĩa vụ Cổ tức Bán khống & Margin Call (`Short Seller Dividend & Squeeze Test`):**
  - Cho thực thể $P$ bán khống $10\%$ cổ phiếu công ty $X$. Khi $X$ chia cổ tức $\text{DPS} = \$2.00$, kiểm tra tiền mặt của $P$ bị trừ đúng $N_{\text{short}} \times \$2.00$. Sau đó đẩy giá $X$ tăng $150\%$ để xác nhận `ShortLiability` tăng tương ứng và kích hoạt cưỡng chế đóng vị thế (Margin Call) khi vượt hạn mức vay.
- **Test 2.4 — Khủng hoảng Thanh khoản Ngân hàng (`IND=1` Bank Run & Bad Debt Write-off Test):**
  - Cho một tập đoàn vay nợ lớn từ Ngân hàng $B$ (`IND=1`) bị phá sản (`Bankruptcy`). Kiểm tra khoản lỗ nợ xấu được trừ vào `BadDebtReserves` và vốn tự có của Ngân hàng $B$, làm giảm hệ số `CAR%` và hạ bậc xếp hạng tín nhiệm của Ngân hàng $B$.
- **Test 2.5 — Cầu nối CAPEX/OPEX Capitalism Lab Không Tính Trùng (`Zero Double-Counting Bridge Test`):**
  - Cho tập đoàn WSR chi $\$50\text{M}$ tiền mặt xây 1 Nhà máy và 1 Cửa hàng bán lẻ của Capitalism Lab. Ngay tại tick giải ngân (trước khi nhà máy chạy), kiểm tra $\Delta \text{NetWorth} \equiv 0$ ($\text{Cash}$ giảm $\$50\text{M}$, `CapAssets` + `WorkingCap` tăng đúng $\$50\text{M}$).

### Tầng 3: Kiểm thử Đối chiếu Trực tiếp với `WSR.EXE` v10.0.22.3 (`Differential Oracle Testing`)
Tận dụng bản cài đặt `C:\Users\LENOVO\Downloads\Wall.Street.Raider.v10.0.22.3`:
- Trong thư mục `resources\app\services\wsr.js` và `ui.dll`, `WSR.EXE` v10.0.22.3 nhận biến môi trường `PORT` (WebSocket) và `REST_PORT` (HTTP REST) khi khởi chạy.
- Chúng ta có thể viết script kiểm thử tự động:
  1. Đọc trực tiếp trạng thái khởi đầu từ `GET http://127.0.0.1:<REST_PORT>/gamestate` của `WSR.EXE` v10.0.22.3 (bao gồm bảng cân đối `activeEntityFinancials`, lãi suất `primeRate`, giá cổ phiếu, lãi suất trái phiếu).
  2. Thực thi cùng một chuỗi lệnh (`Event 1020` Buy Stock, `Event 1030` Sell Stock, `Event 1310` Borrow Money, `Event 1420` Issue Bonds, `Event 625` Set Dividend, v.v.) trên cả `WSR.EXE` v10.0.22.3 và `eagle_capital_engine.py`.
  3. So sánh chênh lệch tuyệt đối trên toàn bộ các trường của `activeEntityFinancials` (`cash`, `tbills`, `workingCap`, `capAssets`, `stockPort`, `bondsOut`, `bankLoan`, `accTax`, `netWorth`, `stockPrice`, `credRating`).

### Tầng 4: Kiểm thử Độ ổn định Dài hạn & Hiệu năng Thời gian Thực (`Multi-Year Monte Carlo & <2ms Tick Benchmark`)
- Chạy mô phỏng liên tục **20 năm (80 quý / 7.200 ngày)** với đầy đủ `1,058+` tập đoàn hoạt động, AI tự động giao dịch, chu kỳ kinh tế mở rộng $\rightarrow$ suy thoái $\rightarrow$ phục hồi:
  - Không có bất kỳ giá trị `NaN`, `Inf`, số âm vô lý (như `SharesOutstanding <= 0`, `StockPrice < 0`, `PrimeRate <= 0`).
  - Phân phối tỷ suất lợi nhuận trên vốn (`ROE`), biên lợi nhuận ngành, và tỷ lệ vỡ nợ trái phiếu nằm trong dải kinh tế thực tế.
  - Thời gian thực thi mỗi tick (`step_tick`) đạt **$< 2.0\text{ ms}$** trên CPU đơn luồng để đảm bảo khi nhúng vào GTA San Andreas (`Project Eagle`) ở Giai đoạn B luôn giữ vững 60 FPS.

---

## 5. Bảng Tham Chiếu Nhanh Địa Chỉ Hàm & Struct Quan Trọng

| Thành phần | Phiên bản / File | Địa chỉ / Vị trí | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `BigLoop` (Master Simulation Loop) | `WSR.EXE` v8.70 / v10.0.22.3 | `0x004C602E` (`103 KB`) / `0x006BFE04` (`181 KB`) | Vòng lặp chính điều phối vĩ mô, ngành, báo cáo quý, cổ tức, thuế và AI thị trường. |
| `CorpInfoItems` (Balance Sheet & NetWorth) | `WSR.EXE` v8.70 | `0x004266F8` (`7,783 B`) | Tính toán toàn bộ các khoản mục Tài sản, Nợ phải trả và `NetWorth` theo 5 chế độ thực thể. |
| `StockPrice` (Equity Valuation) | `WSR.EXE` v8.70 | `0x0042C812` (`16,570 B`) | Định giá cổ phiếu kết hợp `NetWorth`, tăng trưởng `EPS`, cổ tức, uy tín quản trị và cung/cầu. |
| `CircControl` (Circular Ownership) | `WSR.EXE` v8.70 | `0x00480D92` (`5,301 B`) | Phát hiện và xử lý chuỗi sở hữu chéo vòng tròn giữa các tập đoàn. |
| `GetCredRating` (Credit Rating `0..9`) | `WSR.EXE` v8.70 | `0x0042B809` (`4,105 B`) | Xếp hạng tín nhiệm `AAA..D` dựa trên `D/E` (hoặc `CAR%` cho Ngân hàng) và độ phủ lãi vay. |
| `CorpTaxCalc` (Corporate Income Tax) | `WSR.EXE` v8.70 | `0x004F9803` (`3,443 B`) | Tính thuế TNDN, khấu trừ cổ tức liên công ty (`DRD`) và chuyển lỗ 4 năm (`LOSS1..4`). |
| `BankAlloc` (Bank Asset/Liability Mgmt) | `WSR.EXE` v8.70 | `0x0061B266` (`12,090 B`) | Quản lý danh mục cho vay, dự phòng nợ xấu, tiền gửi và vay liên ngân hàng cho `IND=1`. |
| `Bankruptcy` (Chapter 11 / Liquidation) | `WSR.EXE` v8.70 | `0x004E667C` (`26,329 B`) | Tái cấu trúc nợ, xóa sổ cổ đông cũ hoặc thanh lý tài sản khi vỡ nợ. |
| `InitUI` & `GameData` UDT Descriptor | `WSR.EXE` v10.0.22.3 | Call `@ 0x0040570A`, UDT `@ 0x0091F7B0` | Khởi tạo cầu nối bộ nhớ chia sẻ giữa PowerBASIC `WSR.EXE` và `ui.dll`. |
| `SyncGameData` | `WSR.EXE` v10.0.22.3 | `0x00708F1D` & `0x0070BB1E` | Đồng bộ biến toàn cục PowerBASIC sang struct `GameData` trước khi gọi `UpdateUI`. |
| `EventDispatch` (`GameEventType` `5..4201`) | `WSR.EXE` v10.0.22.3 | `0x0040652C..0x0040CE4C` (`26,912 B`) | Bộ điều phối trung tâm nhận lệnh giao dịch từ `ui.dll!PollEvent` và gọi các hàm `Front*`. |
| `SerializeEntityFinancials` | `ui.dll` v10.0.22.3 | `0x10042C54` | Đọc struct `GameData` và xuất JSON `activeEntityFinancials` (`aef`) cho Electron UI. |
| `SerializePlayerFinancials` | `ui.dll` v10.0.22.3 | `0x1003EFD6` | Đọc struct `GameData` và xuất JSON `activeEntityPlayerFinancials` (`aep`) cho Electron UI. |

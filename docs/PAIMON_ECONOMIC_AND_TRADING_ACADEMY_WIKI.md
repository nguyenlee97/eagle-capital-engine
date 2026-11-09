# 🎓 PAIMON ECONOMIC & TRADING ACADEMY — CẨM NANG & WIKI TOÀN TẬP
**(Interactive In-Game Guidance, Spotlight Tutorial, Inspect/Explain Mode, Full Textbook & Live `gpt-6-luna` AI Tutor)**

---

## 1. TỔNG QUAN TRIẾT LÝ & KIẾN TRÚC HỆ THỐNG

Trong **EagleCapitalEngine v2.0** (`http://127.0.0.1:8765`), người chơi (**`#1 Aether`**) bắt đầu tại mốc thời gian **`2010-Q1 (01/01)`** với số vốn khởi điểm vỏn vẹn **`$30,000` (`$0.03M` — Street Hustler Mode)** giữa một đại dương kinh tế gồm **1,078 tập đoàn**, **20 quỹ ETF** và **320 nhà đầu tư AI thuộc 24 Archetypes**.

Để giúp người chơi mới hoàn toàn (chưa từng chơi *Wall Street Raider* lẫn *Capitalism Lab*, chưa rành tài chính/đọc nến) làm chủ mọi nút bấm và con số ngay trên màn hình, **Paimon Economic & Trading Academy** được tích hợp trực tiếp vào Web Workstation với **2 Trụ cột cốt lõi**:

1. **Trụ cột 1 — Hệ thống Bài giảng Tương tác, Spotlight Cầm Tay Chỉ Việc & Chế độ Soi Giải Thích (`Interactive Curriculum, Spotlight & Inspect Mode`)**:
   - **Giáo trình 9 Học phần (`M0`..`M8`) & 36 Bài thực hành có kiểm chứng (`M0_Q1`..`M8_Q4`)**: Mỗi bài học gồm lời giảng sinh động của Paimon, công thức toán học đóng khung (`📐 Công thức / Quy tắc Toán học`), nhiệm vụ thực hành cụ thể (`🎯 Nhiệm vụ thực hành cho Aether`), nút **`🎯 Chỉ Tận Nơi (Spotlight)`** vẽ vòng sáng vàng nhấp nháy + mũi tên chỉ thẳng vào nút bấm/biểu đồ/ô nhập liệu trên cả 4 Tab, và nút **`⚡ Làm Mẫu (Auto-Step)`** thực thi mẫu thao tác đó ngay trên giao diện.
   - **Tự động Kiểm chứng Hoàn thành (`Auto-Verify DOM & Engine State`)**: Khi Aether thực hiện đúng thao tác (hoặc bấm `⚡ Làm Mẫu`), hệ thống tự động bắt sự kiện DOM / trạng thái Engine, đánh dấu hoàn thành Quest (`✓`), lưu tiến độ xuống `saves/paimon_academy_progress.json` và chuyển sang bước tiếp theo.
   - **Chế độ Soi & Giải thích Tự do (`🔍 Inspect: ON/OFF`)**: Khi bật nút này trên thanh công cụ trên cùng, rê chuột hoặc bấm vào bất kỳ nút bấm, ô nhập liệu, bảng biểu hay biểu đồ nến nào trên cả 4 Tab sẽ hiện ngay hộp giải thích Tiếng Việt của Paimon (hơn **55 mục từ điển chuyên sâu**: *Thành phần này là gì? Công thức tính ra sao? Khi nào nên dùng?*).
   - **Sách Giáo Khoa & Từ Điển Kinh Tế Học Toàn Tập (`📖 Sách Kinh Tế`)**: Cửa sổ tra cứu toàn màn hình tổng hợp trọn vẹn 9 Học phần (36 bài giảng) và 55+ mục từ điển thuật ngữ, hỗ trợ tìm kiếm tức thì theo từ khóa (`RSI`, `Hammer`, `Doji`, `P/B`, `ROCE`, `3x3`, `DRD`, `SpinOff`, `Swap`...) và nhảy thẳng tới bài thực hành tương ứng.

2. **Trụ cột 2 — Cố Vấn Giải Đáp Trực Tiếp Theo Ngữ Cảnh Màn Hình (`Live Context-Aware AI Tutor — gpt-6-luna`)**:
   - Ngay bên dưới bảng **Paimon Academy** là khung **Chat Hỏi Đáp Chuyên Sâu** kết nối trực tiếp tới model **`gpt-6-luna`** (kèm cơ chế fallback xác định `100%` dựa trên dữ liệu thực khi offline).
   - Mỗi khi Aether bấm các nút hỏi nhanh (`🕯️ Giải thích Nến & RSI đang xem`, `📊 Phân tích Mã đang chọn (P/B + Kỹ thuật)`, `🏭 Tối ưu Mặt bằng 3×3 hiện tại`, `💡 Gợi ý Bước Tiếp Theo cho $30k`) hoặc gõ câu hỏi bất kỳ, Backend tự động đính kèm gói **`Live Telemetry Context`** chứa toàn bộ con số đang hiển thị trên màn hình:
     * Ngày giờ & Vĩ mô (`2010-Qx`, `GDP Growth`, `CPI Inflation`, `Prime Rate`, `Unemployment`, giá `Dầu`, `Vàng`, `BTC`, `WSR Index`).
     * Trạng thái ví của `#1 Aether` (`Net Worth`, `Cash`, `Debt`, `Credit Rating`, danh mục `Long/Short`, công ty con đang kiểm soát).
     * Toàn bộ thông số cơ bản của tập đoàn đang chọn trên bảng (`Stock Price`, `Book Value/sh`, `P/B`, `ROCE`, `EPS`, `Dividend`, `Public Float %`, `Cash`, `Debt`, `CapLab EBIT`).
     * Toàn bộ thông số kỹ thuật trên **Bảng Nến Nhật `#ohlcv-canvas`** đang mở (`Open`, `High`, `Low`, `Close`, `Volume`, `MA7`, `MA20`, `Bollinger Upper/Lower`, `RSI(14)`, `Candlestick Pattern`).
     * Trạng thái nhà máy/cửa hàng **Capitalism Lab `3×3`** đang chọn (`Firm Type`, `Product`, `Unit Price`, `Market Share`, `Quality`, `Brand`, `Revenue`, `EBIT`, `Supply Chain Shield`, và cấu hình 9 ô `Slot #1..#9`).

---

## 2. HƯỚNG DẪN SỬ DỤNG CÁC CÔNG CỤ CỦA PAIMON TRÊN GIAO DIỆN

Trên **Thanh Công Cụ Trên Cùng (Top Header Bar)** của `http://127.0.0.1:8765`, bạn có 3 nút điều khiển màu vàng kim của Paimon:

| Nút bấm trên Header | ID DOM | Chức năng chi tiết |
|---|---|---|
| **`🎓 Paimon Academy`** | `#btn-paimon-academy-toggle` | Bật / tắt bảng **Paimon Economic & Trading Academy** ở góc phải màn hình. Bảng này có thể thu gọn (`_`) hoặc mở rộng bất cứ lúc nào mà không che khuất bàn giao dịch. |
| **`🔍 Inspect: OFF / ON`** | `#btn-paimon-inspect-toggle` | Bật **Chế độ Soi & Giải thích Tự do**. Khi bật (`ON`), rê chuột vào bất kỳ nút bấm, cột bảng, hay cây nến nào để đọc giải thích Tiếng Việt, công thức toán học và mẹo thực chiến từ Paimon. |
| **`📖 Sách Kinh Tế`** | `#btn-paimon-textbook-modal` | Mở cửa sổ **Sách Giáo Khoa & Từ Điển Kinh Tế Học Toàn Tập** để đọc liền mạch cả 9 Học phần (36 bài học) và tra cứu 55+ thuật ngữ tài chính/sản xuất. |

Ngoài ra, ngay trên **Bảng Nến Nhật (`#ohlcv-canvas`)** ở giữa Tab 1:
- **Rê chuột trực tiếp lên từng cây nến**: Hệ thống sẽ đóng khung vàng quanh cây nến đó và hiển thị **Giải phẫu chi tiết cây nến đang trỏ chuột** ngay tại thanh `#chart-explain-banner` bên dưới biểu đồ (*Nến Tăng/Giảm bao nhiêu `%`, tỷ lệ `% Thân nến`, `% Râu trên`, `% Râu dưới`, ý nghĩa lực mua/bán của cây nến đó*).
- **Bấm vào nhãn Mẫu Nến (`#chart-pattern-badge`) hoặc `RSI(14)` (`#chart-rsi-badge`)**: Hiển thị giải thích chuyên sâu về mẫu hình nến hiện tại (`Doji`, `Hammer`, `Shooting Star`, `Bullish/Bearish Engulfing`, `Marubozu`) và trạng thái quá mua/quá bán của `RSI(14)`.

---

## 3. CẨM NANG ĐỌC NẾN NHẬT (OHLCV) & PHÂN TÍCH KỸ THUẬT CHO NGƯỜI MỚI

### 3.1. Giải phẫu một cây Nến Nhật (`OHLCV`)
Mỗi cây nến đại diện cho cuộc chiến giữa phe Mua (Bò) và phe Bán (Gấu) trong 1 nhịp thời gian:
- **`O` (Open — Giá mở cửa)** & **`C` (Close — Giá đóng cửa)**: Tạo thành **Thân nến (Real Body)**:
  * **Nến Xanh (`Close >= Open`)**: Phe Mua thắng thế, đẩy giá đóng cửa cao hơn lúc mở cửa.
  * **Nến Đỏ (`Close < Open`)**: Phe Bán thắng thế, đè giá đóng cửa thấp hơn lúc mở cửa.
- **`H` (High — Giá cao nhất)** & **`L` (Low — Giá thấp nhất)**: Tạo thành **Râu nến trên (`Upper Wick`)** và **Râu nến dưới (`Lower Wick`)**:
  * **Râu dưới dài (`Lower Wick >= 45%` tổng biên độ `H - L`)**: Giá từng bị đạp xuống rất sâu nhưng có lực cầu bắt đáy mạnh mẽ đẩy ngược lên lại.
  * **Râu trên dài (`Upper Wick >= 45%` tổng biên độ `H - L`)**: Phe mua cố đẩy giá lên đỉnh cao nhưng bị phe bán xả hàng dội ngược xuống.
- **`V` (Volume — Khối lượng giao dịch)**: Các cột màu xanh/đỏ ở đáy biểu đồ. Một pha bứt phá (`Breakout`) hoặc đảo chiều chỉ thực sự đáng tin cậy khi đi kèm cột `Volume` cao vọt!

### 3.2. Năm Mẫu Hình Nến Đảo Chiều & Tiếp Diễn Quan Trọng Nhất
1. **`Doji (Lưỡng Lự)`**: $|\text{Close} - \text{Open}| \le 12\% \times (\text{High} - \text{Low})$. Thân nến mỏng dính như sợi chỉ — phe Mua và phe Bán giằng co bất phân thắng bại, báo hiệu xu hướng cũ đang cạn lực.
2. **`Hammer (Nến Búa — Đảo Chiều Tăng)`**: Râu dưới dài gấp $\ge 2$ lần thân nến, râu trên rất ngắn. Xuất hiện ở vùng đáy khi phe bán cố đạp giá xuống nhưng phe mua vét sạch hàng đẩy giá đóng cửa lên cao — tín hiệu tạo đáy cực đẹp!
3. **`Shooting Star (Sao Băng — Đảo Chiều Giảm)`**: Râu trên dài gấp $\ge 2$ lần thân nến, nằm ở vùng đỉnh. Báo hiệu phe mua bị xả hàng úp sọt từ trên đỉnh — nên chốt lời hoặc chuẩn bị bán khống (`Short`).
4. **`Bullish / Bearish Engulfing (Nhấn Chìm Tăng / Giảm)`**: Cây nến sau có thân to nuốt trọn toàn bộ thân cây nến ngược màu trước đó — cú đảo chiều áp đảo hoàn toàn.
5. **`Bullish / Bearish Marubozu (Cường Lực)`**: Thân nến chiếm $> 80\%$ toàn bộ chiều dài cây nến, hầu như không có râu — một phe kiểm soát tuyệt đối phiên giao dịch.

### 3.3. Bộ Ba Chỉ Báo Kỹ Thuật Trên Biểu Đồ (`MA7/MA20`, `Bollinger Bands`, `RSI(14)`)
- **Đường Trung bình động `MA7` (Vàng) & `MA20` (Tím)**:
  $$\text{MA}_n = \frac{1}{n}\sum_{i=0}^{n-1} P_{t-i}$$
  Khi đường ngắn hạn `MA7` cắt lên trên đường dài hạn `MA20` (**Golden Cross**), xu hướng tăng ngắn hạn hình thành. Ngược lại, `MA7` cắt xuống dưới `MA20` (**Death Cross**) báo hiệu xu hướng giảm.
- **Dải `Bollinger Bands (20, 2σ)`**:
  $$\text{Upper Band} = \text{MA}_{20} + 2\sigma_{20}, \qquad \text{Lower Band} = \text{MA}_{20} - 2\sigma_{20}$$
  Khoảng $95\%$ biến động giá nằm trong hai biên này. Khi hai biên co thắt hẹp lại (**Bollinger Squeeze**), thị trường đang nén lò xo chuẩn bị nổ sóng lớn. Khi giá chạm biên dưới kèm nến `Hammer` và `RSI < 30`, xác suất bật tăng hồi phục rất cao.
- **Chỉ số Sức mạnh Tương đối `RSI(14)`** (Thang điểm `0` – `100`):
  $$\text{RSI}(14) = 100 - \frac{100}{1 + \frac{\text{AvgGain}_{14}}{\text{AvgLoss}_{14}}}$$
  * **`RSI < 30` (`OVERSOLD` — Quá bán)**: Giá bị bán tháo quá đà, canh tìm điểm mua bắt đáy.
  * **`RSI > 70` (`OVERBOUGHT` — Quá mua)**: Giá tăng quá nóng, hạn chế mua đuổi (`FOMO`), canh chốt lời.
  * **`30 <= RSI <= 70` (`NEUTRAL`)**: Vùng trung tính, giao dịch thuận theo xu hướng `MA7/MA20`.

---

## 4. TỔNG HỢP 9 HỌC PHẦN (`M0`..`M8`) & 36 BÀI THỰC HÀNH (`QUESTS`)

| Học phần | Tên Học phần | Các Bài thực hành (`Quests`) & Kiến thức trọng tâm |
|---|---|---|
| **`M0`** | **Làm Quen Bàn Làm Việc & Quy Luật Vận Hành Cơ Bản** | • `M0_Q1`: Bức tranh tổng thể 4 Tab (Sàn Phố Wall WSR <-> Đế chế Sản xuất CapLab `3×3` <-> 320 AI Investors <-> Vĩ mô & Lưu trữ).<br>• `M0_Q2`: Phương trình Kế toán bất biến $\text{Total Assets} \equiv \text{Total Liabilities} + \text{Net Worth}$ và chỉ số tín nhiệm `Credit Rating` (`AAA`..`D`).<br>• `M0_Q3`: Tư cách pháp nhân `Acting As` (Giao dịch bằng ví cá nhân `#1 Aether` vs. dùng tiền của Công ty con).<br>• `M0_Q4`: Nhịp thời gian `+1 Subtick` (`< 2 ms`) vs. `+1 Quarter` (`90 ngày` quyết toán thuế, lãi vay, lương, cổ tức). |
| **`M1`** | **Kinh Tế Học Vĩ Mô & Chu Kỳ Tiền Tệ** | • `M1_Q1`: Đọc thanh Vĩ mô (`GDP Growth`, lạm phát `CPI`, lãi suất cơ bản `Prime Rate`).<br>• `M1_Q2`: Biểu đồ giá Dầu thô (`OIL`), Vàng (`GOLD`), `BTC/USD` và tác động chi phí năng lượng lên nhà máy.<br>• `M1_Q3`: Mô phỏng cú sốc Stagflation (`S2: Oil $135`) & Fed nâng lãi suất.<br>• `M1_Q4`: Trú ẩn vào Trái phiếu Chính phủ (`GovBond`) và Vàng khi vĩ mô bất ổn. |
| **`M2`** | **Nghệ Thuật Đọc Biểu Đồ Nến Nhật (`OHLCV`) & PTKT** | • `M2_Q1`: Giải phẫu cây nến Nhật (`Open`, `High`, `Low`, `Close`, `Volume`, Thân nến & Râu nến) bằng cách rê chuột trực tiếp lên `#ohlcv-canvas`.<br>• `M2_Q2`: Nhận diện 5 mẫu nến đảo chiều (`Doji`, `Hammer`, `Shooting Star`, `Engulfing`, `Marubozu`).<br>• `M2_Q3`: Kết hợp xu hướng `MA7/MA20` và dải biến động `Bollinger Bands (20, 2σ)`.<br>• `M2_Q4`: Đọc xung lực `RSI(14)` (`Quá mua > 70` vs. `Quá bán < 30`) để chọn thời điểm vào lệnh chuẩn xác. |
| **`M3`** | **Đọc Bảng Cân Đối Kế Toán & Đầu Tư Cổ Phiếu/ETF Với `$30,000`** | • `M3_Q1`: Lọc ngành (`Banks/Insur`, `ETFs`, `All Corps`) và phân biệt Tập đoàn niêm yết vs. Nhà đầu tư cá nhân (`320 Investors`).<br>• `M3_Q2`: Đọc Bảng Cân Đối Kế Toán (`Cash`, `CapLab R&D/Firms`, `Debt`, `P/B`, `ROCE`, `EPS`, `Public Float >= 25%`).<br>• `M3_Q3`: Mua lô nhỏ `100sh` (`Micro-Lot`) phù hợp túi tiền `$30,000` và kiểm tra `Est. Cost` (gồm phí `0.15%`).<br>• `M3_Q4`: Theo dõi lãi/lỗ trên bảng `Holdings`, chốt lời nhanh bằng nút `Sell All` và đầu tư chứng chỉ quỹ `ETF (#1581..#1600)`. |
| **`M4`** | **Trái Phiếu, Tín Dụng Ngân Hàng & Bán Khống (`Short`)** | • `M4_Q1`: Giao dịch Trái phiếu Chính phủ (`GovBond`) và Trái phiếu Doanh nghiệp (`CorpBond`) với lô nhỏ `$5k`.<br>• `M4_Q2`: Cơ chế Đòn bẩy Tín dụng (`Borrow Loan` / `Repay Loan`) theo lãi suất $\text{Rate} = \text{Prime} + \text{Spread}_{\text{Rating}}$.<br>• `M4_Q3`: Cơ chế Bán khống (`Short Stock`) kiếm lời khi giá giảm & rủi ro cháy tài khoản (`Short Squeeze`).<br>• `M4_Q4`: Mua trả kho đóng vị thế bán khống (`Cover Short`) và cầu nối tiền tệ hai chiều `GTA SA Wallet Bridge`. |
| **`M5`** | **Khởi Nghiệp Thực Chiến (`$30k` Startup) & Mặt Bằng `3×3`** | • `M5_Q1`: Thành lập `Bootstrapped Startup` (`$20,000` vốn tự có + `$60,000` vay ngân hàng = `$80,000` vốn điều lệ).<br>• `M5_Q2`: Giải phẫu Mặt bằng Nội khu `3×3` (`9 ô` bộ phận + `18` mũi tên luồng hàng nội bộ) và thay đổi chức năng từng ô (`PURCH`, `SALES`, `MKT`, `R&D`, `EXTERN`).<br>• `M5_Q3`: Huấn luyện nhân sự cả 9 ô (`Train All 9 Units +Lv`) để tăng năng suất `(1 + 0.12 * (Lv - 1))` và rút tiền lời từ Startup về ví Aether qua Cổ tức (`Set Dividend`).<br>• `M5_Q4`: Xây dựng cửa hàng mới với nút vốn siêu nhỏ `$15k (Micro Store)` và tinh chỉnh công thức cạnh tranh `PRQ` ($\text{Score} = w_P \frac{100}{P} + w_Q Q + w_B B$). |
| **`M6`** | **Chuỗi Cung Ứng Đa Tầng, R&D Công Nghệ & Tập Đoàn Đa Ngành** | • `M6_Q1`: Khám phá 8 nhóm cơ sở kinh tế (`Factory`, `Retail`, `R&D`, `Mine/Well`, `Farm`, `Real Estate`, `Bank/HQ`, `Service`).<br>• `M6_Q2`: Chuỗi cung ứng đa đầu vào (`Input 1..3 -> Output`) và Khiên Tự Chủ Nội Bộ (`INTERNAL SHIELD` chống đứt gãy nguồn cung).<br>• `M6_Q3`: Đầu tư Viện R&D nâng cấp `38` ngành công nghệ (`Tech Level -> Product Quality`).<br>• `M6_Q4`: Liên thông lợi nhuận 2 chiều: `EBIT` từ các nhà máy ở Tab 2 tự động chảy về két tiền mặt (`Cash`) và đẩy giá cổ phiếu trên Sàn WSR ở Tab 1. |
| **`M7`** | **Vũ Khí Tài Chính Cấp Cao — Options, Futures, Swaps, Thuế & M&A** | • `M7_Q1`: Giao dịch Hợp đồng Tương lai Hàng hóa (`OIL`, `GOLD`, `WHEAT`) & `BTC/USD`.<br>• `M7_Q2`: Quyền chọn Mua (`Buy Call`), Quyền chọn Bán (`Buy Put`) và Bán quyền chọn thu phí (`Write Call`) định giá theo mô hình Black–Scholes.<br>• `M7_Q3`: Hợp đồng Hoán đổi Lãi suất (`Interest Rate Swap — Pay Fixed 4.5%, Receive Floating Prime`) để khóa rủi ro lãi suất.<br>• `M7_Q4`: Thâu tóm Tập đoàn (`Control >= 20%`), Tách công ty con miễn thuế (`80% Tax-Free Spin-Off`), Khấu trừ thuế cổ tức tập đoàn (`DRD 70%–100%`) và Khởi kiện Thương mại (`Lawsuit`). |
| **`M8`** | **Sinh Tồn Qua 6 Đại Khủng Hoảng (`S1`–`S6`) & 320 AI Archetypes** | • `M8_Q1`: Phân tích bảng xếp hạng `320 AI Investors` thuộc `24 Archetypes` (Cá mập Phố Wall vs. hội `$30k Street Hustlers`).<br>• `M8_Q2`: Đọc nhật ký phá sản (`Wipeout / Margin Call Feed`) để rút bài học quản trị rủi ro đòn bẩy.<br>• `M8_Q3`: Thử lửa qua 6 kịch bản đại khủng hoảng vĩ mô (`S1` Bong bóng AI, `S2` Dầu `$135`, `S3` Đứt cáp Đài Loan, `S4` Ngân hàng sụp đổ, `S5` Siêu lạm phát, `S6` Chống độc quyền).<br>• `M8_Q4`: Lưu trữ và Khôi phục Trạng thái Nguyên tử (`Save / Load Full-Fidelity State`) bảo toàn `100%` tài sản (`$0.000000` sai số). |

---

## 5. CẤU TRÚC GÓI `LIVE TELEMETRY CONTEXT` & CÁCH ĐẶT CÂU HỎI CHO PAIMON (`gpt-6-luna`)

Mỗi khi bạn gửi câu hỏi trong khung **Chat Hỏi Đáp Chuyên Sâu Với Paimon**, hàm `build_live_telemetry_context()` trong [`paimon_academy.py`](file:///c:/Users/LENOVO/Desktop/GTA/staging/project-eagle/eagle-capital-engine-20261108/paimon_academy.py) tự động trích xuất trạng thái thực của thế giới tại đúng mili-giây đó và đính kèm vào prompt gửi tới `gpt-6-luna`:

```text
[BẢN CHỤP TRẠNG THÁI THỰC TẾ TRÊN MÀN HÌNH CỦA AETHER]
- Thời gian & Vĩ mô: 2010-Q1 (01/01) | GDP Growth=2.50% | CPI Inflation=2.00% | Prime Rate=3.25% | Unemployment=5.00%
- Giá Tài sản Vĩ mô: Dầu (OIL)=$75.00 | Vàng (GOLD)=$1800.00 | BTC=$42000.00 | WSR Index=1000.00
- Bài học hiện tại: M2 (Nghệ Thuật Đọc Biểu Đồ Nến Nhật OHLCV & Phân Tích Kỹ Thuật) -> Quest M2_Q1
- Ví của #1 Aether: NetWorth=$0.0300M ($30,000) | Cash=$0.0300M ($30,000) | Debt=$0.0000M | Credit=BBB
- Tập đoàn đang chọn xem (#27 WFC): Giá CP=$24.85 | Book/sh=$22.40 | P/B=1.11x | ROCE=11.4% | EPS=$2.15 | Public Float=100.0%
- Biểu đồ Nến Nhật đang mở (SELECTED_CORP): Nến cuối O=24.10, H=25.05, L=23.60, C=24.85, Vol=145 | MA7=24.32, MA20=23.95 | Bollinger=[22.80 .. 25.10] | RSI(14)=54.2 | Mẫu nến: Hammer (Nến Búa - Tín hiệu Đảo Chiều Tăng)
- Nhà máy/Cửa hàng CapLab 3x3 đang chọn (Firm #1): Loại=FACTORY | Sản phẩm=SMARTPH | Giá bán=$440 | Thị phần=18.5% | EBIT=$4.250M | Chuỗi cung ứng=INTERNAL SHIELD
```

Nhờ gói dữ liệu trực tiếp này, bạn có thể hỏi Paimon những câu hỏi cực kỳ cụ thể như:
- *"Paimon ơi, cây nến vừa xuất hiện trên biểu đồ có râu dưới dài nghĩa là gì? Kết hợp với RSI(14) hiện tại thì có nên mua 100 cổ phiếu mã đang chọn không?"*
- *"So sánh giữa P/B, ROCE và tín hiệu MA7/MA20 của công ty đang chọn, tại sao đây là khoản đầu tư tốt hay xấu cho số vốn $30,000 của tôi?"*
- *"Nhìn vào mặt bằng 3×3 của nhà máy đang chọn, tôi nên đổi ô nào hoặc huấn luyện nhân sự ra sao để tăng biên lợi nhuận EBIT?"*

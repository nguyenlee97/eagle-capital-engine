# Cẩm Nang Toàn Tập Tính Năng, Cơ Chế & Hướng Dẫn Chơi EagleCapitalEngine v2.0 (WSR v10 × Capitalism Lab v11)

**Tài liệu nền tảng (Stepping Stone Document) cho Người chơi & Hệ thống Paimon Interactive Academy**  
**Mốc thời gian khởi đầu:** `2010-Q1 (01/01)` (Đồng bộ timeline GTA San Andreas — Project Eagle)  
**Địa chỉ Web Workstation:** `http://127.0.0.1:8765`

---

## Phần 1: Giải Đáp Trực Tiếp Các Thắc Mắc Khi Vừa Vào Game & Các Lỗi Đã Khắc Phục Triệt Để

Khi bạn mở giao diện lần trước và bấm thử các tính năng, bạn đã gặp một loạt hiện tượng khó hiểu. Dưới đây là nguyên nhân chính xác và cách hệ thống đã được sửa lại:

### 1.1. "Vừa vào game bấm vào list Entity thấy một đống thứ thì đó là gì?"
Trong thế giới của **EagleCapitalEngine**, mọi chủ thể tham gia thị trường đều là một **Thực thể Tài chính (`FinancialEntity`)** có mã số định danh `#ID`:
- **`#1` (`Aether`)**: Chính là **BẠN** — người chơi cá nhân khởi đầu năm `2010-Q1` với **`$30,000` (`$0.03M`) tiền mặt** (hoặc `$1,000M` nếu bật chế độ Sandbox).
- **`#2..#5` và `#2001..#2320` (`320 Investors` — Chế độ `PLAYER_INDIVIDUAL` / `AI-INV`)**: Là **324 nhà đầu tư cá nhân và quỹ AI** đang sống và giao dịch cùng bạn trong thế giới này (từ các cá con `$30k` khác cho tới các tỷ phú như Warren B., Carl I., Jim S.). **Lưu ý quan trọng:** Đây là *con người / nhà đầu tư*, không phải công ty cổ phần niêm yết trên sàn, nên họ **không phát hành cổ phiếu** (cột `Price` của họ hiện dấu `—`). Bạn bấm vào họ ở mục `320 Investors` là để **soi danh mục đầu tư của họ** xem họ đang mua/bán khống mã nào!
- **`#11..#1580` (`All Corps` / `Banks/Insur` — Công ty Cổ phần Niêm yết)**: Là **1,058 tập đoàn đang hoạt động** (và 522 khe dự phòng `#61..` dành cho công ty Startup mới thành lập), chia làm 3 loại:
  1. `BANK` (`COMMERCIAL_BANK`, ngành #1): 50 Ngân hàng thương mại (như `#11 CMB`, `#13 WFC`, `#14 BAC`, `#27 UBS`) — nơi nhận tiền gửi và cho bạn/các công ty vay tiền (`Borrow Loan`).
  2. `INSUR` (`INSURANCE_COMPANY`, ngành #2): 35 Tập đoàn bảo hiểm.
  3. `IND` (`INDUSTRIAL_HOLDING`, ngành #3..#70): 973 Tập đoàn sản xuất, bán lẻ, công nghệ, dầu khí, khai khoáng, bất động sản, phần mềm...
- **`#1581..#1600` (`ETFs (20)` — Quỹ Hoán Đổi Danh Mục `ETF_FUND`)**: Là **20 quỹ ETF niêm yết** (quỹ chỉ số ngành, quỹ trái phiếu, quỹ đòn bẩy `2x Bull` / `-2x Bear`). Bạn mua bán chứng chỉ quỹ ETF y hệt như mua cổ phiếu!

### 1.2. "`Aether Ventures #61 (S61)` là cái gì mà lúc nãy vừa vào đã thấy và tự mua được?"
- **Nguyên nhân lúc nãy**: Bộ kiểm thử tự động `run_workstation_e2e_qa.py` chạy trực tiếp trên server đang mở và ở bước cuối đã bấm nút **Lập công ty Startup (`Incorporate Bootstrapped Startup`)**, tạo ra công ty con `#61 Aether Ventures (S61)` rồi để nguyên trạng thái đó trên server mà chưa bấm `Reset World`. Khi bạn mở trình duyệt lên, bạn nhìn thấy trạng thái sau khi test đã chạy xong.
- **Đã khắc phục**:
  1. Cuối mọi bài test tự động, hệ thống luôn gọi `Reset World` để trả server về trạng thái **New Game `2010-Q1` sạch 100%** (`Acting As: #1 Aether ($30,000)`).
  2. Khi bạn tự lập công ty Startup (ví dụ `#61 S61`), Engine đã chặn việc công ty tự đặt lệnh `Buy Long` mua chính cổ phiếu của mình (`buyer_id == target_corp_id`), đồng thời giao diện không bao giờ tự điền mã công ty bạn đang điều khiển vào ô `TARGET CORP ID`.

### 1.3. "Sao thử mua cổ phiếu bên `All Corps` lại bị báo lỗi `BUY_STOCK: Insufficient public float shares`?"
- **Nguyên nhân lúc nãy**:
  1. Trong dữ liệu gốc `wsr101.dat`, có một số công ty con bị công ty mẹ nắm giữ `100%` cổ phần, khiến lượng cổ phiếu trôi nổi ngoài thị trường (`Public Free Float`) bằng `0`.
  2. Ngoài ra, ở chế độ `$30,000`, các ô nhập liệu mặc định lúc trước đang để số lượng của tỷ phú (`0.01M = 10,000 cổ phiếu` trị giá hơn `$350,000`, hoặc trái phiếu `$10M`).
- **Đã khắc phục**:
  1. Khi khởi tạo thế giới `2010-Q1`, **100% các tập đoàn niêm yết (`#11..#1600`) đều được đảm bảo giữ tối thiểu `25%` (`>= 25.0M` cổ phiếu = 25 triệu cổ phiếu) trôi nổi tự do (`Public Float`)** trên sàn. Ngay cả các công ty Startup mới thành lập cũng phát hành `20%` cổ phần ra `Public Float` (Founder nắm `80%`).
  2. Mặc định ô `Shares (M)` ở chế độ `$30k` được đặt sẵn là **`0.0001` (`100 cổ phiếu`)**, ô `Notional ($M)` là **`0.005` (`$5,000`)**, và ô `Loan ($M)` là **`0.01` (`$10,000`)**. Bạn bấm vào **bất kỳ công ty nào** trong `All Corps`, `Banks/Insur`, hay `ETFs (20)` rồi bấm `Buy Long` đều khớp lệnh thành công ngay lập tức!

### 1.4. "Sao nhiều cổ phiếu giá y xì nhau (`$11.3`, `$14.91`) và có công ty Net Worth âm quá trời (`-$2.7B`, hạng `D`) ngay lúc đầu?"
- **Nguyên nhân lúc nãy**: Khi nạp bảng cân đối từ `wsr101.dat` cho một số ngân hàng (như `#15 MFG`, `#16 MBK`), khoản nợ trái phiếu phát hành (`straight_bonds_out`) chưa được cộng tương ứng vào quy mô tài sản cho vay ban đầu (`base_scale`), làm Tổng Nợ > Tổng Tài Sản -> **Net Worth bị âm ngay từ ngày đầu tiên**. Khi Net Worth âm, giá trị sổ sách (`Book Value`) chạm sàn `$0.05`, khiến công thức định giá cổ phiếu trả về cùng một mức giá sàn giống hệt nhau (`$14.91` / `$11.3`).
- **Đã khắc phục**: Chuẩn hóa toàn bộ quy mô tài sản khởi đầu theo đúng cấu trúc nợ của từng tập đoàn trong `_initialize_world()`, đồng thời khởi tạo `ROCE%`, `EPS` và hệ số định giá `P/B` riêng biệt cho từng công ty. Hiện tại ở `2010-Q1`, **không có bất kỳ công ty nào bị âm Net Worth lúc khởi đầu** và mỗi mã cổ phiếu đều có mức giá riêng biệt, tự nhiên.

### 1.5. "Mấy cái nút trên biểu đồ nến (`#13 WFC`, `BTC/USD`, `OIL`, `GOLD`, `WSR Index`, `Pattern`, `RSI`, `MA7/20`, `Bollinger`) là gì mà lúc nãy bấm không thấy gì?"
- **Nguyên nhân lúc nãy**: Lỗi tên biến JavaScript (`latestDashboard` thay vì `lastDashboardData`) trong hàm xử lý nút bấm biểu đồ khiến khi bạn click các nút trên biểu đồ, hàm vẽ lại canvas không được gọi!
- **Đã khắc phục & Nâng cấp**:
  1. Đã sửa dứt điểm lỗi biến JS và tắt cache HTML để trình duyệt luôn nhận code mới nhất.
  2. Giờ đây khi bạn bấm vào **bất kỳ nút nào trên thanh biểu đồ nến**, biểu đồ sẽ lập tức vẽ lại kèm **Watermark tên tài sản & giá hiện tại in đậm ngay trong lòng biểu đồ**, đồng thời thanh giải thích **`💡 #chart-explain-banner`** ngay dưới đáy biểu đồ sẽ hiện chữ tiếng Việt giải thích chi tiết nút bạn vừa bấm:
     - **`#13 WFC` (Selected Stock)**: Xem biểu đồ nến 36 kỳ của mã cổ phiếu/ETF đang chọn.
     - **`BTC/USD`**: Xem biểu đồ nến của Bitcoin (đồng thời tự chuyển ô chọn tài sản phái sinh bên phải sang `BTC`).
     - **`OIL`**: Xem biểu đồ nến giá Dầu thô WTI (`$/thùng`).
     - **`GOLD`**: Xem biểu đồ nến giá Vàng giao ngay (`$/oz`).
     - **`WSR Index`**: Xem biểu đồ nến Chỉ số Chứng khoán Tổng hợp toàn thị trường.
     - **Nút Mẫu Nến (`Bullish Trend Candle` / `Hammer` / `Doji` / `Engulfing`...)**: Bấm vào sẽ giải thích mẫu hình nến hiện tại đang báo hiệu phe Mua hay phe Bán thắng thế.
     - **Nút `RSI(14)`**: Bấm vào sẽ giải thích chỉ số sức mạnh tương đối hiện tại đang ở vùng Quá mua (`>=70`), Quá bán (`<=30`) hay Trung tính (`30–70`).
     - **Nút `MA7/20`**: Bật/tắt 2 đường trung bình động `MA7` (xanh cyan) và `MA20` (vàng cam) kèm giải thích điểm cắt `Golden Cross / Death Cross`.
     - **Nút `Bollinger`**: Bật/tắt dải `Bollinger Bands (20, ±2σ)` màu tím kèm giải thích biên hỗ trợ/kháng cự.

---

## Phần 2: Giải Mã Thanh Thời Gian & Thanh Chỉ Số Vĩ Mô Trên Cùng (Top Header & Time Controls)

### 2.1. Sáu Ô Chỉ Số Vĩ Mô Trên Cùng (Macro Ribbon)
Từ trái sang phải:
1. **`DATE / QTR` (`2010-Q1 (01/01)`)**: Thời gian hiện tại trong game (Năm `2010`, Quý `1`, Tháng `01`, Ngày `01`).
2. **`GDP (CAPLAB IMPULSE)` (`2.8% (+0.0455%)`)**:
   - Số đầu (`2.8%`): Tốc độ tăng trưởng kinh tế vĩ mô (`GDP Growth`). Khi GDP cao, doanh thu các công ty và nhu cầu mua sắm của người dân trong các thành phố đều tăng.
   - Số trong ngoặc (`+0.0455%`): Đóng góp thực tế từ các nhà máy/cửa hàng bên **Capitalism Lab** bơm ngược lên nền kinh tế vĩ mô WSR!
3. **`CPI INFLATION / PRIME` (`2.4% / 6.5%`)**:
   - `CPI Inflation` (`2.4%`): Tỷ lệ lạm phát. Nếu lạm phát tăng quá cao, chi phí vận hành nhà máy (`OPEX`) tăng và Ngân hàng Trung ương sẽ tăng lãi suất.
   - `Prime Rate` (`6.5%`): **Lãi suất cơ bản** của ngân hàng. Đây là con số quyền lực nhất Phố Wall:
     * Khi `Prime Rate` **tăng** (ví dụ kịch bản `S1` lên `18%`): Lãi vay ngân hàng đắt đỏ, định giá `P/E` của cổ phiếu bị ép giảm, giá Trái phiếu giảm mạnh, người dân ít thuê nhà (`REIT Occupancy` giảm).
     * Khi `Prime Rate` **giảm**: Tiền rẻ, cổ phiếu và bất động sản tăng giá, vay tiền mở nhà máy cực lợi.
4. **`OIL / GOLD / BTC` (`$75 / $2000 / $65k`)**: Giá giao ngay của 3 tài sản vĩ mô chuẩn: Dầu thô (`$75/thùng`), Vàng (`$2,000/oz`), và Bitcoin (`$65,000`). Nếu giá Dầu tăng vọt (ví dụ lên `$160`), các mỏ dầu (`OIL`) lãi đậm nhưng các nhà máy sản xuất (`FACTORY`) không tự chủ được nguyên liệu sẽ bị đội giá vốn (`COGS`).
5. **`AETHER ($30K HUSTLER)` (`$30,000`)**: Tổng tài sản ròng (`Net Worth = Tổng Tài Sản - Tổng Nợ`) của cá nhân bạn (`#1 Aether`).
6. **`5-REGIME AUDIT` (`PASS (9.1e-13)`)**: Bộ kiểm toán kế toán tự động kiểm tra phương trình $\text{Assets} \equiv \text{Liabilities} + \text{Equity}$ trên toàn bộ 1,915 thực thể ở mọi mili-giây để đảm bảo **không bao giờ có bug mất tiền hay lệch sổ sách**.

### 2.2. Các Nút Điều Khiển Thời Gian & Chế Độ Chơi (Thanh Điều Khiển Giữa)
- **`Acting As: #1 Aether ($30k)` (Ô chọn Chủ thể Hành động — Cực kỳ quan trọng!)**:
  - Cho biết **AI ĐANG LÀ NGƯỜI RÚT VÍ RA LỆNH**.
  - Lúc mới vào game, bạn điều khiển cá nhân **`#1 Aether`**.
  - Khi bạn mở một công ty Startup (ví dụ `#61 Aether Ventures`) hoặc mua thâu tóm `>= 20%` cổ phần một tập đoàn để nắm quyền kiểm soát (`My Controlled`), công ty đó sẽ xuất hiện trong danh sách `Acting As` này! Khi bạn chuyển `Acting As` sang công ty con, mọi lệnh mua cổ phiếu, vay tiền, hay xây nhà máy sẽ dùng **tiền trong két của công ty con đó** chứ không dùng tiền túi cá nhân của Aether!
- **`Mode: $30k Hustler (Switch to $1B)`**: Chuyển đổi tức thì giữa chế độ Khởi nghiệp thực tế với `$30,000` và chế độ Tỷ phú Sandbox với `$1,000,000,000` (`$1B`).
- **Ba nút Tua Thời Gian (`+1 Subtick`, `+1 Day`, `+1 Quarter`)**:
  1. **`+1 Subtick` (Nhịp vi mô trong ngày — `< 0.2 ms`)**: Làm giá cổ phiếu, hàng hóa (`OIL`, `GOLD`), và `BTC` dao động nhẹ theo cung-cầu từng tích tắc để bạn lướt sóng ngắn hạn hoặc xem bảng điện nhảy số.
  2. **`+1 Day` (Qua 1 Ngày giao dịch)**: Tiến lịch thêm 1 ngày, cập nhật cây nến ngày mới trên biểu đồ OHLCV, tính lãi vay/trái phiếu theo ngày.
  3. **`+1 Quarter (Full Sim)` (Qua 1 Quý = 3 Tháng — Nhịp chính của Game)**:
     - Đây là nút tổng kết toàn bộ nền kinh tế sau mỗi Quý (`Q1 -> Q2 -> Q3 -> Q4`):
     - Tất cả 1,078 tập đoàn và các nhà máy/cửa hàng Capitalism Lab tính toán Doanh thu, Chi phí (`COGS`), Lợi nhuận (`EBIT`), đóng Thuế, và trả **Cổ tức (`Dividends`)** về ví cho bạn.
     - Toàn bộ **320 Nhà đầu tư AI** thực hiện các quyết định mua/bán/mở công ty/cháy tài khoản (`Wipeout & Respawn`).
     - Các hợp đồng Quyền chọn (`Options`), Hoán đổi lãi suất (`Swaps`), và Vụ kiện (`Lawsuits`) được thanh toán.
- **`🧠 Live gpt-6-luna Batch`**: Gọi trực tiếp mô hình AI `gpt-6-luna` dưới nền để 24 nhà đầu tư dẫn đầu các trường phái (`Archetype Leads`) viết lại chiến lược đầu tư 4 quý mới dựa trên tình hình vĩ mô hiện tại.

---

## Phần 3: Hướng Dẫn Toàn Bộ Tính Năng Tab 1 — Sàn Giao Dịch Phố Wall (WSR v10 Terminal)

Tab 1 được chia làm **3 cột rõ ràng**:

### Cột Trái: Danh Bạ Thực Thể (`Entity & Corp Directory`)
- **5 Nút Lọc Nhanh**:
  - `All Corps`: Xem toàn bộ các tập đoàn sản xuất, thương mại, ngân hàng, ETF đang niêm yết.
  - `My Controlled`: Chỉ hiện các công ty mà Aether đang nắm quyền kiểm soát (Startup do bạn lập hoặc công ty bạn mua `>= 20%` cổ phần và là cổ đông lớn nhất).
  - `Banks/Insur`: Chỉ hiện 50 Ngân hàng và 35 Công ty Bảo hiểm.
  - `ETFs (20)`: Chỉ hiện 20 Quỹ ETF (`#1581..#1600`).
  - `320 Investors`: Xem danh sách 320 Nhà đầu tư AI để soi danh mục của họ.
- **Nút màu cam `Aether (#1)`**: Bấm bất kỳ lúc nào để quay về xem Bảng Cân Đối Kế Toán cá nhân của chính bạn (`#1 Aether`).

### Cột Giữa: Báo Cáo Tài Chính, Bảng Nến OHLCV & Danh Mục Cổ Phiếu
1. **3 Thẻ Tóm Tắt Trên Cùng**: Tiền mặt (`CASH & T-BILLS`), Tổng Tài Sản (`TOTAL ASSETS`), và Tài Sản Ròng (`NET WORTH / EQUITY`) của thực thể đang xem.
2. **Bảng Nến Nhật OHLCV & Chỉ Báo Kỹ Thuật**:
   - Chuyển đổi giữa cổ phiếu đang chọn (`#13 WFC`), `BTC/USD`, `OIL`, `GOLD`, `WSR Index`.
   - Rê chuột trên biểu đồ để đọc giá `Open / High / Low / Close / Volume / MA7 / MA20` của từng cây nến.
3. **Bảng Cân Đối Kế Toán 5 Chế Độ (`bs-table-body`)**: Hiển thị chi tiết từng khoản mục Tài sản, Nợ phải trả, Giá cổ phiếu, Tổng số cổ phần lưu hành (`Shares Out`), Lượng cổ phiếu trôi nổi có thể mua (`Free Float`), và Ai đang kiểm soát công ty (`Controller`).
4. **Bảng Danh Mục Cổ Phiếu & Vị Thế Bán Khống (`Unified Stock Holdings & Shorts`)**:
   - Có 2 nút chuyển chế độ xem:
     * **`My / Actor Portfolio` (Mặc định)**: Luôn hiển thị cổ phiếu mà **bạn (hoặc công ty bạn đang điều khiển ở `Acting As`)** đang nắm giữ.
     * **`Viewed Entity`**: Hiển thị cổ phiếu mà công ty hoặc nhà đầu tư AI bạn đang bấm chọn bên cột trái nắm giữ.
   - Trên mỗi dòng cổ phiếu bạn đang giữ có nút **`Sell All`** (bán chốt lời toàn bộ mã đó chỉ với 1 click) hoặc **`Cover`** (mua trả lại cổ phiếu đã bán khống).

### Cột Phải: Bàn Thực Thi Lệnh Đa Tài Sản (`WSR v10 Multi-Asset Execution Desk`)

Gồm 4 khu vực từ trên xuống dưới:

#### Khu vực 1: Mua / Bán / Bán Khống Cổ Phiếu & ETF (`#11..#1600`)
- **`ACTOR ENTITY ID`**: Mã thực thể đang bỏ tiền ra giao dịch (tự động đồng bộ với `Acting As`, mặc định là `1` = Aether).
- **`TARGET CORP ID`**: Mã công ty/ETF bạn muốn mua hoặc bán khống (tự động điền khi bạn bấm vào bất kỳ công ty/ETF nào ở bảng bên trái).
- **Thanh `Target & Est. Cost`**: Tự động nhân `Số lượng cổ phiếu` × `Giá cổ phiếu` để báo trước cho bạn lệnh này tốn bao nhiêu đô-la.
- **Ô `Shares (M)` & Các nút chọn nhanh**:
  - Đơn vị tính của WSR là **Triệu cổ phiếu (`M`)**:
    * Nút **`100sh`** (`0.0001M` = `100 cổ phiếu`): Lô nhỏ dành cho người chơi vốn `$30,000` (chỉ tốn khoảng `$2,000–$5,000`).
    * Nút **`10k`** (`0.01M` = `10,000 cổ phiếu`): Dành cho vốn từ `$500,000` trở lên.
    * Nút **`1M`** (`1.0M` = `1,000,000 cổ phiếu` = `1%` công ty): Dành cho triệu phú/tỷ phú đi thâu tóm.
    * Nút **`Max`**: Tự động tính số lượng cổ phiếu tối đa mà `80%` tiền mặt hiện tại của bạn mua được!
- **4 Nút Đặt Lệnh**:
  - **`📈 Buy Long`**: Mua cổ phiếu nắm giữ (giá tăng thì lãi, mỗi quý được nhận tiền cổ tức).
  - **`Sell Long`**: Bán bớt số lượng cổ phiếu đang giữ theo số ghi ở ô `Shares (M)`.
  - **`📉 Short` (Bán khống)**: Vay cổ phiếu để bán khi bạn dự đoán công ty sắp sập giá (giá giảm thì bạn lãi; nhưng lưu ý: cần có `Net Worth >= 50%` giá trị lệnh khống làm ký quỹ, và nếu công ty chia cổ tức thì người bán khống phải bỏ tiền túi đền cổ tức đó!).
  - **`Cover Short`**: Mua lại cổ phiếu để đóng vị thế bán khống và chốt lời/cắt lỗ.

#### Khu vực 2: Trái Phiếu, Hàng Hóa (`OIL`/`GOLD`), Crypto (`BTC`), Quyền Chọn (`Options`) & Hoán Đổi Lãi Suất (`Swaps`)
- **Ô `Notional ($M)` & Nút `$5k` / `$10M`**:
  - Giá trị giao dịch tính bằng Triệu USD (`$M`). Với vốn `$30,000`, hãy bấm nút **`$5k`** (`0.005M` = `$5,000`).
- **Ô chọn Tài sản (`OIL`, `GOLD`, `COPPER`, `WHEAT`, `BTC`, `ETH`)**: Chọn loại hàng hóa hoặc Crypto bạn muốn giao dịch.
- **8 Nút Công Cụ Tài Chính**:
  1. **`Buy GovBond`**: Mua Trái phiếu Chính phủ bằng số tiền ở `Notional ($M)` — an toàn tuyệt đối, nhận lãi cố định mỗi quý, và tăng giá khi lãi suất thị trường giảm.
  2. **`Sell GovBond`**: Bán Trái phiếu Chính phủ đang giữ để thu tiền mặt về.
  3. **`Buy CorpBond`**: Mua Trái phiếu Doanh nghiệp của công ty ở `TARGET CORP ID` (lãi suất cao hơn Trái phiếu Chính phủ).
  4. **`Futures/Crypto`**: Giao dịch Hợp đồng Tương lai Hàng hóa (`OIL`, `GOLD`, `COPPER`, `WHEAT`) hoặc mua/bán `BTC`/`ETH` theo giá trị `Notional ($M)`.
  5. **`Buy Call` (Mua Quyền chọn Mua)**: Đặt cược cổ phiếu `TARGET CORP ID` sẽ **tăng giá mạnh** với số vốn nhỏ (tính theo số lượng cổ phiếu ở ô `Shares (M)`).
  6. **`Buy Put` (Mua Quyền chọn Bán)**: Đặt cược cổ phiếu `TARGET CORP ID` sẽ **giảm giá mạnh** (hoặc dùng để bảo hiểm danh mục).
  7. **`Write Call` (Bán Quyền chọn Mua)**: Thu tiền phí (`Premium`) ngay lập tức, nhưng chịu rủi ro nếu cổ phiếu tăng vọt.
  8. **`Rate Swap` (Hợp đồng Hoán đổi Lãi suất)**: Ký hợp đồng trả lãi cố định `6.5%` và nhận lãi thả nổi `Prime Rate` trên mệnh giá `Notional ($M)` trong 4 quý (nếu `Prime Rate` tăng lên `10%–18%`, bạn sẽ được nhận chênh lệch tiền tươi mỗi quý!).

#### Khu vực 3: Ngân Hàng, Cổ Tức, Chia Tách Công Ty, Cố Vấn ETF & Kiện Tụng (`Banking, M&A, ETF Advisory & Lawsuits`)
- **Ô `Loan/Claim $M` & Nút `$10k`**: Số tiền muốn vay/trả nợ ngân hàng hoặc số tiền đòi bồi thường khi kiện (mặc định `0.01M` = `$10,000`).
- **`Borrow Loan` / `Repay Loan`**: Vay thêm tiền mặt từ Ngân hàng thương mại (trong hạn mức tín dụng `Credit Line Limit` dựa trên hạng tín nhiệm `AAA..C` của bạn) hoặc trả bớt nợ vay.
- **`Set Dividend`**: Ra lệnh cho công ty ở `TARGET CORP ID` chia cổ tức tiền mặt (`$0.25/cổ phiếu`). *(Lưu ý: Công ty mục tiêu phải có đủ tiền mặt trả cổ tức).*
- **`80% SpinOff`**: Nếu công ty mẹ (`ACTOR`) đang sở hữu công ty con (`TARGET`), nút này sẽ tách cổ phần công ty con chia cho các cổ đông (miễn thuế 100% nếu sở hữu `>= 80%`).
- **`ETF Advisor`**: Đăng ký làm Cố vấn Quản lý cho Quỹ ETF `#1581` để thu phí quản lý (`Advisory Fee`) hàng quý.
- **`⚔️ Lawsuit` (Đâm đơn kiện Chống độc quyền)**: Công ty `ACTOR` kiện công ty `TARGET` đòi bồi thường số tiền ở `Loan/Claim $M` (tốn `2%` án phí, kết quả xử thắng/thua sẽ nổ ra khi qua quý).

#### Khu vực 4: Cầu Nối Ví Tiền GTA San Andreas (`Stage B — GTA Wallet Bridge`)
- **`Deposit GTA` / `Withdraw GTA`**: Mô phỏng việc nạp tiền từ ví nhân vật Aether trong GTA San Andreas vào sàn đầu tư hoặc rút tiền lãi từ sàn về lại ví GTA SA.

---

## Phần 4: Hướng Dẫn Toàn Bộ Tính Năng Tab 2 — Khởi Nghiệp & Đế Chế Sản Xuất Capitalism Lab (`3x3 Floorplan`)

Nếu Tab 1 là nơi bạn đầu tư tài chính, thì **Tab 2** là nơi bạn trực tiếp **mở cửa hàng, xây nhà máy, điều hành dây chuyền sản xuất `3x3` và cạnh tranh thị phần bán lẻ tại 128 thành phố**!

### 4.1. Với `$30,000` ban đầu, tôi bắt đầu ở Tab 2 như thế nào? (Cột Trái Trên: `$30k Street Hustler Startup Incubator`)
Một nhà máy lớn tốn hàng chục triệu đô, nhưng với `$30,000` cá nhân, bạn có khung **Vườn Ươm Khởi Nghiệp (`$30k Startup Incubator`)** ở góc trên bên trái Tab 2:
1. **`Founder ID`**: Mặc định là `1` (Aether).
2. **`Seed Eq ($M)`**: Số vốn tự có bạn bỏ vào công ty (mặc định `0.02M` = **`$20,000`**, giữ lại `$10,000` tiền mặt dự phòng trong túi Aether).
3. **`Loan x`**: Đòn bẩy vay vốn ngân hàng khởi nghiệp (mặc định `3.0x` -> Ngân hàng cho công ty mới vay thêm **`$60,000`**, tổng vốn công ty mới có **`$80,000`**!).
4. **`First Firm`**: Chọn loại cơ sở kinh doanh đầu tiên của bạn (`RETAIL` Cửa hàng bán lẻ, `FACTORY` Xưởng sản xuất nhỏ, `SOFTWARE` Studio phần mềm, hoặc `RD` Phòng nghiên cứu).
5. Bấm nút vàng **`🚀 Incorporate Bootstrapped Startup + Open 1st Firm`**:
   - Hệ thống lập tức thành lập công ty cổ phần của riêng bạn (ví dụ `#61 Aether Ventures (S61)` — bạn nắm `80%` cổ phần kiểm soát tuyệt đối), mở ngay cơ sở kinh doanh đầu tiên tại thành phố và mặt hàng bạn chọn, đồng thời tự động chuyển `Acting As` sang công ty `#61`!

### 4.2. Cột Giữa Tab 2: Danh Sách Các Cơ Sở Kinh Doanh (`Active Capitalism Lab Physical Firms`)
- **8 Nút Lọc Loại Hình Cơ Sở (Có Icon Gốc Của Capitalism Lab)**:
  - `All`, `Factory` (Nhà máy chế tạo), `Retail` (Cửa hàng bán lẻ), `R&D` (Viện nghiên cứu công nghệ), `Mine/Oil` (Mỏ khoáng sản & Giàn khoan dầu), `Farm` (Nông trại), `Software` (Xưởng phần mềm/Internet/Telecom), `Real Estate` (Chung cư `APARTMEN` & Cao ốc văn phòng `COMMERCI`).
- **Thông số trên mỗi Thẻ Cơ Sở (Firm Card)**:
  - **Chủ sở hữu (`Owner`)** & **Thành phố (`City`)**.
  - **`Q` (Quality — Chất lượng sản phẩm)**, **`Brand` (Điểm thương hiệu)**, **`Px` (Giá bán mỗi đơn vị)**.
  - **`Share` (Thị phần tại thành phố đó %)**, **`COGS` (Tỷ lệ giá vốn hàng bán %)**, và huy hiệu **`Shield (1..3)`** (nếu công ty tự chủ được 1–3 nguồn nguyên liệu đầu vào trong cùng tập đoàn, giúp giảm mạnh giá vốn và chống sốc giá nguyên liệu!).
  - **`Rev` (Doanh thu quý gần nhất)** và **`EBIT` (Lợi nhuận hoạt động quý gần nhất)**.

### 4.3. Cột Phải Tab 2: Mặt Bằng Nội Bộ `3x3` (`9 Ô Bộ Phận`) & Thanh Chỉnh Giá/Quảng Cáo (`PRQ`)
Khi bạn bấm vào bất kỳ thẻ cơ sở nào ở cột giữa, cột phải sẽ hiển thị **Mặt bằng `3x3` (`9 ô`) chuẩn Capitalism Lab**:
- **Ý nghĩa các loại ô bộ phận (`Unit Roles`)**:
  - **`PUR` (`Purchasing Unit`)**: Bộ phận thu mua nguyên vật liệu đầu vào (ví dụ nhà máy Smartphone cần mua `CCD + CPU + PLASTIC`).
  - **`MFT` (`Manufacturing Unit`)**: Dây chuyền lắp ráp/chế tạo nguyên liệu thành thành phẩm.
  - **`SALE` (`Sales Unit`)**: Bộ phận xuất hàng và bán hàng ra thị trường.
  - **`INV` (`Inventory Warehouse`)**: Kho chứa hàng dự trữ.
  - **`EXTERN` (`Advertising / Marketing Unit`)**: Bộ phận quảng cáo giúp tăng điểm thương hiệu (`Brand`) mỗi quý.
  - **`RD` / `TECH` / `RADRD`**: Bộ phận nghiên cứu nâng cấp công nghệ sản phẩm.
- **Cách thao tác trên Mặt bằng `3x3`**:
  1. **Đổi chức năng của bất kỳ ô nào (`#1..#9`)**: Bấm chuột vào ô đó trên lưới `3x3` -> Chọn chức năng mới ở ô `Slot Role` bên dưới -> Bấm **`Assign Unit`**.
  2. **Huấn luyện toàn bộ nhân sự (`Train All 9 Units (+Lv)`)**: Nâng cấp cấp độ sao (`★Lv1 -> ★Lv9`) cho cả 9 bộ phận, giúp tăng năng suất và cộng thêm điểm Chất lượng sản phẩm (`Quality`).
  3. **Thanh Điểm Cạnh Tranh `PRQ` (`Quality + Brand + Price = Overall Rating`)**:
     - Cho thấy trọng số người tiêu dùng quan tâm tới Chất lượng (`Quality`), Thương hiệu (`Brand`), và Giá bán (`Price`).
     - Bạn có thể chỉnh trực tiếp **Giá bán (`FIRM UNIT PRICE $`)** và **Ngân sách Quảng cáo (`ADVERTISING $M/QTR`)** ở 2 ô dưới cùng rồi bấm **`Update PRQ`**:
       * Giảm giá bán (`Unit Price`) hoặc tăng quảng cáo (`Advertising`) sẽ làm tăng `Overall Rating`, giúp bạn **cướp thị phần (`Market Share %`)** từ tay đối thủ khi bấm `+1 Quarter`!

---

## Phần 5: Sự Giao Thoa 2 Chiều Giữa Wall Street Raider & Capitalism Lab (Tại Sao Hai Thế Giới Này Bổ Trợ Hoàn Hảo Cho Nhau?)

Mọi hành động bạn làm ở Tab 1 (WSR) và Tab 2 (Capitalism Lab) đều tác động qua lại theo **4 Vòng Lặp Kinh Tế Thực**:

1. **Chiều từ Capitalism Lab (Tab 2) $\rightarrow$ Wall Street Raider (Tab 1)**:
   - Khi công ty của bạn (hoặc của AI) xây dựng nhà máy, mở cửa hàng bán lẻ và giành được thị phần tại các thành phố ở Tab 2, **Doanh thu (`Revenue`) và Lợi nhuận (`EBIT`) thực tế từ các cơ sở đó được cộng trực tiếp vào Báo cáo Kết quả Kinh doanh và Tiền mặt của Tập đoàn mẹ ở Tab 1**!
   - Công ty làm ăn có lãi ở Tab 2 $\rightarrow$ `Net Worth`, `ROCE%`, và `EPS` của tập đoàn ở Tab 1 tăng lên $\rightarrow$ **Giá cổ phiếu trên sàn WSR (Tab 1) tự động tăng giá**, giúp bạn giàu lên từ cả lợi nhuận kinh doanh lẫn giá trị cổ phiếu!
   - Tổng vốn đầu tư xây nhà máy (`CAPEX`) ở Tab 2 tạo xung lực thúc đẩy tăng trưởng `GDP` ở Tab 1; nếu các cửa hàng bán lẻ đồng loạt tăng giá bán quá cao sẽ đẩy chỉ số lạm phát `CPI` ở Tab 1 tăng lên.
2. **Chiều từ Wall Street Raider (Tab 1) $\rightarrow$ Capitalism Lab (Tab 2)**:
   - Khi giá hàng hóa trên sàn WSR (`OIL`, `COPPER`, `GOLD`, `WHEAT`) tăng vọt ở Tab 1 $\rightarrow$ Các mỏ khai khoáng (`MINE`, `OIL`) ở Tab 2 thu siêu lợi nhuận, trong khi các nhà máy (`FACTORY`) không tự chủ được nguyên liệu bị tăng chi phí đầu vào (`COGS`).
   - Khi lạm phát `CPI` và lãi suất `Prime Rate` ở Tab 1 tăng cao $\rightarrow$ Chi phí vận hành (`OPEX`) của các cửa hàng/nhà máy ở Tab 2 tăng lên và tỷ lệ lấp đầy bất động sản (`REIT Occupancy`) giảm xuống.
   - Khi bạn dùng kỹ thuật tài chính ở Tab 1 (vay ngân hàng `Borrow Loan`, phát hành trái phiếu, hoặc dùng tiền lãi cổ phiếu/phái sinh) $\rightarrow$ Bạn có nguồn vốn dồi dào để mở thêm nhà máy, viện `R&D` và thôn tính chuỗi cung ứng ở Tab 2!

---

## Phần 6: Kịch Bản Chơi Mẫu Từ Bước 1 Dành Cho Người Mới (`$30,000` Street Hustler Walkthrough)

Nếu bạn vừa mở `http://127.0.0.1:8765`, hãy thử làm theo đúng **5 bước khởi đầu chuẩn chỉnh** sau:

- **Bước 1 (Mua lô cổ phiếu đầu tiên với `$30,000`)**:
  1. Ở **Tab 1**, bấm vào một ngân hàng hoặc tập đoàn lớn ở cột trái (ví dụ `#13 WFC`).
  2. Nhìn lên **Bảng Nến OHLCV** ở cột giữa: bấm thử các nút `BTC/USD`, `OIL`, `GOLD`, `#13 WFC`, `Pattern`, `RSI(14)` để xem biểu đồ và đọc giải thích ở dòng xanh bên dưới.
  3. Nhìn sang cột phải: ô `Shares (M)` đang để sẵn `0.0001` (`100 cổ phiếu`, tốn khoảng `$4,000`). Bấm nút xanh **`📈 Buy Long`**.
  4. Nhìn xuống bảng **`Unified Stock Holdings`** ở cuối cột giữa: bạn sẽ thấy ngay vị thế `LONG` `0.0001M` cổ phiếu `WFC` của mình!
- **Bước 2 (Thử mua Trái phiếu Chính phủ & Vay vốn nhỏ)**:
  1. Ở cột phải khu vực 2, bấm nút **`$5k`** (`0.005M`) rồi bấm **`Buy GovBond`** -> Bạn vừa mua `$5,000` Trái phiếu Chính phủ!
  2. Ở khu vực 3, bấm nút **`$10k`** (`0.01M`) rồi bấm **`Borrow Loan`** -> Ngân hàng giải ngân thêm `$10,000` tiền mặt vào ví Aether!
- **Bước 3 (Khởi nghiệp mở Công ty & Cửa hàng đầu tiên bên Capitalism Lab)**:
  1. Chuyển sang **Tab 2 (`2. CapLab 3×3 Floorplan & $30k Startup Incubator`)**.
  2. Ở góc trên bên trái (`$30k Street Hustler Startup Incubator`), giữ nguyên `Seed Eq = 0.02` (`$20,000`) và `Loan x = 3.0`, bấm nút vàng **`🚀 Incorporate Bootstrapped Startup + Open 1st Firm`**.
  3. Ngay lập tức, công ty `#61 Aether Ventures (S61)` của bạn ra đời kèm cửa hàng `#10` ở cột giữa, và mặt bằng `3x3` của cửa hàng hiện ra ở cột phải!
- **Bước 4 (Tối ưu Mặt bằng `3x3` & Giành thị phần)**:
  1. Ở cột phải Tab 2, bấm nút vàng **`Train All 9 Units (+Lv)`** để nâng cấp trình độ nhân viên cả 9 ô.
  2. Ở ô `UNIT PRICE ($)` bên dưới, thử giảm giá bán đi khoảng `5%–10%` và tăng nhẹ `ADVERTISING`, rồi bấm **`Update PRQ`**.
- **Bước 5 (Tua thời gian qua Quý mới để thu tiền)**:
  1. Bấm nút màu cam **`+1 Quarter (Full Sim)`** trên thanh điều khiển giữa.
  2. Quan sát doanh thu (`Rev`), lợi nhuận (`EBIT`) và thị phần (`Share %`) của cửa hàng bạn tăng lên, đồng thời kiểm tra **Tab 3 (`320 Investors`)** và **Tab 4 (`News Wire`)** để xem toàn bộ thị trường vừa vận động ra sao!

---

## Phần 7: Paimon Economic & Trading Academy (Cầm Tay Chỉ Việc, Spotlight, Inspect Mode, Sách Giáo Khoa & Cố Vấn Trực Tiếp `gpt-6-luna`)

Ngay trên thanh điều khiển trên cùng của giao diện Web (`http://127.0.0.1:8765`), bạn có bộ 3 nút điều khiển của **Paimon Economic & Trading Academy**:

1. **`✨ Paimon Academy (0/36)` (`#btn-paimon-academy-toggle`)**:
   - Bật / thu gọn bảng **Paimon Economic & Trading Academy** ở góc phải màn hình.
   - Bao gồm **9 Học phần (`M0` đến `M8`)** và **36 Bài thực hành tương tác (`M0_Q1` đến `M8_Q4`)**:
     * **`🎯 Chỉ Tận Nơi` (`#btn-paimon-spotlight`)**: Vẽ vòng sáng vàng nhấp nháy + hộp thoại chỉ điểm trực tiếp vào đúng nút bấm, ô nhập liệu, bảng biểu hoặc cây nến trên màn hình.
     * **`⚡ Làm Mẫu` (`#btn-paimon-auto-exec`)**: Paimon tự động thực hiện thao tác mẫu của bài học đó ngay trên giao diện và đánh dấu hoàn thành Quest (`✅`).
     * **Tự động Kiểm chứng (`Auto-Verify`)**: Khi bạn tự tay bấm đúng nút hoặc thực hiện đúng giao dịch mà Paimon giao, hệ thống tự động ghi nhận hoàn thành và lưu vào `saves/paimon_academy_progress.json`.
2. **`🔍 Inspect: OFF / ON` (`#btn-paimon-inspect-toggle`)**:
   - Khi bật sang **`ON`**, chỉ cần rê chuột lên bất kỳ nút bấm, ô nhập liệu, bảng cân đối kế toán, biểu đồ nến `#ohlcv-canvas` hay lưới mặt bằng `3×3`, hộp thoại **Paimon Inspect** sẽ hiện ra giải thích bằng Tiếng Việt:
     * **💡 Là gì**: Ý nghĩa kinh tế / tài chính đời thường.
     * **📐 Công thức**: Công thức toán học chính xác trong Engine.
     * **🎯 Khi nào dùng**: Mẹo ra quyết định thực chiến cho Aether.
3. **`📖 Sách Kinh Tế` (`#btn-paimon-textbook-modal`)**:
   - Mở cửa sổ **Sách Giáo Khoa Kinh Tế Học, Đọc Nến Nhật & Đại Tư Bản Paimon** toàn màn hình, chứa trọn bộ 9 Học phần (36 bài giảng) và Từ điển Bách khoa 55+ thuật ngữ, có thanh tìm kiếm tức thì (`#paimon-wiki-search`) và nút **`🎯 Học & Chỉ Tận Nơi`** để nhảy thẳng tới từng bài thực hành.
4. **Khung Chat Hỏi Đáp Trực Tiếp Cùng Paimon (`gpt-6-luna` Live Context-Aware Tutor)**:
   - Nằm ngay nửa dưới bảng Paimon Academy, đi kèm 4 nút gợi ý hỏi nhanh (`🕯️ Soi Nến & RSI hiện tại`, `🤔 Tại sao chọn mã này?`, `🏭 Khám bệnh mặt bằng 3×3`, `💰 Nước đi tiếp theo?`) và ô nhập câu hỏi tự do.
   - Mỗi câu hỏi gửi đi đều được tự động đính kèm **Bản chụp Trạng thái Thực tế (`Live Telemetry Context`)** gồm toàn bộ chỉ số vĩ mô, ví tiền `#1 Aether`, thông số cơ bản (`P/B`, `ROCE`, `EPS`, `Float`), thông số kỹ thuật của cây nến đang mở (`OHLCV`, `MA7/MA20`, `Bollinger`, `RSI(14)`, `Pattern`) và mặt bằng `3×3` đang chọn.
   - Xem tài liệu chuyên sâu tại: [`docs/PAIMON_ECONOMIC_AND_TRADING_ACADEMY_WIKI.md`](PAIMON_ECONOMIC_AND_TRADING_ACADEMY_WIKI.md).


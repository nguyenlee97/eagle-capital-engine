# Prompt Bàn Giao Cho Hội Thoại Mới: Xây Dựng Hệ Thống "Paimon Economic & Trading Academy" (Interactive Guidance + Candlestick/Macro/CapLab Mastery + Live AI Tutor)

Bạn có thể copy toàn bộ khối nội dung trong khung dưới đây và dán thẳng vào hội thoại mới:

---

```markdown
# MỤC TIÊU TÁC VỤ: XÂY DỰNG "PAIMON ECONOMIC & TRADING ACADEMY" (INTERACTIVE IN-GAME GUIDANCE, SPOTLIGHT TUTORIAL & LIVE AI TUTOR) TRÊN WEB WORKSTATION

## 1. Bối cảnh & Trạng thái hiện tại của Workspace
Chúng ta đang làm việc tại workspace `c:\Users\LENOVO\Desktop\GTA\staging\project-eagle\eagle-capital-engine-20261108` (Giai đoạn A — **EagleCapitalEngine v2.0** hợp nhất **Wall Street Raider v10.0.22.3** + **Capitalism Lab v11.0.98** + **320 AI Investors thuộc 24 Archetypes**).

Trước khi bắt đầu, hãy đọc kỹ các tài liệu và file cốt lõi sau để nắm 100% kiến trúc và toàn bộ tính năng đã được kiểm thử E2E:
1. **`docs/EAGLE_CAPITAL_GAMEPLAY_AND_FEATURE_BIBLE.md` (BẮT BUỘC ĐỌC ĐẦU TIÊN — Cẩm nang Toàn tập Tính năng, Cơ chế Kinh tế & Luồng Chơi Thực Chiến từ `$30,000` đến Đại Tư Bản)**: Tài liệu này giải thích chi tiết từng nút bấm, từng bảng biểu, từng công cụ giao dịch trên cả 4 Tab, cơ chế liên thông 2 chiều WSR <-> Capitalism Lab, và lộ trình khởi đầu chuẩn cho người chơi mới. Đây là nền tảng kiến thức chuẩn xác 100% để bạn thiết kế nội dung bài giảng cho Paimon.
2. `docs/EAGLE_WORKSTATION_V2_E2E_UX_REPORT.md` (Báo cáo kiểm thử E2E 20 pha toàn diện trên trình duyệt, xác nhận mọi tính năng từ `$30k` micro-lot cổ phiếu/ETF/Trái phiếu/Vàng/Dầu/Vay ngân hàng/Mở Startup + `3x3` Floorplan cho tới `$1B` Phái sinh/M&A/LBO đều hoạt động hoàn hảo 100%).
3. `AGENTS.md` và `EAGLE_CAPITAL_ENGINE_SPEC.md` (Kiến trúc tổng thể & quy tắc không sửa file game gốc WSR/CapLab hay GTA SA runtime trong Stage A).
4. `eagle_capital_engine.py` (Core Engine hợp nhất WSR + Capitalism Lab, bắt đầu tại mốc thời gian **2010-Q1 (01/01)** đồng bộ với timeline GTA Project Eagle; đảm bảo 100% công ty khởi đầu có `Net Worth > 0`, giá cổ phiếu phân hóa tự nhiên, `>= 25%` cổ phiếu tự do lưu hành `public_float_shares`, và bảo vệ chống tự mua chính mình hoặc mua nhầm nhà đầu tư cá nhân).
5. `eagle_workstation_server.py` và `ui/index.html` (Server HTTP cổng `8765` + Giao diện Web 4 Tab đã tích hợp **Bảng Nến Nhật OHLCV + Volume + MA7/MA20 + Bollinger Bands + RSI(14) + Nhận diện Mô hình Nến tự động + Thanh giải thích tín hiệu trực tiếp `#chart-explain-banner`** ngay tại cột giữa Tab 1).
6. `luna_ai_orchestrator.py` (Bộ điều phối LLM `gpt-6-luna` qua OpenAI-compatible API).

## 2. Triết lý Gameplay & Bài toán của Người dùng (Rất quan trọng)
- **Vai trò của người chơi (`#1 Aether`)**: Tôi khởi đầu ở năm **2010-Q1** chỉ với **$30,000 (`$0.03M` — Street Hustler Mode)** giữa một thế giới kinh tế sống động gồm 1,078 tập đoàn và 320 nhà đầu tư AI (từ các cá con `$30k` khác cho tới các cá mập tỷ phú, quỹ đầu cơ, chaebol độc quyền).
- **Tâm thế "Cá con giữa đại dương"**: Việc có những AI trở thành siêu bá chủ hay độc quyền không ảnh hưởng tiêu cực tới tôi — đúng như ngoài đời thực, tôi chỉ là một cá con dùng số vốn nhỏ kiếm được từ trong game để học cách sinh tồn, đầu tư kiếm chác từ thị trường, mở cửa hàng/nhà máy khởi nghiệp và tích lũy tài sản dần dần.
- **Vấn đề cốt lõi cần giải quyết**:
  1. Tôi **không quá rành về kinh tế/tài chính** và **chưa từng chơi Wall Street Raider lẫn Capitalism Lab bao giờ**. Dù đã có tài liệu `docs/EAGLE_CAPITAL_GAMEPLAY_AND_FEATURE_BIBLE.md`, khi vào chơi trực tiếp trên giao diện, tôi cần một người thầy cầm tay chỉ việc ngay trên màn hình để không bị ngợp trước hàng trăm chỉ số, biểu đồ nến OHLCV, báo cáo tài chính và mặt bằng `3x3`.
  2. Tôi muốn chơi và làm chủ hoàn toàn trò này **trên giao diện Web (`http://127.0.0.1:8765`) một thời gian** để tinh chỉnh mọi thứ thật mượt trước khi đem tích hợp vào GTA San Andreas ở Stage B.
  3. Do đó, tôi cần xây dựng một **Hệ thống Hướng dẫn Tương tác Siêu To Khổng Lồ (Interactive Guidance & Economic Academy)** không khác gì một **"Cuốn sách Kinh tế học, Đọc Nến/Phân tích Kỹ thuật, Đầu tư Phố Wall & Quản trị Doanh nghiệp tương tác trực tiếp trong game"**, với người dẫn đường mang **Identity của Paimon** (bạn đồng hành của Aether).

## 3. Chân dung & Vai trò của Paimon trong Giai đoạn này
- **Identity & Giọng điệu của Paimon**:
  - Giữ đúng tính cách đặc trưng của Paimon khi đồng hành cùng Aether (nhí nhảnh, nhiệt tình, đôi lúc hài hước kiểu "kho báu/Mora/tiền tươi thóc thật", nhưng khi giảng về kinh tế, đọc nến Nhật OHLCV, soi báo cáo tài chính, phân tích cung-cầu hay bày mưu tính kế trên thương trường thì cực kỳ sắc sảo, rõ ràng, dễ hiểu cho người mới bắt đầu).
  - Mọi thuật ngữ tiếng Anh trên giao diện (`OHLCV`, `Doji`, `Hammer`, `Engulfing`, `MA7/MA20`, `Bollinger Bands`, `RSI(14)`, `Prime Rate`, `CPI`, `ROCE`, `P/B`, `Short Selling`, `Call/Put Option`, `COGS`, `3x3 Floorplan`, `DRD Tax`, `LBO`, v.v.) đều phải được Paimon giải thích bằng ngôn ngữ đời thường, có ví dụ minh họa gắn liền với chính con số và cây nến đang hiển thị trên màn hình của Aether.
- **Chế độ vận hành thế giới (Heuristic-First Baseline)**:
  - Trong suốt quá trình tôi học và chơi cơ bản, thế giới 1,078 công ty và 320 AI vận hành **100% bằng cơ chế Heuristic nội tại + Playbook sẵn có** (mượt mà, chuẩn kinh tế học, không tốn chi phí gọi API ngầm cho đám đông AI).
  - Chưa làm tính năng "Paimon tự động đánh nhau với các AI khác thay người chơi" ở bước này; hiện tại Paimon tập trung 100% vào vai trò **Người Thầy Dẫn Đường (Interactive Step-by-Step Guide)** và **Cố Vấn Giải Đáp Trực Tiếp (Live Context-Aware Q&A Tutor)**.
- **Hai trụ cột tính năng của Paimon cần xây dựng trên Web UI**:
  1. **Trụ cột 1 — Hệ thống Bài giảng Tương tác & Spotlight Cầm Tay Chỉ Việc (Interactive Curriculum & Guided Quests)**:
     - Giao diện có bảng/ngăn **Paimon Academy & Guide** luôn có thể bật/tắt hoặc thu gọn, đi kèm **Hiệu ứng Spotlight / Highlight khung viền phát sáng + mũi tên chỉ tận nơi** vào từng nút bấm, từng cây nến trên `#ohlcv-canvas`, từng ô nhập liệu, từng dòng báo cáo trên cả 4 Tab.
     - Mỗi bài học không chỉ là chữ đọc suông mà là **Interactive Quest (Thực hành có kiểm chứng)**: Paimon giao nhiệm vụ cụ thể (ví dụ: *"Aether hãy bấm vào bộ lọc `Banks/Insur`, chọn một ngân hàng, nhìn lên Bảng Nến xem `RSI(14)` và mẫu nến hiện tại đang báo gì, sau đó bấm nút `100sh` rồi xem dòng tính tiền `Est. Cost` nhé!"*), hệ thống tự động bắt sự kiện DOM / trạng thái Engine để xác nhận Aether đã làm đúng và tự động chuyển sang bước tiếp theo.
     - Có chế độ **"Tự do khám phá có giải thích (Inspect / Explain Mode)"**: Khi bật chế độ này và rê chuột hoặc bấm vào bất kỳ chỉ số/biểu đồ nến/nút bấm nào trên màn hình, Paimon sẽ giải thích ngay thành phần đó là gì, công thức tính ra sao, và khi nào nên dùng (bám sát nội dung trong `docs/EAGLE_CAPITAL_GAMEPLAY_AND_FEATURE_BIBLE.md`).
  2. **Trụ cột 2 — Khung Chat Hỏi Đáp Chuyên Sâu Với Paimon Sau/Trong Mỗi Bài Học (`gpt-6-luna` Context-Aware Advisor)**:
     - Ngay trong bảng của Paimon có khung **Chat trực tiếp với Paimon** (kết nối `gpt-6-luna`).
     - Mỗi khi tôi đặt câu hỏi, backend tự động đính kèm **Bản chụp Trạng thái Thực tế (Live Telemetry Context)**: Bài học hiện tại đang ở bước nào, vĩ mô năm `2010-Qx` đang ra sao (`GDP`, `CPI`, `Prime Rate`, giá Dầu/Vàng), dữ liệu **Bảng Nến OHLCV + `MA7/MA20` + `Bollinger` + `RSI(14)` + Mẫu hình nến** của tài sản đang xem, ví tiền & danh mục của Aether (`#1`), thông số chi tiết của công ty/nhà máy mà Aether đang bấm xem, và lý do đằng sau các biến động gần nhất.
     - Nhờ đó, sau mỗi bài học hoặc ngay giữa lúc chơi, tôi có thể hỏi Paimon bất kỳ câu hỏi nào:
       * *"Paimon ơi, cây nến vừa xuất hiện trên biểu đồ có râu dưới dài ngoằng nghĩa là gì? Có nên mua lúc này không?"*
       * *"Tại sao ở bước này lại chọn mua cổ phiếu ngân hàng này mà không phải mã kia? Decision-making reason kết hợp giữa Phân tích Cơ bản (P/B, ROCE) và Phân tích Kỹ thuật (Nến, RSI, MA) ở đây là gì?"*
       * *"Nhìn vào mặt bằng 3x3 của nhà máy #1 hiện tại, tại sao biên lợi nhuận lại thấp và tôi nên sửa ô nào?"*

## 4. Khung Chương Trình Học "Từ Vỡ Lòng Đến Đại Tư Bản" (Curriculum 9 Học Phần)
Hãy thiết kế kho nội dung bài giảng đồ sộ, chi tiết như một cuốn sách kinh tế học & trading thực chiến (bám sát đầy đủ mọi tính năng trong `docs/EAGLE_CAPITAL_GAMEPLAY_AND_FEATURE_BIBLE.md`), chia làm **9 Học phần (Modules)** từ dễ đến khó:

1. **Học phần 0 — Làm Quen Bàn Làm Việc & Quy Luật Vận Hành Cơ Bản (Onboarding & UI Mastery)**:
   - Giải thích bức tranh tổng thể: Sự kết hợp giữa **Sàn Tài Chính Phố Wall (Tab 1 - WSR)** và **Đế Chế Sản Xuất/Bán Lẻ Đời Thực (Tab 2 - Capitalism Lab)** trong bối cảnh khởi đầu năm `2010-Q1`.
   - Hướng dẫn đọc thanh chỉ số trên cùng, phân biệt rõ **`Acting As`** (Ai đang rút hầu bao ra lệnh: Cá nhân Aether `#1` hay Công ty do Aether làm chủ) với **`Viewed Entity`** (Công ty hoặc Nhà đầu tư AI đang được soi ở cột giữa).
   - Cách điều khiển nhịp thời gian (`+1 Subtick`, `+1 Day`, `+1 Quarter`), chuyển đổi chế độ `$30k Street Hustler` / `$1,000M Tycoon`, và lưu/tải game (`Save/Load`).
2. **Học phần 1 — Kinh Tế Học & Kế Toán Vỡ Lòng Cho Người Mới (Financial Literacy & Fundamental Analysis 101)**:
   - Cầm tay chỉ việc đọc từng dòng trên **Bảng Cân Đối Kế Toán 5 Chế Độ (Balance Sheet)**: Tiền mặt (`Cash & T-Bills`), Tài sản cố định (`CapAssets`), Vốn lưu động (`Working Capital`), Nợ vay (`Bank Loans & Bonds`), và Tài sản ròng (`Net Worth / Equity`). Tại sao $\text{Tổng Tài Sản} = \text{Nợ Phải Trả} + \text{Vốn Chủ Sở Hữu}$?
   - Giải thích bản chất của Cổ phiếu (`Shares Outstanding`, `Free Float`), Giá trị sổ sách (`Book Value`, tỷ số `P/B`), Tỷ suất sinh lời trên vốn (`ROCE%`), Lợi nhuận trên cổ phiếu (`EPS`, `P/E`), Cổ tức (`Dividend`), và Xếp hạng tín nhiệm (`AAA` xuống `D`).
3. **Học phần 2 — Nghệ Thuật Đọc Nến Nhật, Khối Lượng & Phân Tích Kỹ Thuật (Candlestick Patterns, Price Action, Volume, MA, Bollinger & RSI)**:
   - Giải phẫu một cây nến Nhật trên **Bảng Nến OHLCV (`#ohlcv-canvas`)**: Giá mở cửa (`Open`), Giá cao nhất (`High` — râu trên), Giá thấp nhất (`Low` — râu dưới), Giá đóng cửa (`Close`), và Cột khối lượng giao dịch (`Volume`). Tại sao nến xanh/đỏ và độ dài râu nến lại cho biết phe Mua (Bò) hay phe Bán (Gấu) đang thắng thế?
   - Hướng dẫn nhận diện các **Mô hình Nến kinh điển** ngay trên biểu đồ: Nến `Doji` (lưỡng lự đảo chiều), Nến búa `Hammer / Pinbar` (bắt đáy tại hỗ trợ), Nến sao băng `Shooting Star` (xả hàng tại kháng cự), Nến nhấn chìm tăng/giảm (`Bullish / Bearish Engulfing`), và Nến cường lực (`Marubozu`).
   - Cách kết hợp các chỉ báo kỹ thuật có sẵn trên bảng nến: Đường trung bình động `MA7` cắt `MA20` (`Golden Cross / Death Cross`), Dải `Bollinger Bands` (co thắt báo hiệu bão giá, chạm biên trên/dưới), và Chỉ số sức mạnh tương đối `RSI(14)` (`> 70` Quá mua coi chừng đu đỉnh, `< 30` Quá bán cơ hội gom hàng).
   - Thực hành chuyển đổi biểu đồ nến giữa **Cổ phiếu đang chọn (`Selected Stock`)**, **`BTC/USD`**, **Dầu thô (`OIL`)**, **Vàng (`GOLD`)**, và **Chỉ số chung (`WSR Index`)**.
4. **Học phần 3 — Chiến Thuật "Cá Con $30,000": Mua Bán Cổ Phiếu Lô Nhỏ, ETF & Trái Phiếu (Micro-Lot Stock, ETF & Bond Trading)**:
   - Với `$30,000` (`$0.03M`), làm sao kết hợp **Phân tích Cơ bản** (chọn công ty làm ăn thật, `P/B` hợp lý, `ROCE` cao, hạng `AAA/AA`) với **Phân tích Kỹ thuật** (đợi `RSI` hạ nhiệt, xuất hiện nến rút chân `Hammer` hoặc `Bullish Engulfing`) để vào lệnh chuẩn xác?
   - Thực hành lọc danh bạ (`All Corps`, `Banks/Insur`, `ETFs (20)`), đọc thanh tính tiền `Est. Cost`, mua lô nhỏ `100 cổ phiếu` (`100sh`), mua Trái phiếu Chính phủ (`Buy GovBond` với `$5k`), theo dõi lời/lỗ trong bảng `My / Actor Portfolio`, nhận cổ tức mỗi quý và bấm `Sell All` chốt lời.
5. **Học phần 4 — Cách Đọc Thị Trường Vĩ Mô, Chu Kỳ Kinh Tế & Soi Danh Mục Cá Mập AI (Macro Reading & Whale Tracking)**:
   - Giải thích mối quan hệ nhân quả giữa `GDP Growth`, Lạm phát `CPI`, Lãi suất cơ bản `Prime Rate`, giá Dầu (`OIL`), Vàng (`GOLD`) và chứng khoán.
   - Thực hành bấm vào **`320 Investors`** và **`Tab 3 (320 AI Investors)`** để soi danh mục của các huyền thoại đầu tư AI, kết hợp đọc bản tin vĩ mô (`Tab 4 News Wire`) để biết dòng tiền thông minh đang chảy vào đâu.
6. **Học phần 5 — Khởi Nghiệp Thực Chiến Bên Capitalism Lab: Mở Công Ty Đầu Tiên & Làm Chủ Mặt Bằng `3x3` (`$30k` Startup & `3x3` Floorplan 101)**:
   - Thực hành dùng `$20,000` vốn góp + đòn bẩy vay ngân hàng `3x` (`$60,000`) trong khung **Startup Incubator (Tab 2)** để lập công ty riêng và mở cửa hàng bán lẻ đầu tiên.
   - Giải phẫu chi tiết **Mặt bằng `3x3` (`9 ô`)**: Ô mua hàng (`PUR`), Ô sản xuất (`MFT`), Ô bán hàng (`SALE`), Ô kho (`INV`), Ô quảng cáo (`EXTERN`), Ô nghiên cứu (`RD`). Ý nghĩa của các mũi tên nối dây chuyền (`Supply Arrows`), cách đổi chức năng từng ô, và cách huấn luyện nhân viên (`Train All 9 Units`).
   - Công thức cạnh tranh thị phần cốt lõi của Capitalism Lab: $\text{Overall Rating} = w_P \cdot \text{Price} + w_Q \cdot \text{Quality} + w_B \cdot \text{Brand}$. Thực hành chỉnh giá bán (`Unit Price`) và ngân sách quảng cáo (`Advertising`) để giành thị phần và có lãi dương (`EBIT > 0`).
7. **Học phần 6 — Chiến Thuật Chuỗi Cung Ứng, R&D Công Nghệ & Xây Dựng Đế Chế Sản Xuất (Supply Chain, R&D & Vertical Integration)**:
   - Phân tích toàn bộ các loại hình cơ sở trong Capitalism Lab: Nhà máy (`Factory`), Cửa hàng (`Retail`), Viện `R&D`, Mỏ khoáng sản/Dầu khí (`Mine/Oil`), Nông trại (`Farm`), Xưởng phần mềm (`Software`), Bất động sản (`Real Estate`).
   - Tại sao tự chủ nguồn nguyên liệu (`Vertical Integration Shield`) lại giúp giảm giá vốn (`COGS`) và đè bẹp đối thủ mua hàng chợ (`Open Market`)? Cách đầu tư `R&D` nâng điểm công nghệ (`Tech Level`) để tạo sản phẩm chất lượng vượt trội.
8. **Học phần 7 — Vũ Khí Phố Wall Nâng Cao: Bán Khống, Hàng Hóa, Crypto, Quyền Chọn & Hoán Đổi Lãi Suất (Advanced Trading & Derivatives)**:
   - Cách kiếm tiền khi biểu đồ nến gãy xu hướng (`Breakdown`) và thị trường sụp đổ: Bán khống cổ phiếu (`Short` & `Cover Short`, rủi ro cháy tài khoản và nghĩa vụ trả cổ tức khi bán khống).
   - Cách giao dịch Trái phiếu Doanh nghiệp (`Corp Bonds`), Hợp đồng tương lai (`Futures` trên biểu đồ nến `OIL`/`GOLD`/`WHEAT`), Crypto (`BTC`/`ETH`), Quyền chọn Mua/Bán (`Call/Put Options`), và Hợp đồng Hoán đổi lãi suất (`Interest Rate Swaps`).
9. **Học phần 8 — Nghệ Thuật Tài Chính Đại Tư Bản: Công Ty Mẹ - Con, Thuế DRD, Thâu Tóm M&A, LBO & Spin-Off (Corporate Raider & Conglomerate Mastery)**:
   - Cách vận hành tập đoàn mẹ (`Holding Company`) nắm quyền kiểm soát (`>= 20%` hoặc `>= 50%`) các công ty con.
   - Bí quyết tối ưu thuế hợp pháp của giới tài phiệt WSR: Khấu trừ thuế cổ tức công ty con (`80%–100% DRD`), kết chuyển lỗ 4 năm (`4-Yr NOL`), tách công ty con miễn thuế (`80% Spin-Off`), vay nợ thâu tóm (`LBO`), làm Cố vấn Quỹ `ETF` (`ETF Advisor` hưởng phí quản lý), và sử dụng công cụ pháp lý (`Antitrust / Harassing Lawsuit`).

## 5. Yêu cầu Quy trình Thực hiện
1. **Bước 1 (Thiết kế kiến trúc trước)**: Trình bày bản thiết kế kỹ thuật chi tiết cho hệ thống **Paimon Economic & Trading Academy** trên Web Workstation (cấu trúc dữ liệu 9 học phần/quest, cơ chế Spotlight/Highlight & Inspect Mode trên DOM và trên Bảng Nến `#ohlcv-canvas`, API kết nối Paimon Chat với `gpt-6-luna` kèm Live Game + OHLCV Context, và bố cục UI gọn đẹp).
2. **Bước 2 (Triển khai & Kiểm thử E2E)**: Sau khi chốt thiết kế, triển khai toàn bộ hệ thống và kiểm thử bằng Playwright để đảm bảo mọi bài học, hiệu ứng chỉ dẫn và khung chat Paimon hoạt động mượt mà 100%.
```

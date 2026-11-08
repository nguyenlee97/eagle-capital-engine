# EagleCapitalEngine — Workspace Rules & Context (Stage A: Unified WSR + Capitalism Lab Native Engine)

## Mục tiêu của Project này
- Đây là project độc lập thực hiện **Giai đoạn A (`Stage A`)**: Hợp nhất toàn bộ cơ sở dữ liệu và mô hình toán học của hai tựa game tài chính/kinh tế chuyên sâu:
  1. **Wall Street Raider** (`C:\Program Files (x86)\wsr`) — Tầng Thượng tầng Tài chính Vĩ mô, Ngân hàng Đầu tư, 1,590 Tập đoàn, 70 Ngành, Trái phiếu `AAA..D`, Options, Futures, Interest Rate Swaps, M&A, Hostile Takeover, LBO, Holding/Subsidiary, Thuế.
  2. **Capitalism Lab** (`C:\Users\LENOVO\Downloads\capitalism lab\[tamhongame.com]_CL\Capitalism Lab`) — Tầng Hạ tầng Kinh tế Thực, Nhà máy, Chuỗi cung ứng (`Input 1..3 -> Output`), Cửa hàng bán lẻ, Viện R&D (`38` công nghệ), Khai khoáng/Nông trại, Bất động sản, Ngân hàng/Bảo hiểm (`7 DLCs`), Cạnh tranh thị phần theo `Quality + Brand - Price`, Lương CEO (`CEO Salary`) và Cổ tức (`Dividends`).
- Đầu ra của project này là khối **`EagleCapitalEngine` (`eagle_capital_engine.py`)** chạy **100% Native Python**, đã được kiểm thử độc lập (`Part A Offline QA`) để sẵn sàng mang sang tích hợp vào **GTA San Andreas (`Project Eagle / gameplay-lab`)** ở **Giai đoạn B (`Stage B`)** qua 2 trục duy nhất: **Tiền (`Money`)** và **Thời gian (`Time`)**.

## Tài nguyên đã có sẵn trong Workspace này (Đọc trước khi làm việc)
1. **Đặc tả kỹ thuật & Kiến trúc hợp nhất:** [`EAGLE_CAPITAL_ENGINE_SPEC.md`](EAGLE_CAPITAL_ENGINE_SPEC.md)
2. **Cơ sở dữ liệu gốc đã trích xuất (`1.77 MB` JSON):** [`data/eagle_wsr_caplab_db.json`](data/eagle_wsr_caplab_db.json) (được tạo bởi [`extract_wsr_caplab_db.py`](extract_wsr_caplab_db.py)), bao gồm:
   - `54` quốc gia, `70` ngành công nghiệp, `1,590` tập đoàn (`1,058` active + `532` slot dự phòng Startup/IPO) và `263` liên kết sở hữu chéo (`<` `>`) từ `CORPNAME.DAT` & `wsr101.dat`.
   - Toàn bộ `56` bảng cơ sở dữ liệu `.DBF` từ `gameset/1STD.SET` của Capitalism Lab (`135` sản phẩm kèm trọng số `PRICE_CN`, `QUALITY_CN`, `BRAND_CN`; `99` công thức sản xuất `MANUFACTURING`; `48` loại `FIRM`; `142` quy cách tòa nhà `FBUILDSTD`; `33` bộ phận `JOB`; `20` loại phần mềm `SOFTWARE_TYPES`; `38` công nghệ `TECH`; `128` thành phố `CITIES`; `64` CEO AI `PERSONS`).
3. **Bản đồ Dịch ngược Binary chi tiết (`x86 Disassembly & Memory/Struct Dumps`):**
   - Wall Street Raider (`WSR.EXE`): [`docs/re_dumps/wsr_subagent_dump.txt`](docs/re_dumps/wsr_subagent_dump.txt)
   - Capitalism Lab (`CapMain.exe` v11.0.98): [`docs/re_dumps/caplab_subagent_dump.txt`](docs/re_dumps/caplab_subagent_dump.txt)

## Nguyên tắc phát triển trong Project này
- **Không sửa đổi** các file gốc tại `C:\Program Files (x86)\wsr` hay `C:\Users\LENOVO\Downloads\capitalism lab\[tamhongame.com]_CL\Capitalism Lab` (chỉ đọc/dịch ngược).
- **Chưa sửa đổi** các file runtime của GTA SA (`C:\Users\LENOVO\Desktop\GTA\Project Eagle\gta sa gameplay-lab`) trong suốt Giai đoạn A; tập trung 100% vào việc hoàn thiện và kiểm thử khối `EagleCapitalEngine` độc lập.
- Đảm bảo phương trình kế toán $\text{Total Assets} \equiv \text{Total Liabilities} + \text{Shareholders' Equity}$ đúng tuyệt đối ở mọi bước thời gian và mọi giao dịch, với hiệu năng mỗi nhịp `< 2 ms` để khi đưa vào GTA SA không gây sụt FPS.

#!/usr/bin/env python3
"""
Paimon Economic & Trading Academy — Curriculum, Inspect Encyclopedia & Live gpt-6-luna Tutor
============================================================================================
Provides the complete backend intelligence for the Web Workstation's Interactive Guidance System:
  1. 9-Module, 36-Quest Interactive Curriculum ("Từ Vỡ Lòng $30,000 Đến Đại Tư Bản"):
     - M0: Làm Quen Bàn Làm Việc & Quy Luật Vận Hành Cơ Bản (Onboarding & UI Mastery)
     - M1: Kinh Tế Học & Kế Toán Vỡ Lòng (Balance Sheet 5 Regimes, P/B, ROCE, EPS, Credit Rating)
     - M2: Nghệ Thuật Đọc Nến Nhật, Khối Lượng & Phân Tích Kỹ Thuật (OHLCV, Patterns, MA7/20, Bollinger, RSI)
     - M3: Chiến Thuật "Cá Con $30,000": Mua Bán Cổ Phiếu Lô Nhỏ, ETF & Trái Phiếu (Micro-Lot Trading)
     - M4: Đọc Thị Trường Vĩ Mô, Chu Kỳ Kinh Tế & Soi Danh Mục Cá Mập AI (Macro & 320 Whale Tracking)
     - M5: Khởi Nghiệp Thực Chiến Bên Capitalism Lab: Mở Công Ty Đầu Tiên & Mặt Bằng 3x3 ($30k Startup & 3x3)
     - M6: Chiến Thuật Chuỗi Cung Ứng, R&D Công Nghệ & Đế Chế Sản Xuất (Supply Chain, R&D & Vertical Shield)
     - M7: Vũ Khí Phố Wall Nâng Cao: Bán Khống, Hàng Hóa, Crypto, Quyền Chọn & Hoán Đổi Lãi Suất (Derivatives)
     - M8: Nghệ Thuật Tài Chính Đại Tư Bản: Công Ty Mẹ-Con, Thuế DRD, Spin-Off, ETF Advisor & Pháp Lý
  2. 68-Entry Inspect/Explain Encyclopedia covering every button, metric, table, chart indicator,
     and 3x3 unit role across all 4 Tabs.
  3. Live Telemetry Context Builder & Context-Aware Paimon AI Tutor powered by gpt-6-luna
     (with deterministic deep-analysis fallback so Q&A works 100% of the time).
"""

import json
import os
import time
import urllib.request
from typing import Any, Dict, List, Optional

from eagle_capital_engine import RATING_LABELS
from luna_ai_orchestrator import DEFAULT_API_KEY, INPUT_COST_PER_1M, OUTPUT_COST_PER_1M

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVES_DIR = os.path.join(WORKSPACE_DIR, "saves")
LOGS_DIR = os.path.join(WORKSPACE_DIR, "logs")
os.makedirs(SAVES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

PAIMON_PROGRESS_PATH = os.path.join(SAVES_DIR, "paimon_academy_progress.json")
PAIMON_CHAT_LOG_PATH = os.path.join(LOGS_DIR, "paimon_chat_calls.jsonl")


# =============================================================================
# 1. COMPLETE 9-MODULE, 36-QUEST INTERACTIVE CURRICULUM
# =============================================================================

PAIMON_CURRICULUM_MODULES: List[Dict[str, Any]] = [
    {
        "module_id": "M0",
        "module_index": 0,
        "title": "Học phần 0: Làm Quen Bàn Làm Việc & Quy Luật Vận Hành (Onboarding 101)",
        "short_title": "M0: Làm Quen UI & Thời Gian",
        "badge": "Vỡ Lòng",
        "summary": (
            "Hiểu bức tranh tổng thể năm 2010-Q1: Sự kết hợp giữa Sàn Tài Chính Phố Wall (Tab 1 - WSR) "
            "và Đế Chế Sản Xuất/Bán Lẻ Đời Thực (Tab 2 - Capitalism Lab), phân biệt rõ 'Acting As' "
            "với 'Viewed Entity', và làm chủ các nút tua thời gian."
        ),
        "quests": [
            {
                "quest_id": "M0_Q1",
                "title": "Bức Tranh Toàn Cảnh 2010-Q1 & Thanh Chỉ Số Vĩ Mô (Macro Ribbon)",
                "tab_id": "tab-wsr",
                "target_selector": ".macro-bar",
                "paimon_speech": (
                    "Chào mừng Aether đến với Phố Wall năm 2010-Q1! Paimon sẽ là Cố vấn Kinh tế kiêm Hoa tiêu "
                    "số 1 của cậu đây! Nhìn lên thanh 6 ô chỉ số trên cùng (Macro Ribbon) nhé: Cậu đang khởi đầu "
                    "ở chế độ '$30k Street Hustler' với đúng $30,000 ($0.03M) tiền mặt giữa 1,078 tập đoàn và "
                    "320 nhà đầu tư AI. Trò chơi này ghép 2 thế giới làm một: Tab 1 là Sàn Chứng Khoán Phố Wall "
                    "(Wall Street Raider), còn Tab 2 là Nhà Máy & Cửa Hàng Đời Thực (Capitalism Lab)!"
                ),
                "formula_note": (
                    "Net Worth (Tài sản ròng) = Total Assets (Tổng Tài Sản) - Total Liabilities (Tổng Nợ). "
                    "Ô '5-REGIME AUDIT: PASS' bảo chứng mọi đồng Mora/USD trong toàn thế giới đều cân bằng tuyệt đối!"
                ),
                "task_instruction": (
                    "Hãy bấm vào thanh chỉ số vĩ mô phía trên cùng (hoặc bấm nút '⚡ Paimon làm mẫu') "
                    "để xác nhận Aether đã sẵn sàng khởi hành tại mốc 2010-Q1 với $30,000!"
                ),
                "auto_action": {"type": "INSPECT_HEADER"},
            },
            {
                "quest_id": "M0_Q2",
                "title": "Phân Biệt Sống Còn: 'Acting As' (Ai Rút Ví) vs 'Viewed Entity' (Đang Soi Ai)",
                "tab_id": "tab-wsr",
                "target_selector": "#acting-as-select",
                "secondary_selector": "#corp-table-body",
                "paimon_speech": (
                    "90% người mới chơi Wall Street Raider lần đầu đều bối rối ở điểm này, nên Paimon dặn kỹ nhé! "
                    "Trên màn hình luôn có 2 khái niệm riêng biệt:\n"
                    "1. 'Acting As' (ô chọn trên thanh điều khiển): Cho biết AI ĐANG LÀ NGƯỜI RÚT VÍ RA LỆNH (lúc đầu là #1 Aether, "
                    "sau này khi cậu lập công ty Startup #61 hay thâu tóm tập đoàn khác thì có thể đổi sang dùng tiền trong két của công ty đó!).\n"
                    "2. 'Viewed Entity' (bảng giữa): Là công ty hoặc nhà đầu tư mà cậu đang BẤM XEM BÁO CÁO. Bấm xem công ty khác không làm mất quyền điều khiển của Aether!"
                ),
                "formula_note": (
                    "Quy tắc: Người trả tiền = Acting As (ACTOR ENTITY ID) | Cổ phiếu mục tiêu được mua/bán = TARGET CORP ID."
                ),
                "task_instruction": (
                    "Hãy bấm chọn một tập đoàn bất kỳ trong bảng 'Entity & Corp Directory' bên trái (ví dụ #13 WFC) "
                    "để soi báo cáo của họ trong khi 'Acting As' vẫn giữ nguyên là #1 Aether!"
                ),
                "auto_action": {"type": "SELECT_ENTITY", "entity_id": 13},
            },
            {
                "quest_id": "M0_Q3",
                "title": "Làm Chủ 3 Nhịp Thời Gian: '+1 Subtick', '+1 Day' & '+1 Quarter'",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-step-day",
                "paimon_speech": (
                    "Thế giới kinh tế này không bắt cậu phải vội! Thời gian chỉ trôi khi Aether bấm 1 trong 3 nút:\n"
                    "• '+1 Subtick' (< 0.2ms): Nhịp vi mô trong ngày, giá cổ phiếu/BTC/Dầu nhúc nhích nhẹ.\n"
                    "• '+1 Day': Tiến lịch 1 ngày giao dịch, vẽ thêm/cập nhật cây nến ngày trên bảng nến OHLCV.\n"
                    "• '+1 Quarter (Full Sim)': Chốt sổ 1 Quý (3 tháng) — cả 1,078 tập đoàn và các nhà máy tính doanh thu, đóng thuế, trả Cổ tức (Dividends) về ví cho cậu!"
                ),
                "formula_note": (
                    "1 Năm = 4 Quý (Q1..Q4) = 12 Tháng = 360 Ngày giao dịch. Mỗi Quý là 1 chu kỳ báo cáo tài chính."
                ),
                "task_instruction": (
                    "Hãy bấm thử nút '+1 Subtick' hoặc '+1 Day' trên thanh điều khiển phía trên để xem bảng điện và giá cổ phiếu chuyển động!"
                ),
                "auto_action": {"type": "SEND_ACTION", "cmd": "STEP_DAY", "payload": {}},
            },
            {
                "quest_id": "M0_Q4",
                "title": "Lưu Trữ Nguyên Tử ('Save/Load') & Chuyển Đổi Chế Độ Chơi (Tab 4)",
                "tab_id": "tab-news",
                "target_selector": "#btn-save-game",
                "paimon_speech": (
                    "Trước khi mang tiền đi đầu tư hay thử nghiệm các kịch bản khủng hoảng vĩ mô (S1..S6), "
                    "người khôn ngoan luôn biết cách Lưu game (Save State)! Ở Tab 4, nút '💾 Save Full-Fidelity State' "
                    "lưu chính xác 100% toàn bộ 1,915 thực thể với sai số 0.000000 USD. Ngoài ra, nút 'Mode: $30k Hustler' "
                    "trên thanh công cụ cho phép cậu đổi sang chế độ Tỷ phú '$1B Sandbox' bất cứ lúc nào muốn thử vũ khí hạng nặng!"
                ),
                "formula_note": (
                    "Save/Load bảo toàn tuyệt đối: Tổng Tiền Mặt + Cổ Phiếu + Nhà Máy + Hợp Đồng Phái Sinh (0.000000 drift)."
                ),
                "task_instruction": (
                    "Hãy chuyển sang 'Tab 4 (4. Stress Scenarios, Save/Load & QA Wire)' và bấm nút xanh '💾 Save Full-Fidelity State'!"
                ),
                "auto_action": {"type": "SEND_ACTION", "cmd": "SAVE_GAME", "payload": {}, "tab_id": "tab-news"},
            },
        ],
    },
    {
        "module_id": "M1",
        "module_index": 1,
        "title": "Học phần 1: Kinh Tế Học & Kế Toán Vỡ Lòng (Balance Sheet & Fundamental Analysis 101)",
        "short_title": "M1: Kế Toán & Phân Tích Cơ Bản",
        "badge": "Nền Tảng",
        "summary": (
            "Đọc hiểu từng dòng trên Bảng Cân Đối Kế Toán 5 Chế độ (Balance Sheet), tại sao Mua tài sản "
            "không làm giảm Net Worth, và ý nghĩa của Book Value (P/B), ROCE%, EPS, Free Float, Xếp hạng tín nhiệm AAA..D."
        ),
        "quests": [
            {
                "quest_id": "M1_Q1",
                "title": "Phương Trình Kế Toán Bất Biến: Tài Sản = Nợ Phải Trả + Vốn Chủ Sở Hữu",
                "tab_id": "tab-wsr",
                "target_selector": "#bs-table-body",
                "paimon_speech": (
                    "Aether nhìn vào cột giữa của Tab 1 nhé! Đó là Bảng Cân Đối Kế Toán (Balance Sheet). "
                    "Đừng sợ chữ kế toán, nó chỉ trả lời 3 câu hỏi cực dễ:\n"
                    "1. 'TOTAL ASSETS' (Tổng Tài Sản): Thực thể này đang nắm giữ những gì có giá trị? (Tiền mặt Cash, Nhà máy CapAssets, Hàng tồn kho WorkingCap, Cổ phiếu, Trái phiếu, Crypto...).\n"
                    "2. 'TOTAL LIABILITIES' (Tổng Nợ Phải Trả): Thực thể này đang nợ ngân hàng, nợ trái phiếu hay nợ thuế bao nhiêu?\n"
                    "3. 'NET WORTH / EQUITY' (Tài Sản Ròng): Lấy Tổng Tài Sản trừ đi Tổng Nợ còn lại bao nhiêu tiền thực chất thuộc về chủ sở hữu!"
                ),
                "formula_note": (
                    "Total Assets = Total Liabilities + Net Worth (Shareholders' Equity). "
                    "Khi cậu lấy $5,000 Cash mua $5,000 Trái phiếu, Cash giảm $5k nhưng Bond tăng $5k -> Net Worth giữ nguyên!"
                ),
                "task_instruction": (
                    "Ở Tab 1, hãy bấm nút màu cam 'Aether (#1)' ở cột trái để hiển thị và đọc Bảng Cân Đối Kế Toán cá nhân của chính Aether!"
                ),
                "auto_action": {"type": "SELECT_ENTITY", "entity_id": 1, "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M1_Q2",
                "title": "5 Chế Độ Bảng Cân Đối (5 Regimes): Tại Sao Ngân Hàng ('BANK') Không Có Nhà Máy?",
                "tab_id": "tab-wsr",
                "target_selector": "#dir-pill-BANKS",
                "secondary_selector": "#bs-table-body",
                "paimon_speech": (
                    "Trong thế giới thực cũng như trong EagleCapitalEngine, không phải công ty nào cũng hạch toán giống nhau! "
                    "Có 5 chế độ kế toán (5 Regimes):\n"
                    "• Tập đoàn sản xuất (IND): Tài sản chính là Nhà máy (CapAssets) và Tồn kho (Working Cap).\n"
                    "• Ngân hàng thương mại (BANK): Không xây nhà máy! Tài sản sinh lời chính của ngân hàng là Dư nợ cho vay (Bank Loans Portfolio), còn Nợ phải trả chính là Tiền gửi của khách hàng (Deposits & CDs)!\n"
                    "• Công ty Bảo hiểm (INSUR): Thu phí bảo hiểm (Insurance Float) đem đi đầu tư Trái phiếu và MBS."
                ),
                "formula_note": (
                    "Ngân hàng (COMMERCIAL_BANK): CAR% (Tỷ lệ an toàn vốn) = Net Worth / Total Assets. Ngân hàng sống bằng chênh lệch lãi cho vay trừ lãi tiền gửi (NIM)."
                ),
                "task_instruction": (
                    "Hãy bấm vào nút lọc 'Banks/Insur' ở cột trái Tab 1, sau đó bấm chọn một Ngân hàng (như #11 CMB hoặc #13 WFC) để xem dòng 'Bank Loans Portfolio' và 'Deposits' trên bảng cân đối!"
                ),
                "auto_action": {"type": "FILTER_AND_SELECT", "filter": "BANKS", "entity_id": 13, "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M1_Q3",
                "title": "Định Giá Cổ Phiếu: Book Value (P/B), ROCE%, EPS & Cổ Phiếu Trôi Nổi (Free Float)",
                "tab_id": "tab-wsr",
                "target_selector": "#bs-table-body",
                "paimon_speech": (
                    "Làm sao biết một cổ phiếu đang ĐẮT hay RẺ? Paimon chỉ cho cậu 4 con số vàng ở cuối bảng cân đối:\n"
                    "1. 'Shares Out' & 'Free Float': Tổng số cổ phần phát hành và số cổ phần đang trôi nổi ngoài chợ mà cậu mua được (luôn >= 25%).\n"
                    "2. 'Book Value/sh' (Giá trị sổ sách mỗi CP) = Net Worth / Shares Out. Nếu giá cổ phiếu trên sàn (Stock Price) thấp hơn hoặc gần bằng Book Value (P/B <= 1.2x), đó là món hời giá trị (Value Stock)!\n"
                    "3. 'ROCE%' (Return on Capital Employed): 100 đồng vốn bỏ vào kinh doanh sinh ra bao nhiêu đồng lãi mỗi năm? Công ty có ROCE > 15% là cỗ máy in tiền!"
                ),
                "formula_note": (
                    "P/B Ratio = (Stock Price × Shares Out) / Net Worth. Giá hợp lý WSR = 0.65 × BookValue/sh + 0.30 × (EPS × P/E) + 0.05 × DividendBonus."
                ),
                "task_instruction": (
                    "Hãy bấm nút lọc 'All Corps' bên trái và bấm chọn một tập đoàn công nghiệp (ví dụ #321 hoặc bất kỳ dòng IND nào) để soi dòng 'Stock Price / Shares Out / Free Float' và 'ROCE% / EPS'!"
                ),
                "auto_action": {"type": "FILTER_AND_SELECT", "filter": "ALL", "entity_id": 321, "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M1_Q4",
                "title": "Xếp Hạng Tín Nhiệm ('AAA' Xuống 'D') & Hạn Mức Vay ('Credit Line')",
                "tab_id": "tab-wsr",
                "target_selector": "#corp-table-body",
                "paimon_speech": (
                    "Nhìn cột 'RTG' ở bảng bên trái kìa Aether! Đó là Xếp hạng Tín nhiệm (Credit Rating) từ cao xuống thấp: "
                    "AAA -> AA -> A -> BBB -> BB -> B -> CCC -> D.\n"
                    "• Hạng AAA/AA: Công ty cực ít nợ, tiền mặt dồi dào, vay ngân hàng được lãi suất ưu đãi bằng đúng Prime Rate.\n"
                    "• Hạng BB/B/CCC: Công ty ngập trong nợ (Junk Rating), lãi vay bị phạt rất nặng và dễ là con mồi cho các quỹ Bán khống (Short Sellers)!"
                ),
                "formula_note": (
                    "Credit Line Limit (Hạn mức ngân hàng cho vay tối đa) phụ thuộc vào Net Worth và Credit Rating (AAA được vay tới 100% Net Worth; CCC bị cắt hạn mức)."
                ),
                "task_instruction": (
                    "Hãy tìm và bấm vào một tập đoàn có hạng tín nhiệm 'AAA' hoặc 'AA' trong danh sách bên trái để kiểm tra sức khỏe tài chính của một 'Blue-Chip'!"
                ),
                "auto_action": {"type": "SELECT_ENTITY", "entity_id": 11, "tab_id": "tab-wsr"},
            },
        ],
    },
    {
        "module_id": "M2",
        "module_index": 2,
        "title": "Học phần 2: Nghệ Thuật Đọc Nến Nhật, Khối Lượng & Phân Tích Kỹ Thuật (OHLCV, MA, Bollinger & RSI)",
        "short_title": "M2: Đọc Nến Nhật & Kỹ Thuật",
        "badge": "Kỹ Thuật",
        "summary": (
            "Giải phẫu cây nến Nhật OHLCV và cột Volume trên #ohlcv-canvas, nhận diện các mẫu hình nến đảo chiều/tiếp diễn "
            "(Doji, Hammer, Shooting Star, Engulfing, Marubozu), và kết hợp MA7/MA20, Bollinger Bands cùng RSI(14)."
        ),
        "quests": [
            {
                "quest_id": "M2_Q1",
                "title": "Giải Phẫu Một Cây Nến Nhật (Open, High, Low, Close) & Cột Khối Lượng (Volume)",
                "tab_id": "tab-wsr",
                "target_selector": "#ohlcv-canvas",
                "paimon_speech": (
                    "Bây giờ Paimon sẽ truyền dạy cho Aether tuyệt kỹ đọc Nến Nhật (Japanese Candlesticks) ngay trên bảng '#ohlcv-canvas' nhé! "
                    "Mỗi cây nến kể lại cuộc chiến giữa Phe Mua (Bò - Bull) và Phe Bán (Gấu - Bear) trong 1 kỳ:\n"
                    "• Thân nến ( phần hộp đặc): Nối giữa Giá Mở Cửa (O - Open) và Giá Đóng Cửa (C - Close). Nếu C >= O (giá tăng), thân nến màu XANH LÁ. Nếu C < O (giá giảm), thân nến màu ĐỎ.\n"
                    "• Râu nến trên (Upper Wick): Đỉnh cao nhất (H - High). Râu trên dài nghĩa là phe Mua cố đẩy lên nhưng bị phe Bán đạp xuống!\n"
                    "• Râu nến dưới (Lower Wick): Đáy thấp nhất (L - Low). Râu dưới dài nghĩa là giá bị đạp xuống nhưng có dòng tiền bắt đáy kéo ngược lên!\n"
                    "• Cột bên dưới (Volume): Khối lượng giao dịch. Nến xanh đi kèm cột Volume cao vọt là dòng tiền cá mập đang gom hàng thật!"
                ),
                "formula_note": (
                    "Biên độ nến (Range) = High - Low | Thân nến (Body) = |Close - Open| | Râu trên = High - max(O,C) | Râu dưới = min(O,C) - Low."
                ),
                "task_instruction": (
                    "Hãy rê chuột qua lại trên biểu đồ nến '#ohlcv-canvas' (hoặc bấm vào biểu đồ) để đọc thông số O / H / L / C / Vol của từng cây nến trên thanh readout!"
                ),
                "auto_action": {"type": "HOVER_CANDLE_CHART", "bar_idx": 35, "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M2_Q2",
                "title": "Nhận Diện 6 Mô Hình Nến Kinh Điển: Doji, Hammer, Shooting Star, Engulfing & Marubozu",
                "tab_id": "tab-wsr",
                "target_selector": "#chart-pattern-badge",
                "secondary_selector": "#chart-explain-banner",
                "paimon_speech": (
                    "Cậu không cần phải tự đo từng milimét râu nến đâu vì Paimon đã gắn sẵn bộ nhận diện Mô hình Nến tự động ở nút 'Pattern' phía trên biểu đồ! "
                    "Hãy nhớ 5 mẫu hình kinh điển này:\n"
                    "1. 'Hammer / Bullish Pinbar' (Nến Búa): Thân nhỏ ở trên, râu dưới dài >= 2 lần thân -> Tín hiệu bắt đáy đảo chiều TĂNG cực mạnh!\n"
                    "2. 'Shooting Star' (Nến Sao Băng): Râu trên dài ngoằng -> Phe bán xả hàng trên đỉnh, coi chừng đảo chiều GIẢM!\n"
                    "3. 'Bullish / Bearish Engulfing' (Nhấn Chìm): Cây nến sau nuốt trọn thân cây nến trước -> Đảo chiều xu hướng quyết liệt!\n"
                    "4. 'Doji': Giá mở cửa và đóng cửa gần trùng nhau (thân mỏng dính) -> Hai phe đang giằng co lưỡng lự.\n"
                    "5. 'Marubozu': Nến thân dài đặc gần như không có râu -> Lực mua/bán áp đảo tuyệt đối!"
                ),
                "formula_note": (
                    "Hammer: LowerWick >= 2.0 × Body & UpperWick <= 0.4 × Body | Doji: Body <= 0.12 × (High - Low)."
                ),
                "task_instruction": (
                    "Hãy bấm vào nút huy hiệu 'Pattern' (#chart-pattern-badge) ở góc phải trên biểu đồ nến để xem Paimon giải phẫu mẫu hình nến hiện tại ở dòng '#chart-explain-banner' bên dưới!"
                ),
                "auto_action": {"type": "CLICK_SELECTOR", "selector": "#chart-pattern-badge", "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M2_Q3",
                "title": "Đường Trung Bình Động 'MA7 / MA20' (Golden Cross) & Dải 'Bollinger Bands'",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-ind-ma",
                "secondary_selector": "#btn-ind-bb",
                "paimon_speech": (
                    "Một cây nến riêng lẻ có thể làm cậu nhiễu, nên các trader Phố Wall luôn bật thêm 2 lớp bản đồ xu hướng:\n"
                    "• 'MA7/20' (Moving Averages): Đường xanh cyan là trung bình giá 7 kỳ gần nhất (MA7 - ngắn hạn); đường vàng cam là trung bình 20 kỳ (MA20 - trung hạn). Khi MA7 cắt từ dưới lên trên MA20 gọi là 'Golden Cross' (Giao cắt vàng -> Báo hiệu sóng TĂNG); cắt xuống dưới là 'Death Cross' (Báo hiệu sóng GIẢM).\n"
                    "• 'Bollinger Bands' (2 đường màu tím): Ôm lấy 95% biến động giá (MA20 ± 2 độ lệch chuẩn σ). Khi 2 dải tím thắt cổ chai là báo hiệu sắp nổ bão giá; khi nến đập vào dải tím dưới thường có lực bật hồi lên!"
                ),
                "formula_note": (
                    "SMA(N) = Tổng(Close của N nến) / N | Bollinger Upper = SMA(20) + 2σ | Bollinger Lower = SMA(20) - 2σ."
                ),
                "task_instruction": (
                    "Hãy bấm thử vào nút 'MA7/20' hoặc nút 'Bollinger' phía trên biểu đồ nến để bật/tắt chỉ báo và đọc giải thích tín hiệu!"
                ),
                "auto_action": {"type": "CLICK_SELECTOR", "selector": "#btn-ind-ma", "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M2_Q4",
                "title": "Chỉ Số Động Lượng 'RSI(14)' & Soi Biểu Đồ Nến Đa Tài Sản (BTC, OIL, GOLD, WSR Index)",
                "tab_id": "tab-wsr",
                "target_selector": "#chart-rsi-badge",
                "secondary_selector": "#chart-sym-BTC",
                "paimon_speech": (
                    "Làm sao biết giá đã tăng quá nóng (dễ đu đỉnh) hay đã giảm quá đà (cơ hội bắt đáy)? Hãy nhìn nút 'RSI(14)'!\n"
                    "• RSI >= 70 (Màu đỏ - Overbought / Quá mua): Phe mua đã hưng phấn tột độ, cẩn thận nhịp chỉnh chốt lời!\n"
                    "• RSI <= 30 (Màu xanh lá - Oversold / Quá bán): Thị trường đang hoảng loạn bán tháo quá mức, nếu kèm nến Hammer rút chân thì là điểm mua vàng!\n"
                    "• RSI 30..70 (Màu xanh cyan - Trung tính): Xu hướng đang chạy ổn định.\n"
                    "Đặc biệt, dãy nút bên trái trên biểu đồ cho phép cậu soi nến của cả Cổ phiếu đang chọn, Bitcoin (BTC/USD), Dầu thô (OIL), Vàng (GOLD) và Chỉ số chung (WSR Index)!"
                ),
                "formula_note": (
                    "RSI(14) = 100 - [100 / (1 + RS)], với RS = Trung bình mức tăng 14 kỳ / Trung bình mức giảm 14 kỳ."
                ),
                "task_instruction": (
                    "Hãy bấm vào nút 'RSI(14)' (#chart-rsi-badge) hoặc bấm chuyển thử sang biểu đồ 'BTC/USD' / 'OIL' / 'GOLD'!"
                ),
                "auto_action": {"type": "CLICK_SELECTOR", "selector": "#chart-rsi-badge", "tab_id": "tab-wsr"},
            },
        ],
    },
    {
        "module_id": "M3",
        "module_index": 3,
        "title": "Học phần 3: Chiến Thuật 'Cá Con $30,000' — Mua Bán Cổ Phiếu Lô Nhỏ, ETF & Trái Phiếu",
        "short_title": "M3: Trading Lô Nhỏ $30k",
        "badge": "Thực Chiến $30k",
        "summary": (
            "Kết hợp Phân tích Cơ bản (P/B, ROCE, hạng tín nhiệm) và Phân tích Kỹ thuật (Nến, RSI, MA) "
            "để chia vốn $30,000 mua lô nhỏ 100 cổ phiếu (100sh), mua chứng chỉ quỹ ETF, mua Trái phiếu Chính phủ $5k và chốt lời."
        ),
        "quests": [
            {
                "quest_id": "M3_Q1",
                "title": "Định Cỡ Lệnh Lô Nhỏ ('100sh = 0.0001M') & Đọc Thanh Tính Tiền 'Est. Cost'",
                "tab_id": "tab-wsr",
                "target_selector": "#order-preview-box",
                "secondary_selector": "#ord-shares",
                "paimon_speech": (
                    "Giờ là lúc rút kiếm xuống tiền thật đây Aether! Vì đơn vị chuẩn của Phố Wall trong WSR là Triệu cổ phiếu (M), "
                    "nếu cậu để 1.0M (1 triệu cổ phiếu) thì tốn hàng chục triệu đô! Với vốn $30,000 ($0.03M), Paimon đã thiết kế sẵn nút "
                    "lô nhỏ '100sh' (0.0001M = 100 cổ phiếu). Trước khi mua bất kỳ mã nào, hãy nhìn hộp '#order-preview-box' để xem "
                    "'Est. Cost' (Chi phí dự kiến) có vừa túi tiền (khoảng $1,500 - $15,000) hay không nhé!"
                ),
                "formula_note": (
                    "0.0001M cổ phiếu = 100 cổ phiếu | Est. Cost = Số cổ phiếu × Giá hiện tại (+ 1% phí môi giới khi khớp lệnh)."
                ),
                "task_instruction": (
                    "Ở Tab 1, hãy chọn một công ty ở bảng bên trái (như #13 WFC hoặc #11 CMB) và bấm nút '100sh' ở cột phải để xem chi phí dự kiến!"
                ),
                "auto_action": {"type": "PRESET_SHARES_100", "entity_id": 13, "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M3_Q2",
                "title": "Khớp Lệnh Mua Cổ Phiếu Đầu Tiên ('📈 Buy Long') & Kiểm Tra Bảng 'Holdings'",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-buy-long",
                "secondary_selector": "#holdings-table-body",
                "paimon_speech": (
                    "Khi cậu đã chọn được công ty có nền tảng tốt (Net Worth dương, hạng tín nhiệm tốt) và kiểm tra biểu đồ nến không bị Quá mua (RSI < 70), "
                    "hãy bấm nút xanh lá '📈 Buy Long'! Ngay lập tức:\n"
                    "• Tiền mặt (Cash) của Aether giảm đi đúng bằng giá trị mua + 1% phí môi giới.\n"
                    "• Cổ phiếu đó xuất hiện ngay trong bảng 'Unified Stock Holdings & Shorts' ở cuối cột giữa với nhãn 'LONG'!\n"
                    "• Khi giá cổ phiếu tăng hoặc công ty trả cổ tức mỗi quý, tài sản của Aether sẽ tăng lên!"
                ),
                "formula_note": (
                    "Giá khớp Mua (Exec Price) = 0.5 × (OldPrice + NewPrice) × 1.01 (1% broker commission)."
                ),
                "task_instruction": (
                    "Hãy bấm nút xanh lá '📈 Buy Long' ở cột phải Tab 1 để mua lô cổ phiếu đầu tiên vào danh mục của Aether!"
                ),
                "auto_action": {"type": "BUY_MICRO_LOT_STOCK", "entity_id": 13, "shares_m": 0.0001, "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M3_Q3",
                "title": "Đa Dạng Hóa Với Quỹ 'ETFs (20)' & Trái Phiếu Chính Phủ An Toàn ('Buy GovBond $5k')",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-buy-govbond",
                "secondary_selector": "#dir-pill-ETFS",
                "paimon_speech": (
                    "Đừng để tiền mặt còn lại nằm ngủ yên! Với phần vốn nhàn rỗi, cá con thông minh có 2 lựa chọn cực kỳ an toàn:\n"
                    "1. Mua Trái phiếu Chính phủ ('Buy GovBond'): Ở khu vực 2 cột phải, bấm nút '$5k' (0.005M = $5,000) rồi bấm 'Buy GovBond' để hưởng lãi suất trái phiếu chính phủ đều đặn và tăng giá khi lãi suất giảm.\n"
                    "2. Mua Chứng chỉ Quỹ ETF: Bấm bộ lọc 'ETFs (20)' bên trái (#1581..#1600) để mua cả một rổ cổ phiếu ngành chỉ bằng 1 lệnh!"
                ),
                "formula_note": (
                    "Giá Trái phiếu Chính phủ (Long GovBond) biến thiên ngược chiều với Lãi suất dài hạn: Khi lãi suất giảm, giá trái phiếu tăng!"
                ),
                "task_instruction": (
                    "Ở khu vực 2 cột phải Tab 1, hãy bấm nút '$5k' rồi bấm nút xanh 'Buy GovBond' (hoặc lọc 'ETFs (20)' và mua 100sh quỹ ETF)!"
                ),
                "auto_action": {"type": "BUY_MICRO_GOVBOND", "notional_m": 0.005, "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M3_Q4",
                "title": "Chốt Lời Tức Thì Bằng Nút 'Sell All' Ngay Trong Bảng Danh Mục",
                "tab_id": "tab-wsr",
                "target_selector": "#holdings-table-body",
                "secondary_selector": "#btn-sell-long",
                "paimon_speech": (
                    "Mua xong rồi thì bán ở đâu cho lẹ? Aether nhìn xuống bảng 'Unified Stock Holdings & Shorts' ở cuối cột giữa nhé! "
                    "Mỗi dòng cổ phiếu cậu đang nắm giữ đều có sẵn nút màu đỏ 'Sell All' ở cột ngoài cùng bên phải. Chỉ cần bấm 1 cú click vào 'Sell All' "
                    "(hoặc bấm 'Sell Long' ở cột phải), toàn bộ cổ phiếu mã đó sẽ được bán ra thị trường và tiền tươi thóc thật chảy ngay về ví Cash của cậu!"
                ),
                "formula_note": (
                    "Lãi vốn thực hiện (Realized Capital Gain) = Tiền thu về (Proceeds) - Giá vốn mua ban đầu (Cost Basis)."
                ),
                "task_instruction": (
                    "Hãy bấm nút 'Sell All' trong bảng 'Unified Stock Holdings' (hoặc bấm nút 'Sell Long' / 'Sell GovBond' ở cột phải) để thực hành chốt lời thu tiền mặt về!"
                ),
                "auto_action": {"type": "SELL_ALL_OR_GOVBOND", "tab_id": "tab-wsr"},
            },
        ],
    },
    {
        "module_id": "M4",
        "module_index": 4,
        "title": "Học phần 4: Đọc Thị Trường Vĩ Mô, Chu Kỳ Kinh Tế & Soi Danh Mục Cá Mập AI (Macro & Whale Tracking)",
        "short_title": "M4: Vĩ Mô & Soi Cá Mập AI",
        "badge": "Vĩ Mô & AI",
        "summary": (
            "Nắm bắt mối quan hệ nhân quả giữa GDP, Lạm phát CPI, Lãi suất Prime Rate, giá Dầu/Vàng, "
            "và cách soi danh mục của 320 Nhà đầu tư AI thuộc 24 Trường phái (Archetypes)."
        ),
        "quests": [
            {
                "quest_id": "M4_Q1",
                "title": "Chu Kỳ Kinh Tế Vĩ Mô: Khi Nào Tiền Rẻ, Khi Nào Bão Lãi Suất?",
                "tab_id": "tab-wsr",
                "target_selector": "#chart-sym-OIL",
                "secondary_selector": ".macro-bar",
                "paimon_speech": (
                    "Muốn bơi cùng cá mập thì phải biết nhìn thủy triều vĩ mô Aether ơi! Hãy nhớ quy luật domino này:\n"
                    "• Khi Giá Dầu (OIL) tăng vọt lên $160/thùng hoặc các cửa hàng tăng giá bán quá cao -> Lạm phát (CPI) bùng phát.\n"
                    "• Để dập lạm phát, Ngân hàng Trung ương sẽ tăng mạnh Lãi suất cơ bản (Prime Rate).\n"
                    "• Khi Prime Rate tăng cao: Tiền vay ngân hàng trở nên đắt đỏ, định giá P/E của cổ phiếu bị ép giảm, giá Trái phiếu sụt giảm, còn các công ty nợ nhiều (hạng BB/CCC) sẽ ngắc ngoải!\n"
                    "• Ngược lại, khi Lạm phát hạ nhiệt và Prime Rate giảm: Tiền rẻ tràn ngập, cổ phiếu và bất động sản bay cao!"
                ),
                "formula_note": (
                    "Taylor Rule trong Engine: Prime Rate ≈ 3.0% + CPI Inflation + 0.35 × GDP Growth. Hệ số P/E thị trường giảm khi Prime Rate tăng."
                ),
                "task_instruction": (
                    "Hãy bấm vào nút 'OIL' hoặc 'GOLD' hoặc 'WSR Index' trên thanh biểu đồ nến ở Tab 1 để quan sát đồ thị chu kỳ giá hàng hóa và chỉ số chung!"
                ),
                "auto_action": {"type": "CLICK_SELECTOR", "selector": "#chart-sym-OIL", "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M4_Q2",
                "title": "Soi Hồ Sơ '320 Investors' Ngay Tại Tab 1 Để Xem Cá Mập Đang Gom Mã Nào",
                "tab_id": "tab-wsr",
                "target_selector": "#dir-pill-INVESTORS",
                "secondary_selector": "#holdings-table-body",
                "paimon_speech": (
                    "Trong đại dương này có 320 nhà đầu tư AI (#2001..#2320) từ các huyền thoại tỷ phú như Warren B. II (#2001), Jim S. (#2002), Carl I. (#2003) "
                    "cho tới các đồng môn khởi nghiệp $30k như Minh K. (#2017) hay hội WSB YOLO (#2024). Khi cậu bấm nút lọc '320 Investors' bên trái:\n"
                    "• Cột 'Price' của họ hiện dấu '—' vì họ là CON NGƯỜI / QUỸ ĐẦU TƯ, không phải công ty phát hành cổ phiếu!\n"
                    "• Khi cậu bấm vào tên bất kỳ nhà đầu tư AI nào, bảng 'Unified Stock Holdings' ở dưới cột giữa sẽ tự động chuyển sang chế độ 'Viewed Entity' để phơi bày toàn bộ cổ phiếu mà cá mập đó đang nắm giữ hoặc bán khống!"
                ),
                "formula_note": (
                    "Guardrail thông minh: Bấm vào Nhà đầu tư AI (#2001..#2320) chỉ bật chế độ Soi Danh Mục (Inspect Mode), giữ nguyên Target Corp ID để cậu không bấm mua nhầm con người!"
                ),
                "task_instruction": (
                    "Ở cột trái Tab 1, hãy bấm nút lọc '320 Investors' rồi bấm vào một nhà đầu tư AI bất kỳ để soi danh mục của họ!"
                ),
                "auto_action": {"type": "FILTER_AND_SELECT", "filter": "INVESTORS", "entity_id": 2001, "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M4_Q3",
                "title": "Khám Phá Ma Trận 24 Trường Phái Đầu Tư & Bộ Não 'gpt-6-luna' (Tab 3)",
                "tab_id": "tab-ai",
                "target_selector": "#cohorts-table-body",
                "secondary_selector": "#luna-theses-box",
                "paimon_speech": (
                    "Chuyển sang Tab 3 nhé Aether! Tại đây cậu nhìn thấy toàn bộ 320 nhà đầu tư AI được chia thành 24 Trường phái (Archetypes) độc lập:\n"
                    "• Cột trái: Thống kê 24 nhóm (từ Săn cổ tức DRD, Bán khống định lượng, Vua Trái phiếu, Trùm Bán lẻ, Trùm R&D Bán dẫn cho tới Khởi nghiệp $30k).\n"
                    "• Cột giữa: Luận điểm chiến lược (Strategic Theses) và Kịch bản 4 quý (Bull/Bear Trigger) do các trưởng nhóm lập ra.\n"
                    "• Cột phải: Bảng xếp hạng Kim tự tháp Tài sản (chuyển đổi giữa 'Top Whales' tỷ phú và '$30k Hustlers' cùng xuất phát điểm với cậu) kèm Nghĩa địa Cháy Tài Khoản ([Gen N] Wipeout & Respawn)!"
                ),
                "formula_note": (
                    "320 AI vận hành siêu mượt (< 1ms) nhờ kết hợp Playbook điều kiện + Thuật toán hành vi đám đông (0 tốn phí API ngầm)."
                ),
                "task_instruction": (
                    "Hãy chuyển sang 'Tab 3 (3. 320 Investors & gpt-6-luna Brain)' và bấm nút '$30k Hustlers' ở cột phải (hoặc bấm vào 1 dòng trong bảng 24 Archetypes)!"
                ),
                "auto_action": {"type": "CLICK_SELECTOR", "selector": "#btn-list-hustlers", "tab_id": "tab-ai"},
            },
            {
                "quest_id": "M4_Q4",
                "title": "Đọc Bản Tin Phố Wall ('News Wire') & Giám Sát 4 Vòng Lặp Giao Thoa (Tab 4)",
                "tab_id": "tab-news",
                "target_selector": "#coupling-telemetry-box",
                "secondary_selector": "#news-feed-box",
                "paimon_speech": (
                    "Ở Tab 4, cậu có 2 bảng tình báo cực kỳ giá trị:\n"
                    "1. 'Decoded WSR News Wire' (bên trái dưới): Phát sóng trực tiếp mọi thương vụ gom cổ phiếu (13F Filing), bán khống, mở nhà máy mới, và các vụ cháy tài khoản trên toàn thị trường.\n"
                    "2. '4-Channel Bidirectional WSR <-> CapLab Coupling' (bên phải trên): Đo lường trực tiếp cách các nhà máy ở Tab 2 bơm tăng trưởng GDP và lạm phát CPI lên Tab 1, và cách giá Dầu/Lãi suất ở Tab 1 tác động ngược xuống chi phí COGS/OPEX của nhà máy ở Tab 2!"
                ),
                "formula_note": (
                    "4 Vòng lặp 2 chiều: (1) CapEx & Giá bán lẻ -> GDP & CPI | (2) Mỏ dầu/khoáng sản <-> Giá Futures & COGS | (3) Lạm phát & Lãi suất -> OPEX & BĐS | (4) R&D Tech -> Đào thải công nghệ cũ."
                ),
                "task_instruction": (
                    "Hãy mở 'Tab 4' và bấm vào bảng '4-Channel Bidirectional Coupling' (hoặc khung tin tức 'News Wire') để kiểm tra mạch máu liên thông của nền kinh tế!"
                ),
                "auto_action": {"type": "INSPECT_TAB4_COUPLING", "tab_id": "tab-news"},
            },
        ],
    },
    {
        "module_id": "M5",
        "module_index": 5,
        "title": "Học phần 5: Khởi Nghiệp Thực Chiến Bên Capitalism Lab — Mở Công Ty Đầu Tiên & Mặt Bằng 3x3",
        "short_title": "M5: Startup $30k & Mặt Bằng 3x3",
        "badge": "Khởi Nghiệp",
        "summary": (
            "Dùng $20,000 vốn tự có + đòn bẩy ngân hàng 3x ($60,000) lập công ty cổ phần riêng, mở cửa hàng/nhà xưởng đầu tiên, "
            "làm chủ mặt bằng 3x3 (9 ô bộ phận), huấn luyện nhân sự và tối ưu công thức PRQ (Price - Quality - Brand)."
        ),
        "quests": [
            {
                "quest_id": "M5_Q1",
                "title": "Vườn Ươm Khởi Nghiệp '$30k': Góp $20k Vốn + Vay Ngân Hàng 3x Để Mở Công Ty Riêng!",
                "tab_id": "tab-caplab",
                "target_selector": "#btn-incorporate-startup",
                "paimon_speech": (
                    "Chỉ mua đi bán lại cổ phiếu lẻ thì bao giờ mới thành Đại Tư Bản hả Aether? Sang Tab 2 ngay thôi! "
                    "Một nhà máy lớn của các tập đoàn tốn $15M-$25M, nhưng với $30,000 trong tay, cậu có 'Vườn Ươm Khởi Nghiệp' ($30k Startup Incubator) ở góc trên bên trái Tab 2:\n"
                    "• Cậu chỉ cần bỏ 'Seed Eq = 0.02M' ($20,000 vốn tự có, giữ lại $10,000 tiền túi dự phòng).\n"
                    "• Ngân hàng thương mại cho công ty mới vay đòn bẩy 'Loan x = 3.0' ($60,000).\n"
                    "• Tổng cộng công ty cổ phần mới của cậu (ví dụ #61 Aether Ventures - cậu nắm 80% cổ phần kiểm soát) có ngay $80,000 để mở Cửa hàng bán lẻ (RETAIL) hoặc Xưởng phần mềm/sản xuất đầu tiên!"
                ),
                "formula_note": (
                    "Vốn Công ty Startup = Seed Equity ($20k) + Bank Loan (3x = $60k) = $80,000. Founder giữ 80% cổ phần (0.80M sh), 20% phát hành tự do lên sàn WSR."
                ),
                "task_instruction": (
                    "Ở góc trên bên trái 'Tab 2 (2. CapLab 3×3 Floorplan & $30k Startup Incubator)', hãy bấm nút vàng '🚀 Incorporate Bootstrapped Startup + Open 1st Firm'!"
                ),
                "auto_action": {"type": "INCORPORATE_STARTUP", "tab_id": "tab-caplab"},
            },
            {
                "quest_id": "M5_Q2",
                "title": "Giải Phẫu Mặt Bằng '3x3' (9 Ô Bộ Phận) & Cách Đổi Chức Năng Từng Ô",
                "tab_id": "tab-caplab",
                "target_selector": "#floorplan-3x3-grid",
                "secondary_selector": "#btn-assign-unit",
                "paimon_speech": (
                    "Tuyệt vời! Công ty của Aether đã ra đời và ô 'Acting As' đã tự động chuyển sang công ty mới của cậu! "
                    "Bây giờ nhìn sang cột phải của Tab 2: Đó là Mặt bằng Nội bộ 3x3 (9 ô bộ phận) chuẩn Capitalism Lab:\n"
                    "• 'PUR' (Purchasing): Bộ phận thu mua hàng hóa/nguyên vật liệu đầu vào.\n"
                    "• 'MFT' (Manufacturing): Dây chuyền lắp ráp nguyên liệu thành thành phẩm.\n"
                    "• 'SALE' (Sales): Quầy xuất hàng và bán hàng thu tiền.\n"
                    "• 'INV' (Inventory): Kho chứa hàng đệm.\n"
                    "• 'EXTERN' (Advertising): Bộ phận Marketing/Quảng cáo giúp tăng điểm Thương hiệu (Brand).\n"
                    "• 'RD' / 'TECH': Phòng nghiên cứu nâng cấp công nghệ.\n"
                    "Cậu có thể bấm vào bất kỳ ô nào (#1..#9), chọn vai trò mới ở 'Slot Role' bên dưới và bấm 'Assign Unit' để tái bố trí dây chuyền!"
                ),
                "formula_note": (
                    "Mũi tên '-> S4,6' trên mỗi ô chỉ hướng luân chuyển hàng hóa từ khâu Thu mua (PUR) -> Sản xuất/Kho (MFT/INV) -> Bán hàng (SALE)."
                ),
                "task_instruction": (
                    "Hãy bấm vào một ô bất kỳ trên lưới 3x3 (ví dụ ô #2), chọn một chức năng ở ô 'Slot Role' (như EXTERN hoặc SALE) rồi bấm nút xanh 'Assign Unit'!"
                ),
                "auto_action": {"type": "REASSIGN_3X3_SLOT", "slot": 1, "role": "EXTERN", "tab_id": "tab-caplab"},
            },
            {
                "quest_id": "M5_Q3",
                "title": "Huấn Luyện Nhân Sự ('Train All 9 Units +Lv') Để Bơm Chất Lượng Sản Phẩm",
                "tab_id": "tab-caplab",
                "target_selector": "#btn-train-staff",
                "paimon_speech": (
                    "Nhìn góc trên bên phải của mỗi ô trong lưới 3x3 có chữ '★Lv4' không Aether? Đó là Cấp độ lành nghề của nhân sự tại bộ phận đó (từ Lv1 đến Lv9)! "
                    "Khi cậu bấm nút vàng 'Train All 9 Units (+Lv)' trên thanh tiêu đề mặt bằng, toàn bộ 9 bộ phận sẽ được nâng cấp kỹ năng thêm +1 cấp sao, "
                    "giúp tăng hiệu suất vận hành và cộng trực tiếp +2.5 điểm vào Chất lượng sản phẩm (Product Quality) của cơ sở đó!"
                ),
                "formula_note": (
                    "Mỗi lần Train All 9 Units: Level của cả 9 ô tăng +1 (tối đa ★Lv9) và Product Quality tăng +2.5 điểm (tối đa 100)."
                ),
                "task_instruction": (
                    "Hãy bấm nút vàng 'Train All 9 Units (+Lv)' ngay phía trên mặt bằng 3x3 ở cột phải Tab 2!"
                ),
                "auto_action": {"type": "TRAIN_FIRM_STAFF", "tab_id": "tab-caplab"},
            },
            {
                "quest_id": "M5_Q4",
                "title": "Công Thức Cạnh Tranh Thị Phần 'PRQ' (Price - Quality - Brand) & Chỉnh Giá Bán",
                "tab_id": "tab-caplab",
                "target_selector": "#btn-update-prq",
                "secondary_selector": "#prq-breakdown-box",
                "paimon_speech": (
                    "Làm sao để khách hàng trong thành phố kéo nhau vào cửa hàng của Aether thay vì mua của đối thủ AI? "
                    "Tất cả nằm ở hộp 'PRQ Breakdown' ngay dưới mặt bằng 3x3! Người tiêu dùng chấm điểm sản phẩm theo 3 trọng số:\n"
                    "1. 'Quality' (Chất lượng - thanh xanh lá): Tăng nhờ R&D, nguyên liệu tốt và huấn luyện nhân viên.\n"
                    "2. 'Brand' (Thương hiệu - thanh xanh cyan): Tăng nhờ chi ngân sách Quảng cáo ('ADVERTISING $M/QTR').\n"
                    "3. 'Price' (Giá bán - thanh vàng): Nếu cậu giảm 'UNIT PRICE ($)' thấp hơn giá chuẩn ('Std $'), điểm Overall Rating sẽ vọt lên, giúp cậu cướp thị phần ('Market Share %')!"
                ),
                "formula_note": (
                    "Overall Rating = (Q × W_qual)/60 + (B × W_brand)/60 + 2 × W_price × (P_std - P_unit)/P_std. Thị phần tỷ lệ thuận với (Overall Rating)^2.2!"
                ),
                "task_instruction": (
                    "Ở dưới cùng cột phải Tab 2, hãy chỉnh nhẹ 'UNIT PRICE ($)' hoặc 'ADVERTISING' rồi bấm nút xanh lá 'Update PRQ'!"
                ),
                "auto_action": {"type": "UPDATE_FIRM_PRQ", "tab_id": "tab-caplab"},
            },
        ],
    },
    {
        "module_id": "M6",
        "module_index": 6,
        "title": "Học phần 6: Chiến Thuật Chuỗi Cung Ứng, R&D Công Nghệ & Xây Dựng Đế Chế Sản Xuất",
        "short_title": "M6: Chuỗi Cung Ứng & R&D",
        "badge": "Đế Chế Thực",
        "summary": (
            "Hiểu rõ 8 loại hình cơ sở trong Capitalism Lab, bí quyết tự chủ nguyên liệu đầu vào (Vertical Integration Shield 1..3) "
            "để giảm giá vốn COGS, hiệu ứng cộng hưởng 480% của Viện R&D 3x3, và cách xây thêm cơ sở mới."
        ),
        "quests": [
            {
                "quest_id": "M6_Q1",
                "title": "8 Loại Hình Cơ Sở Kinh Doanh Trong Capitalism Lab (Từ Mỏ Khoáng Sản Tới Cao Ốc)",
                "tab_id": "tab-caplab",
                "target_selector": "#firmtype-filter-bar",
                "paimon_speech": (
                    "Ở cột giữa Tab 2, Aether có thanh lọc 8 loại hình cơ sở chuẩn Capitalism Lab:\n"
                    "• 'Factory' (Nhà máy): Chế tạo tối đa 3 nguyên liệu đầu vào (INPUT 1..3) thành thành phẩm.\n"
                    "• 'Retail' (Cửa hàng): Bán lẻ trực tiếp cho người dân tại 128 đô thị.\n"
                    "• 'R&D' (Viện nghiên cứu): Phát minh công nghệ mới, không bán hàng trực tiếp nhưng quyết định trần Chất lượng của cả tập đoàn.\n"
                    "• 'Mine/Oil' & 'Farm': Khai thác Vàng, Dầu, Đồng, Gỗ, Nông sản ở thượng nguồn.\n"
                    "• 'Software' & 'Real Estate': Xưởng phần mềm biên lãi gộp cực cao và Chung cư/Cao ốc văn phòng thu tiền thuê ổn định!"
                ),
                "formula_note": (
                    "Mỗi loại cơ sở có cấu trúc doanh thu và mặt bằng 3x3 riêng biệt, tất cả lợi nhuận EBIT đều chảy về Tập đoàn mẹ ở Tab 1."
                ),
                "task_instruction": (
                    "Hãy bấm thử vào các nút icon lọc loại hình cơ sở ('Factory', 'R&D', 'Mine/Oil', 'All') trên thanh '#firmtype-filter-bar' ở cột giữa Tab 2!"
                ),
                "auto_action": {"type": "FILTER_CAPLAB_FIRMS", "firm_type": "FACTORY", "tab_id": "tab-caplab"},
            },
            {
                "quest_id": "M6_Q2",
                "title": "Khiên Tự Chủ Chuỗi Cung Ứng ('Vertical Shield 1..3') — Tại Sao Nhà Máy #7 Lãi Đậm Hơn #1?",
                "tab_id": "tab-caplab",
                "target_selector": "#caplab-firms-grid",
                "secondary_selector": "#fp-shield-badge",
                "paimon_speech": (
                    "Aether có thắc mắc tại sao trên thẻ các nhà máy có cái hiện 'COGS 58%' màu xám, có cái lại hiện huy hiệu xanh lá 'Shield (3)' không? "
                    "Đó chính là bí mật Chuỗi Cung Ứng Dọc (Vertical Integration):\n"
                    "• Nhìn Nhà máy #1 (sản xuất SMARTPH từ CCD + CPU + PLASTIC): Tập đoàn #321 chưa tự sản xuất được 3 linh kiện đó nên phải mua ngoài chợ (Open Market) với giá vốn đắt đỏ (COGS = 58% doanh thu), và nếu giá Dầu/Đồng tăng sốc là bị đội chi phí ngay!\n"
                    "• Ngược lại, nhìn Tập đoàn #322: Họ sở hữu cả nhà máy làm Khung xe (#4 CARBODY), Động cơ (#5 ENGINE), Bánh xe (#6 WHEEL) rồi cấp nội bộ cho Nhà máy Ô tô (#7 CAR) -> Đạt 'Shield (3)', kéo giá vốn COGS tụt xuống cực thấp và miễn nhiễm bão giá nguyên liệu!"
                ),
                "formula_note": (
                    "Mỗi nguyên liệu đầu vào tự chủ trong cùng Tập đoàn (hoặc Công ty mẹ-con >=50%) giúp giảm ~7% tỷ lệ COGS và cộng thưởng Chất lượng đầu vào!"
                ),
                "task_instruction": (
                    "Ở cột giữa Tab 2, hãy bấm chọn thẻ nhà máy '#7 FACTORY — CAR' (bấm nút 'All' hoặc 'Factory' nếu cần) để xem 'Recipe: CARBODY + ENGINE + WHEEL -> CAR' và huy hiệu 'Vertical Shield: 3 Inputs'!"
                ),
                "auto_action": {"type": "SELECT_FIRM", "firm_id": 7, "tab_id": "tab-caplab"},
            },
            {
                "quest_id": "M6_Q3",
                "title": "Viện Nghiên Cứu 'R&D 3x3' (Cộng Hưởng 480%) & Đòn Huỷ Diệt Công Nghệ Lạc Hậu",
                "tab_id": "tab-caplab",
                "target_selector": "#caplab-firms-grid",
                "secondary_selector": "#floorplan-3x3-grid",
                "paimon_speech": (
                    "Trong Capitalism Lab, nếu cậu chỉ giảm giá bán thì đối thủ cũng giảm theo. Vũ khí tạo hào kinh tế bền vững nhất là Viện Nghiên Cứu R&D! "
                    "Khi cậu mở một trung tâm R&D có đủ 9 phòng Lab trên mặt bằng 3x3 (ô #5 ở chính giữa là 'Core Tech Leader' kết nối với 8 phòng Lab vệ tinh xung quanh), "
                    "tốc độ nghiên cứu được nhân tới 480% (Team Synergy)! Khi điểm công nghệ của cậu vượt đỉnh thế giới (TopTech > 100), chất lượng hàng của cậu vượt trội, "
                    "đồng thời các tập đoàn đối thủ bên WSR không chịu làm R&D sẽ bị phạt giảm lợi nhuận vì Lạc hậu công nghệ (Tech Obsolescence)!"
                ),
                "formula_note": (
                    "Bảng Synergy R&D 3x3 (1..9 units): [100%, 130%, 160%, 200%, 240%, 290%, 350%, 410%, 480%]. Đủ 9 ô đạt tốc độ gấp 4.8 lần!"
                ),
                "task_instruction": (
                    "Hãy bấm chọn cơ sở '#2 RD — SMARTPH' ở cột giữa Tab 2 (bấm lọc 'All' hoặc 'R&D') để quan sát cấu trúc 3x3 của Viện Nghiên Cứu!"
                ),
                "auto_action": {"type": "SELECT_FIRM", "firm_id": 2, "tab_id": "tab-caplab"},
            },
            {
                "quest_id": "M6_Q4",
                "title": "Mở Rộng Đế Chế: Xây Dựng Cơ Sở Mới ('Construct Firm') Với Cầu Nối Không Hạch Toán Kép",
                "tab_id": "tab-caplab",
                "target_selector": "#btn-construct-firm",
                "paimon_speech": (
                    "Khi công ty của cậu (hoặc tập đoàn cậu đang điều khiển) muốn mở thêm nhà máy, cửa hàng ở thành phố mới hay xây mỏ khai khoáng, "
                    "hãy dùng khung '🏗️ Construct New Capitalism Lab Firm' ở nửa dưới cột trái Tab 2! "
                    "Đặc biệt: Nếu cậu đang điều khiển công ty Startup nhỏ, Paimon đã thêm nút chọn nhanh '$15k Micro' (hoặc tự động co giãn quy mô CAPEX vừa với két tiền của Startup) "
                    "và đảm bảo nguyên tắc 'Zero Double-Counting': Tiền mặt bỏ ra xây nhà máy chuyển 1:1 thành Tài sản cố định (CapAssets) và Tồn kho (WorkingCap), không mất đi một xu Net Worth nào!"
                ),
                "formula_note": (
                    "Tại thời điểm xây Firm: ΔCash = -(CAPEX + Inventory), ΔCapAssets = +CAPEX, ΔWorkingCap = +Inventory => ΔTotalAssets = 0, ΔNetWorth = 0."
                ),
                "task_instruction": (
                    "Ở nửa dưới cột trái Tab 2, hãy bấm nút xanh lá 'Construct Firm (Zero Double-Counting CAPEX Bridge)' để xây thêm một cơ sở kinh doanh mới!"
                ),
                "auto_action": {"type": "CONSTRUCT_NEW_FIRM", "tab_id": "tab-caplab"},
            },
        ],
    },
    {
        "module_id": "M7",
        "module_index": 7,
        "title": "Học phần 7: Vũ Khí Phố Wall Nâng Cao — Bán Khống, Hàng Hóa, Crypto, Quyền Chọn & Hoán Đổi Lãi Suất",
        "short_title": "M7: Bán Khống & Phái Sinh",
        "badge": "Phái Sinh",
        "summary": (
            "Kiếm tiền ngay cả khi thị trường sụp đổ bằng Bán khống (Short Selling), giao dịch Hợp đồng tương lai hàng hóa "
            "(OIL, GOLD, WHEAT, COPPER), Crypto (BTC, ETH), Quyền chọn Mua/Bán (Call/Put Options) và Hoán đổi lãi suất (Rate Swaps)."
        ),
        "quests": [
            {
                "quest_id": "M7_Q1",
                "title": "Bán Khống Cổ Phiếu ('📉 Short' & 'Cover Short') — Kiếm Tiền Khi Cổ Phiếu Sập & Bẫy Cổ Tức",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-short-stock",
                "secondary_selector": "#btn-cover-short",
                "paimon_speech": (
                    "Nếu Aether soi thấy một công ty làm ăn bết bát, nợ ngập đầu (hạng BB/CCC) hoặc biểu đồ nến xuất hiện Shooting Star / RSI > 75 sắp sập, "
                    "làm sao kiếm tiền từ cú sập đó? Hãy dùng '📉 Short' (Bán khống)!\n"
                    "• Cơ chế: Cậu vay cổ phiếu để bán lấy tiền mặt ngay ở giá cao (ví dụ $100). Khi giá sập xuống $70, cậu bấm 'Cover Short' mua trả lại với giá $70 -> Bỏ túi $30/cp tiền lãi!\n"
                    "• 2 Rủi ro sống còn phải nhớ:\n"
                    "  1. Nếu giá không giảm mà tăng vọt (Short Squeeze), khoản nợ Short Liability phình to có thể gây cháy tài khoản (Margin Call)!\n"
                    "  2. Nếu công ty đó chia cổ tức trong lúc cậu đang Short, cậu phải MÓC TIỀN TÚI đền đúng số cổ tức đó cho chủ cổ phiếu!"
                ),
                "formula_note": (
                    "Yêu cầu Ký quỹ Bán khống: Net Worth >= 50% giá trị lệnh Short. Phương trình bảo toàn CP: Tổng Long + Public Float - Tổng Short == Shares Outstanding."
                ),
                "task_instruction": (
                    "Ở Tab 1 cột phải, hãy bấm nút '100sh', bấm nút đỏ '📉 Short' để thử mở vị thế bán khống, sau đó có thể bấm 'Cover Short' để đóng vị thế!"
                ),
                "auto_action": {"type": "SHORT_AND_COVER_DEMO", "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M7_Q2",
                "title": "Giao Dịch Hợp Đồng Tương Lai Hàng Hóa ('OIL/GOLD Futures') & Crypto ('BTC/ETH')",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-trade-deriv",
                "secondary_selector": "#deriv-asset",
                "paimon_speech": (
                    "Ở khu vực 2 cột phải Tab 1, Aether có thể giao dịch trực tiếp các tài sản vĩ mô nóng nhất thế giới:\n"
                    "• Hợp đồng Tương lai Hàng hóa ('OIL', 'GOLD', 'COPPER', 'WHEAT' Futures): Cậu chỉ cần ký quỹ 15% tiền mặt (Initial Margin = 15% × Notional) để nắm giữ hợp đồng tương lai trị giá bằng cả cục Notional ($M)! Khi giá Dầu hoặc Vàng tăng, tài sản của cậu tăng theo đòn bẩy!\n"
                    "• Tiền mã hóa ('BTC', 'ETH' Crypto): Mua bán trực tiếp Bitcoin và Ethereum theo số tiền ở ô 'Notional ($M)' (bấm '$5k' = 0.005M để mua $5,000 BTC ngay với ví $30k)!"
                ),
                "formula_note": (
                    "Futures Initial Margin = 15% × Notional ($M). Số hợp đồng (Contracts) = Notional / Spot Price."
                ),
                "task_instruction": (
                    "Ở khu vực 2 cột phải Tab 1, hãy bấm nút '$5k', chọn 'OIL Futures' hoặc 'BTC Crypto' ở ô chọn tài sản, rồi bấm nút cam 'Futures/Crypto'!"
                ),
                "auto_action": {"type": "TRADE_MICRO_DERIV", "asset": "BTC", "notional_m": 0.005, "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M7_Q3",
                "title": "Quyền Chọn Mua & Bán ('Buy Call', 'Buy Put', 'Write Call') — Đòn Bẩy & Bảo Hiểm",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-buy-call",
                "secondary_selector": "#btn-buy-put",
                "paimon_speech": (
                    "Quyền chọn (Options) là vũ khí đòn bẩy sắc bén nhất Phố Wall:\n"
                    "• 'Buy Call' (Mua Quyền chọn Mua): Bỏ một khoản phí nhỏ (Premium) để đặt cược cổ phiếu mục tiêu sẽ TĂNG GIÁ MẠNH vượt giá thực hiện (Strike Price = 105% Spot). Nếu đoán sai, cậu chỉ mất tối đa khoản phí Premium!\n"
                    "• 'Buy Put' (Mua Quyền chọn Bán): Đặt cược cổ phiếu sẽ SẬP MẠNH, hoặc dùng làm 'hợp đồng bảo hiểm' cho cổ phiếu cậu đang nắm giữ.\n"
                    "• 'Write Call' (Bán Quyền chọn): Thu tiền phí Premium về ví ngay lập tức, nhưng nếu không có sẵn cổ phiếu bảo chứng (Naked Option) mà giá cổ phiếu tăng vọt thì sẽ gánh khoản nợ Naked Option Liability rất lớn!"
                ),
                "formula_note": (
                    "Option Price (WSR GetOptionPrice) = Intrinsic Value + Time Premium × VolatilityMult × InterestRateMult."
                ),
                "task_instruction": (
                    "Hãy bấm nút '100sh' ở khu vực 1, sau đó bấm nút xanh 'Buy Call' hoặc 'Buy Put' ở khu vực 2 cột phải Tab 1!"
                ),
                "auto_action": {"type": "BUY_MICRO_OPTION", "opt_type": "CALL", "shares_m": 0.0001, "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M7_Q4",
                "title": "Hợp Đồng Hoán Đổi Lãi Suất ('Rate Swap') & Trái Phiếu Doanh Nghiệp ('Buy CorpBond')",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-rate-swap",
                "secondary_selector": "#btn-buy-corpbond",
                "paimon_speech": (
                    "Làm sao các quỹ vĩ mô như Stan D. (#2006) kiếm hàng trăm triệu đô khi Ngân hàng Trung ương tăng lãi suất? Họ dùng 'Rate Swap' (Interest Rate Swap - IRS)!\n"
                    "• Khi bấm 'Rate Swap', cậu ký hợp đồng 4 quý: Cậu trả lãi suất cố định 6.5%/năm và NHẬN về lãi suất thả nổi 'Prime Rate' trên mệnh giá Notional.\n"
                    "• Nếu lạm phát bùng lên và Prime Rate tăng lên 10% - 18% (như kịch bản S1), mỗi quý đối tác phải trả tiền mặt chênh lệch lãi suất trực tiếp vào ví của cậu!\n"
                    "• Ngoài ra, nút 'Buy CorpBond' giúp cậu mua Trái phiếu Doanh nghiệp với mức sinh lời cao hơn Trái phiếu Chính phủ!"
                ),
                "formula_note": (
                    "Thanh toán Swap mỗi Quý: ΔCash = Notional × (Prime Rate - Fixed Rate 6.5%) × 0.25 / 100."
                ),
                "task_instruction": (
                    "Ở khu vực 2 cột phải Tab 1, hãy bấm nút màu tím 'Rate Swap' (hoặc nút xanh cyan 'Buy CorpBond')!"
                ),
                "auto_action": {"type": "CREATE_MICRO_SWAP", "notional_m": 0.01, "tab_id": "tab-wsr"},
            },
        ],
    },
    {
        "module_id": "M8",
        "module_index": 8,
        "title": "Học phần 8: Nghệ Thuật Tài Chính Đại Tư Bản — Công Ty Mẹ-Con, Thuế DRD, Spin-Off, ETF & Pháp Lý",
        "short_title": "M8: Đại Tư Bản & M&A/Thuế",
        "badge": "Đại Tư Bản",
        "summary": (
            "Làm chủ các nghiệp vụ đỉnh cao của giới tài phiệt Phố Wall: Đòn bẩy vay ngân hàng, cấu trúc Holding/Subsidiary, "
            "miễn thuế cổ tức 80%-100% DRD, chuyển lỗ 4 năm (NOL), tách công ty con (80% Spin-Off), Cố vấn ETF, Kiện tụng và Cầu nối Ví GTA SA."
        ),
        "quests": [
            {
                "quest_id": "M8_Q1",
                "title": "Đòn Bẩy Tín Dụng Ngân Hàng ('Borrow Loan' / 'Repay Loan') & Thâu Tóm Quyền Kiểm Soát",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-borrow-loan",
                "secondary_selector": "#btn-repay-loan",
                "paimon_speech": (
                    "Tại sao phải chờ tích góp từng đồng khi cậu có hạn mức tín dụng ngân hàng (Credit Line)? "
                    "Ở khu vực 3 cột phải Tab 1, nút 'Borrow Loan' cho phép Aether (hoặc công ty của Aether) vay tiền mặt trực tiếp từ Ngân hàng thương mại (IND=1) "
                    "để gom cổ phiếu thâu tóm hoặc xây thêm nhà máy!\n"
                    "• Khi cậu (hoặc công ty mẹ) mua gom đủ >= 20% cổ phần của một tập đoàn và là cổ đông lớn nhất, cậu chính thức nắm quyền Kiểm soát (Controller) tập đoàn đó!\n"
                    "• Khi nắm >= 50% cổ phần, toàn bộ chuỗi cung ứng nhà máy/mỏ khoáng sản của công ty con sẽ được liên thông Khiên Tự Chủ (Vertical Shield) với công ty mẹ!"
                ),
                "formula_note": (
                    "Ngưỡng quyền lực WSR: >= 20% (Kiểm soát điều hành / Controlled Corp) | >= 50% (Hợp nhất chuỗi cung ứng & cho phép Thanh lý) | >= 80% (Miễn thuế 100% DRD & Spin-Off)."
                ),
                "task_instruction": (
                    "Ở khu vực 3 cột phải Tab 1, hãy bấm nút '$10k' rồi bấm nút xanh 'Borrow Loan' (hoặc 'Repay Loan') để thực hành điều phối đòn bẩy ngân hàng!"
                ),
                "auto_action": {"type": "BORROW_MICRO_LOAN", "amount_m": 0.01, "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M8_Q2",
                "title": "Bí Mật Thuế Tài Phiệt WSR: Khấu Trừ Cổ Tức 80%–100% (DRD), Chuyển Lỗ 4 Năm & 'Set Dividend'",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-set-dividend",
                "paimon_speech": (
                    "Đây là bí mật giúp các tập đoàn Holding (như Berkshire của Warren B.) giàu gấp bội nhà đầu tư cá nhân:\n"
                    "• Nếu cá nhân Aether (#1) nhận cổ tức tiền mặt, Aether phải đóng thuế thu nhập cá nhân trên 100% số cổ tức đó.\n"
                    "• Nhưng nếu Aether dùng Công ty mẹ (ví dụ #61 Aether Ventures) đi mua cổ phiếu công ty khác: Theo luật thuế DRD (Dividends Received Deduction) của WSR, Công ty mẹ được MIỄN THUẾ 80% cổ tức (chỉ tính thuế trên 20%!), và nếu sở hữu >= 80% công ty con thì được MIỄN THUẾ 100% CỔ TỨC!\n"
                    "• Ngoài ra, nếu công ty bị lỗ năm nay, khoản lỗ đó được lưu vào 4 giỏ '4-Year NOL Carryforward' để khấu trừ thuế cho 4 năm có lãi tiếp theo!"
                ),
                "formula_note": (
                    "Luật thuế DRD (CorpTaxCalc): Cá nhân chịu thuế 100% cổ tức | Công ty mẹ nắm <80% chịu thuế trên 20% cổ tức (80% DRD) | Công ty mẹ nắm >=80% miễn thuế 100%!"
                ),
                "task_instruction": (
                    "Hãy bấm nút vàng 'Set Dividend' ở khu vực 3 cột phải Tab 1 để phát lệnh chia cổ tức tiền mặt từ công ty mục tiêu về ví các cổ đông!"
                ),
                "auto_action": {"type": "PAY_DIVIDEND_DEMO", "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M8_Q3",
                "title": "Làm Cố Vấn Quản Lý Quỹ ETF ('ETF Advisor') & Nghiệp Vụ Tách Công Ty Con ('80% SpinOff')",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-etf-advisor",
                "secondary_selector": "#btn-spinoff-sub",
                "paimon_speech": (
                    "Ở khu vực 3 cột phải còn có 2 chiêu thức tạo dòng tiền của giới tinh hoa Phố Wall:\n"
                    "1. 'ETF Advisor': Bấm nút này để đăng ký làm Cố vấn Quản lý cho Quỹ ETF (#1581). Mỗi khi qua Quý (+1 Quarter), quỹ ETF sẽ tự động trích phí quản lý (Advisory Fee 0.4%/năm trên tổng tài sản ròng hàng trăm triệu đô của quỹ) trả thẳng vào ví tiền mặt của cậu mà không chịu rủi ro biến động giá!\n"
                    "2. '80% SpinOff': Khi Công ty mẹ của cậu sở hữu cổ phần một Công ty con, nút này tách cổ phần Công ty con chia trực tiếp cho các cổ đông (và được miễn thuế lãi vốn 100% nếu sở hữu >= 80%)!"
                ),
                "formula_note": (
                    "Phí quản lý ETF mỗi quý = NAV_ETF × (AdvisoryFee% / 100) × 0.25. Spin-Off >= 80% sở hữu: Capital Gains Tax = $0!"
                ),
                "task_instruction": (
                    "Hãy bấm nút xanh cyan 'ETF Advisor' ở khu vực 3 cột phải Tab 1 để trở thành Cố vấn Quản lý Quỹ ETF #1581!"
                ),
                "auto_action": {"type": "BECOME_ETF_ADVISOR_DEMO", "tab_id": "tab-wsr"},
            },
            {
                "quest_id": "M8_Q4",
                "title": "Đâm Đơn Kiện Chống Độc Quyền ('⚔️ Lawsuit') & Cầu Nối Ví Tiền GTA San Andreas ('Stage B Bridge')",
                "tab_id": "tab-wsr",
                "target_selector": "#btn-deposit-gta",
                "secondary_selector": "#btn-lawsuit",
                "paimon_speech": (
                    "Chúc mừng Aether đã đi tới bài học cuối cùng của Học viện Kinh tế Paimon! Hai công cụ cuối cùng ở góc dưới bên phải Tab 1 là:\n"
                    "1. '⚔️ Lawsuit' (Kiện Chống Độc Quyền): Đâm đơn kiện đối thủ cạnh tranh đòi bồi thường số tiền ở ô 'Loan/Claim $M' (tốn 2% án phí luật sư, tòa sẽ tuyên án sau 4 quý với xác suất thắng 45%!).\n"
                    "2. '🎮 Stage B — GTA San Andreas Wallet Bridge' ('Deposit GTA' / 'Withdraw GTA'): Đây chính là chiếc cầu nối đưa toàn bộ số tiền lãi cậu kiếm được trên sàn Phố Wall & Capitalism Lab rút thẳng về ví tiền mặt của nhân vật Aether trong thế giới mở GTA San Andreas (Project Eagle)!"
                ),
                "formula_note": (
                    "Deposit GTA ($ USD) -> +$M vào Cash của #1 Aether | Withdraw GTA ($ USD) -> Rút Cash từ sàn về ví GTA SA của Aether."
                ),
                "task_instruction": (
                    "Hãy bấm nút 'Deposit GTA' hoặc 'Withdraw GTA' (hoặc nút '⚔️ Lawsuit') ở cuối cột phải Tab 1 để hoàn thành trọn vẹn 9 Học phần của Paimon Academy!"
                ),
                "auto_action": {"type": "GTA_BRIDGE_DEMO", "tab_id": "tab-wsr"},
            },
        ],
    },
]


# =============================================================================
# 2. INSPECT / EXPLAIN ENCYCLOPEDIA (68+ UI ELEMENTS, METRICS & CONCEPTS)
# =============================================================================

PAIMON_INSPECT_DICTIONARY: Dict[str, Dict[str, str]] = {
    "hdr-date": {
        "title": "📅 DATE / QTR — Đồng Hồ Thời Gian Thế Giới (2010-Q1)",
        "what": "Hiển thị Năm, Quý (Q1..Q4), Tháng và Ngày hiện tại của nền kinh tế (khởi đầu tại 2010-Q1 đồng bộ với timeline GTA San Andreas Project Eagle).",
        "formula": "1 Năm = 4 Quý = 12 Tháng = 360 Ngày giao dịch (10 Subticks = 1 Ngày; 90 Ngày = 1 Quý).",
        "when_to_use": "Theo dõi thời điểm sắp kết thúc Quý để chuẩn bị đón báo cáo lợi nhuận, thu tiền cổ tức và xem AI tái cơ cấu danh mục.",
    },
    "hdr-gdp": {
        "title": "📈 GDP (CAPLAB IMPULSE) — Tăng Trưởng Kinh Tế Vĩ Mô & Xung Lực Nhà Máy",
        "what": "Con số đầu là tốc độ tăng trưởng GDP thực tế của nền kinh tế WSR. Con số trong ngoặc (+%) là xung lực tăng trưởng do các nhà máy/cửa hàng bên Capitalism Lab đóng góp trực tiếp!",
        "formula": "ΔGDP_Impulse = clamp(Total_CapLab_CapEx × 0.00025, -0.4%, +1.2%).",
        "when_to_use": "Khi GDP tăng cao (> 3%), sức mua của người dân tại 128 thành phố và lợi nhuận ROCE% của các ngành sản xuất đều tăng mạnh — hãy ưu tiên mua cổ phiếu và mở rộng cửa hàng!",
    },
    "hdr-prime": {
        "title": "🏦 CPI INFLATION / PRIME RATE — Lạm Phát & Lãi Suất Cơ Bản",
        "what": "CPI là tỷ lệ lạm phát giá tiêu dùng; Prime Rate là lãi suất cho vay cơ bản của hệ thống ngân hàng — con số quyền lực nhất Phố Wall.",
        "formula": "Prime Rate ≈ 3.0% + CPI Inflation + 0.35 × GDP Growth (Taylor Rule).",
        "when_to_use": "Khi Prime Rate tăng vọt (ví dụ kịch bản S1 lên 18%), hãy tránh vay nợ nhiều, có thể ký hợp đồng Rate Swap hoặc mua Trái phiếu khi lãi suất đạt đỉnh. Khi Prime Rate giảm, hãy tích cực vay vốn mở rộng đế chế!",
    },
    "hdr-commod": {
        "title": "🛢️ OIL / GOLD / BTC — Giá Giao Ngay Dầu Thô, Vàng & Bitcoin",
        "what": "Giá giao ngay (Spot Price) của 3 tài sản chuẩn: Dầu thô WTI ($/thùng), Vàng ($/oz) và Bitcoin ($).",
        "formula": "Biến động theo cung-cầu vĩ mô từng Subtick và được làm dịu nếu có nhiều mỏ khai thác vật lý (MINE/OIL) bên Capitalism Lab.",
        "when_to_use": "Khi giá Dầu tăng cao, các công ty dầu khí/mỏ khoáng sản lãi lớn nhưng các nhà máy chưa tự chủ nguyên liệu (không có Shield) sẽ bị tăng giá vốn COGS.",
    },
    "hdr-nw": {
        "title": "💰 AETHER NET WORTH — Tổng Tài Sản Ròng Của Bạn (#1 Aether)",
        "what": "Tổng giá trị tài sản thực sự thuộc về cá nhân Aether sau khi đã cộng tiền mặt, cổ phiếu, trái phiếu, crypto, quyền chọn và trừ đi mọi khoản nợ vay ngân hàng / bán khống.",
        "formula": "Net Worth = Total Assets - Total Liabilities (Khởi đầu Street Hustler = $30,000).",
        "when_to_use": "Đây là thước đo thành tựu của bạn trên hành trình từ 'Cá con $30,000' vươn lên thành Đại Tư Bản!",
    },
    "hdr-inv": {
        "title": "🛡️ 5-REGIME AUDIT — Kiểm Toán Bất Biến Kế Toán Toàn Cầu",
        "what": "Bộ kiểm toán tự động kiểm tra phương trình kế toán và bảo toàn cổ phiếu trên toàn bộ 1,915 thực thể ở mọi mili-giây.",
        "formula": "|TotalAssets - (TotalLiabilities + NetWorth)| < 1e-4 & Sum(Long) + Float - Sum(Short) == SharesOut.",
        "when_to_use": "Luôn hiển thị PASS để đảm bảo hệ thống tài chính vận hành chính xác 100%, không bao giờ có tiền ảo hay mất tài sản khi giao dịch.",
    },
    "acting-as-select": {
        "title": "🎭 ACTING AS — Chọn Chủ Thể Đang Trực Tiếp Ra Lệnh & Rút Ví",
        "what": "Quyết định xem AI ĐANG LÀ NGƯỜI BỎ TIỀN RA GIAO DỊCH: Cá nhân #1 Aether hay một Công ty con do Aether nắm quyền kiểm soát (ví dụ #61 Aether Ventures).",
        "formula": "Mọi nút đặt lệnh ở cột phải Tab 1 và xây nhà máy ở Tab 2 sẽ dùng tiền mặt (Cash) của thực thể đang chọn ở Acting As.",
        "when_to_use": "Dùng #1 Aether khi giao dịch bằng ví cá nhân; chuyển sang Công ty con khi muốn dùng tiền trong két công ty để xây nhà máy hoặc mua cổ phiếu hưởng ưu đãi miễn thuế cổ tức 80%-100% DRD!",
    },
    "btn-mode-toggle": {
        "title": "🔄 MODE TOGGLE — Chuyển Đổi '$30k Street Hustler' <-> '$1B Sandbox'",
        "what": "Chuyển đổi tức thì giữa chế độ Khởi nghiệp thực chiến với $30,000 và chế độ Tỷ phú Sandbox với $1,000,000,000 ($1B).",
        "formula": "$30k Hustler: Cash = $0.03M | $1B Sandbox: Cash = $1,000.0M + quyền kiểm soát tập đoàn mẫu #321.",
        "when_to_use": "Chơi ở chế độ $30k Hustler để trải nghiệm cảm giác đi lên từ hai bàn tay trắng; bật $1B Sandbox khi muốn thử nghiệm ngay các thương vụ thâu tóm hàng trăm triệu đô.",
    },
    "btn-step-subtick": {
        "title": "⏱️ +1 SUBTICK — Nhịp Giao Dịch Vi Mô Trong Ngày (< 0.2 ms)",
        "what": "Cho thị trường nhích 1 nhịp vi mô trong ngày: giá cổ phiếu, hàng hóa (OIL, GOLD) và BTC dao động nhẹ theo cung cầu.",
        "formula": "10 Subticks = 1 Ngày giao dịch.",
        "when_to_use": "Dùng khi bạn muốn quan sát bảng điện nhảy số thời gian thực hoặc canh điểm vào lệnh lướt sóng ngắn hạn.",
    },
    "btn-step-day": {
        "title": "📆 +1 DAY — Tiến Lịch Thêm 1 Ngày Giao Dịch",
        "what": "Qua 1 ngày lịch, cập nhật/tạo cây nến mới trên bảng biểu đồ OHLCV. Cứ mỗi 90 ngày sẽ tự động kích hoạt quyết toán Quý.",
        "formula": "30 Ngày = 1 Tháng | 90 Ngày = 1 Quý.",
        "when_to_use": "Dùng khi đang phân tích kỹ thuật trên biểu đồ nến OHLCV và muốn xem cây nến tiếp theo hình thành ra sao.",
    },
    "btn-step-quarter": {
        "title": "⏩ +1 QUARTER (FULL SIM) — Quyết Toán Toàn Bộ Nền Kinh Tế Qua 1 Quý (3 Tháng)",
        "what": "Nút nhịp chính của trò chơi: Chạy toàn bộ chu kỳ kinh tế vĩ mô, tính doanh thu/lợi nhuận (EBIT) cho các nhà máy Capitalism Lab, thu thuế, trả lương CEO, chia Cổ tức tiền mặt (Dividends), và cho 320 AI thực hiện nước đi hàng quý.",
        "formula": "1 Quý = 3 Tháng. Cập nhật GDP, CPI, Prime Rate, EBIT, EPS, Dividends, Options/Swaps/Lawsuits.",
        "when_to_use": "Bấm sau khi bạn đã hoàn tất các lệnh mua bán cổ phiếu hoặc tinh chỉnh mặt bằng 3x3 / giá bán cửa hàng trong quý hiện tại để thu lợi nhuận!",
    },
    "btn-luna-batch": {
        "title": "🧠 LIVE GPT-6-LUNA BATCH — Gọi AI Cập Nhật Chiến Lược 24 Trường Phái",
        "what": "Gọi bất đồng bộ mô hình LLM gpt-6-luna để các nhà đầu tư trưởng nhóm (Archetype Leads) phân tích vĩ mô hiện tại và viết lại Playbook 4 quý mới.",
        "formula": "Chạy ngầm (Non-blocking Thread) không làm đơ giao diện; trong lúc bình thường 320 AI đã tự chạy bằng Heuristic/Playbook nội tại (0 tốn phí API).",
        "when_to_use": "Chỉ cần bấm khi vừa kích hoạt một cú sốc vĩ mô lớn (như S1..S6) và muốn xem các cá mập AI viết luận điểm chiến lược mới trên Tab 3.",
    },
    "ohlcv-canvas": {
        "title": "🕯️ BẢNG NẾN NHẬT OHLCV & KHỐI LƯỢNG (JAPANESE CANDLESTICK CHART)",
        "what": "Biểu đồ 36 cây nến Nhật hiển thị Giá Mở cửa (Open), Cao nhất (High), Thấp nhất (Low), Đóng cửa (Close), Khối lượng (Volume), đường MA7 (Xanh), MA20 (Cam) và dải Bollinger Bands (Tím).",
        "formula": "Nến Xanh: Close >= Open (Phe Mua thắng) | Nến Đỏ: Close < Open (Phe Bán thắng). Rê chuột lên từng cây nến để đọc chi tiết!",
        "when_to_use": "Luôn nhìn biểu đồ nến trước khi bấm Buy Long hay Short để tránh mua đuổi ngay đỉnh kháng cự hoặc bán tháo ngay đáy hỗ trợ!",
    },
    "chart-pattern-badge": {
        "title": "🔍 CANDLESTICK PATTERN — Bộ Nhận Diện Mô Hình Nến Tự Động",
        "what": "Tự động phân tích hình dáng thân nến và râu nến của 2 cây nến gần nhất để gọi tên mô hình: Doji, Hammer (Búa), Shooting Star (Sao băng), Bullish/Bearish Engulfing (Nhấn chìm), hay Marubozu.",
        "formula": "So sánh tỷ lệ Body / Range và UpperWick / LowerWick theo chuẩn Price Action.",
        "when_to_use": "Bấm vào nút này bất cứ lúc nào để đọc giải thích tiếng Việt ngay bên dưới biểu đồ xem mẫu nến hiện tại đang ủng hộ phe Mua hay phe Bán!",
    },
    "chart-rsi-badge": {
        "title": "⚡ RSI(14) — Chỉ Số Sức Mạnh Tương Đối (Relative Strength Index)",
        "what": "Đo tốc độ và biên độ thay đổi giá của 14 cây nến gần nhất trên thang điểm từ 0 đến 100.",
        "formula": "RSI = 100 - [100 / (1 + AvgGain14 / AvgLoss14)]. >= 70: Quá mua (Overbought) | <= 30: Quá bán (Oversold).",
        "when_to_use": "Khi RSI <= 30 kèm nến rút chân Hammer là cơ hội bắt đáy tuyệt đẹp; khi RSI >= 70 hãy cẩn thận rủi ro điều chỉnh ngắn hạn!",
    },
    "bs-table-body": {
        "title": "📊 5-REGIME BALANCE SHEET — Bảng Cân Đối Kế Toán Chi Tiết",
        "what": "Liệt kê toàn bộ Tài sản (Cash, CapAssets, WorkingCap, Stocks, Bonds, Derivatives/Crypto, Bank Loans) và Nợ phải trả (Loans, Bonds Out, Short Liability, Deposits, Taxes) của thực thể đang xem.",
        "formula": "Total Assets - Total Liabilities = Net Worth (Shareholders' Equity).",
        "when_to_use": "Dùng để thẩm định sức khỏe thực chất của một tập đoàn trước khi mua cổ phiếu hoặc cho vay/thâu tóm.",
    },
    "holdings-table-body": {
        "title": "💼 UNIFIED STOCK HOLDINGS & SHORTS — Danh Mục Cổ Phiếu & Bán Khống",
        "what": "Hiển thị tất cả các vị thế cổ phiếu Mua nắm giữ (LONG) và Bán khống (SHORT) của bạn ('My / Actor Portfolio') hoặc của thực thể đang soi ('Viewed Entity').",
        "formula": "Stake % = (Shares Held / Shares Outstanding) × 100% | Market Value = Shares Held × Spot Price.",
        "when_to_use": "Theo dõi tỷ lệ sở hữu (Stake %) và bấm nút 'Sell All' để chốt lời hoặc 'Cover' để đóng vị thế bán khống chỉ với 1 click.",
    },
    "floorplan-3x3-grid": {
        "title": "🏭 3×3 INTERNAL FLOORPLAN — Mặt Bằng Nội Bộ 9 Ô Chuẩn Capitalism Lab",
        "what": "Mô phỏng 9 bộ phận chức năng bên trong Nhà máy, Cửa hàng, Viện R&D hoặc Mỏ khoáng sản: PUR (Thu mua), MFT (Sản xuất), SALE (Bán hàng), INV (Kho), EXTERN (Quảng cáo), RD/TECH (Nghiên cứu).",
        "formula": "Hiệu suất dây chuyền phụ thuộc vào sự cân bằng giữa đầu vào (PUR) -> chế biến (MFT) -> đầu ra (SALE) và cấp độ nhân viên (★Lv1..9).",
        "when_to_use": "Bấm vào từng ô để nâng cấp hoặc đổi chức năng bộ phận (ví dụ thêm ô EXTERN để tăng Brand hoặc thêm ô SALE khi hàng tồn kho đầy).",
    },
    "prq-breakdown-box": {
        "title": "🏆 PRQ COMPETITIVENESS — Thanh Điểm Cạnh Tranh Chất Lượng, Thương Hiệu & Giá Bán",
        "what": "Phân tích 3 yếu tố quyết định khách hàng tại thành phố chọn mua hàng của bạn hay của đối thủ: Quality (Chất lượng), Brand (Thương hiệu), và Price (Giá bán so với giá chuẩn Std).",
        "formula": "Overall Rating = (Q × W_qual)/60 + (B × W_brand)/60 + 2 × W_price × (P_std - P_unit)/P_std.",
        "when_to_use": "Nếu thấy Market Share % thấp, hãy nhìn xem mặt hàng đó có trọng số Price hay Quality/Brand cao hơn để giảm giá bán (Unit Price) hoặc tăng quảng cáo (Advertising) cho trúng đích!",
    },
    "dir-search": {
        "title": "🔎 DIRECTORY SEARCH — Tìm Kiếm Nhanh Mã Cổ Phiếu, Tên Công Ty Hoặc ID",
        "what": "Ô lọc tức thì trong danh bạ 1,078 công ty/ETF và 320 nhà đầu tư AI theo Mã Ticker (ví dụ WFC, C321), Tên công ty hoặc Số ID.",
        "formula": "Khớp chuỗi con không phân biệt hoa thường trên Ticker, Name và Entity ID.",
        "when_to_use": "Gõ mã cổ phiếu bạn muốn tra cứu hoặc để trống để xem toàn bộ danh sách theo bộ lọc.",
    },
    "dir-pill-ALL": {
        "title": "🌐 ALL CORPS — Hiển Thị Tất Cả Tập Đoàn Trên Sàn",
        "what": "Bộ lọc hiển thị toàn bộ các tập đoàn công nghiệp, ngân hàng, bảo hiểm và quỹ ETF đang niêm yết.",
        "formula": "Tổng cộng 1,078 tập đoàn + 20 quỹ ETF.",
        "when_to_use": "Dùng khi muốn duyệt rộng toàn thị trường để săn cơ hội đầu tư.",
    },
    "dir-pill-CONTROLLED": {
        "title": "👑 MY CONTROLLED — Các Công Ty Do Aether Kiểm Soát Điều Hành",
        "what": "Chỉ lọc ra các công ty mà Aether (#1) đang là Chủ tịch/CEO hoặc nắm quyền kiểm soát (>= 20% cổ phần và là cổ đông lớn nhất, hoặc Startup do Aether sáng lập).",
        "formula": "Controlled_By_ID == 1 hoặc nằm trong CEO_Of_Corp_IDs của #1.",
        "when_to_use": "Bấm vào đây để kiểm tra nhanh các công ty con thuộc đế chế của bạn!",
    },
    "dir-pill-BANKS": {
        "title": "🏦 BANKS / INSUR — Nhóm Ngân Hàng Thương Mại & Công Ty Bảo Hiểm",
        "what": "Lọc riêng các Ngân hàng thương mại (IND=1, như #13 WFC) và Công ty Bảo hiểm (IND=2).",
        "formula": "Regime in ('COMMERCIAL_BANK', 'INSURANCE_COMPANY').",
        "when_to_use": "Dùng khi muốn đầu tư cổ phiếu tài chính trả cổ tức đều hoặc chọn ngân hàng đối tác để vay tiền / gửi tiền.",
    },
    "dir-pill-ETFS": {
        "title": "📦 20 ETFs — Danh Sách 20 Quỹ Hoán Đổi Danh Mục (#1581..#1600)",
        "what": "Lọc riêng 20 quỹ ETF đại diện cho các rổ ngành và trái phiếu trên sàn WSR.",
        "formula": "Giá ETF bám sát NAV (Net Asset Value per Share) của rổ tài sản quỹ nắm giữ.",
        "when_to_use": "Rất phù hợp cho người mới bắt đầu muốn đa dạng hóa rủi ro chỉ với 1 lệnh mua 100sh, hoặc dùng để đăng ký làm Cố vấn Quỹ (ETF Advisor) thu phí quản lý!",
    },
    "dir-pill-INVESTORS": {
        "title": "🦈 320 INVESTORS — Danh Bạ 320 Nhà Đầu Tư AI (Cá Con & Cá Mập)",
        "what": "Hiển thị danh sách 320 nhà đầu tư AI thuộc 24 trường phái (từ #2001 Warren B., #2002 Carl I. đến các cá con $30k).",
        "formula": "320 AI = 24 Archetype Leads + 72 Smart Disciples + 224 Crowd/Hustler Investors.",
        "when_to_use": "Bấm vào bất kỳ cá mập nào trong danh sách này để soi trộm Bảng Cân Đối Kế Toán và Danh Mục Cổ Phiếu mà họ đang gom mua hoặc bán khống!",
    },
    "dir-regime-select": {
        "title": "🏛️ REGIME FILTER — Lọc Theo 5 Chế Độ Kế Toán (5 Balance Sheet Regimes)",
        "what": "Lọc chính xác từng chế độ kế toán trong thế giới WSR: IND (INDUSTRIAL_HOLDING — Tập đoàn Sản xuất/Đa ngành), BANK (COMMERCIAL_BANK — Ngân hàng Thương mại), INSUR (INSURANCE_COMPANY — Bảo hiểm), ETF (ETF_FUND — Quỹ Hoán đổi Danh mục), hoặc AI-INV (PLAYER_INDIVIDUAL — Nhà đầu tư Cá nhân/AI).",
        "formula": "5 Chế độ: INDUSTRIAL_HOLDING | COMMERCIAL_BANK | INSURANCE_COMPANY | ETF_FUND | PLAYER_INDIVIDUAL.",
        "when_to_use": "Dùng khi bạn muốn tách riêng Ngân hàng (BANK) khỏi Bảo hiểm (INSUR), hoặc chỉ lọc các Tập đoàn Sản xuất (IND) để tìm mục tiêu thâu tóm!",
    },
    "dir-sort-select": {
        "title": "🔃 DIRECTORY SORT — Sắp Xếp Danh Bạ Theo Giá, Tài Sản Ròng, ROCE%, P/B & Hạng Tín Nhiệm",
        "what": "Sắp xếp toàn bộ 1,078 tập đoàn và 320 nhà đầu tư tăng dần (▲) hoặc giảm dần (▼) theo ID, Ticker, Regime, Giá cổ phiếu (Price), Tài sản ròng (NetWorth), Hạng tín nhiệm (AAA -> D), ROCE% hoặc P/B. Bạn cũng có thể bấm trực tiếp vào tiêu đề các cột trên bảng để đảo chiều sắp xếp!",
        "formula": "P/B thấp + ROCE% cao + Hạng tín nhiệm AAA/AA = Cổ phiếu giá trị kim cương (Value Compounder).",
        "when_to_use": "Chọn 'Sort: P/B ▲ (Cheap Value)' hoặc 'Sort: ROCE% ▼ (High -> Low)' để săn ngay những công ty sinh lời khủng nhưng đang có giá cổ phiếu rẻ nhất sàn!",
    },
    "dir-pagination": {
        "title": "📄 DIRECTORY PAGINATION — Phân Trang Danh Bạ (1,078 Tập Đoàn + 320 AI)",
        "what": "Thanh điều hướng phân trang cho phép duyệt toàn bộ 1,399 thực thể trong thế giới mà không bị giới hạn ở 100 dòng đầu tiên (gồm nút Trang đầu «, Trang trước ‹, Trang sau ›, Trang cuối » và chọn số dòng mỗi trang 25 / 50 / 100 / 250 / All).",
        "formula": "Tổng số trang = ceil(Tổng số thực thể khớp bộ lọc / Số dòng mỗi trang).",
        "when_to_use": "Dùng để lật qua từng trang danh bạ hoặc chuyển sang 100/pg, 250/pg, All khi muốn quét toàn cảnh thị trường.",
    },
    "chart-asset-select": {
        "title": "📊 CHART ASSET SELECTOR — Chọn Tài Sản Hiển Thị Trên Bảng Nến OHLCV",
        "what": "Chuyển đổi biểu đồ nến Nhật giữa Công ty đang chọn (Selected Corp), Bitcoin (BTC/USD), Dầu thô (WTI Crude Oil), Vàng (Gold Spot) và Chỉ số Chung (WSR Composite Index).",
        "formula": "Cập nhật thời gian thực 36 cây nến OHLCV + Volume + MA7/MA20 + Bollinger + RSI(14).",
        "when_to_use": "Chuyển qua OIL/GOLD/BTC trước khi giao dịch Futures/Crypto, hoặc để ở Selected Corp khi soi cổ phiếu.",
    },
    "btn-buy-long": {
        "title": "📈 BUY LONG — Mua Nắm Giữ Cổ Phiếu (Long Equity Position)",
        "what": "Mua cổ phiếu của công ty mục tiêu (`Target Corp ID`) bằng tiền mặt của chủ thể đang chọn ở `Acting As`. Cổ phiếu mua từ lượng lưu hành tự do (`Public Float`).",
        "formula": "Chi phí = Số lượng CP (M) × Giá Spot × (1 + Hệ số trượt giá nếu mua lô lớn).",
        "when_to_use": "Khi cổ phiếu có nền tảng tốt (ROCE cao, P/B hợp lý, hạng BBB..AAA) và biểu đồ nến báo tín hiệu đảo chiều tăng (Hammer, Bullish Engulfing, RSI thoát vùng quá bán).",
    },
    "btn-sell-long": {
        "title": "💰 SELL LONG — Bán Chốt Lời / Cắt Lỗ Cổ Phiếu Đang Nắm Giữ",
        "what": "Bán bớt hoặc bán toàn bộ số cổ phiếu đang nắm giữ của công ty mục tiêu để thu tiền mặt về ví.",
        "formula": "Lãi vốn thực nhận (Realized Capital Gain) = (Giá bán - Giá vốn trung bình) × Số CP bán. Nếu có lãi sẽ tính thuế lãi vốn (CapTax).",
        "when_to_use": "Khi cổ phiếu đã đạt mục tiêu lợi nhuận, xuất hiện nến đảo chiều giảm (Shooting Star, Bearish Engulfing, RSI > 75) hoặc khi bạn cần gom tiền mặt để mở công ty khởi nghiệp!",
    },
    "btn-short-stock": {
        "title": "📉 SHORT — Bán Khống Cổ Phiếu (Đặt Cược Giá Sập)",
        "what": "Vay cổ phiếu trên sàn để bán lấy tiền mặt ngay ở giá hiện tại, với kỳ vọng giá cổ phiếu sẽ giảm sâu để mua trả lại (Cover Short) với giá rẻ hơn.",
        "formula": "Yêu cầu ký quỹ: Net Worth >= 50% giá trị lệnh Short. Lưu ý: Người bán khống phải trả tiền đền bù cổ tức nếu công ty chia cổ tức!",
        "when_to_use": "Khi phát hiện công ty làm ăn thua lỗ nặng, nợ ngập đầu (hạng CCC/D) hoặc nến đạt đỉnh bong bóng (RSI > 80).",
    },
    "btn-cover-short": {
        "title": "🔄 COVER SHORT — Mua Trả Lại Cổ Phiếu Đã Bán Khống (Đóng Vị Thế Short)",
        "what": "Dùng tiền mặt mua lại cổ phiếu trên sàn để trả nợ vị thế bán khống, hiện thực hóa lợi nhuận (nếu giá đã giảm) hoặc cắt lỗ (nếu giá tăng).",
        "formula": "Lãi/Lỗ Bán khống = Giá trị lúc Short ban đầu - Chi phí mua trả lại (Cover Cost).",
        "when_to_use": "Khi giá cổ phiếu đã sập về vùng hỗ trợ (RSI < 30) để chốt lời vị thế Short, hoặc cắt lỗ ngay trước khi bị Short Squeeze!",
    },
    "act-shares-m": {
        "title": "🔢 SHARES (MILLIONS) — Ô Nhập Khối Lượng Cổ Phiếu Giao Dịch (Đơn Vị: Triệu CP)",
        "what": "Số lượng cổ phiếu bạn muốn Mua, Bán, Bán khống hoặc Mua Quyền chọn, tính bằng đơn vị Triệu cổ phiếu (1.0 = 1,000,000 CP; 0.0001 = 100 CP).",
        "formula": "Est. Cost = Shares (M) × $1,000,000 × Spot Price ($).",
        "when_to_use": "Với vốn $30,000, hãy dùng các nút chọn nhanh 100sh (0.0001M), 500sh (0.0005M) hoặc 2,500sh (0.0025M) ngay bên dưới!",
    },
    "btn-lot-100sh": {
        "title": "🪙 100sh (0.0001M) — Nút Chọn Nhanh Lô Vi Mô 100 Cổ Phiếu",
        "what": "Điền ngay con số 0.0001 (tương đương 100 cổ phiếu) vào ô khối lượng giao dịch.",
        "formula": "Nếu giá cổ phiếu là $28.50, lô 100sh chỉ tốn $2,850 (chưa tới 10% ví $30,000 của Aether).",
        "when_to_use": "Nút bấm vàng dành riêng cho người chơi khởi nghiệp $30k để chia nhỏ vốn mua được từ 5 đến 10 mã cổ phiếu khác nhau!",
    },
    "btn-buy-govbond": {
        "title": "🏛️ BUY GOVBOND — Mua Trái Phiếu Chính Phủ Dài Hạn (Kênh Trú Ẩn An Toàn)",
        "what": "Dùng tiền mặt mua Trái phiếu Chính phủ hưởng lãi suất cố định an toàn tuyệt đối (0% rủi ro vỡ nợ).",
        "formula": "Giá Trái phiếu Chính phủ biến động ngược chiều với lãi suất dài hạn (Long Bond Rate).",
        "when_to_use": "Khi thị trường chứng khoán biến động xấu hoặc khi lãi suất đã đạt đỉnh và sắp hạ nhiệt (giá trái phiếu sẽ tăng mạnh).",
    },
    "btn-sell-govbond": {
        "title": "💵 SELL GOVBOND — Bán Trái Phiếu Chính Phủ Thu Tiền Mặt",
        "what": "Bán danh mục Trái phiếu Chính phủ đang nắm giữ theo tỷ giá thị trường hiện tại để thu tiền mặt ngay lập tức.",
        "formula": "Tiền thu về = Mệnh giá bán × (Market Bond Price / 100).",
        "when_to_use": "Khi cần rút vốn từ kênh trú ẩn an toàn sang mua cổ phiếu bắt đáy hoặc mở nhà máy.",
    },
    "btn-buy-corpbond": {
        "title": "📜 BUY CORPBOND — Mua Trái Phiếu Doanh Nghiệp Lãi Suất Cao",
        "what": "Mua trái phiếu do tập đoàn mục tiêu phát hành để hưởng lãi suất (Yield) cao hơn Trái phiếu Chính phủ.",
        "formula": "Lợi suất phụ thuộc vào Hạng tín nhiệm (AAA..CCC) của công ty phát hành.",
        "when_to_use": "Khi muốn thu dòng tiền lãi cố định cao từ các tập đoàn có dòng tiền ổn định.",
    },
    "btn-trade-deriv": {
        "title": "🛢️₿ FUTURES / CRYPTO — Giao Dịch Hợp Đồng Tương Lai Hàng Hóa & Tiền Mã Hóa",
        "what": "Thực hiện giao dịch mua/bán trên tài sản đang chọn ở ô Asset bên cạnh: Hợp đồng tương lai OIL, GOLD, COPPER, WHEAT (ký quỹ 15%) hoặc mua/bán trực tiếp BTC, ETH.",
        "formula": "Futures Initial Margin = 15% × Notional ($M) | Crypto = Thanh toán 100% theo Notional ($M).",
        "when_to_use": "Dùng để đầu cơ theo sóng giá Dầu/Vàng/Bitcoin hoặc phòng vệ rủi ro (Hedge) giá nguyên liệu đầu vào cho nhà máy.",
    },
    "btn-buy-call": {
        "title": "🚀 BUY CALL — Mua Quyền Chọn Mua (Đòn Bẩy Tăng Giá)",
        "what": "Trả một khoản phí nhỏ (Option Premium) để có quyền mua cổ phiếu mục tiêu ở giá Strike (105% giá hiện tại) trong 2 quý tới.",
        "formula": "Lỗ tối đa = Phí Premium đã trả | Lãi tiềm năng = Không giới hạn khi giá cổ phiếu tăng vọt!",
        "when_to_use": "Khi bạn cực kỳ tin tưởng cổ phiếu sắp bứt phá mạnh (ví dụ có MA7 cắt lên MA20 + nến Marubozu xanh).",
    },
    "btn-buy-put": {
        "title": "🛡️ BUY PUT — Mua Quyền Chọn Bán (Đặt Cược Giá Giảm / Bảo Hiểm Danh Mục)",
        "what": "Trả phí Premium để có quyền bán cổ phiếu mục tiêu ở giá Strike (95% giá hiện tại) khi thị trường sập.",
        "formula": "Giá trị nội tại (Intrinsic Value) = max(0, Strike Price - Spot Price) × Số CP.",
        "when_to_use": "Dùng để kiếm lời lớn khi dự báo cổ phiếu sắp sập mà không sợ rủi ro cháy tài khoản như Short Selling, hoặc dùng để bảo hiểm cho cổ phiếu đang giữ.",
    },
    "btn-write-call": {
        "title": "✍️ WRITE CALL — Bán (Phát Hành) Quyền Chọn Mua Để Thu Phí Premium Ngay",
        "what": "Đóng vai nhà cái bán hợp đồng quyền chọn cho thị trường để thu tiền phí Premium về ví ngay lập tức.",
        "formula": "Nếu có sẵn cổ phiếu (Covered Call) thì rất an toàn; nếu không có cổ phiếu (Naked Call) sẽ phát sinh nghĩa vụ nợ Naked Option Liability.",
        "when_to_use": "Khi dự báo cổ phiếu đi ngang (Sideways - nến Doji) để ăn trọn tiền phí thời gian (Time Decay).",
    },
    "btn-rate-swap": {
        "title": "🔄 RATE SWAP — Hợp Đồng Hoán Đổi Lãi Suất (Interest Rate Swap - IRS)",
        "what": "Ký hợp đồng phái sinh lãi suất kỳ hạn 4 quý: Trả lãi cố định 6.5%/năm và Nhận lãi thả nổi Prime Rate trên mệnh giá Notional.",
        "formula": "Dòng tiền nhận mỗi Quý = Notional × (Prime Rate - 6.5%) × 0.25 / 100.",
        "when_to_use": "Vũ khí tối thượng khi lạm phát và lãi suất Prime Rate tăng cao (> 6.5%) hoặc dùng để bảo hiểm chi phí lãi vay ngân hàng!",
    },
    "btn-borrow-loan": {
        "title": "🏦 BORROW LOAN — Vay Tín Dụng Ngân Hàng (Đòn Bẩy Tài Chính)",
        "what": "Vay tiền mặt từ ngân hàng thương mại (lãi suất tính theo Prime Rate + biên độ tín nhiệm) để bổ sung vốn lưu động hoặc đầu tư.",
        "formula": "Hạn mức vay phụ thuộc vào Net Worth và Hạng tín nhiệm (AAA..CCC) của chủ thể vay.",
        "when_to_use": "Khi cơ hội đầu tư (ROCE của nhà máy hoặc cổ phiếu) có tỷ suất sinh lời cao hơn lãi suất vay ngân hàng!",
    },
    "btn-repay-loan": {
        "title": "💳 REPAY LOAN — Trả Bớt Nợ Vay Ngân Hàng",
        "what": "Dùng tiền mặt đang có để trả bớt gốc khoản vay ngân hàng, giúp giảm chi phí lãi vay hàng quý và nâng hạng tín nhiệm (Credit Rating).",
        "formula": "ΔCash = -RepayAmount, ΔBankLoan = -RepayAmount => ΔNetWorth = 0 (Giảm đòn bẩy nợ).",
        "when_to_use": "Khi lãi suất Prime Rate tăng cao hoặc khi bạn có dư tiền mặt muốn làm sạch bảng cân đối kế toán.",
    },
    "btn-set-dividend": {
        "title": "💸 SET DIVIDEND — Phát Lệnh Chia Cổ Tức Tiền Mặt Cho Cổ Đông",
        "what": "Trích tiền mặt từ két của công ty để trả cổ tức cho tất cả các cổ đông đang nắm giữ cổ phiếu (bao gồm cả Aether và Công ty mẹ).",
        "formula": "Nếu Công ty mẹ sở hữu >= 80% cổ phần, cổ tức nhận về được MIỄN THUẾ 100% (100% DRD)!",
        "when_to_use": "Khi công ty con làm ăn có lãi lớn và bạn muốn rút tiền mặt hợp pháp từ công ty về ví cá nhân hoặc công ty mẹ.",
    },
    "btn-spinoff-sub": {
        "title": "🧬 80% SPINOFF — Tách Công Ty Con Phân Phối Cổ Phần Miễn Thuế",
        "what": "Công ty mẹ (Acting As) phân phối toàn bộ cổ phần đang nắm giữ tại Công ty con (Target Corp ID) trực tiếp cho các cổ đông của công ty mẹ.",
        "formula": "Nếu tỷ lệ sở hữu >= 80%: Miễn thuế lãi vốn 100% (Tax-Free Spin-Off); nếu < 80%: Chịu thuế lãi vốn doanh nghiệp.",
        "when_to_use": "Khi muốn tái cấu trúc tập đoàn đa ngành và trao trả trực tiếp cổ phần công ty con về ví của Aether.",
    },
    "btn-etf-advisor": {
        "title": "🎖️ ETF ADVISOR — Đăng Ký Làm Cố Vấn Quản Lý Quỹ ETF (#1581)",
        "what": "Bổ nhiệm chủ thể đang chọn làm Cố vấn Quản lý cho Quỹ ETF để thu phí quản lý định kỳ mỗi quý.",
        "formula": "Advisory Fee mỗi Quý = 0.1% × Tổng Tài Sản Ròng (NAV) của Quỹ ETF (~0.4%/năm).",
        "when_to_use": "Nguồn thu nhập thụ động (Passive Income) tuyệt vời cho Aether mà không cần bỏ vốn mua cổ phiếu!",
    },
    "btn-lawsuit": {
        "title": "⚖️ LAWSUIT — Đệ Đơn Kiện Pháp Lý / Chống Độc Quyền (Corporate Litigation)",
        "what": "Khởi kiện tập đoàn mục tiêu ra tòa án kinh tế với mức bồi thường yêu cầu tính theo ô Amount ($M).",
        "formula": "Án phí tạm ứng (Legal Retainer) = 2% giá trị đơn kiện. Xác suất thắng kiện = 38% (xử vào các kỳ quyết toán Quý).",
        "when_to_use": "Khi muốn tấn công pháp lý đối thủ cạnh tranh hoặc tìm kiếm khoản tiền bồi thường đột biến.",
    },
    "btn-deposit-gta": {
        "title": "🚓 DEPOSIT FROM GTA — Nạp Tiền Từ Ví GTA San Andreas Vào Sàn Tài Chính",
        "what": "Chuyển tiền mặt kiếm được từ các nhiệm vụ trong GTA San Andreas (Project Eagle) vào ví đầu tư của #1 Aether theo tỷ lệ chuẩn 1:1.",
        "formula": "$1.00 GTA Wallet === $1.00 EagleCapitalEngine ($0.000001M).",
        "when_to_use": "Khi bạn vừa làm nhiệm vụ trong GTA SA có thêm tiền mặt và muốn nạp vào sàn để mua cổ phiếu hoặc mở thêm cửa hàng!",
    },
    "btn-withdraw-gta": {
        "title": "💵 WITHDRAW TO GTA — Rút Tiền Lãi Từ Sàn Về Ví Nhân Vật GTA San Andreas",
        "what": "Rút tiền mặt từ ví đầu tư của #1 Aether về lại ví nhân vật Aether trong GTA San Andreas.",
        "formula": "Trừ trực tiếp từ Cash của #1 Aether và cộng 1:1 vào GTA Wallet.",
        "when_to_use": "Khi đầu tư thắng lớn hoặc nhận cổ tức và muốn rút tiền về GTA SA để mua siêu xe, vũ khí, bất động sản!",
    },
    "btn-incorporate-startup": {
        "title": "🚀 INCORPORATE STARTUP — Thành Lập Công Ty Khởi Nghiệp Mở Cửa Hàng Đầu Tiên ($18,000)",
        "what": "Dùng số vốn nhỏ từ $10,000 - $25,000 trong ví cá nhân của Aether để thành lập một Công ty Cổ phần hoàn toàn mới (100% cổ phần của Aether, Aether làm CEO lương $25k/năm) và xây luôn 1 cơ sở kinh doanh đầu tiên!",
        "formula": "70% vốn góp dùng xây Cửa hàng/Nhà máy + 20% nhập Hàng tồn kho + 10% giữ làm Tiền mặt dự phòng trong két công ty.",
        "when_to_use": "Bước ngoặt quan trọng nhất của người chơi $30k để chuyển mình từ người đi buôn cổ phiếu lẻ thành Ông Chủ Doanh Nghiệp!",
    },
    "btn-construct-firm": {
        "title": "🏗️ CONSTRUCT FIRM — Xây Dựng Thêm Nhà Máy / Cửa Hàng / Viện R&D Mới",
        "what": "Dùng tiền mặt của tập đoàn đang chọn ở Acting As để xây thêm cơ sở vật lý mới tại 1 trong 128 thành phố.",
        "formula": "Zero Double-Counting Bridge: ΔCash = -(CAPEX + Inventory), ΔCapAssets = +CAPEX, ΔWorkingCap = +Inventory => Bảo toàn Net Worth 100%.",
        "when_to_use": "Khi muốn mở rộng chuỗi cửa hàng bán lẻ, xây nhà máy tự chủ nguyên liệu hoặc lập Viện R&D công nghệ cao.",
    },
    "btn-train-staff": {
        "title": "🎓 TRAIN ALL 9 UNITS (+Lv) — Huấn Luyện Nâng Cấp Toàn Bộ 9 Bộ Phận Trong Mặt Bằng 3×3",
        "what": "Tăng +1 cấp độ kỹ năng (★Lv, tối đa Lv9) cho toàn bộ 9 ô bộ phận trên mặt bằng 3x3 của cơ sở đang chọn.",
        "formula": "Mỗi lần huấn luyện tăng ngay +2.5 điểm Product Quality và cải thiện năng suất vận hành (Utilization %).",
        "when_to_use": "Cách nhanh nhất và rẻ nhất để nâng điểm Chất lượng (Quality) cho cửa hàng/nhà máy mới mở!",
    },
    "btn-assign-unit": {
        "title": "🔧 ASSIGN UNIT — Gán Lại Chức Năng Bộ Phận Cho Ô Đang Chọn Trên Lưới 3×3",
        "what": "Đổi vai trò của ô (Slot #1..#9) trên mặt bằng 3x3 thành PUR (Thu mua), MFT (Sản xuất), SALE (Bán hàng), INV (Kho), EXTERN (Quảng cáo), RD/TECH (Nghiên cứu) hoặc LABEL (Nhãn hiệu riêng).",
        "formula": "Tự động cập nhật sơ đồ mặt bằng 3x3 và cộng +1.2 điểm Quality tối ưu hóa.",
        "when_to_use": "Khi muốn tùy biến dây chuyền bên trong nhà máy/cửa hàng để giải quyết điểm nghẽn tồn kho hoặc đẩy mạnh thương hiệu.",
    },
    "btn-update-prq": {
        "title": "⚡ UPDATE PRQ — Áp Dụng Giá Bán Mới & Ngân Sách Quảng Cáo Để Giành Thị Phần",
        "what": "Cập nhật Giá bán đơn vị (Unit Price $) và Ngân sách quảng cáo mỗi quý (Advertising $M/Qtr) cho cơ sở đang chọn, tính toán lại ngay lập tức Thị phần (Market Share %) và Lợi nhuận (EBIT)!",
        "formula": "Market Share = Score_i^2.2 / (Sum(Score^2.2) + LocalCompetitorAnchor).",
        "when_to_use": "Sau khi điều chỉnh giá bán thấp hơn giá chuẩn (Std Price) 5%-10% hoặc tăng quảng cáo để bứt phá doanh thu!",
    },
    "btn-save-game": {
        "title": "💾 SAVE — Lưu Toàn Bộ Thế Giới Kinh Tế Với Độ Chính Xác Tuyệt Đối (0.000000 Loss)",
        "what": "Lưu toàn bộ trạng thái 1,078 tập đoàn, 20 ETFs, 320 nhà đầu tư AI, các nhà máy 3x3 và danh mục của Aether xuống file JSON.",
        "formula": "Atomic Save/Load: Sai số tài sản trước và sau khi Load = 0.000000.",
        "when_to_use": "Bấm lưu trước khi thực hiện các thương vụ mạo hiểm hoặc trước khi kích hoạt kịch bản khủng hoảng S1..S6!",
    },
    "btn-load-game": {
        "title": "📂 LOAD — Khôi Phục Trạng Thái Thế Giới Đã Lưu",
        "what": "Nạp lại toàn bộ trạng thái thế giới từ bản lưu gần nhất.",
        "formula": "Khôi phục 100% tiền mặt, cổ phiếu, nợ vay, nhà máy và lịch sử vĩ mô.",
        "when_to_use": "Khi muốn quay lại thời điểm trước một quyết định đầu tư sai lầm hoặc sau khi thử nghiệm kịch bản Stress Test.",
    },
    "btn-reset-game": {
        "title": "🔄 RESET — Khởi Tạo Lại Thế Giới Mới Tại Mốc 2010-Q1",
        "what": "Đặt lại toàn bộ thế giới về ngày đầu tiên 2010-Q1 (01/01) theo chế độ hiện tại ($30k Hustler hoặc $1B Sandbox).",
        "formula": "Tái sinh mới toàn bộ 1,078 công ty và 320 nhà đầu tư AI.",
        "when_to_use": "Khi bạn muốn bắt đầu một ván chơi mới tinh từ đầu.",
    },
}


# =============================================================================
# 3. LIVE TELEMETRY CONTEXT BUILDER & PAIMON AI TUTOR (GPT-6-LUNA + FALLBACK)
# =============================================================================

class PaimonAcademyEngine:
    def __init__(self, api_key: str = DEFAULT_API_KEY, model_name: str = "gpt-6-luna") -> None:
        self.api_key = api_key
        self.model_name = "gpt-6-luna" if model_name in ("gpt-6.1-luna", "gpt-6-luna") else model_name
        self.progress_state: Dict[str, Any] = {
            "active_module_id": "M0",
            "active_quest_id": "M0_Q1",
            "completed_quests": [],
            "inspect_mode_on": False,
            "chat_history": [],
            "total_chat_calls": 0,
            "total_chat_tokens": 0,
            "total_chat_cost_usd": 0.0,
        }
        self._load_progress()

    def _load_progress(self) -> None:
        if os.path.isfile(PAIMON_PROGRESS_PATH):
            try:
                with open(PAIMON_PROGRESS_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                if isinstance(saved, dict):
                    self.progress_state.update(saved)
            except Exception:
                pass

    def save_progress(self) -> None:
        try:
            with open(PAIMON_PROGRESS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.progress_state, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def reset_progress(self) -> Dict[str, Any]:
        self.progress_state = {
            "active_module_id": "M0",
            "active_quest_id": "M0_Q1",
            "completed_quests": [],
            "inspect_mode_on": False,
            "chat_history": [],
            "total_chat_calls": self.progress_state.get("total_chat_calls", 0),
            "total_chat_tokens": self.progress_state.get("total_chat_tokens", 0),
            "total_chat_cost_usd": self.progress_state.get("total_chat_cost_usd", 0.0),
        }
        self.save_progress()
        return self.progress_state

    def update_progress(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if "active_module_id" in payload:
            self.progress_state["active_module_id"] = str(payload["active_module_id"])
        if "active_quest_id" in payload:
            self.progress_state["active_quest_id"] = str(payload["active_quest_id"])
        if "completed_quest_id" in payload:
            qid = str(payload["completed_quest_id"])
            if qid and qid not in self.progress_state["completed_quests"]:
                self.progress_state["completed_quests"].append(qid)
        if "completed_quests" in payload and isinstance(payload["completed_quests"], list):
            for qid in payload["completed_quests"]:
                if qid not in self.progress_state["completed_quests"]:
                    self.progress_state["completed_quests"].append(str(qid))
        if "inspect_mode_on" in payload:
            self.progress_state["inspect_mode_on"] = bool(payload["inspect_mode_on"])
        self.save_progress()
        return self.progress_state

    def get_academy_payload(self) -> Dict[str, Any]:
        total_quests = sum(len(m.get("quests", [])) for m in PAIMON_CURRICULUM_MODULES)
        return {
            "modules": PAIMON_CURRICULUM_MODULES,
            "inspect_dict": PAIMON_INSPECT_DICTIONARY,
            "progress": self.progress_state,
            "total_modules": len(PAIMON_CURRICULUM_MODULES),
            "total_quests": total_quests,
        }

    def build_live_telemetry_context(
        self,
        app_state: Any,
        active_entity_id: int = 1,
        acting_as_id: int = 1,
        selected_firm_id: int = 1,
        chart_symbol: str = "SELECTED_CORP",
        active_module_id: Optional[str] = None,
        active_quest_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Builds a rich, exact real-time snapshot of Aether's screen, OHLCV chart candles,
        viewed entity financials, selected 3x3 Capitalism Lab firm, and macro indicators.
        """
        e = app_state.engine
        mod_id = active_module_id or self.progress_state.get("active_module_id", "M0")
        q_id = active_quest_id or self.progress_state.get("active_quest_id", "M0_Q1")

        # Find current quest metadata
        quest_meta = {"quest_id": q_id, "title": "", "task_instruction": ""}
        for m in PAIMON_CURRICULUM_MODULES:
            if m["module_id"] == mod_id:
                for q in m["quests"]:
                    if q["quest_id"] == q_id:
                        quest_meta = {
                            "module_id": mod_id,
                            "module_title": m["title"],
                            "quest_id": q_id,
                            "quest_title": q["title"],
                            "task_instruction": q["task_instruction"],
                        }
                        break

        aether = e.entities.get(1)
        actor = e.entities.get(acting_as_id) or aether
        viewed = e.entities.get(active_entity_id) or aether

        # Compute viewed entity P/B and valuation metrics
        viewed_pb = 0.0
        viewed_book_ps = 0.0
        if viewed.shares_outstanding > 0:
            viewed_book_ps = round(viewed.net_worth / viewed.shares_outstanding, 2)
            viewed_pb = round((viewed.stock_price * viewed.shares_outstanding) / max(0.01, viewed.net_worth), 2)

        # Get OHLCV series for current chart symbol
        corp_for_chart = active_entity_id if (11 <= active_entity_id <= 1600 and viewed.regime != "PLAYER_INDIVIDUAL") else 13
        c_ent = e.entities.get(corp_for_chart, e.entities[13])
        if chart_symbol == "BTC":
            series = app_state.get_or_init_ohlcv_series("BTC", e.crypto_prices.get("BTC", 65000.0), "BTC / USD Crypto")
        elif chart_symbol == "OIL":
            series = app_state.get_or_init_ohlcv_series("OIL", e.commodity_prices.get("OIL", 75.0), "WTI Crude Oil ($/bbl)")
        elif chart_symbol == "GOLD":
            series = app_state.get_or_init_ohlcv_series("GOLD", e.commodity_prices.get("GOLD", 2000.0), "Gold Spot ($/oz)")
        elif chart_symbol == "STOCK_INDEX":
            series = app_state.get_or_init_ohlcv_series("STOCK_INDEX", e.commodity_prices.get("STOCK_INDEX", 4500.0), "WSR Composite Index")
        else:
            series = app_state.get_or_init_ohlcv_series(
                f"CORP_{corp_for_chart}", c_ent.stock_price, f"#{corp_for_chart} {c_ent.ticker} ({c_ent.name})"
            )

        bars = series.get("bars", [])
        last_bar = bars[-1] if bars else {"t": "2010-Q1", "o": 10.0, "h": 10.5, "l": 9.8, "c": 10.2, "v": 250.0}
        rng = max(1e-6, last_bar["h"] - last_bar["l"])
        body = abs(last_bar["c"] - last_bar["o"])
        u_wick = last_bar["h"] - max(last_bar["o"], last_bar["c"])
        l_wick = min(last_bar["o"], last_bar["c"]) - last_bar["l"]

        # Selected Capitalism Lab Firm telemetry
        firm_obj = e.firms.get(selected_firm_id) or (next(iter(e.firms.values())) if e.firms else None)
        firm_ctx: Dict[str, Any] = {}
        if firm_obj:
            recipe = e.recipes.get(firm_obj.product_code)
            pdata = e.products.get(firm_obj.product_code, {})
            layout = app_state.firm_custom_layouts.get(firm_obj.firm_id) or []
            role_counts: Dict[str, int] = {}
            for cell in layout:
                r = cell.get("role", "MFT")
                role_counts[r] = role_counts.get(r, 0) + 1
            firm_ctx = {
                "firm_id": firm_obj.firm_id,
                "owner_corp_id": firm_obj.owner_corp_id,
                "firm_type": firm_obj.firm_type,
                "city": firm_obj.city_name,
                "product": firm_obj.product_code,
                "recipe_inputs": [recipe.get("INPUT1"), recipe.get("INPUT2"), recipe.get("INPUT3")] if recipe else [],
                "quality": round(firm_obj.product_quality, 1),
                "brand": round(firm_obj.brand_rating, 1),
                "unit_price": round(firm_obj.unit_price, 2),
                "std_price": float(pdata.get("PRICE", 100.0) or 100.0),
                "market_share_pct": round(firm_obj.market_share * 100.0, 2),
                "cogs_ratio_pct": round(firm_obj.cogs_ratio * 100.0, 1),
                "integrated_inputs_shield": firm_obj.integrated_inputs_count,
                "adv_budget_millions": round(firm_obj.advertising_budget_millions, 4),
                "last_q_rev_millions": round(firm_obj.last_quarter_revenue_millions, 4),
                "last_q_ebit_millions": round(firm_obj.last_quarter_ebit_millions, 4),
                "unit_training_level": firm_obj.unit_training_level,
                "layout_3x3_role_counts": role_counts,
            }

        # Top 3 Peer Comparison Stocks (so Paimon can explain why one stock is better than another)
        peer_comparisons = []
        for cid in e.active_corp_ids[:45]:
            c = e.entities[cid]
            if not c.is_active or c.net_worth <= 0 or c.shares_outstanding <= 0:
                continue
            pb = (c.stock_price * c.shares_outstanding) / max(1.0, c.net_worth)
            peer_comparisons.append({
                "id": cid,
                "ticker": c.ticker,
                "name": c.name[:22],
                "regime": c.regime,
                "price": round(c.stock_price, 2),
                "pb": round(pb, 2),
                "roce_pct": round(c.roce_pct, 1),
                "rating": RATING_LABELS.get(c.credit_rating, "BBB"),
            })
        top_value_peers = sorted(peer_comparisons, key=lambda x: x["pb"])[:4]
        top_roce_peers = sorted(peer_comparisons, key=lambda x: x["roce_pct"], reverse=True)[:4]

        return {
            "date": f"{e.year}-Q{e.quarter} ({e.month:02d}/{e.day:02d})",
            "game_mode": app_state.game_mode,
            "current_lesson": quest_meta,
            "macro": {
                "gdp_growth_pct": round(e.gdp_growth_pct, 2),
                "cpi_inflation_pct": round(e.inflation_pct, 2),
                "prime_rate_pct": round(e.prime_rate_pct, 2),
                "long_bond_price": round(e.get_long_gov_bond_price(), 2),
                "commodities": {k: round(v, 2) for k, v in e.commodity_prices.items()},
                "crypto": {k: round(v, 2) for k, v in e.crypto_prices.items()},
            },
            "aether_wallet": {
                "cash_usd": round(aether.cash * 1_000_000.0, 2),
                "net_worth_usd": round(aether.net_worth * 1_000_000.0, 2),
                "bank_loan_usd": round(aether.bank_loan * 1_000_000.0, 2),
                "controlled_corp_ids": sorted(list(aether.ceo_of_corp_ids)),
            },
            "acting_as_entity": {
                "id": actor.entity_id,
                "name": actor.name,
                "ticker": actor.ticker,
                "regime": actor.regime,
                "cash_millions": round(actor.cash, 5),
                "net_worth_millions": round(actor.net_worth, 5),
                "holdings_count": len(actor.stock_holdings),
                "shorts_count": len(actor.short_positions),
            },
            "viewed_entity": {
                "id": viewed.entity_id,
                "name": viewed.name,
                "ticker": viewed.ticker,
                "regime": viewed.regime,
                "credit_rating": RATING_LABELS.get(viewed.credit_rating, "BBB"),
                "stock_price": round(viewed.stock_price, 2),
                "book_value_per_share": viewed_book_ps,
                "pb_ratio": viewed_pb,
                "roce_pct": round(viewed.roce_pct, 2),
                "annual_eps": round(viewed.annual_eps, 2),
                "dividend_per_share": round(viewed.dividend_per_share, 3),
                "cash_millions": round(viewed.cash, 4),
                "total_assets_millions": round(viewed.total_assets, 4),
                "total_liabilities_millions": round(viewed.total_liabilities, 4),
                "net_worth_millions": round(viewed.net_worth, 4),
                "free_float_shares_millions": round(e.public_float_shares.get(viewed.entity_id, 0.0), 2),
            },
            "ohlcv_chart_telemetry": {
                "symbol_key": series.get("symbol_key"),
                "label": series.get("label"),
                "current_price": series.get("current_price"),
                "rsi14": series.get("rsi14"),
                "pattern": series.get("pattern"),
                "sma7_latest": series.get("sma7", [None])[-1],
                "sma20_latest": series.get("sma20", [None])[-1],
                "bb_upper_latest": series.get("bb_upper", [None])[-1],
                "bb_lower_latest": series.get("bb_lower", [None])[-1],
                "latest_candle": {
                    **last_bar,
                    "direction": "BULLISH_GREEN" if last_bar["c"] >= last_bar["o"] else "BEARISH_RED",
                    "body_pct_of_range": round((body / rng) * 100.0, 1),
                    "upper_wick_pct_of_range": round((u_wick / rng) * 100.0, 1),
                    "lower_wick_pct_of_range": round((l_wick / rng) * 100.0, 1),
                },
                "recent_5_bars": bars[-5:],
            },
            "selected_caplab_firm": firm_ctx,
            "market_peer_benchmarks": {
                "lowest_pb_value_stocks": top_value_peers,
                "highest_roce_momentum_stocks": top_roce_peers,
            },
        }

    def _build_deterministic_paimon_fallback(self, question: str, ctx: Dict[str, Any]) -> str:
        """
        High-precision context-aware Paimon tutor response generator used as an instant fallback
        if the external API is unreachable or times out, referencing exact live numbers from ctx.
        """
        q_low = question.lower()
        chart = ctx["ohlcv_chart_telemetry"]
        candle = chart["latest_candle"]
        viewed = ctx["viewed_entity"]
        firm = ctx["selected_caplab_firm"]
        macro = ctx["macro"]
        wallet = ctx["aether_wallet"]
        peers = ctx["market_peer_benchmarks"]

        if any(k in q_low for k in ("nến", "candle", "râu", "rsi", "ma7", "ma20", "bollinger", "chart", "biểu đồ")):
            rsi = float(chart.get("rsi14") or 50.0)
            rsi_comment = (
                f"vùng QUÁ MUA (RSI = {rsi} >= 70, cẩn thận áp lực chốt lời ngắn hạn)"
                if rsi >= 70
                else (
                    f"vùng QUÁ BÁN (RSI = {rsi} <= 30, giá đã giảm sâu, rất dễ có nhịp bật hồi)"
                    if rsi <= 30
                    else f"vùng TRUNG TÍNH ổn định (RSI = {rsi})"
                )
            )
            sma7 = chart.get("sma7_latest")
            sma20 = chart.get("sma20_latest")
            ma_comment = (
                f"Đường MA7 (${sma7}) đang nằm TRÊN MA20 (${sma20}) -> Xu hướng ngắn hạn đang ủng hộ phe Mua (Golden Cross)!"
                if (sma7 and sma20 and sma7 >= sma20)
                else f"Đường MA7 (${sma7}) đang nằm DƯỚI MA20 (${sma20}) -> Xu hướng ngắn hạn đang điều chỉnh, nên chờ giá vượt lại MA20 hoặc râu dưới rút chân."
            )
            return (
                f"✨ **Paimon soi Biểu đồ Nến [{chart['label']}] ngay trên màn hình của Aether đây!**\n\n"
                f"1. **Giải phẫu cây nến mới nhất (`{candle['t']}`):**\n"
                f"   - **Giá Mở cửa (`O`):** `${candle['o']}` | **Đóng cửa (`C`):** `${candle['c']}` ({'Nến XANH - Phe Mua thắng' if candle['c'] >= candle['o'] else 'Nến ĐỎ - Phe Bán ép giá'}).\n"
                f"   - **Đỉnh râu trên (`H`):** `${candle['h']}` (chiếm `{candle['upper_wick_pct_of_range']}%` biên độ) | **Đáy râu dưới (`L`):** `${candle['l']}` (chiếm `{candle['lower_wick_pct_of_range']}%` biên độ).\n"
                f"   - **Mẫu hình nhận diện:** **`{chart['pattern']}`** với khối lượng `Vol = {candle['v']}K`.\n"
                f"2. **Chỉ báo Kỹ thuật kết hợp (`RSI` + `MA7/20` + `Bollinger`):**\n"
                f"   - **`RSI(14)`:** Đang ở {rsi_comment}.\n"
                f"   - **Xu hướng `MA7/MA20`:** {ma_comment}\n"
                f"   - **Dải `Bollinger`:** Biên trên `${chart.get('bb_upper_latest')}` / Biên dưới `${chart.get('bb_lower_latest')}`.\n"
                f"3. **Lời khuyên thực chiến của Paimon cho Aether (Ví hiện có `${wallet['cash_usd']:,.0f}`):**\n"
                f"   - Với vốn hiện tại, nếu cậu muốn vào lệnh mã này, hãy chia nhỏ bằng nút **`100sh`** (`0.0001M` CP) để quản trị rủi ro, kết hợp kiểm tra `P/B = {viewed['pb_ratio']}x` và `ROCE = {viewed['roce_pct']}%` nhé!"
            )

        if any(k in q_low for k in ("3x3", "nhà máy", "cửa hàng", "firm", "biên lợi nhuận", "cogs", "thị phần", "prq", "sửa ô")):
            if firm:
                shield_txt = (
                    f"đã tự chủ được `{firm['integrated_inputs_shield']}` nguồn nguyên liệu (`Vertical Shield`)"
                    if firm["integrated_inputs_shield"] > 0
                    else f"chưa tự chủ được nguyên liệu đầu vào (`integrated_inputs = 0`), phải mua ngoài chợ nên `COGS = {firm['cogs_ratio_pct']}%` doanh thu"
                )
                return (
                    f"🏭 **Paimon khám bệnh cho Cơ sở `#{firm['firm_id']} {firm['firm_type']}` ({firm['product']} tại {firm['city']}) đây!**\n\n"
                    f"1. **Tại sao biên lợi nhuận và EBIT hiện tại là `${firm['last_q_ebit_millions']}M` trên doanh thu `${firm['last_q_rev_millions']}M`?**\n"
                    f"   - Cơ sở này hiện {shield_txt}.\n"
                    f"   - Điểm Chất lượng hiện tại `Quality = {firm['quality']}`, Thương hiệu `Brand = {firm['brand']}`, Giá bán `${firm['unit_price']}` (so với giá chuẩn `${firm['std_price']}`), đang chiếm **`{firm['market_share_pct']}%` thị phần**.\n"
                    f"   - Cấu trúc `3x3` hiện tại: `{firm['layout_3x3_role_counts']}` (Trình độ nhân sự trung bình `★Lv{firm['unit_training_level']}`).\n"
                    f"2. **3 Bước Aether nên làm ngay trên Tab 2 để tăng lãi (`EBIT`):**\n"
                    f"   - **Bước 1:** Bấm nút vàng **`Train All 9 Units (+Lv)`** để nâng cấp sao cho cả 9 ô, giúp tăng ngay `+2.5 Quality`!\n"
                    f"   - **Bước 2:** Nếu điểm `Brand` còn thấp, hãy bấm vào ô `#2` hoặc `#9` trên lưới `3x3`, đổi sang **`EXTERN (Advertising)`** và bấm `Assign Unit`, hoặc chỉnh giá bán thấp hơn giá chuẩn `5%–10%` rồi bấm **`Update PRQ`** để cướp thêm thị phần!\n"
                    f"   - **Bước 3 (Dài hạn):** Mở thêm viện `R&D` hoặc mỏ/nhà máy nguyên liệu thượng nguồn (`{', '.join([x for x in firm['recipe_inputs'] if x]) or 'Raw Inputs'}`) để bật khiên `Vertical Shield` giảm mạnh `COGS`!"
                )

        best_val = peers["lowest_pb_value_stocks"][0] if peers["lowest_pb_value_stocks"] else {"id": 13, "ticker": "WFC", "pb": 1.0, "roce_pct": 12.0, "rating": "AA"}
        best_roce = peers["highest_roce_momentum_stocks"][0] if peers["highest_roce_momentum_stocks"] else {"id": 321, "ticker": "C321", "pb": 1.2, "roce_pct": 18.0, "rating": "AA"}
        return (
            f"💡 **Paimon phân tích chiến lược cho Aether tại `{ctx['date']}` (Ví tiền mặt: `${wallet['cash_usd']:,.0f}`, Tài sản ròng: `${wallet['net_worth_usd']:,.0f}`):**\n\n"
            f"1. **Đánh giá thực thể đang xem (`#{viewed['id']} {viewed['ticker']} - {viewed['name']}`):**\n"
            f"   - **Phân tích Cơ bản (Fundamental):** Chế độ `{viewed['regime']}`, Hạng tín nhiệm **`{viewed['credit_rating']}`**, Giá cổ phiếu **`${viewed['stock_price']}`** so với Giá trị sổ sách **`${viewed['book_value_per_share']}/cp`** (`P/B = {viewed['pb_ratio']}x`), Tỷ suất sinh lời **`ROCE = {viewed['roce_pct']}%`**, `EPS = ${viewed['annual_eps']}`.\n"
            f"   - **Phân tích Kỹ thuật (Technical):** Biểu đồ `{chart['label']}` đang có mẫu nến **`{chart['pattern']}`**, `RSI(14) = {chart['rsi14']}`, `MA7 = ${chart.get('sma7_latest')}` vs `MA20 = ${chart.get('sma20_latest')}`.\n"
            f"2. **So sánh với các cơ hội hàng đầu trên sàn lúc này:**\n"
            f"   - **Cổ phiếu rẻ nhất theo tài sản (`Low P/B`):** `#{best_val['id']} {best_val['ticker']}` (`P/B = {best_val['pb']}x`, hạng `{best_val['rating']}`).\n"
            f"   - **Cổ phiếu sinh lời mạnh nhất (`High ROCE`):** `#{best_roce['id']} {best_roce['ticker']}` (`ROCE = {best_roce['roce_pct']}%`, hạng `{best_roce['rating']}`).\n"
            f"3. **Bối cảnh Vĩ mô (`GDP = {macro['gdp_growth_pct']}%`, `CPI = {macro['cpi_inflation_pct']}%`, `Prime Rate = {macro['prime_rate_pct']}%`):**\n"
            f"   - Bài học hiện tại của cậu là **{ctx['current_lesson'].get('quest_title', '')}**: {ctx['current_lesson'].get('task_instruction', '')}"
        )

    def ask_paimon_tutor(
        self,
        question: str,
        app_state: Any,
        active_entity_id: int = 1,
        acting_as_id: int = 1,
        selected_firm_id: int = 1,
        chart_symbol: str = "SELECTED_CORP",
        active_module_id: Optional[str] = None,
        active_quest_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calls gpt-6-luna with Paimon's persona and full live game/OHLCV/3x3 telemetry context.
        Logs token usage and falls back gracefully if offline.
        """
        q_clean = (question or "").strip()
        if not q_clean:
            q_clean = "Paimon ơi, giải thích cho tôi màn hình hiện tại, cây nến trên biểu đồ và bước tiếp theo nên làm gì nhé!"

        live_ctx = self.build_live_telemetry_context(
            app_state=app_state,
            active_entity_id=active_entity_id,
            acting_as_id=acting_as_id,
            selected_firm_id=selected_firm_id,
            chart_symbol=chart_symbol,
            active_module_id=active_module_id,
            active_quest_id=active_quest_id,
        )

        sys_prompt = (
            "Bạn là PAIMON — người bạn đồng hành nhí nhảnh, thông thái và là Huấn luyện viên Kinh tế, Đọc Nến Nhật (OHLCV) & "
            "Đầu tư Phố Wall kiêm Quản trị Chuỗi cung ứng của Aether (#1) trong game EagleCapitalEngine v2.0 (hợp nhất Wall Street Raider v10 + Capitalism Lab v11).\n"
            "NGUYÊN TẮC TRẢ LỜI BẮT BUỘC:\n"
            "1. Xưng 'Paimon' và gọi người chơi là 'Aether' (hoặc 'cậu'). Giữ giọng điệu nhiệt tình, đáng yêu kiểu Paimon (thích Mora/kho báu) nhưng khi phân tích kinh tế, kế toán, đọc nến Nhật OHLCV, chỉ báo RSI/MA/Bollinger và mặt bằng 3x3 thì CỰC KỲ SẮC SẢO, DỄ HIỂU cho người mới bắt đầu.\n"
            "2. BẮT BUỘC trích dẫn chính xác các con số thực tế từ JSON `LIVE_TELEMETRY_CONTEXT` đính kèm (ví dụ: giá đóng cửa/mở cửa/râu nến hiện tại, RSI(14), mẫu hình nến, P/B, ROCE%, tiền mặt của Aether, thông số mặt bằng 3x3 của Firm đang chọn, vĩ mô GDP/CPI/Prime Rate).\n"
            "3. Giải thích rõ 'TẠI SAO' (Decision-making reason): Kết hợp giữa Phân tích Cơ bản (P/B, ROCE, Credit Rating, COGS Shield) và Phân tích Kỹ thuật (Nến, râu nến, Volume, MA7/MA20, Bollinger, RSI) để Aether hiểu bản chất.\n"
            "4. Trình bày gọn gàng bằng gạch đầu dòng, dài khoảng 140 - 260 từ tiếng Việt."
        )

        # Keep last 4 chat messages for continuity
        recent_history = self.progress_state.get("chat_history", [])[-4:]
        messages: List[Dict[str, str]] = [{"role": "system", "content": sys_prompt}]
        for h in recent_history:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": str(h["content"])[:600]})

        user_payload = (
            f"LIVE_TELEMETRY_CONTEXT:\n{json.dumps(live_ctx, ensure_ascii=False, separators=(',', ':'))}\n\n"
            f"CÂU HỎI CỦA AETHER: {q_clean}"
        )
        messages.append({"role": "user", "content": user_payload})

        t0 = time.perf_counter()
        answer_text = ""
        model_used = self.model_name
        p_tok = 0
        c_tok = 0
        cost_usd = 0.0
        used_live_api = False

        try:
            req_body = json.dumps({
                "model": self.model_name,
                "messages": messages,
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=req_body,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=22) as resp:
                raw_resp = json.loads(resp.read().decode("utf-8"))
            answer_text = raw_resp["choices"][0]["message"]["content"].strip()
            model_used = raw_resp.get("model", self.model_name)
            usage = raw_resp.get("usage", {})
            p_tok = int(usage.get("prompt_tokens", 0))
            c_tok = int(usage.get("completion_tokens", 0))
            cost_usd = (p_tok / 1_000_000.0) * INPUT_COST_PER_1M + (c_tok / 1_000_000.0) * OUTPUT_COST_PER_1M
            used_live_api = True
        except Exception:
            answer_text = self._build_deterministic_paimon_fallback(q_clean, live_ctx)
            model_used = "paimon-deterministic-engine"

        latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        # Update chat history & telemetry counters
        self.progress_state.setdefault("chat_history", []).append({"role": "user", "content": q_clean})
        self.progress_state["chat_history"].append({
            "role": "assistant",
            "content": answer_text,
            "model": model_used,
            "latency_ms": latency_ms,
        })
        if len(self.progress_state["chat_history"]) > 30:
            self.progress_state["chat_history"] = self.progress_state["chat_history"][-30:]

        if used_live_api:
            self.progress_state["total_chat_calls"] = int(self.progress_state.get("total_chat_calls", 0)) + 1
            self.progress_state["total_chat_tokens"] = int(self.progress_state.get("total_chat_tokens", 0)) + p_tok + c_tok
            self.progress_state["total_chat_cost_usd"] = round(
                float(self.progress_state.get("total_chat_cost_usd", 0.0)) + cost_usd, 6
            )
        self.save_progress()

        call_log = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "question": q_clean,
            "model": model_used,
            "used_live_api": used_live_api,
            "latency_ms": latency_ms,
            "prompt_tokens": p_tok,
            "completion_tokens": c_tok,
            "cost_usd": round(cost_usd, 6),
            "active_quest_id": live_ctx["current_lesson"].get("quest_id"),
            "viewed_entity_id": live_ctx["viewed_entity"]["id"],
            "chart_symbol": live_ctx["ohlcv_chart_telemetry"]["symbol_key"],
            "answer_preview": answer_text[:220],
        }
        try:
            with open(PAIMON_CHAT_LOG_PATH, "a", encoding="utf-8") as lf:
                lf.write(json.dumps(call_log, ensure_ascii=False) + "\n")
        except Exception:
            pass

        return {
            "ok": True,
            "question": q_clean,
            "answer": answer_text,
            "model": model_used,
            "used_live_api": used_live_api,
            "latency_ms": latency_ms,
            "prompt_tokens": p_tok,
            "completion_tokens": c_tok,
            "estimated_cost_usd": round(cost_usd, 6),
            "live_context_summary": {
                "date": live_ctx["date"],
                "viewed_ticker": live_ctx["viewed_entity"]["ticker"],
                "viewed_price": live_ctx["viewed_entity"]["stock_price"],
                "viewed_pb": live_ctx["viewed_entity"]["pb_ratio"],
                "chart_symbol": live_ctx["ohlcv_chart_telemetry"]["label"],
                "chart_pattern": live_ctx["ohlcv_chart_telemetry"]["pattern"],
                "chart_rsi14": live_ctx["ohlcv_chart_telemetry"]["rsi14"],
                "selected_firm_id": live_ctx["selected_caplab_firm"].get("firm_id"),
            },
            "progress": self.progress_state,
        }

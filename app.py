from pathlib import Path
from datetime import datetime, timezone
import html
import json
import re
import sqlite3
import unicodedata

import joblib
import pandas as pd
import streamlit as st


ROOT = Path(__file__).parent
MODEL_PATH = ROOT / "models" / "scam_classifier.joblib"
REPORT_PATH = ROOT / "reports" / "evaluation.json"
FEEDBACK_PATH = ROOT / "reports" / "feedback.sqlite"
ABSTAIN_MARGIN = 0.20

st.set_page_config(page_title="Nhận diện tin nhắn lừa đảo", page_icon="🛡️", layout="wide")
st.markdown(f"<style>{(ROOT / 'assets' / 'web.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


@st.cache_resource
def load_artifacts():
    if not MODEL_PATH.exists():
        return None, None
    model = joblib.load(MODEL_PATH)
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8")) if REPORT_PATH.exists() else None
    return model, report


def init_metrics_storage():
    FEEDBACK_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(FEEDBACK_PATH) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS feedback_counts (vote TEXT PRIMARY KEY, total INTEGER NOT NULL)")
        connection.execute("""CREATE TABLE IF NOT EXISTS analysis_counts (
            channel TEXT NOT NULL, outcome TEXT NOT NULL, total INTEGER NOT NULL,
            PRIMARY KEY(channel, outcome))""")
        connection.execute("""CREATE TABLE IF NOT EXISTS app_settings (
            name TEXT PRIMARY KEY, value TEXT NOT NULL)""")
        connection.execute("""CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
            channel TEXT NOT NULL, outcome TEXT NOT NULL, message TEXT NOT NULL)""")
        connection.execute("""CREATE TABLE IF NOT EXISTS review_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
            channel TEXT NOT NULL, message TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', reviewed_label INTEGER)""")


def record_analysis(channel, outcome):
    """Persist aggregate counts only; no message text or per-message record is stored."""
    init_metrics_storage()
    with sqlite3.connect(FEEDBACK_PATH) as connection:
        connection.execute(
            "INSERT INTO analysis_counts(channel, outcome, total) VALUES (?, ?, 1) "
            "ON CONFLICT(channel, outcome) DO UPDATE SET total = total + 1",
            (channel, outcome),
        )


def record_feedback(vote):
    init_metrics_storage()
    with sqlite3.connect(FEEDBACK_PATH) as connection:
        connection.execute(
            "INSERT INTO feedback_counts(vote, total) VALUES (?, 1) "
            "ON CONFLICT(vote) DO UPDATE SET total = total + 1", (vote,)
        )


def get_history_preference():
    if not FEEDBACK_PATH.exists():
        return False
    with sqlite3.connect(FEEDBACK_PATH) as connection:
        try:
            row = connection.execute("SELECT value FROM app_settings WHERE name = 'history_enabled'").fetchone()
            return bool(row and row[0] == "true")
        except sqlite3.OperationalError:
            return False


def save_history_preference():
    init_metrics_storage()
    value = "true" if st.session_state.get("history_enabled", False) else "false"
    with sqlite3.connect(FEEDBACK_PATH) as connection:
        connection.execute(
            "INSERT INTO app_settings(name, value) VALUES ('history_enabled', ?) "
            "ON CONFLICT(name) DO UPDATE SET value = excluded.value", (value,)
        )


def save_history(message, channel, outcome):
    init_metrics_storage()
    created_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    with sqlite3.connect(FEEDBACK_PATH) as connection:
        connection.execute(
            "INSERT INTO analysis_history(created_at, channel, outcome, message) VALUES (?, ?, ?, ?)",
            (created_at, channel, outcome, message),
        )


def read_history(limit=50):
    if not FEEDBACK_PATH.exists():
        return []
    with sqlite3.connect(FEEDBACK_PATH) as connection:
        try:
            return connection.execute(
                "SELECT id, created_at, channel, outcome, message FROM analysis_history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        except sqlite3.OperationalError:
            return []


def delete_history():
    if FEEDBACK_PATH.exists():
        with sqlite3.connect(FEEDBACK_PATH) as connection:
            connection.execute("DELETE FROM analysis_history")


def redact_sensitive_text(text):
    """Mask common direct identifiers before a sample enters the local review queue."""
    text = re.sub(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[EMAIL]", text, flags=re.I)
    text = re.sub(r"https?://\S+|www\.\S+", "[LINK]", text, flags=re.I)
    text = re.sub(r"(?<!\w)(?:\+?84|0)(?:[\s().-]?\d){8,10}(?!\w)", "[PHONE]", text)
    text = re.sub(r"(?<!\w)\d{8,}(?!\w)", "[NUMBER]", text)
    text = re.sub(r"(?i)(\b(?:otp|mã xác thực|ma xac thuc|mã pin|ma pin)\s*[:：]?\s*)\d{4,8}\b", r"\1[CODE]", text)
    return text


def add_review_sample(channel, message):
    init_metrics_storage()
    created_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    with sqlite3.connect(FEEDBACK_PATH) as connection:
        cursor = connection.execute(
            "INSERT INTO review_queue(created_at, channel, message) VALUES (?, ?, ?)",
            (created_at, channel, message),
        )
        return cursor.lastrowid


def read_review_queue(status="pending"):
    if not FEEDBACK_PATH.exists():
        return []
    with sqlite3.connect(FEEDBACK_PATH) as connection:
        try:
            if status == "approved":
                return connection.execute(
                    "SELECT id, created_at, channel, message, status, reviewed_label FROM review_queue WHERE status = 'approved' ORDER BY id DESC"
                ).fetchall()
            return connection.execute(
                "SELECT id, created_at, channel, message, status, reviewed_label FROM review_queue WHERE status = ? ORDER BY id DESC",
                (status,),
            ).fetchall()
        except sqlite3.OperationalError:
            return []


def update_review_status(sample_id, status, reviewed_label=None):
    with sqlite3.connect(FEEDBACK_PATH) as connection:
        connection.execute(
            "UPDATE review_queue SET status = ?, reviewed_label = ? WHERE id = ?",
            (status, reviewed_label, sample_id),
        )


def render_highlighted_message(text):
    """Highlight signal phrases in escaped user text; no raw HTML from input is trusted."""
    patterns = [
        r"https?://[^\s<>]+|www\.[^\s<>]+|\b[\w-]+\.(?:com|vn|net|org|top|info)\b",
        r"\b(?:otp|mã\s*xác\s*thực|ma\s*xac\s*thuc|mật\s*khẩu|mat\s*khau|đăng\s*nhập|dang\s*nhap|mã\s*pin|ma\s*pin)\b",
        r"\b(?:chuyển\s*tiền|chuyen\s*tien|nộp\s*phí|nop\s*phi|thanh\s*toán\s*ngay|thanh\s*toan\s*ngay|chuyển\s*khoản|chuyen\s*khoan)\b",
        r"\b(?:trúng\s*thưởng|trung\s*thuong|trúng\s*giải|trung\s*giai|nhận\s*quà|nhan\s*qua|quà\s*tặng|qua\s*tang|hoàn\s*tiền|hoan\s*tien)\b",
        r"\b(?:khẩn\s*cấp|khan\s*cap|ngay\s*lập\s*tức|ngay\s*lap\s*tuc|khóa\s*tài\s*khoản|khoa\s*tai\s*khoan|tạm\s*khóa|tam\s*khoa|tuyển\s*cộng\s*tác\s*viên|tuyen\s*cong\s*tac\s*vien|ngân\s*hàng|ngan\s*hang|vietcombank|techcombank|agribank|bidv|vpbank|tpbank)\b",
    ]
    combined = re.compile("|".join(f"(?:{pattern})" for pattern in patterns), re.I)
    pieces = []
    last = 0
    for match in combined.finditer(text):
        pieces.append(html.escape(text[last:match.start()]))
        pieces.append(f'<mark style="background:#ffe08a;color:#342600;padding:2px 4px;border-radius:4px">{html.escape(match.group(0))}</mark>')
        last = match.end()
    pieces.append(html.escape(text[last:]))
    return "<div style='white-space:pre-wrap;line-height:1.8;padding:12px;border:1px solid #7775;border-radius:10px'>" + "".join(pieces) + "</div>"


def read_usage_metrics():
    result = {"analyses": {}, "feedback": {"useful": 0, "incorrect": 0}}
    if not FEEDBACK_PATH.exists():
        return result
    with sqlite3.connect(FEEDBACK_PATH) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS feedback_counts (vote TEXT PRIMARY KEY, total INTEGER NOT NULL)")
        connection.execute("""CREATE TABLE IF NOT EXISTS analysis_counts (
            channel TEXT NOT NULL, outcome TEXT NOT NULL, total INTEGER NOT NULL,
            PRIMARY KEY(channel, outcome))""")
        result["analyses"] = {
            (channel, outcome): total
            for channel, outcome, total in connection.execute(
                "SELECT channel, outcome, total FROM analysis_counts"
            )
        }
        result["feedback"].update(dict(connection.execute("SELECT vote, total FROM feedback_counts")))
    return result


def explain_linear_prediction(model, text, limit=5, direction=1):
    """Show the strongest linear features toward one class; these are clues, not proof."""
    try:
        features = model.named_steps["features"]
        classifier = model.named_steps["classifier"]
        vector = features.transform([text])
        names = features.get_feature_names_out()
        contribution = vector.toarray()[0] * classifier.coef_[0] * direction
        indices = contribution.argsort()[::-1]
        results = []
        seen = set()
        for idx in indices:
            value = float(contribution[idx])
            term = names[idx].split("__", 1)[-1]
            if value <= 0 or not term.strip() or term in {"[PHONE]", "[NUMBER]", "[TIME]", "[DATE]", "[MONEY]"}:
                continue
            if term not in seen:
                results.append((term, value))
                seen.add(term)
            if len(results) == limit:
                break
        return results
    except Exception:
        return []


def find_signals(text):
    normalized = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    checks = [
        ("Nhắc tới ngân hàng/dịch vụ tài chính", r"\b(ngan hang|vietcombank|techcombank|agribank|bidv|mb bank|vpbank|acb|tpbank|vcb digibank)\b"),
        ("Yêu cầu mã OTP hoặc thông tin đăng nhập", r"\b(otp|ma xac thuc|mat khau|dang nhap|ma pin)\b"),
        ("Hứa trúng thưởng, quà tặng hoặc hoàn tiền", r"\b(trung thuong|trung giai|nhan qua|qua tang|hoan tien)\b"),
        ("Thúc giục hoặc đe dọa khóa tài khoản", r"(khan cap|ngay lap tuc|trong vong \d+|khoa tai khoan|tam khoa|bi phat)"),
        ("Đề nghị chuyển tiền hoặc nộp phí", r"(chuyen tien|nop phi|thanh toan ngay|phi xac minh|chuyen khoan)"),
        ("Dụ việc làm/đầu tư lợi nhuận cao", r"(viec nhe luong cao|thu nhap cao|loi nhuan cao|bao dam loi nhuan|tuyen cong tac vien)"),
        ("Có đường dẫn cần kiểm tra", r"(?:https?://|www\.|\b[a-z0-9-]+\.(?:com|vn|net|org|top|info)\b)"),
    ]
    return [name for name, pattern in checks if re.search(pattern, normalized, re.I)]


def classify_message(model, report, text):
    margin = float(model.decision_function([text])[0])
    threshold = float((report or {}).get("decision_threshold", {}).get("value", 0.0))
    predicted_scam = margin >= threshold
    signals = find_signals(text)
    too_short = len(text.split()) <= 3 and not signals
    borderline_without_signals = predicted_scam and not signals and margin < threshold + ABSTAIN_MARGIN
    if too_short:
        outcome = "insufficient"
    elif borderline_without_signals:
        outcome = "review"
    else:
        outcome = "scam" if predicted_scam else "normal"
    return {
        "outcome": outcome,
        "margin": margin,
        "threshold": threshold,
        "signals": signals,
    }


def safety_steps(signals):
    steps = ["Đừng bấm liên kết, gọi số điện thoại trong tin nhắn hoặc cài ứng dụng theo hướng dẫn từ người gửi."]
    if any("OTP" in signal or "đăng nhập" in signal for signal in signals):
        steps.append("Không cung cấp OTP, mật khẩu hoặc mã PIN cho bất kỳ ai, kể cả người tự xưng là nhân viên ngân hàng/cơ quan nhà nước.")
    if any("ngân hàng" in signal or "chuyển tiền" in signal or "nộp phí" in signal for signal in signals):
        steps.append("Tự mở ứng dụng ngân hàng hoặc gọi số trên thẻ/website chính thức để xác minh; không chuyển tiền để “xác minh” hay nhận thưởng.")
    if any("đường dẫn" in signal for signal in signals):
        steps.append("Kiểm tra tên miền cẩn thận; an toàn nhất là tự nhập địa chỉ website chính thức thay vì mở liên kết nhận được.")
    if any("trúng thưởng" in signal or "việc làm" in signal for signal in signals):
        steps.append("Cảnh giác với yêu cầu nộp phí trước để nhận quà, việc làm hoặc lợi nhuận được cam kết.")
    if any("Thúc giục" in signal for signal in signals):
        steps.append("Không hành động vì bị thúc ép. Tạm dừng và xác minh qua kênh chính thức bạn tự tìm được.")
    if len(steps) == 1:
        steps.append("Nếu chưa chắc, hỏi người gửi qua một kênh liên lạc khác mà bạn đã biết là đáng tin cậy.")
    return steps


model, report = load_artifacts()
usage = read_usage_metrics()
st.markdown("""
<div class="hero">
  <div class="eyebrow">TIN NHẮN TIẾNG VIỆT · CÔNG CỤ HỖ TRỢ XÁC MINH</div>
  <h1>Kiểm tra tin nhắn.<br><span>Nhận biết dấu hiệu lừa đảo.</span></h1>
  <p>Phân tích nội dung, tìm hiểu kết quả và chọn bước xác minh phù hợp.</p>
  <div class="hero-meta"><span>Xử lý trên máy này</span><span>Kiểm định trên SMS</span><span>Zalo / email: thử nghiệm</span></div>
</div>
""", unsafe_allow_html=True)

analysis_tab, batch_tab, overview_tab, guide_tab = st.tabs(["Phân tích tin nhắn", "Kiểm tra nhiều mẫu", "Tổng quan", "Hướng dẫn & an toàn"])

examples = {
    "Lời chào ngắn": "Xin chào, bạn khỏe không?",
    "Tin nhắn có liên kết": "Đơn hàng đang chờ xác nhận. Vui lòng truy cập https://example.invalid/verify để cập nhật thông tin.",
    "Tin nhắn yêu cầu OTP": "Chúc mừng bạn trúng thưởng! Gửi mã OTP để nhận quà ngay hôm nay.",
    "Tin nhắn bình thường": "Chiều nay mình ghé đón bạn lúc 6 giờ nhé.",
}
demo_scenarios = [
    ("Trao đổi bạn bè", "Bình thường", "Tối nay mình gửi bạn tài liệu bài tập nhé."),
    ("Hẹn nhóm học", "Bình thường", "Nhóm mình học lúc 3 giờ chiều ở thư viện nha."),
    ("Báo giao hàng", "Bình thường", "Đơn hàng của bạn đã được giao thành công. Cảm ơn bạn đã mua sắm."),
    ("Thông báo giao dịch an toàn", "Bình thường", "Giao dịch thanh toán tại cửa hàng đã hoàn tất. Nếu không nhận ra giao dịch, tự mở ứng dụng ngân hàng để kiểm tra."),
    ("Nhắc bảo mật OTP", "Bình thường", "Ngân hàng không bao giờ yêu cầu bạn cung cấp OTP. Hãy giữ kín mã xác thực và chỉ liên hệ tổng đài chính thức."),
    ("Giả mạo khóa tài khoản", "Lừa đảo", "Tài khoản ngân hàng của bạn sẽ bị khóa trong hôm nay. Bấm link để xác minh thông tin ngay."),
    ("Báo trúng thưởng", "Lừa đảo", "Chúc mừng bạn đã trúng thưởng. Nộp phí nhận quà ngay hôm nay."),
    ("Dụ việc làm online", "Lừa đảo", "Tuyển cộng tác viên làm tại nhà, thu nhập cao. Chuyển phí hồ sơ để nhận nhiệm vụ."),
    ("Giả mạo phí giao hàng", "Lừa đảo", "Đơn hàng đang bị giữ. Thanh toán phí giao hàng tại https://giaohang.example.invalid để nhận ngay."),
    ("Mạo danh người thân", "Lừa đảo", "Con đang cần tiền gấp, chuyển khoản vào tài khoản này giúp con, đừng gọi lại."),
    ("Dụ đầu tư lợi nhuận", "Lừa đảo", "Đầu tư hôm nay, cam kết lợi nhuận cao và hoàn vốn trong 7 ngày. Nhắn tin để tham gia."),
    ("Dụ cài ứng dụng", "Lừa đảo", "Cài ứng dụng này để nhận quà và cấp quyền truy cập điện thoại để xác minh."),
]
if "message_input" not in st.session_state:
    st.session_state.message_input = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if st.session_state.get("analysis_logic_version") != 2:
    st.session_state.analysis_result = None
    st.session_state.analysis_logic_version = 2
if "history_enabled" not in st.session_state:
    st.session_state.history_enabled = get_history_preference()


def load_example():
    st.session_state.message_input = examples.get(st.session_state.get("example_choice", ""), "")


def clear_message():
    st.session_state.message_input = ""
    st.session_state.analysis_result = None


def start_review_form():
    current = st.session_state.get("analysis_result") or {}
    st.session_state.review_message = redact_sensitive_text(current.get("message", ""))
    st.session_state.review_form_open = True


with analysis_tab:
    st.info("Mô hình được huấn luyện/đánh giá trên SMS tiếng Việt. Zalo và email chưa có kiểm định riêng; kết quả ở các kênh đó chỉ nên xem là gợi ý.")
    if model is None:
        st.error("Chưa có mô hình. Hãy chạy `python train.py` trong thư mục dự án trước.")
    compose, settings = st.columns([2.3, 1], gap="large")
    with settings:
        with st.container(border=True):
            st.markdown("### Tùy chọn phân tích")
            channel = st.selectbox("Nguồn tin nhắn", ["SMS", "Zalo", "Email"])
            st.toggle(
                "Lưu lịch sử trên máy", key="history_enabled",
                help="Lưu nội dung và kết quả cục bộ cho đến khi bạn xóa lịch sử.",
                on_change=save_history_preference,
            )
            if st.session_state.history_enabled:
                st.caption("Đang lưu nội dung. Xem và xóa lịch sử tại Tổng quan.")
            else:
                st.caption("Không lưu các tin mới vào lịch sử. Lịch sử cũ, nếu có, vẫn nằm trong Tổng quan.")
            st.divider()
            st.markdown("**Trước khi kiểm tra**")
            st.caption("Ẩn tên, số tài khoản, mật khẩu và mã OTP thật trong nội dung.")
            st.markdown("**Cách đọc kết quả**")
            st.caption("Cảnh báo là gợi ý để xác minh. Tin thuộc nhóm bình thường vẫn có thể tiềm ẩn rủi ro.")
    with compose:
        st.markdown("### Nội dung cần kiểm tra")
        st.caption("Dán toàn bộ tin nhắn để hệ thống có thêm ngữ cảnh.")
        st.selectbox("Thử nhanh một ví dụ", ["Chọn ví dụ…", *examples.keys()], key="example_choice", on_change=load_example)
        st.text_area("Dán nội dung SMS hoặc tin nhắn", height=210, placeholder="Nhập hoặc dán tin nhắn tại đây…", key="message_input")
        run_col, clear_col = st.columns([3, 1])
        analyze = run_col.button("Phân tích tin nhắn", type="primary", width="stretch", disabled=(model is None))
        clear_col.button("Xóa nội dung", on_click=clear_message, width="stretch")
        st.caption("Kết quả hỗ trợ tham khảo, không xác nhận danh tính hay ý định của người gửi.")

    if analyze:
        cleaned_text = st.session_state.message_input.strip()
        if not cleaned_text:
            st.info("Hãy nhập nội dung tin nhắn trước khi phân tích.")
            st.session_state.analysis_result = None
        else:
            prediction = classify_message(model, report, cleaned_text)
            outcome = prediction["outcome"]
            record_analysis(channel, outcome)
            st.session_state.analysis_result = {
                "channel": channel,
                "outcome": outcome,
                "message": cleaned_text,
                "margin": prediction["margin"],
                "threshold": prediction["threshold"],
                "signals": prediction["signals"],
                "scam_terms": explain_linear_prediction(model, cleaned_text, direction=1),
                "normal_terms": explain_linear_prediction(model, cleaned_text, direction=-1),
            }
            st.session_state.last_feedback = None
            st.session_state.review_form_open = False
            if st.session_state.history_enabled:
                save_history(cleaned_text, channel, outcome)
            usage = read_usage_metrics()

    result = st.session_state.analysis_result
    if not result:
        st.markdown('<div class="empty-result"><strong>Kết quả sẽ xuất hiện tại đây</strong><p>Nhập nội dung hoặc chọn một ví dụ, sau đó bấm Phân tích tin nhắn.</p></div>', unsafe_allow_html=True)
    if result:
        st.markdown("### Kết quả")
        if result["channel"] != "SMS":
            st.warning(f"Kênh {result['channel']} chưa được kiểm định riêng; hãy xem kết quả như gợi ý, không phải kết luận.")
        if result["outcome"] == "insufficient":
            st.info("**Chưa đủ ngữ cảnh để phân loại.** Tin nhắn quá ngắn và không có dấu hiệu cụ thể. Hãy xem thêm nội dung trước/sau hoặc xác minh người gửi.")
        elif result["outcome"] == "review":
            st.warning("**Cần xem xét thêm.** Điểm mô hình chỉ nhỉnh hơn ngưỡng cảnh báo và không có dấu hiệu từ khóa độc lập. Chưa đủ căn cứ để kết luận tin này là lừa đảo.")
        elif result["outcome"] == "scam":
            st.error("**Có dấu hiệu rác/lừa đảo.** Tạm dừng thao tác và xác minh qua kênh chính thức.")
        else:
            st.success("**Mô hình xếp nội dung vào nhóm bình thường.** Nhãn này không đảm bảo tin nhắn an toàn.")

        st.markdown("**Dấu hiệu được tìm thấy trong nội dung**")
        st.markdown(render_highlighted_message(result["message"]), unsafe_allow_html=True)

        st.markdown("#### Vì sao hệ thống đưa ra gợi ý này?")
        st.caption(f"Điểm SVM {result['margin']:.3f}; ngưỡng cảnh báo {result['threshold']:.3f}. Điểm này không phải xác suất. Các cụm từ bên dưới cho biết đặc trưng nào tác động tới điểm, không chứng minh ý định người gửi.")
        explain_left, explain_right = st.columns(2)
        with explain_left:
            st.markdown("**Kéo về phía rác/lừa đảo**")
            if result["scam_terms"]:
                for term, _ in result["scam_terms"]:
                    st.markdown(f"- `{term}`")
            else:
                st.caption("Không có cụm từ nổi bật theo hướng này.")
        with explain_right:
            st.markdown("**Kéo về phía bình thường**")
            if result["normal_terms"]:
                for term, _ in result["normal_terms"]:
                    st.markdown(f"- `{term}`")
            else:
                st.caption("Không có cụm từ nổi bật theo hướng này.")

        st.markdown("#### Dấu hiệu phát hiện và bước nên làm")
        signals = result["signals"]
        if signals:
            for signal in signals:
                st.markdown(f"- Phát hiện: **{signal}**")
        else:
            st.write("Không khớp dấu hiệu từ khóa đã cấu hình; điều này không xác nhận tin nhắn an toàn.")
        for step in safety_steps(signals):
            st.markdown(f"- {step}")

        st.markdown("**Kết quả này có hữu ích không?** Chỉ lưu bộ đếm tổng hợp cục bộ; không lưu tin nhắn hoặc nhãn riêng của tin.")
        f1, f2 = st.columns(2)
        if f1.button("Kết quả phù hợp", width="stretch"):
            record_feedback("useful")
            st.session_state.last_feedback = "useful"
            usage = read_usage_metrics()
        if f2.button("Kết quả chưa đúng", width="stretch"):
            record_feedback("incorrect")
            st.session_state.last_feedback = "incorrect"
            start_review_form()
            usage = read_usage_metrics()
        if st.session_state.get("last_feedback"):
            st.success("Cảm ơn bạn. Phản hồi chỉ cập nhật thống kê tổng hợp; chưa tự động huấn luyện lại mô hình.")
        st.caption(f"Phản hồi trên máy này: {usage['feedback']['useful']} phù hợp · {usage['feedback']['incorrect']} chưa đúng.")
        if st.session_state.get("review_form_open"):
            st.warning("Mẫu sẽ được lưu vào hàng chờ cục bộ để bạn duyệt. Một số dữ liệu thường gặp đã được che tự động; hãy kiểm tra và xóa tên, địa chỉ hoặc thông tin cá nhân còn sót trước khi gửi.")
            with st.form("review_sample_form"):
                st.text_area("Nội dung đã ẩn danh (có thể sửa)", key="review_message", height=140)
                consent = st.checkbox("Tôi đã kiểm tra nội dung và muốn lưu mẫu này vào hàng chờ duyệt trên máy.")
                submitted = st.form_submit_button("Gửi vào hàng chờ duyệt", type="primary")
            if submitted:
                reviewed_text = redact_sensitive_text(st.session_state.get("review_message", "")).strip()
                if not consent:
                    st.error("Hãy xác nhận đã kiểm tra nội dung trước khi gửi mẫu.")
                elif len(reviewed_text) < 4:
                    st.error("Mẫu quá ngắn để đưa vào hàng chờ.")
                else:
                    add_review_sample(result["channel"], reviewed_text)
                    st.session_state.review_form_open = False
                    st.success("Đã thêm mẫu đã ẩn danh vào hàng chờ. Mẫu chưa được đưa vào huấn luyện.")
                    st.rerun()

    with st.expander("Thử thêm 12 kịch bản minh họa để trao đổi với giáo viên"):
        st.caption("Đây là ví dụ tự soạn, nhãn mong đợi chỉ để thảo luận, không phải dữ liệu kiểm định. Chạy thử không làm thay đổi thống kê, lịch sử hay mô hình.")
        if st.button("Chạy bộ kịch bản", disabled=(model is None), key="run_demo_scenarios"):
            scenario_rows = []
            for name, expected, scenario_text in demo_scenarios:
                prediction = classify_message(model, report, scenario_text)
                outcome = prediction["outcome"]
                outcome_label = {
                    "scam": "Cảnh báo",
                    "normal": "Bình thường",
                    "review": "Cần xem xét",
                    "insufficient": "Chưa đủ ngữ cảnh",
                }[outcome]
                # The model UI says "Cảnh báo" while the illustrative expected label
                # says "Lừa đảo". Compare their meaning, not the display wording.
                comparable_expected = "Cảnh báo" if expected == "Lừa đảo" else expected
                exact_match = outcome_label == comparable_expected
                scenario_rows.append({
                    "Kịch bản": name,
                    "Nội dung mẫu": scenario_text,
                    "Nhãn mong đợi (minh họa)": expected,
                    "Kết quả hệ thống": outcome_label,
                    "Khớp nhãn": "Có" if exact_match else "Không",
                    "Dấu hiệu từ khóa": "; ".join(prediction["signals"]) or "Không thấy",
                    "Điểm SVM": round(prediction["margin"], 3),
                })
            st.dataframe(pd.DataFrame(scenario_rows), hide_index=True, width="stretch")
            matches = sum(row["Khớp nhãn"] == "Có" for row in scenario_rows)
            st.write(f"Khớp nhãn minh họa: **{matches}/{len(scenario_rows)}**. Không dùng con số này làm độ chính xác của mô hình.")
            false_alerts = [row["Kịch bản"] for row in scenario_rows if row["Nhãn mong đợi (minh họa)"] == "Bình thường" and row["Kết quả hệ thống"] == "Cảnh báo"]
            missed_scams = [row["Kịch bản"] for row in scenario_rows if row["Nhãn mong đợi (minh họa)"] == "Lừa đảo" and row["Kết quả hệ thống"] == "Bình thường"]
            uncertain = [row["Kịch bản"] for row in scenario_rows if row["Kết quả hệ thống"] in {"Cần xem xét", "Chưa đủ ngữ cảnh"}]
            if false_alerts:
                st.error("Cảnh báo nhầm trong ví dụ bình thường: " + ", ".join(false_alerts))
            if missed_scams:
                st.warning("Ví dụ lừa đảo bị xếp bình thường: " + ", ".join(missed_scams))
            if uncertain:
                st.info("Chưa có kết luận rõ: " + ", ".join(uncertain))


    if report:
        with st.expander("Chất lượng mô hình trên tập SMS kiểm tra"):
            metrics = report.get("metrics", {})
            m1, m2, m3 = st.columns(3)
            m1.metric("Macro F1", f"{metrics.get('macro_f1', 0):.3f}")
            m2.metric("Precision cảnh báo", f"{metrics.get('scam_precision', 0):.3f}")
            m3.metric("Recall lừa đảo", f"{metrics.get('scam_recall', 0):.3f}")
            st.caption(f"Tập SMS kiểm tra gồm {report.get('test_size', '—'):,} mẫu. Đây là đánh giá mô hình, không phải số liệu sử dụng của bạn.")
            matrix = report.get("confusion_matrix", [])
            if len(matrix) == 2 and all(len(row) == 2 for row in matrix):
                st.markdown("**Ma trận nhầm lẫn** · hàng là nhãn thật, cột là dự đoán")
                st.dataframe(pd.DataFrame(
                    [[matrix[0][0], matrix[0][1]], [matrix[1][0], matrix[1][1]]],
                    index=["Thật: bình thường", "Thật: rác/lừa đảo"],
                    columns=["Dự đoán: bình thường", "Dự đoán: rác/lừa đảo"],
                ), width="stretch")
                st.caption(f"Trong tập này, có {matrix[0][1]} tin bình thường bị cảnh báo nhầm và {matrix[1][0]} tin lừa đảo bị bỏ sót.")
            st.warning("Precision cảnh báo trên tập kiểm tra thấp hơn mục tiêu khi chọn ngưỡng. Vì vậy, cảnh báo không phải kết luận chắc chắn; các ví dụ minh họa cũng cho thấy mô hình có thể nhầm ngữ cảnh.")

with batch_tab:
    st.subheader("Kiểm tra một bộ tin nhắn")
    st.caption("Mỗi dòng là một tin, tối đa 100 tin và 2.000 ký tự/tin. Kết quả chỉ giữ trong phiên, không ghi lịch sử hoặc hàng chờ. Chỉ nhập nội dung đã ẩn danh.")
    with st.form("batch_analysis"):
        batch_text = st.text_area("Danh sách tin nhắn", height=180)
        batch_labels = st.text_input("Nhãn tham chiếu tùy chọn, cách nhau bằng dấu phẩy", help="0 = bình thường, 1 = rác/lừa đảo. Số nhãn phải bằng số tin. Chỉ dùng nhãn đã được người duyệt xác nhận.")
        batch_submit = st.form_submit_button("Phân tích bộ mẫu", disabled=model is None)
    if batch_submit:
        messages = [line.strip() for line in batch_text.splitlines() if line.strip()]
        labels = None
        error = None
        if not messages or len(messages) > 100 or any(len(t) > 2000 for t in messages):
            error = "Hãy nhập từ 1 đến 100 tin, mỗi tin tối đa 2.000 ký tự."
        if batch_labels.strip():
            parts = [part.strip() for part in batch_labels.split(",")]
            if len(parts) != len(messages) or any(part not in {"0", "1"} for part in parts):
                error = "Nhãn phải là 0 hoặc 1 và khớp số lượng tin."
            else:
                labels = [int(part) for part in parts]
        if error:
            st.session_state.pop("batch_results", None)
            st.error(error)
        else:
            rows = []
            names = {"normal": "Bình thường", "scam": "Cảnh báo", "review": "Cần xem xét", "insufficient": "Chưa đủ ngữ cảnh"}
            for idx, message in enumerate(messages):
                result = classify_message(model, report, message)
                verdict = result["outcome"]
                comparison = "Chưa có nhãn"
                if labels is not None:
                    comparison = ("Chưa kết luận" if verdict in {"review", "insufficient"} else
                                  "Khớp" if (verdict == "scam") == bool(labels[idx]) else
                                  "Cảnh báo nhầm" if verdict == "scam" else "Bỏ sót")
                rows.append({"STT": idx + 1, "Nội dung": message, "Kết quả": names[verdict],
                             "Điểm SVM": round(result["margin"], 4),
                             "Nhãn tham chiếu": labels[idx] if labels is not None else None,
                             "Đối chiếu": comparison})
            st.session_state.batch_results = rows
    if st.session_state.get("batch_results"):
        rows = st.session_state.batch_results
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        counts = pd.Series([r["Đối chiếu"] for r in rows]).value_counts()
        st.write(" · ".join(f"{label}: {counts.get(label, 0)}" for label in ["Khớp", "Cảnh báo nhầm", "Bỏ sót", "Chưa kết luận", "Chưa có nhãn"]))
        st.caption("Đối chiếu dựa trên nhãn bạn nhập. Kết quả bộ mẫu này không thay thế đánh giá trên tập kiểm tra độc lập. Điểm SVM không phải xác suất.")
        st.download_button("Tải báo cáo JSON", json.dumps(rows, ensure_ascii=False, indent=2), "ket-qua-bo-mau.json", "application/json")
        if st.button("Xóa kết quả bộ mẫu"):
            st.session_state.pop("batch_results", None)
            st.rerun()

with overview_tab:
    st.subheader("Thống kê sử dụng trên máy này")
    analysis_counts = usage["analyses"]
    outcome_labels = {"scam": "Có dấu hiệu", "normal": "Nhóm bình thường", "insufficient": "Chưa đủ ngữ cảnh"}
    outcome_labels["review"] = "Cần xem xét"
    total = sum(analysis_counts.values())
    scam_total = sum(value for (channel_name, outcome), value in analysis_counts.items() if outcome == "scam")
    normal_total = sum(value for (channel_name, outcome), value in analysis_counts.items() if outcome == "normal")
    unsure_total = sum(value for (channel_name, outcome), value in analysis_counts.items() if outcome == "insufficient")
    review_total = sum(value for (channel_name, outcome), value in analysis_counts.items() if outcome == "review")
    feedback_total = usage["feedback"]["useful"] + usage["feedback"]["incorrect"]
    a, b, c, d, e = st.columns(5)
    a.metric("Phân tích", total)
    b.metric("Có dấu hiệu", scam_total)
    c.metric("Chưa đủ ngữ cảnh", unsure_total)
    d.metric("Cần xem xét", review_total)
    e.metric("Phản hồi", feedback_total)
    st.caption("Bộ đếm được lưu cục bộ. Nội dung chỉ được giữ nếu bật lịch sử hoặc tự gửi mẫu đã ẩn danh vào hàng chờ. Các con số phản hồi là đánh giá chủ quan, không phải độ chính xác đã kiểm chứng.")

    if total:
        rows = [
            {"Kênh": channel_name, "Kết quả": outcome_labels.get(outcome, outcome), "Số lượt": value}
            for (channel_name, outcome), value in analysis_counts.items()
        ]
        usage_table = pd.DataFrame(rows).sort_values(["Kênh", "Kết quả"])
        st.markdown("#### Phân tích theo kênh và kết quả")
        st.dataframe(usage_table, hide_index=True, width="stretch")
        chart = usage_table.pivot(index="Kênh", columns="Kết quả", values="Số lượt").fillna(0)
        st.bar_chart(chart)
    else:
        st.info("Chưa có lượt phân tích nào. Kết quả sẽ xuất hiện ở đây sau lần phân tích đầu tiên.")

    st.markdown("#### Phản hồi người dùng")
    f1, f2 = st.columns(2)
    f1.metric("Đánh giá phù hợp", usage["feedback"]["useful"])
    f2.metric("Đánh giá chưa đúng", usage["feedback"]["incorrect"])
    st.caption("Phản hồi chỉ là bộ đếm; hệ thống không gắn phản hồi với nội dung tin nhắn và không tự đưa dữ liệu vào huấn luyện.")

    st.divider()
    st.subheader("Lịch sử phân tích trên máy này")
    history = read_history()
    if history:
        st.caption(f"Đang lưu {len(history)} lượt gần nhất; lịch sử chỉ được ghi khi bạn bật tùy chọn ở mục Phân tích.")
        for record_id, created_at, channel_name, outcome, message in history:
            label = outcome_labels.get(outcome, outcome)
            with st.expander(f"{created_at} · {channel_name} · {label}"):
                st.write(message)
                st.caption("Nội dung được lưu cục bộ trên máy này.")
        confirm_clear = st.checkbox("Tôi muốn xóa toàn bộ lịch sử đã lưu", key="confirm_clear_history")
        if st.button("Xóa lịch sử", disabled=not confirm_clear):
            delete_history()
            st.session_state.confirm_clear_history = False
            st.success("Đã xóa lịch sử phân tích.")
            st.rerun()
    else:
        st.info("Chưa có lịch sử. Bật tùy chọn lưu ở mục Phân tích để ghi lại các lượt sau.")

    st.divider()
    st.subheader("Duyệt mẫu phản hồi sai")
    pending = read_review_queue("pending")
    st.caption("Mẫu trong hàng chờ đã qua bước che một số dữ liệu thường gặp. Người duyệt cần kiểm tra nội dung và chọn nhãn thật; không mẫu nào tự động vào dữ liệu huấn luyện.")
    if pending:
        for sample_id, created_at, channel_name, message, status, reviewed_label in pending:
            with st.expander(f"Mẫu #{sample_id} · {created_at} · {channel_name}"):
                st.markdown(render_highlighted_message(message), unsafe_allow_html=True)
                st.caption("Hãy xác minh mẫu không còn tên, địa chỉ hoặc dữ liệu cá nhân trước khi duyệt.")
                approve_normal, approve_scam, reject = st.columns(3)
                if approve_normal.button("Nhãn thật: bình thường", key=f"approve_normal_{sample_id}", width="stretch"):
                    update_review_status(sample_id, "approved", 0)
                    st.rerun()
                if approve_scam.button("Nhãn thật: rác/lừa đảo", key=f"approve_scam_{sample_id}", width="stretch"):
                    update_review_status(sample_id, "approved", 1)
                    st.rerun()
                if reject.button("Từ chối mẫu", key=f"reject_{sample_id}", width="stretch"):
                    update_review_status(sample_id, "rejected")
                    st.rerun()
    else:
        st.info("Hàng chờ hiện chưa có mẫu nào.")

    rejected = read_review_queue("rejected")
    if rejected:
        with st.expander(f"Mẫu đã từ chối ({len(rejected)})"):
            st.caption("Mẫu từ chối vẫn nằm cục bộ trong cơ sở dữ liệu để tránh xóa nhầm; chúng không được xuất vào CSV đã duyệt.")
            for sample_id, created_at, channel_name, message, status, reviewed_label in rejected:
                st.markdown(f"**Mẫu #{sample_id} · {channel_name} · {created_at}**")
                st.markdown(render_highlighted_message(message), unsafe_allow_html=True)

    approved = read_review_queue("approved")
    if approved:
        approved_frame = pd.DataFrame(
            [{"message": row[3], "label": row[5], "channel": row[2]} for row in approved],
            columns=["message", "label", "channel"],
        )
        st.markdown(f"**Mẫu đã duyệt:** {len(approved)} · Nhãn được người duyệt xác nhận. Giữ cột kênh khi xem xét đưa mẫu vào dữ liệu.")
        st.download_button(
            "Tải CSV mẫu đã duyệt để xem xét trước khi nhập dữ liệu",
            data=approved_frame.to_csv(index=False).encode("utf-8-sig"),
            file_name="reviewed_scam_samples.csv",
            mime="text/csv",
        )

with guide_tab:
    st.subheader("Quy trình kiểm tra an toàn")
    st.markdown("""
    1. **Tạm dừng:** đừng bấm đường dẫn, gọi số điện thoại trong tin nhắn, chuyển tiền hay cài ứng dụng theo hướng dẫn của người gửi.
    2. **Bảo vệ thông tin:** không cung cấp OTP, mật khẩu, mã PIN hoặc thông tin ngân hàng qua tin nhắn/cuộc gọi đến.
    3. **Tự xác minh:** tự mở ứng dụng chính thức hoặc tìm số tổng đài trên thẻ/website chính thức. Không dùng số và đường dẫn do tin nhắn cung cấp.
    4. **Nếu đã chia sẻ thông tin:** liên hệ ngay ngân hàng/dịch vụ qua kênh chính thức để khóa hoặc bảo vệ tài khoản; đổi mật khẩu nếu đã tiết lộ.

    ### Cách đọc kết quả
    - “Có dấu hiệu” là cảnh báo để kiểm tra thêm, không phải kết luận chắc chắn.
    - “Nhóm bình thường” không đảm bảo an toàn; mô hình có thể bỏ sót chiêu thức mới.
    - “Chưa đủ ngữ cảnh” xuất hiện với tin rất ngắn không có dấu hiệu cụ thể.
    - “Cần xem xét thêm” được dùng khi điểm chỉ vừa vượt ngưỡng nhưng không có dấu hiệu từ khóa; đây là vùng thận trọng, không phải nhãn xác suất.
    - Các cụm từ giải thích là đặc trưng ảnh hưởng đến điểm của mô hình, không phải bằng chứng về người gửi.
    - Điểm SVM không phải xác suất. Mô hình được đánh giá trên SMS; kết quả Zalo/email chưa được kiểm chứng riêng.

    ### Dữ liệu và cách đánh giá
    - Bộ dữ liệu: **Vietnamese Quality-Assured SMS Scam Dataset**, giấy phép **CC BY 4.0**; phiên bản dữ liệu được tải ngày 15/10/2026.
    - Tập phát triển gồm 2.394 tin; tập kiểm tra gồm 597 tin. Mô hình được chọn bằng kiểm định chéo 5 phần trên tập phát triển.
    - Trên tập kiểm tra, mô hình phân loại đúng 408 tin bình thường và 151 tin rác/lừa đảo; cảnh báo nhầm 31 tin bình thường và bỏ sót 7 tin lừa đảo.
    - Tập kiểm tra này đã từng được xem trong một lần chạy trước của dự án, nên kết quả hiện tại không phải đánh giá mù hoàn toàn. Ví dụ tự soạn trong ứng dụng cũng không thay thế một tập kiểm tra độc lập.
    - Nhãn “rác/lừa đảo” được gộp chung; hệ thống chưa xác định đáng tin cậy từng loại chiêu trò. Zalo/email chưa có bộ kiểm định riêng.

    Kết quả chi tiết và cấu hình nằm trong `reports/RESULTS.md` và `reports/evaluation.json` của dự án.

    ### Quyền riêng tư
    Mặc định, ứng dụng không lưu nội dung sau khi phân tích. Nếu bật tùy chọn lịch sử, nội dung và kết quả được lưu trong `reports/feedback.sqlite` trên máy này cho đến khi bạn xóa. Nếu gửi mẫu phản hồi sai, ứng dụng che email, số điện thoại, chuỗi số dài và đường dẫn phổ biến, rồi yêu cầu bạn kiểm tra/sửa nội dung trước khi lưu vào hàng chờ cục bộ. Không có nội dung nào được gửi ra dịch vụ bên ngoài.
    """)

st.caption("Dữ liệu huấn luyện: Vietnamese Quality-Assured SMS Scam Dataset, CC BY 4.0. Chỉ dán nội dung đã ẩn danh.")

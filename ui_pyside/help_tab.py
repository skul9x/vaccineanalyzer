from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from version import APP_VERSION, VERSION_STRING

class HelpTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        # Mặc định load Dark mode trước, controller sẽ update sau nếu cần
        self.render_help("Dark")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.help_browser = QTextBrowser()
        self.help_browser.setOpenExternalLinks(True)
        # Xóa border mặc định để trông liền mạch với nền
        self.help_browser.setStyleSheet("font-size: 14px; padding: 10px; border: none;")
        layout.addWidget(self.help_browser)

    def render_help(self, theme_name="Dark"):
        """
        Tạo nội dung HTML với màu sắc CSS tương ứng theo theme.
        Cập nhật hướng dẫn sử dụng cho giao diện mới (v4.8.4).
        """
        is_dark = (theme_name == "Dark")
        
        # Bảng màu động cho HTML
        c = {
            "text": "#E0E0E0" if is_dark else "#333333",
            "h_border": "#3B82F6" if is_dark else "#2563EB",
            "h_text": "#60A5FA" if is_dark else "#1D4ED8",
            "h3_text": "#F3F4F6" if is_dark else "#0F172A",
            
            # Phím tắt (Keybox)
            "key_bg": "#374151" if is_dark else "#EEEEEE",
            "key_border": "#4B5563" if is_dark else "#CCCCCC",
            "key_text": "#F3F4F6" if is_dark else "#333333",
            
            # Note Box (Xanh dương)
            "note_bg": "rgba(30, 58, 138, 0.4)" if is_dark else "#EFF6FF",
            "note_border": "#3B82F6" if is_dark else "#2563EB",
            "note_text": "#DBEAFE" if is_dark else "#1E3A8A",
            
            # Warning Box (Đỏ)
            "warn_bg": "rgba(127, 29, 29, 0.4)" if is_dark else "#FEF2F2",
            "warn_border": "#EF4444" if is_dark else "#EF4444",
            "warn_text": "#FECACA" if is_dark else "#991B1B",
            
            # Success Box (Xanh lá)
            "success_bg": "rgba(5, 150, 105, 0.2)" if is_dark else "#ECFDF5",
            "success_border": "#10B981" if is_dark else "#059669",
            "success_text": "#A7F3D0" if is_dark else "#065F46",

            # Legend Colors
            "legend_green": "#10B981" if is_dark else "#059669",
            "legend_orange": "#F59E0B" if is_dark else "#D97706",
            "legend_blue": "#60A5FA" if is_dark else "#2563EB",
            "legend_his": "#818CF8" if is_dark else "#4338CA"
        }

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; line-height: 1.7; color: {c['text']}; }}
                h1 {{ color: {c['h_text']}; border-bottom: 2px solid {c['h_border']}; padding-bottom: 10px; font-size: 24px; }}
                h2 {{ color: {c['h_text']}; margin-top: 25px; border-bottom: 1px dashed {c['h_border']}; padding-bottom: 5px; font-size: 18px; }}
                h3 {{ color: {c['h3_text']}; margin-top: 20px; font-weight: bold; font-size: 16px; }}
                .key {{ background-color: {c['key_bg']}; border: 1px solid {c['key_border']}; border-radius: 4px; padding: 2px 8px; font-family: monospace; font-weight: bold; color: {c['key_text']}; }}
                ul {{ margin-top: 5px; padding-left: 20px; }}
                li {{ margin-bottom: 10px; }}
                .note {{ background-color: {c['note_bg']}; border-left: 4px solid {c['note_border']}; padding: 15px; margin: 15px 0; color: {c['note_text']}; border-radius: 4px; }}
                .warning {{ background-color: {c['warn_bg']}; border-left: 4px solid {c['warn_border']}; padding: 15px; margin: 15px 0; color: {c['warn_text']}; border-radius: 4px; }}
                .success {{ background-color: {c['success_bg']}; border-left: 4px solid {c['success_border']}; padding: 15px; margin: 15px 0; color: {c['success_text']}; border-radius: 4px; }}
                .step {{ font-weight: bold; color: {c['h_text']}; }}
                .icon {{ font-size: 16px; }}
            </style>
        </head>
        <body>

            <h1>📖 HƯỚNG DẪN SỬ DỤNG</h1>
            <p>Phần mềm <b>Vaccine Analyzer</b> phiên bản <b>{VERSION_STRING}</b> - Hỗ trợ tra cứu và quản lý tiêm chủng.</p>

            <h2>🖥️ BỐ CỤC MÀN HÌNH</h2>
            <p>Màn hình chính chia làm <b>3 cột lớn</b>:</p>
            
            <table style="width:100%; border-collapse: collapse; margin: 15px 0;">
                <tr>
                    <td style="width:33%; padding: 10px; vertical-align: top; border: 1px solid {c['h_border']}; border-radius: 8px;">
                        <b style="color:{c['legend_his']}">🔍 CỘT TRÁI</b><br>
                        • <b>TRA CỨU BỆNH NHÂN</b>: Nhập SĐT để tìm bệnh nhân<br>
                        • <b>CHỈ ĐỊNH HÔM NAY (HIS)</b>: Danh sách bệnh nhân từ phòng khám
                    </td>
                    <td style="width:33%; padding: 10px; vertical-align: top; border: 1px solid {c['legend_green']}; border-radius: 8px;">
                        <b style="color:{c['legend_green']}">📋 CỘT GIỮA</b><br>
                        <b>LỊCH SỬ TIÊM CHỦNG</b><br>
                        Hiển thị các mũi đã tiêm từ Cổng Quốc Gia
                    </td>
                    <td style="width:33%; padding: 10px; vertical-align: top; border: 1px solid {c['legend_orange']}; border-radius: 8px;">
                        <b style="color:{c['legend_orange']}">📅 CỘT PHẢI</b><br>
                        <b>KẾ HOẠCH & DỰ BÁO</b><br>
                        Các mũi cần tiêm, thiếu hoặc sắp đến hạn
                    </td>
                </tr>
            </table>

            <h2>🚀 CÁCH SỬ DỤNG (3 BƯỚC)</h2>

            <div class="success">
                <b>✨ Quy trình nhanh:</b> Double-click bệnh nhân HIS → Xem kết quả → Đặt hẹn F10
            </div>

            <h3><span class="step">Bước 1:</span> Tra cứu bệnh nhân</h3>
            <p><b>Cách 1 - Từ danh sách HIS:</b></p>
            <ul>
                <li>Nhìn vào bảng <b>"CHỈ ĐỊNH HÔM NAY (HIS)"</b> ở cột trái bên dưới</li>
                <li><span class="key">Double Click</span> vào tên bệnh nhân → Hệ thống tự động tra cứu</li>
            </ul>
            
            <p><b>Cách 2 - Nhập số điện thoại:</b></p>
            <ul>
                <li>Gõ SĐT vào ô <b>"TRA CỨU BỆNH NHÂN"</b></li>
                <li>Nhấn <span class="key">Enter</span> hoặc click nút 🔍</li>
                <li>Kết quả hiện ra trong danh sách bên dưới</li>
            </ul>

            <h3><span class="step">Bước 2:</span> Chọn bệnh nhân và phân tích</h3>
            <ul>
                <li>Khi kết quả tìm kiếm hiện ra, <span class="key">Double Click</span> vào tên để <b>phân tích lịch sử tiêm</b></li>
                <li>Hoặc click icon <b>☁️ đám mây</b> bên phải để <b>đẩy cổng</b> (bổ sung mũi tiêm lên Cổng Quốc Gia)</li>
            </ul>
            
            <div class="note">
                💡 <b>Giải thích icon:</b><br>
                • <b>☁️ Icon đám mây</b> = Đẩy cổng (thêm mũi tiêm thiếu lên Cổng Quốc Gia)<br>
                • <b>Double-click tên</b> = Phân tích lịch sử tiêm chủng
            </div>

            <h3><span class="step">Bước 3:</span> Đặt hẹn tiêm</h3>
            <ul>
                <li>Sau khi phân tích, nhìn sang cột <b>"KẾ HOẠCH & DỰ BÁO"</b></li>
                <li>Chọn mũi vắc-xin cần hẹn</li>
                <li>Nhấn phím <span class="key">F10</span> hoặc nút <b>"ĐẶT HẸN"</b></li>
                <li>Chọn loại vắc-xin trong hộp thoại → Xác nhận</li>
            </ul>

            <h2>⚡ PHÍM TẮT</h2>
            <table style="width:100%; margin: 10px 0;">
                <tr>
                    <td style="padding: 8px;"><span class="key">Enter</span></td>
                    <td style="padding: 8px;">Tìm kiếm theo SĐT đã nhập</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><span class="key">Double Click</span></td>
                    <td style="padding: 8px;">Phân tích bệnh nhân được chọn</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><span class="key">F10</span></td>
                    <td style="padding: 8px;">Mở hộp thoại đặt lịch hẹn tiêm</td>
                </tr>
            </table>

            <h2>📤 TÍNH NĂNG KHÁC</h2>
            
            <h3>Xuất ảnh gửi Zalo</h3>
            <ul>
                <li>Click nút <b>📤 Xuất</b> ở đầu cột "Lịch sử tiêm" hoặc "Kế hoạch"</li>
                <li>Ảnh được tạo tự động, thư mục mở ngay để gửi cho khách</li>
            </ul>

            <h3>Thay đổi giao diện</h3>
            <ul>
                <li>Click icon <b>🌙/☀️</b> ở góc trên bên phải để đổi Dark/Light mode</li>
            </ul>

            <div class="warning">
                ⚠️ <b>Gặp lỗi kết nối?</b><br>
                Bấm nút <b>"Đăng nhập lại"</b> (góc trên phải) để làm mới phiên làm việc.
            </div>

            <hr style="border: 0; border-top: 1px solid #555; margin-top: 30px;">
            <p style="font-size: 12px; color: #888; text-align: center;">
                <b>Vaccine Analyzer {VERSION_STRING}</b><br>
                Tối ưu hóa quy trình tiêm chủng
            </p>
        </body>
        </html>
        """
        
        self.help_browser.setHtml(html_content)
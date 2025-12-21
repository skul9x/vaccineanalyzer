import qtawesome as qta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QTableWidget, QHeaderView, QAbstractItemView,
    QFrame, QSizePolicy, QStyledItemDelegate
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRegularExpression, Signal, QSize, QRect, QEvent
from PySide6.QtGui import QColor, QBrush, QRegularExpressionValidator
from .loading_overlay import LoadingOverlay
from .assigned_list_view import AssignedListView

class AutoClearLineEdit(QLineEdit):
    def focusInEvent(self, event):
        self.clear()
        super().focusInEvent(event)


class PatientResultItem(QWidget):
    """Custom widget for each patient search result with inline push icon."""
    push_clicked = Signal(int)  # Emits the row index
    
    def __init__(self, name, dob, gender=None, row_index=0, parent=None):
        super().__init__(parent)
        self.row_index = row_index
        self.setup_ui(name, dob, gender)
    
    def setup_ui(self, name, dob, gender):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Gender icon
        icon_name = 'fa5s.user'
        color = '#64748B'
        if gender == 1:
            icon_name = 'fa5s.male'
            color = '#3B82F6'
        elif gender == 0:
            icon_name = 'fa5s.female'
            color = '#EC4899'
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(18, 18))
        icon_lbl.setFixedSize(20, 20)
        
        # Patient info
        info_lbl = QLabel(f"{name} - NS: {dob}")
        info_lbl.setStyleSheet("font-size: 13px; color: #334155;")
        
        # Push gateway button
        self.push_btn = QPushButton()
        self.push_btn.setIcon(qta.icon('fa5s.cloud-upload-alt', color='#059669'))
        self.push_btn.setFixedSize(28, 28)
        self.push_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.push_btn.setToolTip("Đẩy cổng")
        self.push_btn.setStyleSheet("""
            QPushButton {
                background-color: #ECFDF5;
                border: 1px solid #A7F3D0;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #D1FAE5;
                border-color: #6EE7B7;
            }
            QPushButton:pressed {
                background-color: #A7F3D0;
            }
        """)
        self.push_btn.clicked.connect(self._on_push_clicked)
        
        layout.addWidget(icon_lbl)
        layout.addWidget(info_lbl, 1)
        layout.addWidget(self.push_btn)
    
    def _on_push_clicked(self):
        self.push_clicked.emit(self.row_index)

class AnalysisTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loading_overlay = LoadingOverlay(self)
        self.profile_anim = None
        self.setup_ui()

    def setup_ui(self):
        # ROOT LAYOUT
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(24) 
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        # === COLUMN 1: PATIENT CONTEXT (Input & HIS) ===
        self.col_context = QWidget()
        # FIX: Removed fixed width to allow expansion into the space freed from History col
        # self.col_context.setFixedWidth(350) 
        
        col1_layout = QVBoxLayout(self.col_context)
        col1_layout.setContentsMargins(0, 0, 0, 0)
        col1_layout.setSpacing(20)
        
        # [CARD 1] SEARCH & PROFILE
        self.search_card = QFrame()
        self.search_card.setProperty("class", "card")
        
        search_layout = QVBoxLayout(self.search_card)
        search_layout.setContentsMargins(20, 20, 20, 20)
        search_layout.setSpacing(16)
        
        # Header
        header_row = QHBoxLayout()
        lbl_search = QLabel("TRA CỨU BỆNH NHÂN")
        lbl_search.setProperty("class", "section_header")
        header_row.addWidget(lbl_search)
        header_row.addStretch()
        
        # Input Area
        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Nhập SĐT (VD: 0912...)")
        self.phone_input.setFixedHeight(42)
        self.phone_input.setClearButtonEnabled(True)
        
        rx = QRegularExpression(r"[0-9]*")
        self.phone_input.setValidator(QRegularExpressionValidator(rx, self.phone_input))
        
        self.search_btn = QPushButton()
        self.search_btn.setIcon(qta.icon('fa5s.search', color='white'))
        self.search_btn.setFixedSize(46, 42)
        self.search_btn.setProperty("class", "primary")
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.setToolTip("Tìm kiếm (Enter)")
        
        input_row.addWidget(self.phone_input)
        input_row.addWidget(self.search_btn)
        
        # Results List - use minimum height, will expand to fill available 35% space
        self.result_list = QListWidget()
        self.result_list.setMinimumHeight(100)  # Minimum for ~3 rows
        self.result_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # IMPORTANT: Always visible - don't hide() to prevent layout jumping
        
        # Signal for push gateway button clicks from result items
        # This will be connected by the controller
        
        search_layout.addLayout(header_row)
        search_layout.addLayout(input_row)
        search_layout.addWidget(self.result_list)
        # Note: No stretch here - result_list will fill remaining space in 35% allocated height
        
        # [CARD 2] HIS
        self.his_card = QFrame()
        self.his_card.setProperty("class", "card")
        his_layout = QVBoxLayout(self.his_card)
        his_layout.setContentsMargins(20, 20, 20, 20)
        his_layout.setSpacing(12)
        
        lbl_his = QLabel("CHỈ ĐỊNH HÔM NAY (HIS)")
        lbl_his.setProperty("class", "section_header")
        lbl_his.setStyleSheet("color: #4F46E5;")
        
        self.view_assigned = AssignedListView()
        his_layout.addWidget(lbl_his)
        his_layout.addWidget(self.view_assigned)
        
        # Fixed height ratio: search_card = 35%, his_card = 65%
        col1_layout.addWidget(self.search_card, 35)
        col1_layout.addWidget(self.his_card, 65)

        # === COLUMN 2: HISTORY (Administered) ===
        self.history_card = QFrame()
        self.history_card.setProperty("class", "card")
        hist_layout = QVBoxLayout(self.history_card)
        hist_layout.setContentsMargins(20, 20, 20, 20)
        hist_layout.setSpacing(12)
        
        hist_header = QHBoxLayout()
        lbl_hist = QLabel("LỊCH SỬ TIÊM CHỦNG")
        lbl_hist.setProperty("class", "section_header")
        lbl_hist.setStyleSheet("color: #059669;")
        
        self.admin_search = QLineEdit()
        self.admin_search.setPlaceholderText("Lọc nhanh...")
        self.admin_search.setFixedWidth(150)
        
        self.export_vaccinated_btn = QPushButton()
        self.export_vaccinated_btn.setIcon(qta.icon('fa5s.file-export', color='#64748B'))
        self.export_vaccinated_btn.setFlat(True)
        self.export_vaccinated_btn.setToolTip("Xuất ảnh")
        
        self.delete_vaccinated_img_btn = QPushButton()
        self.delete_vaccinated_img_btn.setIcon(qta.icon('fa5s.trash', color='#EF4444'))
        self.delete_vaccinated_img_btn.setFlat(True)
        self.delete_vaccinated_img_btn.setToolTip("Xóa ảnh cũ")
        
        hist_header.addWidget(lbl_hist)
        hist_header.addStretch()
        hist_header.addWidget(self.admin_search)
        hist_header.addWidget(self.export_vaccinated_btn)
        hist_header.addWidget(self.delete_vaccinated_img_btn)
        
        self.admin_table = QTableWidget()
        self.admin_table.setColumnCount(3)
        self.admin_table.setHorizontalHeaderLabels(["Vắc-xin", "Mũi", "Ngày tiêm"])
        
        h_header = self.admin_table.horizontalHeader()
        h_header.setSectionResizeMode(0, QHeaderView.Stretch)
        h_header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.admin_table.setColumnWidth(1, 50)
        h_header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.admin_table.setColumnWidth(2, 110)
        
        self.admin_table.verticalHeader().setVisible(False)
        self.admin_table.setAlternatingRowColors(True)
        self.admin_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.admin_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.admin_table.setShowGrid(False)
        self.admin_table.setSortingEnabled(True)
        
        hist_layout.addLayout(hist_header)
        hist_layout.addWidget(self.admin_table)
        
        # === COLUMN 3: PLAN ===
        self.plan_card = QFrame()
        self.plan_card.setProperty("class", "card")
        plan_layout = QVBoxLayout(self.plan_card)
        plan_layout.setContentsMargins(20, 20, 20, 20)
        plan_layout.setSpacing(12)
        
        plan_header = QHBoxLayout()
        lbl_plan = QLabel("KẾ HOẠCH & DỰ BÁO")
        lbl_plan.setProperty("class", "section_header")
        lbl_plan.setStyleSheet("color: #D97706;")
        
        self.missing_search = QLineEdit()
        self.missing_search.setPlaceholderText("Lọc...")
        self.missing_search.setFixedWidth(120)
        
        self.export_missing_btn = QPushButton()
        self.export_missing_btn.setIcon(qta.icon('fa5s.file-image', color='#64748B'))
        self.export_missing_btn.setFlat(True)
        self.export_missing_btn.setToolTip("Xuất ảnh")
        
        self.delete_missing_img_btn = QPushButton()
        self.delete_missing_img_btn.setIcon(qta.icon('fa5s.trash', color='#EF4444'))
        self.delete_missing_img_btn.setFlat(True)
        
        plan_header.addWidget(lbl_plan)
        plan_header.addStretch()
        plan_header.addWidget(self.missing_search)
        plan_header.addWidget(self.export_missing_btn)
        plan_header.addWidget(self.delete_missing_img_btn)
        
        self.missing_table = QTableWidget()
        self.missing_table.setColumnCount(2)
        self.missing_table.setHorizontalHeaderLabels(["Nội dung", "Dự kiến"])
        
        m_header = self.missing_table.horizontalHeader()
        m_header.setSectionResizeMode(0, QHeaderView.Stretch)
        m_header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.missing_table.setColumnWidth(1, 110)
        
        self.missing_table.verticalHeader().setVisible(False)
        self.missing_table.setAlternatingRowColors(True)
        self.missing_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.missing_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.missing_table.setShowGrid(False)
        self.missing_table.setSortingEnabled(True)
        
        self.schedule_btn = QPushButton("ĐẶT HẸN (F10)")
        self.schedule_btn.setIcon(qta.icon('fa5s.calendar-plus', color='white'))
        self.schedule_btn.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B; color: white; border: none;
                border-radius: 8px; padding: 12px; font-size: 14px; font-weight: 700;
            }
            QPushButton:hover { background-color: #D97706; }
        """)
        self.schedule_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        plan_layout.addLayout(plan_header)
        plan_layout.addWidget(self.missing_table)
        plan_layout.addWidget(self.schedule_btn)
        
        # === ADD TO MAIN LAYOUT (Revised Proportions) ===
        # Previous: 0(Fixed350) : 4 : 3
        # New:      3(Stretch)  : 3 : 3  (Search gets same weight as others, effectively +30% width)
        main_layout.addWidget(self.col_context, 3) 
        main_layout.addWidget(self.history_card, 3)
        main_layout.addWidget(self.plan_card, 3)

    def set_loading(self, is_loading, msg="Đang xử lý..."):
        self.loading_overlay.show_loading(is_loading, msg)
        self.setEnabled(not is_loading)

    def set_phone_error(self, has_error):
        if has_error:
            self.phone_input.setStyleSheet("border: 1px solid #EF4444;")
        else:
            self.phone_input.setStyleSheet("")

    # Deprecated profile methods removed since profile container was eliminated
    # The search controller now handles patient info and push directly in the result list
class AppTheme:
    """
    Central Theme Registry for the Application.
    Defines color palettes and generates QSS stylesheets dynamically.
    """
    
    # 1. LIGHT (Default Medical Theme)
    LIGHT = {
        "bg_main": "#F1F5F9",       "bg_sidebar": "#FFFFFF", "bg_card": "#FFFFFF",
        "text_main": "#0F172A",     "text_secondary": "#64748B", "text_header": "#1E293B",
        "primary": "#0284C7",       "primary_hover": "#0369A1", "primary_text": "#FFFFFF",
        "border": "#E2E8F0",        "input_bg": "#FFFFFF", "input_focus": "#0284C7",
        "table_head_bg": "#F8FAFC", "table_head_txt": "#475569", "table_row_alt": "#F8FAFC",
        "selection_bg": "#E0F2FE",  "selection_txt": "#0369A1",
        "success": "#10B981",       "success_hover": "#059669",
        "warning": "#F59E0B",       "danger": "#EF4444",
        "success_bg": "#ECFDF5",    "success_text": "#065F46",
        "warning_bg": "#FFFBEB",    "warning_text": "#92400E",
        "danger_bg": "#FEF2F2",     "danger_text": "#991B1B",
        "info_bg": "#F0F9FF",       "info_text": "#075985",
        "neutral_bg": "#F1F5F9",    "neutral_text": "#475569",
        "sidebar_hover": "#F8FAFC", "sidebar_active": "#F0F9FF", "sidebar_border_active": "#0284C7"
    }

    # 2. DARK (Professional Dark Mode)
    DARK = {
        "bg_main": "#0F172A",       "bg_sidebar": "#1E293B", "bg_card": "#1E293B",
        "text_main": "#F8FAFC",     "text_secondary": "#94A3B8", "text_header": "#FFFFFF",
        "primary": "#38BDF8",       "primary_hover": "#7DD3FC", "primary_text": "#0F172A",
        "border": "#334155",        "input_bg": "#334155", "input_focus": "#38BDF8",
        "table_head_bg": "#1E293B", "table_head_txt": "#E2E8F0", "table_row_alt": "#0F172A",
        "selection_bg": "#0369A1",  "selection_txt": "#FFFFFF",
        "success": "#34D399",       "success_hover": "#059669",
        "warning": "#FBBF24",       "danger": "#F87171",
        "success_bg": "#064E3B",    "success_text": "#D1FAE5",
        "warning_bg": "#78350F",    "warning_text": "#FEF3C7",
        "danger_bg": "#7F1D1D",     "danger_text": "#FEE2E2",
        "info_bg": "#0C4A6E",       "info_text": "#E0F2FE",
        "neutral_bg": "#374151",    "neutral_text": "#E2E8F0",
        "sidebar_hover": "#334155", "sidebar_active": "#1E293B", "sidebar_border_active": "#38BDF8"
    }

    # 3. OCEAN (Deep Blue Theme)
    OCEAN = {
        "bg_main": "#0B1120",       "bg_sidebar": "#111827", "bg_card": "#1F2937",
        "text_main": "#F0F9FF",     "text_secondary": "#9CA3AF", "text_header": "#E0F2FE",
        "primary": "#0EA5E9",       "primary_hover": "#38BDF8", "primary_text": "#FFFFFF",
        "border": "#374151",        "input_bg": "#374151", "input_focus": "#0EA5E9",
        "table_head_bg": "#111827", "table_head_txt": "#9CA3AF", "table_row_alt": "#111827",
        "selection_bg": "#075985",  "selection_txt": "#FFFFFF",
        "success": "#2DD4BF",       "success_hover": "#14B8A6",
        "warning": "#FACC15",       "danger": "#FB7185",
        "success_bg": "#134E4A",    "success_text": "#CCFBF1",
        "warning_bg": "#713F12",    "warning_text": "#FEF08A",
        "danger_bg": "#881337",     "danger_text": "#FFE4E6",
        "info_bg": "#0C4A6E",       "info_text": "#E0F2FE",
        "neutral_bg": "#374151",    "neutral_text": "#E5E7EB",
        "sidebar_hover": "#374151", "sidebar_active": "#1F2937", "sidebar_border_active": "#0EA5E9"
    }

    # 4. FOREST (Nature Theme)
    FOREST = {
        "bg_main": "#F0FDF4",       "bg_sidebar": "#FFFFFF", "bg_card": "#FFFFFF",
        "text_main": "#064E3B",     "text_secondary": "#374151", "text_header": "#065F46",
        "primary": "#059669",       "primary_hover": "#10B981", "primary_text": "#FFFFFF",
        "border": "#A7F3D0",        "input_bg": "#FFFFFF", "input_focus": "#059669",
        "table_head_bg": "#DCFCE7", "table_head_txt": "#166534", "table_row_alt": "#F0FDF4",
        "selection_bg": "#DCFCE7",  "selection_txt": "#064E3B",
        "success": "#16A34A",       "success_hover": "#15803D",
        "warning": "#D97706",       "danger": "#DC2626",
        "success_bg": "#DCFCE7",    "success_text": "#14532D",
        "warning_bg": "#FFFBEB",    "warning_text": "#78350F",
        "danger_bg": "#FEF2F2",     "danger_text": "#7F1D1D",
        "info_bg": "#F0F9FF",       "info_text": "#0C4A6E",
        "neutral_bg": "#E2E8F0",    "neutral_text": "#1F2937",
        "sidebar_hover": "#F0FDF4", "sidebar_active": "#DCFCE7", "sidebar_border_active": "#059669"
    }

    # 5. SUNSET (Warm Theme)
    SUNSET = {
        "bg_main": "#2A2438",       "bg_sidebar": "#352F44", "bg_card": "#352F44",
        "text_main": "#F9FAFB",     "text_secondary": "#D1D5DB", "text_header": "#FCE7F3",
        "primary": "#DB2777",       "primary_hover": "#EC4899", "primary_text": "#FFFFFF",
        "border": "#5C5470",        "input_bg": "#5C5470", "input_focus": "#DB2777",
        "table_head_bg": "#5C5470", "table_head_txt": "#F3E8FF", "table_row_alt": "#2A2438",
        "selection_bg": "#831843",  "selection_txt": "#FCE7F3",
        "success": "#34D399",       "success_hover": "#059669",
        "warning": "#FBBF24",       "danger": "#F87171",
        "success_bg": "#064E3B",    "success_text": "#D1FAE5",
        "warning_bg": "#78350F",    "warning_text": "#FEF3C7",
        "danger_bg": "#7F1D1D",     "danger_text": "#FEE2E2",
        "info_bg": "#4C1D95",       "info_text": "#E9D5FF",
        "neutral_bg": "#5C5470",    "neutral_text": "#E5E7EB",
        "sidebar_hover": "#5C5470", "sidebar_active": "#5C5470", "sidebar_border_active": "#DB2777"
    }

    # 6. FUTURISTIC (Cyber Theme)
    FUTURISTIC = {
        "bg_main": "#09090B",       "bg_sidebar": "#18181B", "bg_card": "#18181B",
        "text_main": "#FAFAFA",     "text_secondary": "#A1A1AA", "text_header": "#FFFFFF",
        "primary": "#D946EF",       "primary_hover": "#E879F9", "primary_text": "#FFFFFF",
        "border": "#27272A",        "input_bg": "#27272A", "input_focus": "#D946EF",
        "table_head_bg": "#27272A", "table_head_txt": "#D946EF", "table_row_alt": "#09090B",
        "selection_bg": "#701A75",  "selection_txt": "#F0ABFC",
        "success": "#4ADE80",       "success_hover": "#BEF264",
        "warning": "#FACC15",       "danger": "#FB7185",
        "success_bg": "#14532D",    "success_text": "#DCFCE7",
        "warning_bg": "#713F12",    "warning_text": "#FEF9C3",
        "danger_bg": "#7F1D1D",     "danger_text": "#FEE2E2",
        "info_bg": "#1E3A8A",       "info_text": "#DBEAFE",
        "neutral_bg": "#27272A",    "neutral_text": "#A1A1AA",
        "sidebar_hover": "#27272A", "sidebar_active": "#27272A", "sidebar_border_active": "#D946EF"
    }

    @staticmethod
    def get_stylesheet(theme_name="Light"):
        themes = {
            "Light": AppTheme.LIGHT, "Dark": AppTheme.DARK,
            "Ocean": AppTheme.OCEAN, "Forest": AppTheme.FOREST,
            "Sunset": AppTheme.SUNSET, "Futuristic": AppTheme.FUTURISTIC
        }
        c = themes.get(theme_name, AppTheme.LIGHT)
        is_dark_mode = theme_name in ["Dark", "Ocean", "Sunset", "Futuristic"]

        primary_btn_css = f"""
        QPushButton[class="primary"] {{
            background-color: {c['primary']}; color: {c['primary_text']}; border: 1px solid {c['primary']};
        }}
        QPushButton[class="primary"]:hover {{
            background-color: {c['primary_hover']}; border-color: {c['primary_hover']};
        }}
        """
        
        success_btn_css = f"""
        QPushButton[class="success"] {{
            background-color: {c['success']}; color: {'#000000' if not is_dark_mode else '#FFFFFF'}; border: 1px solid {c['success']};
        }}
        QPushButton[class="success"]:hover {{
            background-color: {c['success_hover']};
        }}
        """

        return f"""
        QWidget {{
            background-color: {c['bg_main']};
            color: {c['text_main']};
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-size: 13px;
        }}

        QWidget#SidebarContainer {{
            background-color: {c['bg_sidebar']};
            border-right: 1px solid {c['border']};
        }}
        QFrame[class="topbar"] {{
            background-color: {c['bg_card']};
            border-bottom: 1px solid {c['border']};
        }}
        QFrame[class="card"], QFrame[class="panel_frame"] {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 12px;
        }}

        QLabel {{ background: transparent; color: {c['text_main']}; }}
        QLabel[class="header_title"] {{ font-size: 18px; font-weight: 700; color: {c['text_header']}; }}
        QLabel[class="section_header"] {{ 
            font-weight: 700; font-size: 13px; text-transform: uppercase; 
            letter-spacing: 0.5px; color: {c['text_secondary']}; padding-bottom: 4px;
        }}

        QLabel[class="badge_success"] {{
            background-color: {c['success_bg']}; color: {c['success_text']};
            border-radius: 6px; padding: 4px 8px; font-weight: 700; font-size: 12px;
        }}
        QLabel[class="badge_warning"] {{
            background-color: {c['warning_bg']}; color: {c['warning_text']};
            border-radius: 6px; padding: 4px 8px; font-weight: 700; font-size: 12px;
        }}
        QLabel[class="badge_danger"] {{
            background-color: {c['danger_bg']}; color: {c['danger_text']};
            border-radius: 6px; padding: 4px 8px; font-weight: 700; font-size: 12px;
        }}
        QLabel[class="badge_info"] {{
            background-color: {c['info_bg']}; color: {c['info_text']};
            border-radius: 6px; padding: 4px 8px; font-weight: 700; font-size: 12px;
        }}
        QLabel[class="badge_neutral"] {{
            background-color: {c['neutral_bg']}; color: {c['neutral_text']};
            border-radius: 6px; padding: 4px 8px; font-weight: 600; font-size: 12px;
        }}

        QPushButton {{
            background-color: {c['bg_card']}; border: 1px solid {c['border']};
            border-radius: 6px; padding: 6px 16px; color: {c['text_main']}; font-weight: 600;
        }}
        QPushButton:hover {{ background-color: {c['sidebar_hover']}; border-color: {c['primary']}; }}
        {primary_btn_css}
        {success_btn_css}
        QPushButton[class="ghost"] {{ background: transparent; border: none; color: {c['text_secondary']}; }}
        QPushButton[class="ghost"]:hover {{ background: {c['sidebar_hover']}; color: {c['text_main']}; }}
        
        QPushButton[class="sidebar_btn"] {{
            background: transparent; border: none; border-left: 3px solid transparent;
            color: {c['text_secondary']}; text-align: left; padding: 10px 16px; font-weight: 500; border-radius: 0;
        }}
        QPushButton[class="sidebar_btn"]:hover {{ background: {c['sidebar_hover']}; color: {c['text_main']}; }}
        QPushButton[class="sidebar_btn"]:checked {{
            background: {c['sidebar_active']}; color: {c['primary']};
            border-left: 3px solid {c['sidebar_border_active']}; font-weight: 700;
        }}

        QLineEdit, QComboBox, QDateEdit, QSpinBox {{
            background-color: {c['input_bg']}; border: 1px solid {c['border']};
            border-radius: 6px; padding: 6px 12px; color: {c['text_main']};
            selection-background-color: {c['primary']}; selection-color: {c['primary_text']};
        }}
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {{
            border: 2px solid {c['input_focus']}; padding: 5px 11px;
        }}

        QTableWidget, QListWidget {{
            background-color: {c['bg_card']}; alternate-background-color: {c['table_row_alt']};
            border: none; gridline-color: transparent; outline: none;
        }}
        QHeaderView::section {{
            background-color: {c['table_head_bg']}; color: {c['table_head_txt']};
            padding: 8px; border: none; border-bottom: 2px solid {c['border']};
            font-weight: 700; text-transform: uppercase; font-size: 11px;
        }}
        QTableWidget::item {{ padding: 6px; border-bottom: 1px solid {c['border']}; }}
        QTableWidget::item:selected, QListWidget::item:selected {{
            background-color: {c['selection_bg']}; color: {c['selection_txt']};
        }}
        
        QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
        QScrollBar::handle:vertical {{ background: {c['border']}; border-radius: 4px; min-height: 20px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

        /* --- TABS (STEP 9) --- */
        QTabWidget::pane {{
            border: 1px solid {c['border']};
            border-radius: 8px;
            background: {c['bg_card']};
            top: -1px;
        }}
        QTabBar::tab {{
            background: transparent;
            color: {c['text_secondary']};
            padding: 10px 20px;
            font-weight: 600;
            border-bottom: 2px solid transparent;
            margin-bottom: -1px;
        }}
        QTabBar::tab:selected {{
            color: {c['primary']};
            border-bottom: 2px solid {c['primary']};
        }}
        QTabBar::tab:hover {{
            color: {c['text_main']};
        }}
        """
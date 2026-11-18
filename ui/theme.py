"""Colours and the global Qt stylesheet."""

import os
import tempfile

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPixmap, QPolygonF

ACCENT = "#d6336c"
ACCENT_HOVER = "#c2255c"
ACCENT_SOFT = "#fdebf1"

def make_arrow_png():
    """Draws a small down-arrow once and returns its path (used by combo boxes)."""
    path = os.path.join(tempfile.gettempdir(), "bloom_combo_arrow.png")
    pix = QPixmap(24, 24)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#6b7388"))
    painter.setPen(Qt.NoPen)
    painter.drawPolygon(QPolygonF([QPointF(6, 9), QPointF(18, 9), QPointF(12, 16)]))
    painter.end()
    pix.save(path, "PNG")
    return path.replace("\\", "/")


def build_stylesheet(arrow):
    return f"""
* {{ font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif; font-size: 14px; color: #1f2430; }}
QMainWindow, QWidget#page, QWidget#content {{ background: #f6f6fa; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}

/* ---------- sidebar ---------- */
QFrame#sidebar {{ background: #ffffff; border-right: 1px solid #e8e8f0; }}
QLabel#brand {{ font-size: 24px; font-weight: 700; color: {ACCENT}; }}
QLabel#brandSub {{ color: #7a8194; font-size: 12px; }}
QPushButton#nav {{
    text-align: left; padding: 11px 16px; border: none; border-radius: 10px;
    background: transparent; color: #4a5164; font-weight: 600;
}}
QPushButton#nav:hover {{ background: #f3f3f8; }}
QPushButton#nav:checked {{ background: {ACCENT_SOFT}; color: {ACCENT}; }}
QLabel#sideFooter {{ color: #7a8194; font-size: 12px; }}

/* ---------- headings & text ---------- */
QLabel#h1 {{ font-size: 26px; font-weight: 700; }}
QLabel#sub {{ color: #6b7388; font-size: 14px; }}
QLabel#cardTitle {{ font-size: 16px; font-weight: 700; }}
QLabel#muted {{ color: #6b7388; }}
QLabel#fieldLabel {{ color: #4a5164; font-weight: 600; }}

/* ---------- cards ---------- */
QFrame#card {{ background: #ffffff; border: 1px solid #e8e8f0; border-radius: 14px; }}
QLabel#statValue {{ font-size: 28px; font-weight: 700; color: {ACCENT}; }}
QLabel#statName {{ color: #6b7388; font-size: 13px; }}
QLabel#statusPill {{
    background: #eef0f6; color: #4a5164; border-radius: 10px;
    padding: 3px 12px; font-weight: 600;
}}

/* ---------- inputs ---------- */
QLineEdit, QComboBox {{
    background: #ffffff; border: 1px solid #d9dbe6; border-radius: 8px;
    padding: 8px 10px; min-height: 20px; selection-background-color: {ACCENT};
    selection-color: #ffffff;
}}
QComboBox:disabled {{ background: #f3f3f8; color: #a3a8ba; }}
QLineEdit:hover, QComboBox:hover {{ border: 1px solid #b9bdd0; }}
QLineEdit:focus, QComboBox:focus {{ border: 1px solid {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 30px; }}
QComboBox::down-arrow {{ image: url({arrow}); width: 12px; height: 12px; }}
QComboBox QAbstractItemView {{
    background: #ffffff; border: 1px solid #d9dbe6; outline: none;
    selection-background-color: {ACCENT_SOFT}; selection-color: {ACCENT};
}}

/* ---------- buttons ---------- */
QPushButton {{
    background: #ffffff; border: 1px solid #d9dbe6; border-radius: 8px;
    padding: 9px 18px; font-weight: 600;
}}
QPushButton:hover {{ background: #f3f3f8; }}
QPushButton:pressed {{ background: #e8e8f0; }}
QPushButton:disabled {{ color: #a3a8ba; background: #f3f3f8; border-color: #e8e8f0; }}
QPushButton#primary {{ background: {ACCENT}; border: none; color: #ffffff; }}
QPushButton#primary:hover {{ background: {ACCENT_HOVER}; }}
QPushButton#primary:disabled {{ background: #efb3c8; color: #ffffff; }}
QPushButton#danger {{ color: #c92a2a; border-color: #f1c4c4; }}
QPushButton#danger:hover {{ background: #fdf0f0; }}
QPushButton#danger:disabled {{ color: #d9a3a3; background: #f3f3f8; border-color: #e8e8f0; }}
QPushButton#iconBtn {{ padding: 7px 0; min-width: 36px; max-width: 36px; }}

/* ---------- progress ---------- */
QProgressBar {{
    background: #eceef5; border: none; border-radius: 9px; min-height: 18px;
    max-height: 18px; text-align: center; font-weight: 600; color: #1f2430;
}}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 9px; }}

/* ---------- tables ---------- */
QTableView {{
    background: #ffffff; alternate-background-color: #faf9fd; border: none;
    gridline-color: transparent; selection-background-color: {ACCENT_SOFT};
    selection-color: #1f2430; outline: none;
}}
QTableView::item {{ padding: 4px 10px; border-bottom: 1px solid #f0f0f6; }}
QHeaderView::section {{
    background: #f3f3f8; color: #3a4154; padding: 11px 10px; border: none;
    border-bottom: 1px solid #e8e8f0; font-weight: 700;
}}
QHeaderView::section:hover {{ background: #eaeaf3; }}

QPlainTextEdit {{
    background: #fbfbfe; border: 1px solid #e8e8f0; border-radius: 10px; padding: 8px;
    font-family: 'Consolas', 'Menlo', monospace; font-size: 13px; color: #3a4154;
}}

QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #cfd2e0; border-radius: 5px; min-height: 36px; }}
QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: #cfd2e0; border-radius: 5px; min-width: 36px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
"""


def apply_theme(app):
    """Call once at start-up: Fusion style, base font and the Bloom stylesheet."""
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(build_stylesheet(make_arrow_png()))

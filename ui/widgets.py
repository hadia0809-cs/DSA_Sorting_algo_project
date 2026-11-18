"""Small reusable pieces shared by several pages."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.constants import ALL_OPERATORS, COLUMNS


def make_card(title=None, subtitle=None):
    """Returns (card_frame, body_layout). Put your widgets in body_layout."""
    card = QFrame()
    card.setObjectName("card")
    outer = QVBoxLayout(card)
    outer.setContentsMargins(22, 20, 22, 22)
    outer.setSpacing(14)
    if title:
        head = QVBoxLayout()
        head.setSpacing(2)
        t = QLabel(title)
        t.setObjectName("cardTitle")
        head.addWidget(t)
        if subtitle:
            s = QLabel(subtitle)
            s.setObjectName("muted")
            s.setWordWrap(True)
            head.addWidget(s)
        outer.addLayout(head)
    return card, outer


def page_header(title, subtitle):
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(2)
    h = QLabel(title)
    h.setObjectName("h1")
    s = QLabel(subtitle)
    s.setObjectName("sub")
    lay.addWidget(h)
    lay.addWidget(s)
    return box


def scrolling(content):
    """Wrap a page body in a scroll area (so small windows still work)."""
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    area.setWidget(content)
    return area


def field_label(text):
    lbl = QLabel(text)
    lbl.setObjectName("fieldLabel")
    return lbl


def combo(items):
    c = QComboBox()
    c.addItems(list(items))
    return c


def style_table(table, row_height=40):
    table.setAlternatingRowColors(True)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setShowGrid(False)
    table.setFrameShape(QFrame.NoFrame)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(row_height)
    table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
    table.horizontalHeader().setHighlightSections(False)


class StatCard(QFrame):
    """Big number with a caption (used on the Scraper and Sort pages)."""

    def __init__(self, caption, value="—"):
        super().__init__()
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(2)
        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")
        name = QLabel(caption)
        name.setObjectName("statName")
        lay.addWidget(self.value_label)
        lay.addWidget(name)

    def set_value(self, text):
        self.value_label.setText(str(text))


class FilterRow(QWidget):
    """[AND|OR|NOT]  column  operator  value  [x]"""

    def __init__(self, on_remove, first=False):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        self.logic = combo(["AND", "OR", "NOT"])
        self.logic.setFixedWidth(86)
        if first:
            self.logic.setEnabled(False)  # nothing to join the first row to
        self.column = combo(COLUMNS)
        self.operator = combo(ALL_OPERATORS)
        self.value = QLineEdit()
        self.value.setPlaceholderText("Value")

        remove = QPushButton("✕")
        remove.setObjectName("iconBtn")
        remove.setToolTip("Remove condition")
        remove.clicked.connect(lambda: on_remove(self))

        lay.addWidget(self.logic)
        lay.addWidget(self.column, 2)
        lay.addWidget(self.operator, 2)
        lay.addWidget(self.value, 3)
        lay.addWidget(remove)


class SortLevelRow(QWidget):
    """Sort by / Then by  column  order  [x]"""

    def __init__(self, on_remove, index):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        self.tag = QLabel("Sort by" if index == 0 else "Then by")
        self.tag.setObjectName("fieldLabel")
        self.tag.setFixedWidth(60)
        self.column = combo(COLUMNS)
        self.order = combo(["Ascending", "Descending"])

        remove = QPushButton("✕")
        remove.setObjectName("iconBtn")
        remove.setToolTip("Remove level")
        remove.clicked.connect(lambda: on_remove(self))

        lay.addWidget(self.tag)
        lay.addWidget(self.column, 2)
        lay.addWidget(self.order, 2)
        lay.addWidget(remove)

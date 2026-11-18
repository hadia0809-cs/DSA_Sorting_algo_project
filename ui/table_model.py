"""Table model for the repositories table."""

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt

from data_store import COLUMN_DEFS, HEADERS


class RepoTableModel(QAbstractTableModel):
    """Feeds the QTableView. Only visible rows are drawn, so 15,000 rows scroll smoothly.
    It starts empty; later you call set_rows(list_of_dicts) to fill it."""

    def __init__(self):
        super().__init__()
        self.rows = []

    def set_rows(self, rows):
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(COLUMN_DEFS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return HEADERS[section]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        _, field, kind = COLUMN_DEFS[index.column()]
        value = self.rows[index.row()][field]
        if role == Qt.DisplayRole:
            if field == "id":
                return str(value)
            if kind == "int":
                return f"{value:,}"
            if kind == "date":
                return value[:10]          # 2024-05-17T10:20:30Z -> 2024-05-17
            return value
        if role == Qt.TextAlignmentRole and kind == "int":
            return int(Qt.AlignRight | Qt.AlignVCenter)
        if role == Qt.ToolTipRole and field == "description":
            return value
        return None

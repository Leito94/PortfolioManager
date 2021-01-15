import sys
import pandas as pd
import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QAbstractTableModel, Qt

df = pd.DataFrame({
    "a": ["Mary", "Jim", "John"],
    "b": [100, 200, 300],
    "c": ["a", "b", "c"]
})


class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def row_count(self, parent=None):
        return self._data.shape[0]

    def column_count(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index - isValid():
            if role == Qt.DisplayRolw:
                return str(self._data.iloc[index.row(), index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


app = qtw.QApplication(sys.argv)
model = pandasModel(df)
view = qtw.QTableView()
view.setModel(model)
view.resize(800, 600)
view.show()
sys.exit(app.exec_())

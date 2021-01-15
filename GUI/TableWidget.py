import sys
from PyQt5.QtWidgets import *
import pandas as pd

portfolio_df = pd.read_csv("../Analysis/test_portfolio.csv", index_col = 0)
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 - QTableWidget'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createTable(portfolio_df)

        self.layout = QGridLayout()
        self.layout.addWidget(self.tableWidget, 0,0)
        self.setLayout(self.layout)

        # Show window
        self.show()

        # Create table

    def createTable(self, portfolio_df):
        self.tableWidget = QTableWidget()

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Row count
        self.tableWidget.setRowCount(len(portfolio_df))

        # Column count
        self.tableWidget.setColumnCount(5)

        columns = portfolio_df.columns
        c = 0
        for col in columns:
            array = portfolio_df[col]
            r = 0
            for row in array:
                self.tableWidget.setItem(r, c, QTableWidgetItem(row))
                r += 1
            c += 1

        self.tableWidget.setHorizontalHeaderLabels(portfolio_df.columns)


        # Table will fit the screen horizontally
        #self.tableWidget.horizontalHeader().setStretchLastSection(True)
        #self.tableWidget.horizontalHeader().setSectionResizeMode(
            #QHeaderView.Stretch)

app = QApplication(sys.argv)
ex = App()
sys.exit(app.exec_())
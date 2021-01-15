import sys
import matplotlib.pyplot as plt
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui
import PyQt5.QtCore as qtc
from bs4 import BeautifulSoup as bs
import requests
import re
import json
import pandas as pd
import numpy as np
import yahoo_fin.stock_info as si
import datetime
from lxml import html
import qdarkstyle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FQtAgg

# get a list of all countries
with open("../countries.json", "r") as f:
    countries = json.load(f)

# List, Dictionary for the dates
years = ["2016", "2017", "2018", "2019", "2020"]
months_days_dict = {
    "January": list(range(1, 32)),
    "February": list(range(1, 29)),
    "March": list(range(1, 32)),
    "April": list(range(1, 31)),
    "May": list(range(1, 32)),
    "June": list(range(1, 31)),
    "July": list(range(1, 32)),
    "August": list(range(1, 32)),
    "September": list(range(1, 31)),
    "October": list(range(1, 32)),
    "November": list(range(1, 31)),
    "December": list(range(1, 32))
}


class MainWindow(qtw.QWidget):
    """Main Window Constructor"""
    # widgets are attached here
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PortfolioManager")
        self.setWindowIcon(QIcon("stock-market.png"))
        self.setLayout(qtw.QHBoxLayout())
        self.restart_program = False
        self.user_interface()
        # End main UI code
        self.show()

    def user_interface(self):
        """Function to create the first User interface. All the widgets are stored in a sublayout."""
        container = qtw.QWidget()
        container.setLayout(qtw.QGridLayout())
        model_1 = QStandardItemModel()
        model_2 = QStandardItemModel()

        # Widgets------------------------------------------------------------------------------------------------------#

        # Labels
        lb_1 = qtw.QLabel("Geben Sie Start- und Enddatum an")
        lb_2 = qtw.QLabel("Startdatum")
        lb_3 = qtw.QLabel("Enddatum")
        lb_4 = qtw.QLabel("Auf welchen Faktoren soll die Analyse basieren?")
        lb_5 = qtw.QLabel("")

        # Comboboxes
        cbo_1 = qtw.QComboBox()
        cbo_1.addItems(years)

        cbo_2 = qtw.QComboBox()
        cbo_2.setModel(model_1)

        cbo_3 = qtw.QComboBox()
        cbo_3.setModel(model_1)

        cbo_4 = qtw.QComboBox()
        cbo_4.addItems(years)

        cbo_5 = qtw.QComboBox()
        cbo_5.setModel(model_2)

        cbo_6 = qtw.QComboBox()
        cbo_6.setModel(model_2)

        # CheckBoxes
        chx_1 = qtw.QCheckBox("Momentum")
        chx_2 = qtw.QCheckBox("Value")
        chx_3 = qtw.QCheckBox("Profit")
        chx_1.setChecked(False)
        chx_2.setChecked(False)
        chx_3.setChecked(False)

        # Button
        self.btn_1 = qtw.QPushButton("Start Analysis")
        self.btn_1.setStyleSheet("font: bold;background-color: green;font-size: 16px")
        # self.btn_1.clicked.connect(start_analysis)
        btn_2 = qtw.QPushButton("Performance until today")
        #btn_2.clicked.connect(past_performance)
        btn_3 = qtw.QPushButton("Quit", clicked = self.close)
        btn_3.setStyleSheet("font: bold; background-color: red")

        # add combobox data
        # add Data
        for k, v in months_days_dict.items():
            month = QStandardItem(k)
            model_1.appendRow(month)
            for value in v:
                day = QStandardItem(str(value))
                month.appendRow(day)

        for k, v in months_days_dict.items():
            month = QStandardItem(k)
            model_2.appendRow(month)
            for value in v:
                day = QStandardItem(str(value))
                month.appendRow(day)

        #cbo_2.currentIndexChanged.connect(update_combo_1)
        #update_combo_1(0)

        #cbo_5.currentIndexChanged.connect(update_combo_2)
        #update_combo_2(0)

        # progress bar
        progress_bar = qtw.QProgressBar(self)
        progress_bar.setValue(0)

        # line edit for investment
        line_1 = qtw.QLineEdit()

        # Layouts------------------------------------------------------------------------------------------------------#

        # Labels
        container.layout().addWidget(lb_1, 0, 0, 1, 6)
        container.layout().addWidget(lb_2, 1, 0, 1, 2)
        container.layout().addWidget(lb_3, 1, 3, 1, 2)
        container.layout().addWidget(lb_4, 3, 0, 1, 4)
        container.layout().addWidget(lb_5, 7, 0, 1, 4)

        # Comboboxes
        container.layout().addWidget(cbo_3, 2, 0)
        container.layout().addWidget(cbo_2, 2, 1)
        container.layout().addWidget(cbo_1, 2, 2)
        container.layout().addWidget(cbo_6, 2, 3)
        container.layout().addWidget(cbo_5, 2, 4)
        container.layout().addWidget(cbo_4, 2, 5)

        # Checkboxes
        container.layout().addWidget(chx_1, 4, 0)
        container.layout().addWidget(chx_2, 4, 1)
        container.layout().addWidget(chx_3, 4, 2)

        # Buttons
        container.layout().addWidget(self.btn_1, 5, 0, 1, 6)
        container.layout().addWidget(btn_3, 0, 5)

        # Progress Bar
        container.layout().addWidget(progress_bar, 6, 0, 1, 6)

        # line edit
        #container.layout().addWidget(self.line_1, 0, 4)

        # table

        self.layout().addWidget(container)


# todo exit code https://intellij-support.jetbrains.com/hc/en-us/community/posts/115000176210-Print-Process-finished-with-exit-code-1?page=1#community_comment_115000225664

class Worker(qtc.QThread):
    """Runs Thread"""




app = qtw.QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet())
mw = MainWindow()
app.exec_()  # tells python to run the app
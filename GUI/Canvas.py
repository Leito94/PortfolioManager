import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FQtAgg
from PyQt5.QtWidgets import *
import pandas as pd

spy = pd.read_csv("test_spy.csv", index_col = 0)
#print(spy)

class Canvas(FQtAgg):
    def __init__(self, parent):
        fig, self.ax = plt.subplots(figsize = (5,4), dpi = 200)
        super().__init__(fig)
        self.setParent(parent)

        fig, ax = plt.subplots(figsize=(5, 4), dpi=200)

        self.ax.plot(spy.index, spy.kum_ret)
        self.ax.plot(spy.index, spy.kum_port_rets)
        self.ax.set(xlabel="date", ylabel="cumulative return",
                    title="SPY vs my Portfolio")
        fig.autofmt_xdate()


        self.ax.grid()

class AppDemo(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(1600, 800)

        chart = Canvas(self)

app = QApplication(sys.argv)
demo = AppDemo()
demo.show()
sys.exit(app.exec_())





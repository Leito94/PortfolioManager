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
from PyQt5.QtWidgets import QApplication

# Import the datasets
price_data = pd.read_csv("../relevant_price_data_from_2016.csv", index_col=0) # todo automatically update price data
fundamental_data = pd.read_csv("../2020-01-25_funds_df.csv", index_col=0)
test_df = price_data[price_data.ticker == "MSFT"]

# get a list of all countries
with open("../countries.json", "r") as f:
    countries = json.load(f)

# List, Dictionary for the dates
years = ["2016", "2017", "2018", "2019", "2020", "2021"]
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
    # widgets are attached here
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PortfolioManager")
        self.setWindowIcon(QIcon("stock-market.png"))
        self.mainLayout = qtw.QGridLayout()
        self.price_data = price_data

        self.model_1 = QStandardItemModel()
        self.model_2 = QStandardItemModel()
        self.setLayout(self.mainLayout)
        # Widgets------------------------------------------------------------------------------------------------------#

        # Labels
        self.lb_1 = qtw.QLabel("Input Start Date and End Date")
        self.lb_2 = qtw.QLabel("Start Date")
        self.lb_3 = qtw.QLabel("End Date")
        self.lb_4 = qtw.QLabel("The Factors the Analysis shall base on")
        self.lb_5 = qtw.QLabel("")
        self.lb_7 = qtw.QLabel("Depth of the Analysis")


        # Comboboxes
        self.cbo_1 = qtw.QComboBox()
        self.cbo_1.addItems(years)

        self.cbo_2 = qtw.QComboBox()
        self.cbo_2.setModel(self.model_1)

        self.cbo_3 = qtw.QComboBox()
        self.cbo_3.setModel(self.model_1)

        self.cbo_4 = qtw.QComboBox()
        self.cbo_4.addItems(years)

        self.cbo_5 = qtw.QComboBox()
        self.cbo_5.setModel(self.model_2)

        self.cbo_6 = qtw.QComboBox()
        self.cbo_6.setModel(self.model_2)

        # CheckBoxes
        self.chx_1 = qtw.QCheckBox("Momentum")
        self.chx_2 = qtw.QCheckBox("Value")
        self.chx_3 = qtw.QCheckBox("Profit")
        self.chx_1.setChecked(False)
        self.chx_2.setChecked(False)
        self.chx_3.setChecked(False)

        # Button
        self.btn_1 = qtw.QPushButton("Start Analysis")
        self.btn_1.setStyleSheet("font: bold;background-color: green;font-size: 16px")
        self.btn_1.clicked.connect(self.start_analysis)
        self.btn_2 = qtw.QPushButton("Performance until today")
        self.btn_2.clicked.connect(self.past_performance)
        self.btn_3 = qtw.QPushButton("Quit", clicked=self.close_program)
        self.btn_3.setStyleSheet("font: bold; background-color: red")
        self.btn_4 = qtw.QPushButton("Update Price Data", clicked=self.update_price_data)
        self.btn_4.setStyleSheet("font: bold; background-color: green")


        # Radio Button
        self.rad_1 = qtw.QRadioButton()
        self.rad_1.setText("Shallow (~2min)")
        self.rad_1.setChecked(True)
        self.rad_2 = qtw.QRadioButton()
        self.rad_2.setText("Normal (~5min)")
        self.rad_3 = qtw.QRadioButton()
        self.rad_3.setText("Deep (~10min)")

        # add combobox data
        # add Data
        for k, v in months_days_dict.items():
            month = QStandardItem(k)
            self.model_1.appendRow(month)
            for value in v:
                day = QStandardItem(str(value))
                month.appendRow(day)

        for k, v in months_days_dict.items():
            month = QStandardItem(k)
            self.model_2.appendRow(month)
            for value in v:
                day = QStandardItem(str(value))
                month.appendRow(day)

        self.cbo_2.currentIndexChanged.connect(self.update_combo_1)
        self.update_combo_1(0)

        self.cbo_5.currentIndexChanged.connect(self.update_combo_2)
        self.update_combo_2(0)

        # progress bar
        self.progress_bar = qtw.QProgressBar(self)
        self.progress_bar.setValue(0)

        # line edit for investment
        self.line_1 = qtw.QLineEdit()

        # Styles
        self.lb_1.setFont(QtGui.QFont("Arial", 13))
        self.lb_2.setFont(QtGui.QFont("Arial", 10))
        self.lb_3.setFont(QtGui.QFont("Arial", 10))
        self.lb_4.setFont(QtGui.QFont("Arial", 10))
        self.lb_7.setFont(QtGui.QFont("Arial", 10))
        self.chx_1.setFont(QtGui.QFont("Arial", 11))
        self.chx_2.setFont(QtGui.QFont("Arial", 11))
        self.chx_3.setFont(QtGui.QFont("Arial", 11))
        self.btn_1.setFont(QtGui.QFont("Arial", 13, QFont.Bold))
        self.rad_1.setFont(QtGui.QFont("Arial", 11))
        self.rad_2.setFont(QtGui.QFont("Arial", 11))
        self.rad_3.setFont(QtGui.QFont("Arial", 11))

        # Layouts------------------------------------------------------------------------------------------------------#

        # Labels
        self.mainLayout.layout().addWidget(self.lb_1, 0, 0, 1, 6)
        self.mainLayout.layout().addWidget(self.lb_2, 1, 0, 1, 2)
        self.mainLayout.layout().addWidget(self.lb_3, 1, 3, 1, 2)
        self.mainLayout.layout().addWidget(self.lb_4, 3, 0, 1, 3)
        self.mainLayout.layout().addWidget(self.lb_5, 7, 0, 1, 4)
        self.mainLayout.layout().addWidget(self.lb_7, 3, 3, 1, 3)

        # Comboboxes
        self.mainLayout.layout().addWidget(self.cbo_3, 2, 0)
        self.mainLayout.layout().addWidget(self.cbo_2, 2, 1)
        self.mainLayout.layout().addWidget(self.cbo_1, 2, 2)
        self.mainLayout.layout().addWidget(self.cbo_6, 2, 3)
        self.mainLayout.layout().addWidget(self.cbo_5, 2, 4)
        self.mainLayout.layout().addWidget(self.cbo_4, 2, 5)

        # Checkboxes
        self.mainLayout.layout().addWidget(self.chx_1, 4, 0)
        self.mainLayout.layout().addWidget(self.chx_2, 4, 1)
        self.mainLayout.layout().addWidget(self.chx_3, 4, 2)

        # Buttons
        self.mainLayout.layout().addWidget(self.btn_1, 5, 0, 1, 6)
        self.mainLayout.layout().addWidget(self.btn_3, 0, 5)
        self.mainLayout.layout().addWidget(self.btn_4, 0, 3, 1 ,2)

        # Progress Bar
        self.mainLayout.layout().addWidget(self.progress_bar, 6, 0, 1, 6)

        # Radio Button
        self.mainLayout.layout().addWidget(self.rad_1, 4, 3)
        self.mainLayout.layout().addWidget(self.rad_2, 4, 4)
        self.mainLayout.layout().addWidget(self.rad_3, 4, 5)

        # line edit
        # self.mainLayout.layout().addWidget(self.line_1, 0, 4)

        # table
        # End main UI code
        self.show()

        self.restart_program = False

    # Functions--------------------------------------------------------------------------------------------------------#

    def close_program(self):
        sys.exit()

    def increase_step(self):
        self.progress_bar.setValue(self.progress_bar.value() + 1)


    def get_maximum_progress(self):
        checked_list = [self.chx_1.isChecked(), self.chx_2.isChecked(), self.chx_3.isChecked()]
        if checked_list == [True, True, True]:
            self.progress_bar.setMaximum(91)
        elif checked_list == [True, False, True] or checked_list == [True, True, False]:
            self.progress_bar.setMaximum(79)
        elif checked_list == [False, True, True]:
            self.progress_bar.setMaximum(59)
        elif checked_list == [True, False, False]:
            self.progress_bar.setMaximum(32)
        elif checked_list == [False, True, False] or checked_list == [False, False, True]:
            self.progress_bar.setMaximum(47)
        elif checked_list == [False, False, False]:
            message = qtw.QMessageBox.critical(self, "Error", "Please choose factors")
            self.restart_program = True

    def update_combo_1(self, index):
        indx = self.model_1.index(index, 0, self.cbo_1.rootModelIndex())
        self.cbo_3.setRootModelIndex(indx)
        self.cbo_3.setCurrentIndex(0)

    def update_combo_2(self, index):
        indx = self.model_2.index(index, 0, self.cbo_5.rootModelIndex())
        self.cbo_6.setRootModelIndex(indx)
        self.cbo_6.setCurrentIndex(0)
        # TODO dont reset day for the two functions above

    def update_price_data(self):

        # setting up the progress bar
        self.progress_bar.setMaximum(100)

        # set label text
        self.lb_5.setText("downloading price data...this may take a while...")

        # get the latest date + 1
        last_date = self.price_data.date.max()
        latest_date = datetime.datetime.strptime(last_date, '%Y-%m-%d')
        latest_date += datetime.timedelta(days=1)
        latest_date = latest_date.strftime("%Y-%m-%d")

        # date today, get last business day
        today = datetime.datetime.today()
        offset = max(1, (today.weekday() + 6) % 7 - 3)
        timedelta = datetime.timedelta(offset)
        today = today - timedelta
        today = today.strftime("%Y-%m-%d")
        print("today: " + today + "\nlast_date: " + last_date + " \nlatest_date: " + latest_date)
        if today == last_date:
            message = qtw.QMessageBox.information(self, "Current Data", "The data is already up to date!")
            return
        # all the tickers
        tickers = self.price_data.ticker.unique()

        # calculate stepsize
        stepsize = len(tickers) // 100
        print("stepsize: " + str(stepsize))

        price_data_list = []
        count = 0

        for ticker in tickers:
            try:
                ticker_data = si.get_data(ticker, start_date=latest_date, end_date=today)
                ticker_data["ticker"] = ticker
                price_data_list.append(ticker_data)
                count += 1
                if count % 200 == 0:
                    print(count)
                if count % stepsize == 0:
                    self.increase_step()
                print("found data for " + ticker)
                QApplication.processEvents()
            except:
                print("could not find price_data for " + ticker)
                count += 1
                if count % 200 == 0:
                    print(count)
                if count % stepsize == 0:
                    self.increase_step()
                QApplication.processEvents()
        # set label text
        self.lb_5.setText("concatenating dataframes")

        # concat the data
        new_data = pd.concat(price_data_list)
        # get relevant columns
        tickers_data = new_data[["ticker", "adjclose"]]

        # correct the names
        tickers_data.insert(0, "date", new_data.index)

        # convert to string
        tickers_data.date = [date.strftime("%Y-%m-%d") for date in tickers_data.date]
        tickers_data.columns = self.price_data.columns

        # compare lengths to avoid errors
        len_old_data = len(self.price_data)

        # add the data together
        self.price_data = self.price_data.append(tickers_data)

        len_new_data = len(self.price_data)

        # compare lengths
        print("length of old data: " + str(len_old_data) + "\n length of new data: " + str(len_new_data))

        # reset progress bar
        self.progress_bar.setValue(0)

        if len_new_data > len_old_data:
            # saving as csv
            self.lb_5.setText("saving dataframe as csv...")

            # save df
            self.price_data.to_csv("../relevant_price_data_from_2016.csv")

            # done
            self.lb_5.setText("")
        else:
            message = qtw.QMessageBox.critical(self, "Error", "Something went wrong.\n The data was not successfully updated!")
            return

    def createTable(self, portfolio_df):

        self.table.setRowCount(len(self.portfolio_df))

        # Column count
        self.tableWidget.setColumnCount(5)

        columns = self.portfolio_df.columns
        c = 0
        for col in columns:
            array = self.portfolio_df[col]
            r = 0
            for row in array:
                self.tableWidget.setItem(r, c, qtw.QTableWidgetItem(row))
                r += 1
            c += 1

    def get_funds_date(self, year, month, day, ticker):

        date = datetime.date(year, month, day)
        self.start_date = date.strftime("%Y-%m-%d")

        # first check if there is a date before the starting date of the analysis
        ticker_funds = fundamental_data[fundamental_data.ticker == ticker]
        ticker_funds = ticker_funds.sort_values(by="date", ascending=False)
        for date in ticker_funds.date:
            if date < self.start_date:
                day = int(date[-2:])
                month = int(date[-5:-3])
                year = int(date[:4])
                date = datetime.date(year, month, day)
                date = date.strftime("%Y-%m-%d")
                return date
        return np.nan

    def get_correct_date(self, day, month, year, test_df):
        date = datetime.date(year, month, day)
        date = date.strftime("%Y-%m-%d")
        while len(test_df[test_df.date == date]) == 0:
            if month == 12 and day == 31:
                year += 1
                day = 1
                month = 1
                date = datetime.date(year, month, day)
                date = date.strftime("%Y-%m-%d")

            else:
                try:
                    day += 1
                    date = datetime.date(year, month, day)
                    date = date.strftime("%Y-%m-%d")

                except:
                    month += 1
                    day = 1
                    date = datetime.date(year, month, day)
                    date = date.strftime("%Y-%m-%d")
        return date

    def get_latest_fundamentals(self):
        self.lb_5.setText("computing fundamental data...")
        funds_dates = []
        funds_ticker = []
        funds_at = []
        funds_op = []
        funds_so = []
        funds_be = []
        prices = []
        # for progress bar. This should be 15 percent.
        count = 0
        stepper = len(fundamental_data.ticker.unique()) // 35

        for ticker in fundamental_data.ticker.unique():

            rel_date = self.get_funds_date(int(self.cbo_1.currentText()),
                                           list(months_days_dict.keys()).index(self.cbo_2.currentText()) + 1,
                                           int(self.cbo_3.currentText()), ticker)
            try:
                funds_at.append(
                    fundamental_data[(fundamental_data.date == rel_date) & (fundamental_data.ticker == ticker)][
                        "assets"].item())
            except:
                funds_at.append(np.nan)

            try:
                funds_be.append(
                    fundamental_data[(fundamental_data.date == rel_date) & (fundamental_data.ticker == ticker)][
                        "book_equity"].item())
            except:
                funds_be.append(np.nan)
            try:
                funds_op.append(
                    fundamental_data[(fundamental_data.date == rel_date) & (fundamental_data.ticker == ticker)][
                        "ebit"].item())
            except:
                funds_op.append(np.nan)
            try:
                funds_so.append(
                    fundamental_data[(fundamental_data.date == rel_date) & (fundamental_data.ticker == ticker)][
                        "shares_outstanding"].item())
            except:
                funds_so.append(np.nan)
            try:
                prices.append(self.start_price[self.start_price.ticker == ticker]["adj_close"].item())
            except:
                prices.append(np.nan)

            funds_dates.append(rel_date)
            funds_ticker.append(ticker)
            count += 1
            if count % stepper == 0:
                self.increase_step()
            QApplication.processEvents()

        self.fund_df = pd.DataFrame({
            "ticker": funds_ticker,
            "date": funds_dates,
            "at": funds_at,
            "op": funds_op,
            "so": funds_so,
            "b_e" : funds_be,
            "adj_close": prices
        })

        # market value
        self.fund_df["mar_cap"] = self.fund_df.so * self.fund_df.adj_close
        # book-to-market
        self.fund_df["beme"] = self.fund_df["b_e"] / self.fund_df["mar_cap"]
        # Profitability
        self.fund_df["prof"] = self.fund_df["op"] / self.fund_df["at"]

        return self.fund_df

    def compute_momentum(self):
        self.lb_5.setText("computing momentum...")
        # two dataframes
        end_price = self.price_data[self.price_data.date == self.end_date]
        momentum_list = []
        mom_ticker_list = []
        # vars for progress bar, here should be 5% progress made
        count = 0
        stepper = len(self.start_price) // 5
        print(stepper)
        for ticker in self.start_price.ticker:
            try:
                date_price = self.start_price[self.start_price.ticker == ticker][:1]["adj_close"].item()
                today_price = end_price[end_price.ticker == ticker][:1]["adj_close"].item()
                momentum = (today_price - date_price) / date_price
                momentum_list.append(momentum)
                mom_ticker_list.append(ticker)
                count += 1
                if count % stepper == 0:
                    self.increase_step()
                QApplication.processEvents()

            except:
                count += 1
                if count % stepper == 0:
                    self.increase_step()



        self.m_df = pd.DataFrame({
            "ticker": mom_ticker_list,
            "momentum": momentum_list
        })

        self.m_df = self.m_df.sort_values(by="momentum", ascending=False)
        self.m_df.reset_index(drop=True, inplace=True)

        return self.m_df

    def momentum_scraping(self):
        self.lb_5.setText("webscraping momentum stocks data...")
        name_list = []

        # for progress bar. This should be 18%
        count = 0
        stepper = len(self.momentum_stocks) // 9
        for ticker in self.momentum_stocks:
            try:
                url = "https://finance.yahoo.com/quote/{}/key-statistics?p={}"
                response = requests.get(url.format(ticker, ticker))
                soup = bs(response.text, "html.parser")
                pattern = re.compile(r"\s--\sData\s--\s")
                script_data = soup.find("script", text=pattern).contents[0]
                start = script_data.find("context") - 2
                json_data = json.loads(script_data[start:-12])
                short_name = json_data["context"]["dispatcher"]["stores"]["QuoteSummaryStore"]["quoteType"]["shortName"]
                name_list.append(short_name)
                count += 1
                if count % stepper == 0:
                    self.increase_step()
                QApplication.processEvents()
            except:
                name_list.append(np.nan)
                count += 1
                if count % stepper == 0:
                    self.increase_step()


        # reset count
        count = 0
        country_list = []

        for ticker in self.momentum_stocks:
            try:
                url = "https://finance.yahoo.com/quote/{}/profile?p={}"

                r = requests.get(url.format(ticker, ticker))
                soup = bs(r.content, features="lxml")
                info = soup.find_all("p", attrs={"class", "D(ib) W(47.727%) Pend(40px)"})
                for c in countries:
                    if c in info[0].text:
                        country_list.append(c)
                        break
                count += 1
                if count % stepper == 0:
                    self.increase_step()
                QApplication.processEvents()
            except:
                country_list.append(np.nan)
                count += 1
                if count % stepper == 0:
                    self.increase_step()

        # reset count
        count = 0
        industry_list = []

        for ticker in self.momentum_stocks:
            try:
                url = "https://finance.yahoo.com/quote/{}/profile?p={}"
                response = requests.get(url.format(ticker, ticker))
                soup = bs(response.text, features="lxml")

                industry = soup.find_all("span", {"class": "Fw(600)"})[0].text
                industry_list.append(industry)
                count += 1
                if count % stepper == 0:
                    self.increase_step()
                QApplication.processEvents()
            except:
                industry_list.append(np.nan)
                count += 1
                if count % stepper == 0:
                    self.increase_step()

        self.momentum_df = pd.DataFrame({
            "ticker": self.momentum_stocks,
            "names": name_list,
            "industry": industry_list,
            "country": country_list

        })
        self.momentum_df = self.momentum_df.dropna()
        return self.momentum_df

    def value_scraping(self):
        self.lb_5.setText("webscraping value stocks data...")
        name_list = []
        # for progress bar. This should be 9%
        count = 0
        stepper = len(self.value_stocks) // 4

        for ticker in self.value_stocks:
            try:
                url_shares_outstanding = "https://finance.yahoo.com/quote/{}/key-statistics?p={}"
                response = requests.get(url_shares_outstanding.format(ticker, ticker))
                soup = bs(response.text, "html.parser")
                pattern = re.compile(r"\s--\sData\s--\s")
                script_data = soup.find("script", text=pattern).contents[0]
                start = script_data.find("context") - 2
                json_data = json.loads(script_data[start:-12])
                short_name = json_data["context"]["dispatcher"]["stores"]["QuoteSummaryStore"]["quoteType"]["shortName"]
                name_list.append(short_name)
                count += 1
                if count % stepper == 0:
                    self.increase_step()
                QApplication.processEvents()
            except:
                name_list.append(np.nan)
                count += 1
                if count % stepper == 0:
                    self.increase_step()
        # reset count
        count = 0
        country_list = []

        for ticker in self.value_stocks:
            try:
                url = "https://finance.yahoo.com/quote/{}/profile?p={}"

                r = requests.get(url.format(ticker, ticker))
                soup = bs(r.content, features="lxml")
                info = soup.find_all("p", attrs={"class", "D(ib) W(47.727%) Pend(40px)"})
                for c in countries:
                    if c in info[0].text:
                        country_list.append(c)
                        break
                count += 1
                QApplication.processEvents()
                if count % stepper == 0:
                    self.increase_step()
            except:
                country_list.append(np.nan)
                count += 1
                if count % stepper == 0:
                    self.increase_step()

        # reset count
        count = 0
        industry_list = []

        for ticker in self.value_stocks:
            try:
                url = "https://finance.yahoo.com/quote/{}/profile?p={}"
                response = requests.get(url.format(ticker, ticker))
                soup = bs(response.text, features="lxml")

                industry = soup.find_all("span", {"class": "Fw(600)"})[0].text
                industry_list.append(industry)
                count += 1
                if count % stepper == 0:
                    self.increase_step()
                QApplication.processEvents()
            except:
                industry_list.append(np.nan)
                count += 1
                if count % stepper == 0:
                    self.increase_step()

        self.value_df = pd.DataFrame({
            "ticker": self.value_stocks,
            "names": name_list,
            "industry": industry_list,
            "country": country_list

        })
        self.value_df = self.value_df.dropna()
        return self.value_df

    def profit_scraping(self):
        self.lb_5.setText("webscraping profit stocks data...")

        name_list = []
        # for progress bar. This should be 9%
        count = 0
        stepper = len(self.profit_stocks) // 4

        for ticker in self.profit_stocks:
            try:
                url_shares_outstanding = "https://finance.yahoo.com/quote/{}/key-statistics?p={}"
                response = requests.get(url_shares_outstanding.format(ticker, ticker))
                soup = bs(response.text, "html.parser")
                pattern = re.compile(r"\s--\sData\s--\s")
                script_data = soup.find("script", text=pattern).contents[0]
                start = script_data.find("context") - 2
                json_data = json.loads(script_data[start:-12])
                short_name = json_data["context"]["dispatcher"]["stores"]["QuoteSummaryStore"]["quoteType"]["shortName"]
                name_list.append(short_name)
                count += 1
                if count % stepper == 0:
                    self.increase_step()
                QApplication.processEvents()
            except:
                name_list.append(np.nan)
                count += 1
                if count % stepper == 0:
                    self.increase_step()

        # reset count
        count = 0
        country_list = []

        for ticker in self.profit_stocks:
            try:
                url = "https://finance.yahoo.com/quote/{}/profile?p={}"

                r = requests.get(url.format(ticker, ticker))
                soup = bs(r.content, features="lxml")
                info = soup.find_all("p", attrs={"class", "D(ib) W(47.727%) Pend(40px)"})
                for c in countries:
                    if c in info[0].text:
                        country_list.append(c)
                        break
                count += 1
                if count % stepper == 0:
                    self.increase_step()
                QApplication.processEvents()
            except:
                country_list.append(np.nan)
                count += 1
                if count % stepper == 0:
                    self.increase_step()

        # reset count
        count = 0
        industry_list = []

        for ticker in self.profit_stocks:
            try:
                url = "https://finance.yahoo.com/quote/{}/profile?p={}"
                response = requests.get(url.format(ticker, ticker))
                soup = bs(response.text, "lxml")

                industry = soup.find_all("span", {"class": "Fw(600)"})[0].text
                industry_list.append(industry)
                count += 1
                if count % stepper == 0:
                    self.increase_step()
                QApplication.processEvents()
            except:
                industry_list.append(np.nan)
                count += 1
                if count % stepper == 0:
                    self.increase_step()

        self.profit_df = pd.DataFrame({
            "ticker": self.profit_stocks,
            "names": name_list,
            "industry": industry_list,
            "country": country_list

        })
        self.profit_df = self.profit_df.dropna()
        return self.profit_df

    def find_next_company(self, df, industry_list, country_list, portfolio):
        portfolio.reset_index(drop=True, inplace=True)
        port_names = portfolio.names.tolist()
        for i in range(len(df)):
            name = df.loc[i]["names"]
            country = df.loc[i]["country"]
            industry = df.loc[i]["industry"]
            if name not in port_names and country_list.count(country) < 4 and industry_list.count(industry) < 4:
                return df.loc[i]

    def diversify_portfolio(self):
        self.lb_5.setText("diversifying the portfolio...")
        if self.chx_1.isChecked():
            self.momentum_df["factor"] = "momentum"
            self.momentum_df.reset_index(drop=True, inplace=True)

        if self.chx_2.isChecked():
            self.value_df["factor"] = "value"
            self.value_df.reset_index(drop=True, inplace=True)

        if self.chx_3.isChecked():
            self.profit_df["factor"] = "profit"
            self.profit_df.reset_index(drop=True, inplace=True)

        industry_list = []
        country_list = []
        self.portfolio_df = pd.DataFrame(columns=["ticker", "names", "industry", "country", "factor"])
        check_list = [self.chx_1.isChecked(), self.chx_2.isChecked(), self.chx_3.isChecked()]

        # if all three are checked
        if check_list == [True, True, True]:
            while len(self.portfolio_df) < self.port_length:
                nones = 0
                new_portfolio_entry = self.find_next_company(self.momentum_df, industry_list, country_list, self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    nones += 1

                new_portfolio_entry = self.find_next_company(self.value_df, industry_list, country_list, self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    nones += 1

                new_portfolio_entry = self.find_next_company(self.momentum_df, industry_list, country_list, self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    nones += 1

                new_portfolio_entry = self.find_next_company(self.profit_df, industry_list, country_list, self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    nones += 1

                if nones == 4:
                    break
        # if only momentum is checked
        if check_list == [True, False, False]:

            while len(self.portfolio_df) < self.port_length:
                new_portfolio_entry = self.find_next_company(self.momentum_df, industry_list, country_list, self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    break
        # if only value is checked
        if check_list == [False, True, False]:

            while len(self.portfolio_df) < self.port_length:
                new_portfolio_entry = self.find_next_company(self.value_df, industry_list, country_list, self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    break
        # if only profit is checked
        if check_list == [False, False, True]:

            while len(self.portfolio_df) < self.port_length:
                new_portfolio_entry = self.find_next_company(self.profit_df, industry_list, country_list, self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    break
        # if momentum and value are checked
        if check_list == [True, True, False]:

            while len(self.portfolio_df) < self.port_length:
                nones = 0
                new_portfolio_entry = self.find_next_company(self.momentum_df, industry_list, country_list, self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    nones += 1

                new_portfolio_entry = self.find_next_company(self.value_df, industry_list, country_list, self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    nones += 1

                if nones == 2:
                    break

        # if momentum and profit are checked
        if check_list == [True, False, True]:

            while len(self.portfolio_df) < self.port_length:
                nones = 0
                new_portfolio_entry = self.find_next_company(self.momentum_df, industry_list, country_list,
                                                             self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    nones += 1

                new_portfolio_entry = self.find_next_company(self.profit_df, industry_list, country_list,
                                                             self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    nones += 1

                if nones == 2:
                    break

        # if value and profit are checked
        if check_list == [False, True, True]:

            while len(self.portfolio_df) < self.port_length:
                nones = 0
                new_portfolio_entry = self.find_next_company(self.value_df, industry_list, country_list,
                                                             self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    nones += 1

                new_portfolio_entry = self.find_next_company(self.profit_df, industry_list, country_list,
                                                             self.portfolio_df)
                if new_portfolio_entry is not None:

                    industry_list.append(new_portfolio_entry.industry)
                    country_list.append(new_portfolio_entry.country)
                    self.portfolio_df = self.portfolio_df.append(new_portfolio_entry)
                else:
                    nones += 1

                if nones == 2:
                    break

        return self.portfolio_df

    def past_performance(self):
        self.lb_5.setText("downloading plot data...")

        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.portfolio_df) * 3)
        self.btn_1.setText("Processing...")

        today = self.price_data.date[-1]  # latest date in our dataset

        port_data = pd.DataFrame()

        for ticker in self.portfolio_df.ticker:
            try:
                stock_df = si.get_data(ticker, start_date=self.end_date, end_date=today)[["adjclose", "ticker"]]
                port_data = port_data.append(stock_df)
                self.increase_step()
                QApplication.processEvents()
            except:
                self.increase_step()

        msci_world = si.get_data("xwd.to", start_date=self.end_date, end_date=today)[["adjclose", "ticker"]]
        nan_ticker = port_data[port_data.adjclose.isna()]["ticker"].unique()

        port_data = port_data[~port_data.ticker.isin(nan_ticker)]
        port_data.reset_index(drop=True, inplace=True)

        unique_tickers = port_data.ticker.unique()
        data_df_list = []
        for ticker in unique_tickers:
            return_list = [np.nan]
            ticker_df = port_data[port_data.ticker == ticker]
            n = 1
            ticker_df.reset_index(drop=True, inplace=True)
            self.increase_step()
            while n <= len(ticker_df) - 1:
                day_ret = ((ticker_df.loc[n]["adjclose"] - ticker_df.loc[n - 1]["adjclose"]) / ticker_df.loc[n - 1][
                    "adjclose"]) * 100
                return_list.append(day_ret)
                n += 1
            ticker_df["returns"] = return_list
            data_df_list.append(ticker_df)
            QApplication.processEvents()

        live_prices = []

        for tick in self.portfolio_df.ticker:
            t = si.get_live_price(tick)
            live_prices.append(t)
            self.increase_step()
            QApplication.processEvents()

        self.portfolio_df["live_price"] = live_prices

        lenghts = [len(i) for i in data_df_list]
        max_len = max(lenghts)
        print("das maximum:", max_len)

        relevant_df_list = []
        for df in data_df_list:
            if len(df) == max_len:
                relevant_df_list.append(df)
                self.increase_step()

        kum_ret = []
        n = 0
        while n < len(msci_world):
            ret = ((msci_world.adjclose[n] - msci_world.adjclose[0]) / msci_world.adjclose[0]) * 100
            kum_ret.append(ret)
            n += 1
        msci_world["kum_ret"] = kum_ret

        for index, df in enumerate(relevant_df_list):
            kum_ret = []
            n = 0
            while n < len(df):
                ret = ((df.adjclose[n] - df.adjclose[0]) / df.adjclose[0]) * 100
                kum_ret.append(ret)
                n += 1
            df["kum_ret"] = kum_ret

        investment = 300
        # TODO add entry with investment

        fraction_list = []

        for price in live_prices:
            fraction = investment / (len(live_prices)) / price
            fraction_list.append(fraction)

        self.portfolio_df["fraction"] = fraction_list

        n = 0
        kum_port_rets = []
        while n < len(msci_world):
            try:
                rets = [relevant_df_list[m].loc[n]["kum_ret"] for m in range(len(relevant_df_list))]
                kum_port_ret = sum(rets) / len(relevant_df_list)
                kum_port_rets.append(kum_port_ret)

                n += 1
                last_date = n
            except:
                last_date = n
                print("return was not calculated for", str(n))
                break
        #msci_world["kum_port_rets"] = kum_port_rets
        print(len(msci_world.index[:last_date]))
        print(len(msci_world.kum_ret[:last_date]))
        print(len(msci_world.index[:last_date]))
        print(len(kum_port_rets))
        plt.plot(msci_world.index[:last_date], msci_world.kum_ret[:last_date], "blue", label="MSCI World Index")
        plt.plot(msci_world.index[:last_date], kum_port_rets, "red", label="My Portfolio")
        plt.legend()
        plt.xlabel("date")
        plt.ylabel("cumulative return")
        plt.title("MSCI World vs My Portfolio")
        plt.show()

        self.btn_1.clicked.disconnect()
        self.btn_1.setText("Start Analysis")
        self.btn_1.clicked.connect(self.start_analysis)
        self.progress_bar.setValue(0)
        self.lb_5.setText("")

    def create_table(self, portfolio_df):
        self.lb_6 = qtw.QLabel("the engine recommends following portfolio:")
        self.tableWidget = qtw.QTableWidget()

        self.tableWidget.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.Stretch)
        # Row count
        self.tableWidget.setRowCount(len(self.portfolio_df))

        # Column count
        self.tableWidget.setColumnCount(len(self.portfolio_df.columns))

        columns = self.portfolio_df.columns
        c = 0
        for col in columns:
            array = self.portfolio_df[col]
            r = 0
            for row in array:
                self.tableWidget.setItem(r, c, qtw.QTableWidgetItem(row))
                r += 1
            c += 1

        self.tableWidget.setHorizontalHeaderLabels(self.portfolio_df.columns)

        # styles
        self.lb_6.setFont(QtGui.QFont("Arial", 12))
        # self.lb_6.setStyleSheet("color: rgb(0,153,76)")
        # self.tableWidget.setStyleSheet("Background-color:rgb(153,153,255);border-radius:14px")
        # todo style table

        # layout
        self.mainLayout.layout().addWidget(self.lb_6, 8, 0, 1, 6)
        self.mainLayout.layout().addWidget(self.tableWidget, 9, 0, 1, 6)

    def start_analysis(self):

        self.get_maximum_progress()
        if self.restart_program:
            self.btn_1.clicked.connect(self.start_analysis)
            self.restart_program = False
            return
        else:
            self.btn_1.disconnect()
            self.btn_1.setText("processing...")
            print("start")
            # set the progress maximums
            # self.btn_1.clicked.connect(stop_program)
            # get the correct dates so that we dont have empty dfs
            today_date = datetime.date.today().strftime("%Y-%m-%d")
            # todo if future is selected restart
            # check input dates
            input_start_date = datetime.date(int(self.cbo_1.currentText()),
                                               list(months_days_dict.keys()).index(self.cbo_2.currentText()) + 1,
                                               int(self.cbo_3.currentText())).strftime("%Y-%m-%d")
            input_end_date = datetime.date(int(self.cbo_4.currentText()),
                                             list(months_days_dict.keys()).index(self.cbo_5.currentText()) + 1,
                                             int(self.cbo_6.currentText())).strftime("%Y-%m-%d")

            print(today_date, input_end_date, input_start_date)

            if input_end_date > today_date or input_start_date > today_date:
                error = qtw.QMessageBox.critical(self, "Error", "Time travel is not yet invented. \n Please no future dates!")
                self.btn_1.clicked.connect(self.start_analysis)
                self.btn_1.setText("Start Analysis")
                return

            self.start_date = self.get_correct_date(int(self.cbo_3.currentText()),
                                               list(months_days_dict.keys()).index(self.cbo_2.currentText()) + 1,
                                               int(self.cbo_1.currentText()), test_df)
            self.end_date = self.get_correct_date(int(self.cbo_6.currentText()),
                                             list(months_days_dict.keys()).index(self.cbo_5.currentText()) + 1,
                                             int(self.cbo_4.currentText()), test_df)
            print(self.end_date)
            if self.end_date < self.start_date or self.end_date == self.start_date:
                error = qtw.QMessageBox.critical(self, "Error", "Start date must be before end date!")
                self.btn_1.clicked.connect(self.start_analysis)
                self.btn_1.setText("Start Analysis")
                return
            else:
                self.start_price = self.price_data[self.price_data.date == self.start_date]
                # compute factor companies depending on checkboxes

                if self.chx_2.isChecked() or self.chx_3.isChecked():

                    self.get_latest_fundamentals()
                    if self.chx_2.isChecked():
                        self.value_stocks_df = self.fund_df.sort_values(by="beme", ascending=False)
                        if self.rad_1.isChecked():
                            self.value_stocks = self.value_stocks_df[:5]["ticker"].to_list()
                            self.value_scraping()
                            print("val done")
                            self.port_length = 10
                        if self.rad_2.isChecked():
                            self.value_stocks = self.value_stocks_df[:15]["ticker"].to_list()
                            self.value_scraping()
                            print("val done")
                            self.port_length = 20
                        if self.rad_3.isChecked():
                            self.value_stocks = self.value_stocks_df[:25]["ticker"].to_list()
                            self.value_scraping()
                            print("val done")
                            self.port_length = 30

                    if self.chx_3.isChecked():
                        self.profit_stocks_df = self.fund_df.sort_values(by="prof", ascending=False)
                        if self.rad_1.isChecked():
                            self.profit_stocks = self.profit_stocks_df[:5]["ticker"].to_list()
                            # TODO for the three dfs insert rows depending on country(industry (dont have too many as theyll be ignored later anywyy)
                            # that means I would have to scrape accordingly (industry and country wuld have to be scraped first
                            self.profit_scraping()
                            print("pro done")
                            self.port_length = 10
                        if self.rad_2.isChecked():
                            self.profit_stocks = self.profit_stocks_df[:15]["ticker"].to_list()
                            self.profit_scraping()
                            print("pro done")
                            self.port_length = 20
                        if self.rad_3.isChecked():
                            self.profit_stocks = self.profit_stocks_df[:25]["ticker"].to_list()
                            self.profit_scraping()
                            print("pro done")
                            self.port_length = 30

                if self.chx_1.isChecked():
                    # momentum df
                    self.compute_momentum()
                    if self.rad_1.isChecked():
                        self.momentum_stocks = self.m_df[:15]["ticker"].to_list()
                        self.momentum_scraping()
                        self.port_length = 10
                    if self.rad_2.isChecked():
                        self.momentum_stocks = self.m_df[:45]["ticker"].to_list()
                        self.momentum_scraping()
                        self.port_length = 20
                    if self.rad_3.isChecked():
                        self.momentum_stocks = self.m_df[:75]["ticker"].to_list()
                        self.momentum_scraping()
                        self.port_length = 30
                # diversify portfolio
                self.diversify_portfolio()
                print(self.portfolio_df)

                self.create_table(self.portfolio_df)
                self.btn_1.setText("Show Past Performance")
                self.btn_1.clicked.connect(self.past_performance)
                self.lb_5.setText("finished")
                self.setWindowState(qtc.Qt.WindowMaximized)


app = qtw.QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet())
mw = MainWindow()
mw.show()
app.exec_()  # tells python to run the app

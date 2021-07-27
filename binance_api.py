import datetime
import tkinter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pandas.core.indexes import base
from tkinter import *
from binance.client import Client
from tkinter.ttk import Frame, Button, Entry, Style
from tkinter import messagebox

"""
This bot contains 2 classes, one (API) for getting data from Binance API you can install it by "pip: install python-binance"
by using this class you can access available coins in Binance market also you can use get daily, hourly,minutely coin data.
another class GUI is a class which inherence from API, you can plot and save data to .xlsx from, and also you can see your balance 
account wallet. 

before the start, you need to register in binance.com and get api_key and api_secret:
client = Client(api_key, api_secret)
"""

# client = Client('api_key' , 'api_secret')

class API:
    def __init__(self):
        self.coins_list = []
        self.available_coins = []
        self.concat_list = []
        self.concat_dataframe = None
        self.active_account = None
        self.cash = None
        self.time_dict = {
            "12h": Client.KLINE_INTERVAL_12HOUR,
            "15m": Client.KLINE_INTERVAL_15MINUTE,
            "1d": Client.KLINE_INTERVAL_1DAY,
            "1h": Client.KLINE_INTERVAL_1HOUR,
            "1m": Client.KLINE_INTERVAL_1MINUTE,
            "1M": Client.KLINE_INTERVAL_1MONTH,
            "1w": Client.KLINE_INTERVAL_1WEEK,
            "2h": Client.KLINE_INTERVAL_2HOUR,
            "30m": Client.KLINE_INTERVAL_30MINUTE,
            "3d": Client.KLINE_INTERVAL_3DAY,
            "3m": Client.KLINE_INTERVAL_3MINUTE,
            "4h": Client.KLINE_INTERVAL_4HOUR,
            "5m": Client.KLINE_INTERVAL_5MINUTE,
            "6h": Client.KLINE_INTERVAL_6HOUR,
            "8h": Client.KLINE_INTERVAL_8HOUR,
        }

    def get_coin(self, *coins, time, days, end=None):
        """
        times " 12h, 15m, 1d, 1h, 1m, 1M, 1w, 2h, 30m, 3d, 3m, 4h, 5m, 6h, 8h
        days : number of days

        return dataframe
        """
        for coin in coins:
            coin = coin + "USDT"
            one = client.get_historical_klines(
                coin, self.time_dict[f"{time}"], f"{days} day ago UTC"
            )
            df = pd.DataFrame(one)
            df.columns = [
                "Open time",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Close time",
                "Quote asset volume",
                "Number of trades",
                "Taker buy base asset volume",
                "Taker buy quote asset volume",
                "ignore",
            ]
            df["Open time"] = pd.to_datetime(df["Open time"], unit="ms")
            df = df.set_index("Open time")
        return df

    def bin_coin_list(self):
        """
        get the list of available coins in binance
        """
        coins = client.get_all_tickers()
        df = pd.DataFrame.from_dict(coins)
        for i, j in enumerate(df.symbol):
            if "BNB" in j:
                k = j.replace("BNB", "")
                print("index ", i, " bin coins is ", j, " coin name ", k)
                self.available_coins.append(k)

    def account_balance(self):
        """
        return deposit_coin, cash
        """
        info = client.get_account()
        active_acount = []
        for diction in info["balances"]:
            asset, free, locked = diction.values()
            if float(free) != 0:
                active_acount.append({"asset": asset, "amount": free})
                if asset == "USDT":
                    self.cash = free

        self.active_account = active_acount

        return active_acount, self.cash


def plot(dataFrame):
    plt.figure(figsize=(10, 8))
    df = dataFrame.copy(deep = True)
    df = df.astype(float)
    df["date"] = pd.to_datetime(df.index)
    df = df.reset_index()
    ax0 = plt.subplot(2, 1, 1)
    ax1 = plt.subplot(2, 1, 2)
    ax0.plot(df["date"], df["Close"], color="red", alpha=0.7, ls="--", label="close")
    ax1.bar(df["date"], df["Volume"], color="darkgreen", alpha=0.6, label="Volume")
    ax1.legend()
    plt.legend()
    ax0.grid()
    ax1.grid()
    plt.tight_layout()
    plt.show()


class GUI(API, Frame):
    def __init__(self, back, bg):
        Frame.__init__(self)
        API.__init__(self)
        Label(self, image=bg).place(x=0, y=0)
        self.coin = None
        self.back = back
        self.create_widgets()

    def get_coins(self):
        self.coin = self.get_coin(
            self.coin_entry.get(),
            time=self.time_entry.get(),
            days=self.period_entry.get(),
        )
        messagebox.showinfo(message="---- get dataframe successfully ----")

    def save(self):
        newWindow = tkinter.Toplevel()
        newWindow.title("saved_file Window")
        newWindow.geometry("350x100+300+300")
        newWindow.configure(background="gray26")
        self.save_file = tkinter.Entry(newWindow, width=30)
        self.save_file.place(x=100, y=20)

        def go():
            weights = self.coin.copy(deep=True)
            weights.to_excel(f"{self.save_file.get()}.xlsx")
            newWindow.destroy()

        bt = tkinter.Button(
            newWindow, text="save", width=10, bd="5", command=go, bg="gray", fg="black"
        ).place(x=140, y=50)

    def plot_coin(self):
        plot(self.coin)

    def quit(self):
        self.back.destroy()

    def show_account(self):
        deposit, cash = self.account_balance()
        coin_list, amount_list, order_book = [], [], pd.DataFrame()
        new_one = Toplevel()
        new_one.title("-- coin repo --")
        new_one.geometry("230x300+300+300")
        scroll = Scrollbar(new_one, orient="vertical", width=8)
        scroll.pack()
        mylist = Listbox(new_one, yscrollcommand=scroll.set, height=200, width=200)
        for dict in deposit:
            for index, val in enumerate(dict.values()):
                if index % 2 == 0:
                    coin_list.append(val)
                else:
                    amount_list.append(val)
        order_book["coin"] = np.array(coin_list)
        order_book["amount"] = np.array(amount_list)
        for coin, amount in zip(order_book["coin"], order_book["amount"]):
            mylist.insert(END, f" you have {amount} amount of {coin}")
        mylist.pack()
        scroll.config(command=mylist.yview)

    def create_widgets(self):
        self.style = Style()
        self.pack(fill=BOTH, expand=True)
        self.style.theme_use("alt")
        self.columnconfigure(0, weight=6)
        self.columnconfigure(1, weight=6)
        self.columnconfigure(0, pad=10)
        self.columnconfigure(1, pad=10)

        self.coin_label = Label(self, text="get_coin", bg="khaki2").grid(
            row=0, column=0, sticky="NSEW", pady=10, padx=10
        )
        self.coin_entry = Entry(self, width=20)
        self.coin_entry.grid(row=0, column=1, padx=10, pady=10)
        self.time_label = Label(self, bg="khaki2", text="Time").grid(
            row=1, column=0, sticky="NSEW", pady=10, padx=10
        )
        self.time_entry = Entry(self, width=20)
        self.time_entry.grid(row=1, column=1, padx=10, pady=10)
        self.period_label = Label(self, bg="khaki2", text="perod_<days>").grid(
            row=3, column=0, sticky="NSEW", pady=10, padx=10
        )
        self.period_entry = Entry(self, width=20)
        self.period_entry.grid(row=3, column=1)
        self.coin_label = tkinter.Button(
            self,
            bd="5",
            text="get_coin",
            fg="khaki1",
            bg="gray26",
            command=self.get_coins,
        ).grid(row=4, column=0, sticky="NSEW", pady=15, padx=10)
        self.coin_label = tkinter.Button(
            self,
            bd="5",
            text="account_info",
            fg="khaki1",
            bg="gray26",
            command=self.show_account,
        ).grid(row=4, column=1, sticky="NSEW", pady=15, padx=10)
        self.coin_label = tkinter.Button(
            self,
            bd="5",
            text="plot_coin",
            fg="khaki1",
            bg="gray26",
            command=self.plot_coin,
        ).grid(row=5, column=0, sticky="NSEW", pady=15, padx=10)

        self.save_but = tkinter.Button(
            self,
            bd="5",
            text="saved_file",
            width=10,
            bg="gray29",
            command=self.save,
            fg="khaki2",
        ).place(x=180, y=300)
        self.quit_but = tkinter.Button(
            self,
            bd="5",
            text="Quit",
            width=10,
            bg="gray29",
            command=self.quit,
            fg="khaki2",
        ).place(x=180, y=350)

def main():
    canvas = Tk()
    canvas.configure(bg="gray29")
    bg = PhotoImage(file="440_400.png")
    canvas.geometry("440x400+300+300")
    GUI(back=canvas, bg=bg)
    canvas.mainloop()


if __name__ == "__main__": main()

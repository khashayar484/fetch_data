import datetime
from hmac import new
import tkinter
from tkinter.constants import TRUE
from typing import Collection
from numpy.lib.arraypad import pad
from numpy.lib.function_base import _select_dispatcher
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time 
from datetime import datetime
import sys
import os
from pandas.core.frame import DataFrame
from pandas.core.indexes import base
from requests.sessions import default_hooks
from sklearn.preprocessing import MinMaxScaler
from tkinter import * 
from binance.client import Client
from tkinter.ttk import Frame, Button, Entry, Style
from tkinter import messagebox



class api():
    def __init__(self ):
        self.coins_list = []
        self.available_coins = []
        self.concat_list = []
        self.concat_dataframe = None
        self.active_account = None
        self.cash = None   
        self.time_dict = { 
        '12h' : Client.KLINE_INTERVAL_12HOUR,
        '15m' : Client.KLINE_INTERVAL_15MINUTE,
        '1d'  : Client.KLINE_INTERVAL_1DAY,
        '1h'  : Client.KLINE_INTERVAL_1HOUR,
        '1m'  : Client.KLINE_INTERVAL_1MINUTE,
        '1M'  : Client.KLINE_INTERVAL_1MONTH,
        '1w'  : Client.KLINE_INTERVAL_1WEEK,
        '2h'  : Client.KLINE_INTERVAL_2HOUR,
        '30m' : Client.KLINE_INTERVAL_30MINUTE,
        '3d'  : Client.KLINE_INTERVAL_3DAY,
        '3m'  : Client.KLINE_INTERVAL_3MINUTE,
        '4h'  : Client.KLINE_INTERVAL_4HOUR,
        '5m'  : Client.KLINE_INTERVAL_5MINUTE,
        '6h'  : Client.KLINE_INTERVAL_6HOUR,
        '8h'  : Client.KLINE_INTERVAL_8HOUR
        }


    def get_coin(self , *coins , time , days , end = None ):
        '''
        times " 12h, 15m, 1d, 1h, 1m, 1M, 1w, 2h, 30m, 3d, 3m, 4h, 5m, 6h, 8h
        days : number of days
        return dataframe
        '''
        
        for coin in coins:
            print('----------> coin is ' , coin , '  time is ' , time , ' days is ' , days)
            coin = coin + 'USDT'

            print('coin is ' , coin)
            print(' time is ' ,  self.time_dict[f'{time}'])
            one = client.get_historical_klines(coin ,  self.time_dict[f'{time}'] , f"{days} day ago UTC")

            df = pd.DataFrame(one)
            df.columns = ['Open time','Open','High','Low','Close','Volume' , 'Close time' , 'Quote asset volume' , 'Number of trades' ,\
                                                    'Taker buy base asset volume' , 'Taker buy quote asset volume' , 'ignore']

            df['Open time'] = pd.to_datetime(df['Open time'] , unit= 'ms')
            df = df.set_index('Open time')

        return df
    

    def concat(self , *coins , time , days , based_col , scale = False , save = False):
        concat = pd.DataFrame([])
        for i in coins:
            print('coin 1 ' , i)
            coin = self.get_coin(i , time = time , days = days )

            df = coin
            print('--------------> based col is ' , based_col)
            con = df[[f'{based_col}']]
            print('con \n' , con)
            con.columns = [f'{i}_{based_col}']
            concat = pd.concat([concat , con] , axis = 1)
        
        print(concat)
        self.concat_dataframe = concat

        if scale:
            mn = MinMaxScaler()
            values = mn.fit_transform(concat)
            df = pd.DataFrame(values , columns = [concat.columns] , index = concat.index)
            print(df)

            for  col in df.columns:
                plt.plot(df[col] , label = col)
            
            plt.title(f'--------------- {days} days -----------------')
            plt.grid()
            plt.legend()
            plt.show()

        return concat

    def balance_info(self , coin):
        '''
        you can access your deposit in binance
        '''
        balance = client.get_asset_balance(asset= coin)
        print('your account is ' , balance)
    
    def save(self , dataframe , name , is_delete = False):
        dir = r'C:\Users\Khashi\Desktop\python\coin_data\{}.xlsx'.format(name)
        if os.path.isfile(dir):
            print('---> u have it')
            if is_delete:
                os.remove(dir)
        else:
            print('u dont have it , saving..')
            dataframe.to_excel(dir)

        print('directory : ' , dir)

    def bin_coin_list(self):
        '''
        get the list of available coins in binance
        ''' 
        coins = client.get_all_tickers()
        df = pd.DataFrame.from_dict(coins)
        for i,j in enumerate(df.symbol):
            if 'BNB' in j:
                k = j.replace('BNB' ,  '')
                print('index ' , i , ' bin coins is ' , j , ' coin name ' , k )
                self.available_coins.append(k)
    
    def info(self):
        '''
        accountType, balances, permissions, etc.
        '''
        info = client.get_account()
        print('your current wallet is ' , info)

    def account_balance(self):
        '''
        get daily account 
        https://python-binance.readthedocs.io/en/latest/
        '''
        deposits = client.get_deposit_history()
        print('your deposit is ' , deposits)
        # info = client.get_account_snapshot(type='SPOT')
        info = client.get_account()
        print('snap shot of your account is ' )

        active_acount = []
        for diction in info['balances']:
            asset , free  , locked = diction.values()
            # print(' coins is ' , asset , ' i have ' , free , ' lock is ' , locked)
            if float(free) != 0:
                # print(' you have this ' , asset , ' and amount is ' , locked)
                active_acount.append({"asset" : asset , 'amount' : free})
                if asset == 'USDT':
                    self.cash = free

        self.active_account = active_acount
        print('my active account is ' , active_acount)
        print('my cash is ' , self.cash , '$')
        
        return active_acount , self.cash
     
    def transaction(self):
        '''
        '''

        pass

def plot(DataFrame):
    fig = plt.figure(figsize=(10,8))
    df = DataFrame
    df = df.astype(float)
    df['date'] = pd.to_datetime(df.index)
    df = df.reset_index()
    ax0 = plt.subplot(2,1,1)
    ax1 = plt.subplot(2,1,2)
    ax0.plot(df['date'] , df['Close']  , color = 'red' , alpha = 0.7 , ls = '--' , label = 'close')
    ax1.bar(df['date'] , df['Volume'] , color = 'darkgreen' , alpha = 0.6 , label = 'Volume')
    ax1.legend()        
    plt.legend()
    ax0.grid()
    ax1.grid()
    plt.tight_layout()
    plt.show()

class gui( api , Frame ):
    def __init__(self , coin_name , back , bg ):
        Frame.__init__(self)
        api.__init__(self)
        Label(self , image= bg ).place(x = 0 , y = 0)
        self.coin = None
        self.coin_name = coin_name
        self.back = back
        self.create_widgets()
    
    def get_coins(self):
        print('------------> coin name is ' , self.coin_entry.get() , 'time is  ' , self.time_entry.get() , ' period is ' , self.period_entry.get())
        self.coin = self.get_coin(self.coin_entry.get() , time = self.time_entry.get() , days = self.period_entry.get())
        print(self.coin)
        messagebox.showinfo(message= '---- get dataframe successfully ----' )

    def save(self):
        newWindow = tkinter.Toplevel()
        newWindow.title("saved_file Window")
        newWindow.geometry("350x350+300+300")
        newWindow.configure(background='black')
        tkinter.Label(newWindow, text ="This is a new window").pack()
        self.save_file = tkinter.Entry(newWindow , width=30)
        self.save_file.pack()

        def go():
            weights = self.coin.copy(deep = True)
            print('----------> your file title is ' , self.save_file.get())
            weights.to_excel(f'{self.save_file.get()}.xlsx')
            print('----------> save DONE !')
            newWindow.destroy()

        bt = tkinter.Button(newWindow, text="saved_file", width= 10 , bd='5' ,  command=go , bg = 'gray' , fg = 'black')
        bt.pack()

    def plot_coin(self):
        plot(self.coin)

    def quit(self):
        self.back.destroy()

    def create_widgets(self):
        self.style = Style()
        self.pack(fill = BOTH , expand=True)
        self.style.theme_use("alt")
        self.columnconfigure(0 , weight = 2)
        self.columnconfigure(1 , weight = 6)
        self.columnconfigure(0 , pad = 5)
        self.columnconfigure(1 , pad = 5 )

        self.coin_label = Label(self , text = 'get_coin' , bg = 'yellow').grid(row = 0 , column=0 , sticky='NSEW' , pady = 10 , padx = 10)
        self.coin_entry = Entry(self , width = 10 )
        self.coin_entry.grid(row = 0 , column=1 , padx=10 , pady = 10)
        self.time_label = Label(self , bg = 'yellow' , text  = 'Time').grid(row = 1, column=0 , sticky='NSEW' , pady = 10 , padx=10)
        self.time_entry = Entry(self , width=10)
        self.time_entry.grid(row = 1 , column=1 , padx = 10 , pady = 10 )
        self.period_label = Label(self , bg = 'yellow' , text = 'perod_<days>').grid(row = 3 , column = 0 , sticky='NSEW' , pady = 10 , padx=10)
        self.period_entry = Entry(self , width= 10)
        self.period_entry.grid(row = 3 , column=1)
        self.coin_label = Button(self , text = 'get_coin'  , command= self.get_coins).grid(row = 4 ,  column=0  , sticky='NSEW' , pady = 15 , padx = 10)
        self.coin_label = Button(self , text = 'plot_coin'  , command= self.plot_coin).grid(row = 4 ,  column=1 , sticky='NSEW' , pady = 15 , padx = 10)

        self.save_but = tkinter.Button(self, text="saved_file", width= 10 , bd='5' ,  command=self.save , bg = 'gray' , fg = 'black').place(x = 120 , y =350)
        self.quit_but = tkinter.Button(self,  text = 'Quit', bd='5' , command = self.quit , width = 10 ).place(x = 320 , y = 350)

def main():
    canvas = Tk()
    canvas.title('--------- Binance API ---------')
    bg = PhotoImage(file = "440_400.png")
    canvas.geometry('440x400+300+300')
    print('-----------------> image obg is ' , bg)
    gui('BTC'  , back = canvas , bg = bg)
    canvas.mainloop()

if __name__ == '__main__': 
    main()

import bs4 as bs
import pickle
import requests
import datetime as dt
import os
import pandas as pd
import pandas_datareader.data as web

def save_sp500_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, "lxml")
    table = soup.find('table', {'class':'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text
            tickers.append(ticker)

    with open("sp500tickers.pickle", "wb") as f:
            pickle.dump(tickers, f)

    print(tickers)

    return tickers

save_sp500_tickers()

def get_data_from_google(reload_sp500=False):
    if reload_sp500:
        tickers = save_sp500_tickers
    else:
        with open('sp500tickers.pickle','rb') as f:
            tickers = pickle.load(f)
    
    if not os.path.exists('stock_dfs'):#check if directory exists
        os.makedirs('stock_dfs')#if not, create new directory

    start = dt.datetime(2000,1,1)
    today = dt.datetime.today()
    end = dt.datetime(today.year, today.month, today.day)


    for ticker in tickers: #loop through ticker list
        query_name = 'NYSE:{}'.format(ticker) #specify exchange, can be further extentiated for nonNYSE stocks
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)): #if file doesn't exist
            try:
                df = web.DataReader(query_name,'google',start,end) #query google for historical data
                df.to_csv('stock_dfs/{}.csv'.format(ticker)) #save csv of data
            except:
                df = web.DataReader(ticker,'google',start,end) #query google for historical data
                df.to_csv('stock_dfs/{}.csv'.format(ticker)) #save csv of data  
        else:
            try:
                print('Already have {}'.format(ticker))
            except:
                print('Cannot obtain data for ' +ticker)

get_data_from_google()

def compile_data():
    with open("sp500tickers.pickle", "rb") as f:
        tickers = pickle.load(f)

    main_df = pd.DataFrame()

    for count, ticker in enumerate(tickers):
        try:
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df.set_index('Date', inplace=True)

            df.rename(columns = {'Close':ticker}, inplace=True)
            df.drop(['Open', 'High', 'Low', 'Volume'], 1, inplace=True)

            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df, how='outer')

        except:
            print('stock_dfs/{}.csv'.format(ticker) + ' not found')


        if count % 10 == 0:
                print(count)

    print(main_df.head())
    main_df.to_csv('sp500_joined_closes.csv')
compile_data()
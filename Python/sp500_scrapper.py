import bs4 as bs
import datetime as dt
import os #Misc operating system interfaces
import pandas as pd
import numpy as np
import pandas_datareader.data as web 
import pickle
import requests
import fix_yahoo_finance #Had to add as their was an issue reteriving the data
import matplotlib.pyplot as plt
from matplotlib import style

style.use('ggplot')

def save_sp500_tickers(): #function for getting the ticker names
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)
        
    with open("sp500tickers.pickle","wb") as f:
        pickle.dump(tickers,f)
        
    return tickers

#print(save_sp500_tickers())

def get_data_from_yahoo(reload_sp500=False): #function for getting the ticker data
  nowork=[]
  if reload_sp500: 
    tickers = save_sp500_tickers()
  else:
      with open("sp500tickers.pickle","rb") as f:
        tickers=pickle.load(f)

  if not os.path.exists('stock_dfs'):
      os.makedirs('stock_dfs')

    #set start and end time for loop
  start = dt.datetime(2000,1,1)
  today = dt.datetime.today()
  end = dt.datetime(today.year, today.month, today.day)
  
  for ticker in tickers: # you could use tickers[], and inside the brackets, say what tickers you want
    if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
      fix_yahoo_finance.pdr_override() #had to add to fix the yahoo issue with cookies
      df = web.get_data_yahoo(ticker, start, end)
      df.to_csv('stock_dfs/{}.csv'.format(ticker))
    if os.path.getsize("stock_dfs/{}.csv".format(ticker)) <= 3:      
      nowork.append(ticker)       
    else:
      print('Already have {}'. format(ticker))
  print(nowork) 

# get_data_from_yahoo()

def compile_data():
    with open("sp500tickers.pickle","rb") as f:
        tickers = pickle.load(f)

    main_df = pd.DataFrame()
    
    for count,ticker in enumerate(tickers):
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
        df.set_index('Date', inplace=True)

        df.rename(columns={'Adj Close':ticker}, inplace=True)
        df.drop(['Open','High','Low','Close','Volume'],1,inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')

        if count % 10 == 0:
            print(count)
    print(main_df.head())
    main_df.to_csv('sp500_joined_closes.csv')

# NOTE - you need to put the header in the top of the 1KB files
# compile_data()

def visualize_data():
    df = pd.read_csv('sp500_joined_closes.csv')
    # df['AAPL'].plot()
    # plt.show()
    df_corr = df.corr() #Correlation matrix (Pearson)
    # These correaltions can be used for pair wise trading straegies like convergence trading
    # Also, having a diverse portfolio means investing in non-correlated stocks
    # however, it is best to correlate between stock return and not stock prices, since
    # stock returns are more likely to follow a normal distribution

    print(df_corr.head())

    #Set up a heat map of the correlation values (correlation table)
    data1 = df_corr.values #gives the inner values (i.e. no headers)
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1,1,1)

    heatmap1 = ax1.pcolor(data1, cmap=plt.cm.RdYlGn)
    fig1.colorbar(heatmap1)
    ax1.set_xticks(np.arange(data1.shape[0])+0.5, minor=False) #Put in ticks at every half mark so we can identify where we get people
    ax1.set_yticks(np.arange(data1.shape[1])+0.5, minor=False)
    ax1.invert_yaxis() # to get rid of the room at the top of the chart
    ax1.xaxis.tick_top() #Makes it look better - to make it more like a table

    column_labels = df_corr.columns
    row_labels = df_corr.index

    ax1.set_xticklabels(column_labels)
    ax1.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap1.set_clim(-1,1) #Scales the correlation between the maximum of the Pearson (i.e. -1 and 1)
    plt.tight_layout()
    plt.show()

visualize_data()
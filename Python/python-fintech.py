import datetime as dt #date time
import matplotlib.pyplot as plt #create plots
from matplotlib import style #stylize graphs
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd #module handles dataframes
import pandas_datareader.data as web #grab data from finance API

style.use('ggplot') #Set style using ggplot

start = dt.datetime(2000, 1, 1) #Set startdate [ yr, m, d]
end = dt.datetime(2016, 12, 31) #Set end date [ yr, m, d]

# df = web.DataReader('TSLA', 'yahoo', start, end) #Extract ('String is ticker name', 'source', start time, end time) and import as dataframe
# print(df.head()) #print header rows of frame
# print(df.tail()) #print end rows of frame
# print(df['Adj Close']) #print specific col
# print(df[['Adj Close', 'High']) #print specific cols

# df.to_csv('tsla.csv') #convert frame to csv

df = pd.read_csv('tsla.csv', parse_dates=True, index_col=0) #read in csv 
##(but can also be json, sql, excel, etc.) and index date as date format

# df['Adj Close'].plot() #plot dataframe - in [] we can pick the column in the df
# plt.show() #show dataframe

df['100ma']= df['Adj Close'].rolling(window=100, min_periods=0).mean() #Create new col in df for 100 moving average
# df.dropna(inplace=True) #Drop NA values in the first 100 rows of 100ma Note: inplace better than df=df.dropna 
# becuase we are just modifying the frame rather than redefining it

#Resampleing the data
df_ohlc = df['Adj Close'].resample('10D').ohlc() #Resample to open, high, low, close based on Adj close
df_ohlc = df_ohlc.reset_index() #reste date index
df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num) #convert date index to mdate format
df_volume = df['Volume'].resample('10D').sum() #resample vol
print(df_ohlc.head())


#MatplotLib plotting
#Create the subplots
fig = plt.figure()
ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1) # 6x1 is the grid size, and 0,0 is the starting pt
ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
ax1.xaxis_date()

candlestick_ohlc(ax1, df_ohlc.values, width=2, colorup='g')
ax2.fill_between(df_volume.index.map(mdates.date2num),df_volume.values,0)
plt.show() #show dataframe
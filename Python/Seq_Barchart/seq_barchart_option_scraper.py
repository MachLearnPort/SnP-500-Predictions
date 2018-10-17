import requests as r
import pandas as pd
import pandas_datareader.data as web
from pandas.tseries.offsets import BDay
import numpy as np
import time
from tqdm import tqdm
import os

from barchart_scraper import barchart_scraper
from barchart_parser import barchart_parser

today = pd.datetime.today().date()
project_dir = "D:\\Users\\Jeff\\Google Drive\\Machine Learning\\SnP-500-prediction\\Python\\Seq_Barchart\\"
# -----------------------------------------------------------------------------
# define utility functions
# -----------------------------------------------------------------------------

def get_first_data(symbol):
    """fn: to get first data and extract expiry dates"""

    # scrape
    scraper = barchart_scraper(symbol)
    response = scraper.post_url()
    expirys = scraper.get_expirys(response)
    # parse response
    parser = barchart_parser(symbol, response)
    first_call_df = parser.create_call_df()
    first_put_df = parser.create_put_df()
    # merge calls + puts
    first_concat = pd.concat([first_call_df, first_put_df], axis=0)
    return first_concat, expirys

# function to get last daily close from Google Finance
get_price = lambda symbol: web.DataReader(
    symbol, 'google', today - 1*BDay(), today)['Close']

# -----------------------------------------------------------------------------
# import symbols
# -----------------------------------------------------------------------------
FILE = project_dir + 'ETFList.Options.Nasdaq__M.csv'
ALL_ETFS =  pd.read_csv(FILE)['Symbol']
drop_symbols = ['ADRE', 'AUNZ', 'CGW', 'DGT', 'DSI', \
                'EMIF', 'EPHE', 'EPU', 'EUSA', 'FAN', \
                'FDD', 'FRN', 'GAF', 'GII', 'GLDI', 'GRU', \
                'GUNR', 'ICN', 'INXX', 'IYY', 'KLD', 'KWT', \
                'KXI', 'MINT', 'NLR', 'PBP', 'PBS', 'PEJ', \
                'PIO', 'PWB', 'PWV', 'SCHO', 'SCHR', 'SCPB', \
                'SDOG', 'SHM', 'SHV', 'THRK', 'TLO', 'UHN', \
                'USCI', 'USV', 'VCSH']
ETFS = [x for x in ALL_ETFS if x not in set(drop_symbols)]
# -----------------------------------------------------------------------------
# run main script body
#
# loop through all etfs
#   loop through expirys for each etf
# -----------------------------------------------------------------------------
t0 = time.time()
all_etfs_data = []
error_symbols = []
for symbol in tqdm(ETFS):
    print()
    print('-'*79)
    print('scraping: ', symbol)
    try:
        last_close_price = get_price(symbol).iloc[0]
        first_concat, expirys = get_first_data(symbol)
        list_dfs_by_expiry = []
        list_dfs_by_expiry.append(first_concat)
        for expiry in tqdm(expirys[1:]):
            print()
            print('scraping expiry: ', expiry)
            scraper = barchart_scraper(symbol)
            tmp_response = scraper.post_url(expiry=expiry)
            print('parsing... ')
            parser = barchart_parser(symbol, tmp_response)
            call_df = parser.create_call_df()
            put_df = parser.create_put_df()
            concat = pd.concat([call_df, put_df], axis=0)
            concat['underlyingPrice'] = [last_close_price] * concat.shape[0]
            list_dfs_by_expiry.append(concat)
            print('parsing complete')
            random_wait = np.random.choice([1,1.25,2.5,3], p=[0.3,0.3,0.25,0.15])
            
            time.sleep(random_wait)
        all_etfs_data.append(pd.concat(list_dfs_by_expiry, axis=0))
    except Exception as e:
        error_symbols.append(symbol)
        print(f'symbol: {symbol}\n error: {e}')
        print()
        continue
# -----------------------------------------------------------------------------
duration =  time.time() - t0
print(f'script run time: ', pd.to_timedelta(duration, unit='s'))

dfx = pd.concat(all_etfs_data, axis=0)
print(dfx.head())
print(dfx.info())
print(f'error symbols:\n{error_symbols}')
# -----------------------------------------------------------------------------
# store table as hdf
# -----------------------------------------------------------------------------
today = pd.datetime.today().date()
file_ = project_dir + f'/Barchart_Options_Data/ETF_options_data_{today}.h5'
dfx.to_hdf(file_, key='data', format='table', mode='w') 
# -----------------------------------------------------------------------------
# kill python process after running script to prevent leakage
# -----------------------------------------------------------------------------
time.sleep(5)
os.kill(os.getpid(), 9)
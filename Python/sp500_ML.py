from collections import Counter
import numpy as np
import pandas as pd
import pickle
from sklearn import svm, cross_validation, neighbors
from sklearn.ensemble import VotingClassifier, RandomForestClassifier #voting classifer uses alot of classifiers

# ML model that determines what to do with a stock in 7 days
# Note: you dont want to look back to far with you ML models, as the relationships between compnaies
# has probably changed (and only look back about 1 - 2 years), as they may not be correlated then 
def process_data_for_labels(ticker):
  hm_days = 7; #How many days in the future do we have to loose/gain x-percent
  df = pd.read_csv('sp500_joined_closes.csv', index_col=0)
  tickers = df.columns.values.tolist() #nested list to seperate each ticker
  df.fillna(0, inplace=True) ##fill all the N/A values with 0

  for i in range (1, hm_days+1): #hm_days+1 so that we get a loop from 1-7 and not 0-7
    
    # Calculate the percent change of the stock
    df['{}_{}d'.format(ticker, i)] = ((df[ticker].shift(-i) - df[ticker]) / df[ticker])     #{} brackets is where we put the items in the format object 
    
    #so for APPL ticker on day 2, we have {ticker}_{i}d -> APPL_2d for the apple ticker on day 2
    # which = (((Price in 2 days from now)-(todays price))/todays price)*100
    # .shift, shifts the index negitively to get future data (up/down shift in the column). 
  df.fillna(0, inplace=True)
  return tickers, df, hm_days

# Define out buy, hold and sell requirments
def buy_sell_hold(*args):
  cols = [c for c in args] #passing cols as parameters into pandas
  #requirement_gen = 0.02
  requirement_buy = 0.025
  requirement_sell = 0.025
  for col in cols:
    if col > requirement_buy:
      return 1
    if col < -requirement_sell:
      return -1
    else:
      return 0

#Extract the feature set of the index we are solving for
def extract_featuresets(ticker):
  tickers, df, hm_days = process_data_for_labels(ticker)

  #Generates a new coloumn in our data frame that determins if we buy sell/hold
  df['{}_target'.format(ticker)]=list(map(buy_sell_hold, *[df['{}_{}d'.format(ticker, i)]for i in range(1, hm_days+1)])) #using list comprehension to map through the docs

  vals = df['{}_target'.format(ticker)].values.tolist()
  str_vals = [str(i) for i in vals]
  print('Data spread:',Counter(str_vals)) #Gives us the buy sell hold spread - which a good spread should be even
  df.fillna(0, inplace=True) #remove NAs
  df = df.replace([np.inf, -np.inf], np.nan) #replace infs
  df.dropna(inplace=True)

  df_vals = df[[ticker for ticker in tickers]].pct_change() #pct_change normalizes our data - percent change from 1 day for all of the companies
  df_vals = df_vals.replace([np.inf, -np.inf], 0)
  df_vals.fillna(0, inplace=True)
  
  X = df_vals.values
  y = df['{}_target'.format(ticker)].values
  
  return X,y,df #return the features, the labels and the dataframe

#extract_featuresets('AAPL')



def do_ml(ticker):
  X, y, df = extract_featuresets(ticker)

  X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.25) #Defining ours training sets for XGboost

  #clf = neighbors.KNeighborsClassifier()
  clf = VotingClassifier([('lsvc', svm.LinearSVC()), 
                          ('knn', neighbors.KNeighborsClassifier()), 
                          ('rfor', RandomForestClassifier())]) #Takes a list of tuples of clasifiers
  clf.fit(X_train, y_train) # train the model - and once we are happy with the confidence, we can just pickle out and use it when ever we want
  # Afterwhich, we can just load the classifier in, call it clf and then used. clf.predict

  confidence = clf.score(X_test, y_test)
  print('Accuracy', confidence)
  predictions = clf.predict(X_test) #can pass a single value or a large list
  print('Predicted spread:', Counter(predictions))

  return confidence

#do_ml('BAC')









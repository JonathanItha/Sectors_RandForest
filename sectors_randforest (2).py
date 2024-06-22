# -*- coding: utf-8 -*-
"""Sectors_RandForest.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_N4opJKEMZxV2SHPklpRqTmRmy7g8T-7

#The  Goal of this code is to determine wich sectors can better predict the future movement of other sectors by using a random forest classifier
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import yfinance as yf

until = '2023-01-01'
start = '2000-01-01'

sectors = {
'energy' : yf.download('^GSPE' , end=until , start=start),
'finance' : yf.download('^SP500-40' , end=until , start=start ),
'health' : yf.download('^SP500-35', end=until , start=start) ,
'tech' : yf.download('^SP500-45', end=until , start=start),
'discr' : yf.download('^SP500-25', end=until , start=start),
'staples' : yf.download('^SP500-30', end=until , start=start),
'commu' : yf.download('^SP500-50', end=until , start=start),
'estate' : yf.download('^SP500-60' , end=until, start=start) ,
'mat' : yf.download('^SP500-15', end=until, start=start)
}


#not found 'estate' : yf.download('^SP500-60' , end=until) , 'mat' : yf.download('^SP500-15', end=until),
'''
for sector, data in sectors.items():
    if data.empty:
        print(f"No data found for {sector}")
    else:
        if 'Close' in data.columns:
            data['Close'].plot(figsize=(14, 7))
            plt.title(f'{sector} Closing Price')
            plt.show()  # This ensures each plot is shown separately
        else:
            print(f"No 'Close' column found in data for {sector}")

'''

print(sectors['energy'].columns)

#Try to predict if the price will go up or down

for sector, data in sectors.items() :
  data['Tomorrow'] = data['Close'].shift(-1)

print(sectors['finance'])

#drop the volume because it contains a lot of 0 value

for sector, data in sectors.items() :
  data = data.drop('Volume' , axis=1)

#adding the vix index and drop the tomorrow col

vix = yf.download('^VIX', start=start , end=until )

for sector, data in sectors.items():
    # Assuming 'Date' is the index and it's in datetime format
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, slow=26, fast=12, smooth=9):
    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    return macd

for sector, data in sectors.items() :
  data['Target'] = (data['Tomorrow'] > data['Close']).astype(int)
  data['vix'] = vix['Close']
  data['Weekday'] = data.index.weekday + 1
  data['RSI'] = calculate_rsi(data['Close'])
  data['MACD'] = calculate_macd(data['Close'])
  data['Return'] = data['Close'].pct_change()

print(sectors['finance']['vix'])

print(sectors['energy'])

for sector, data in sectors.items() :
  data = data.drop('Tomorrow' , axis=1)

energy = sectors['energy']
finance = sectors['finance']
health = sectors['health']
tech = sectors['tech']
discr = sectors['discr']
staples = sectors['staples']
commu = sectors['commu']
estate = sectors['estate']
mat = sectors['mat']

"""#Fist step
To find which sector the test model is the most efficeint.
"""

#ain the model

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score , accuracy_score

model = RandomForestClassifier(n_estimators=100 , min_samples_split=10, random_state=42  )

def train_test_model(data) :
  hs = [2 , 5 , 60 , 250]

  for h in hs :
    rol_av = data.rolling(h).mean()
    mean_col = f'Close_Mean_{h}'
    data[mean_col] = rol_av['Return']

    stand_dev = data.rolling(h).std()
    st_col = f'Stand_dev_{h}'
    data[st_col] = stand_dev['Return']


  new_var = ['Open', 'High', 'Low', 'Close', 'vix', 'Weekday', 'RSI', 'MACD', 'Return', 'Close_Mean_2',
       'Stand_dev_2', 'Close_Mean_5', 'Stand_dev_5', 'Close_Mean_60',
       'Stand_dev_60', 'Close_Mean_250', 'Stand_dev_250']

  data = data.dropna()

  train = data.iloc[:-250]
  test = data.iloc[-250 :]


  fig , ax = plt.subplots(figsize=(14, 7))
  train['Close'].plot(ax=ax , label='train')
  test['Close'].plot(ax=ax , label='test')
  plt.title('Closing Price')
  ax.legend()
  plt.show()

  data['Return'].plot(figsize=(14, 7))
  plt.ylabel('Return')
  plt.xlabel('Date')
  plt.title('Return')
  plt.show()

  model.fit(train[new_var] , train['Target'])

  pred = model.predict_proba(test[new_var])[: , 1]
  pred[pred >= 0.6] = 1
  pred[pred < 0.6] = 0

  pred = pd.Series(pred , index=test.index)

  feature_importances = model.feature_importances_
  importances_df = pd.DataFrame({'feature': new_var, 'importance': feature_importances})
  importances_df = importances_df.sort_values(by='importance', ascending=False)
  plt.figure(figsize=(10, 6))
  plt.barh(importances_df['feature'], importances_df['importance'])
  plt.xlabel('Importance')
  plt.ylabel('Feature')
  plt.title('Feature Importance')
  plt.gca().invert_yaxis()
  plt.show()

  matcorr = data[new_var]

  corr = matcorr.corr()
  plt.figure(figsize=(10, 8))
  sns.heatmap(corr, annot=False )
  plt.title('Correlation Matrix')
  plt.show()

  preci_score = precision_score(test['Target'] , pred )
  acc = accuracy_score(test['Target'] , pred)

  real = test['Target'].sum()
  trad = pred.sum()

  return  print(f'real number of days up {real}')  ,  print(f'predicted day up : {trad}') , print(f'precision score : {preci_score}') , print(f'Accuracy : {acc}')

energy_model = train_test_model(energy)

finace_model = train_test_model(finance)

heath_model = train_test_model(health)

tech_model = train_test_model(tech)

disc_model = train_test_model(discr)

staples_model = train_test_model(staples)

commu_model = train_test_model(commu)

estate_model = train_test_model(estate)

mat_model = train_test_model(mat)

"""#Second step
Try to improuve the process by removing the 5 less important features, to only keep 12 instead of 17 feature and see the result

The result is worst that the fisrt step then we will ignore this part
"""

def best_model(data) :
  hs = [2 , 5 , 60 , 250]

  for h in hs :
    rol_av = data.rolling(h).mean()
    mean_col = f'Close_Mean_{h}'
    data[mean_col] = rol_av['Return']

    stand_dev = data.rolling(h).std()
    st_col = f'Stand_dev_{h}'
    data[st_col] = stand_dev['Return']


  new_var = [ 'vix', 'Weekday', 'RSI', 'MACD', 'Return', 'Close_Mean_2',
       'Stand_dev_2', 'Close_Mean_5', 'Stand_dev_5', 'Close_Mean_60',
       'Stand_dev_60', 'Close_Mean_250', 'Stand_dev_250']

  data = data.dropna()

  train = data.iloc[:-250]
  test = data.iloc[-250 :]


  model.fit(train[new_var] , train['Target'])

  pred = model.predict_proba(test[new_var])[: , 1]
  pred[pred >= 0.6] = 1
  pred[pred < 0.6] = 0

  pred = pd.Series(pred , index=test.index)


  preci_score = precision_score(test['Target'] , pred )
  acc = accuracy_score(test['Target'] , pred)

  real = test['Target'].sum()
  trad = pred.sum()

  return  print(f'real number of days up {real}')  ,  print(f'predicted day up : {trad}') , print(f'precision score : {preci_score}') , print(f'Accuracy : {acc}')

'''
def best_model(data) :
  hs = [2 , 5 , 60 , 250]

  for h in hs :
    rol_av = data.rolling(h).mean()
    mean_col = f'Close_Mean_{h}'
    data[mean_col] = rol_av['Return']

    stand_dev = data.rolling(h).std()
    st_col = f'Stand_dev_{h}'
    data[st_col] = stand_dev['Return']


  new_var = ['Close', 'vix', 'Weekday', 'RSI', 'MACD', 'Return', 'Close_Mean_2',
       'Stand_dev_2', 'Close_Mean_5', 'Stand_dev_5', 'Close_Mean_60',
       'Stand_dev_60', 'Close_Mean_250', 'Stand_dev_250']

  data = data.dropna()

  train = data.iloc[:-250]
  test = data.iloc[-250 :]

  model.fit(train[new_var] , train['Target'])

  feature_importances = model.feature_importances_
  importances_df = pd.DataFrame({'feature': new_var, 'importances_df': feature_importances})
  optim_var = importances_df[importances_df['importances_df'] > 0.05]['feature'].tolist()


  model.fit(train[optim_var] , train['Target'])

  pred = model.predict_proba(test[optim_var])[: , 1]
  pred[pred >= 0.6] = 1
  pred[pred < 0.6] = 0

  pred = pd.Series(pred , index=test.index)


  preci_score = precision_score(test['Target'] , pred )
  acc = accuracy_score(test['Target'] , pred)

  real = test['Target'].sum()
  trad = pred.sum()

  return  print(f'real number of days up {real}')  ,  print(f'predicted day up : {trad}') , print(f'precision score : {preci_score}') , print(f'Accuracy : {acc}') , print(optim_var)
  '''

best_model(energy)

best_model(finance)

best_model(health)

best_model(tech)

best_model(discr)

best_model(staples)

best_model(commu)

best_model(estate)

best_model(mat)

"""#Third Step

After notice that the Tech sector had better resuts compare to other, The goal is now to train the model only in Tech sector and test it in the other sectors and see the resuts

We have have in overall the best result. The model only trained in tech sectors and test in the other have a better over all result.
"""

#Gonna train the model only on tech cause he has a better restult and test it on the other sector

t_model = RandomForestClassifier(n_estimators=100 , min_samples_split=10, random_state=42  )

tech.dropna(inplace=True)

tech

tech.columns

t_train = tech.iloc[:-250]
t_test = tech.iloc[-250:]

new_var = ['Open', 'High', 'Low', 'Close', 'vix', 'Weekday', 'RSI', 'MACD', 'Return', 'Close_Mean_2',
       'Stand_dev_2', 'Close_Mean_5', 'Stand_dev_5', 'Close_Mean_60',
       'Stand_dev_60', 'Close_Mean_250', 'Stand_dev_250']

t_model.fit(t_train[new_var] , t_train['Target'])

tpred = t_model.predict_proba(t_test[new_var])[: , 1]
tpred[tpred >= 0.6] = 1
tpred[tpred < 0.6] = 0

tpred = pd.Series(tpred , index=t_test.index)

tpreci_score = precision_score(t_test['Target'] , tpred )
tacc = accuracy_score(t_test['Target'] , tpred)

treal = t_test['Target'].sum()
trad = tpred.sum()

print(f'real number of days up {treal}')
print(f'predicted day up : {trad}')
print(f'precision score : {tpreci_score}')
print(f'Accuracy : {tacc}')

t_model = RandomForestClassifier(n_estimators=100 , min_samples_split=10, random_state=42  )

t_train = tech.iloc[:-250]
t_test = tech.iloc[-250:]

new_var = ['Open', 'High', 'Low', 'Close', 'vix', 'Weekday', 'RSI', 'MACD', 'Return', 'Close_Mean_2',
       'Stand_dev_2', 'Close_Mean_5', 'Stand_dev_5', 'Close_Mean_60',
       'Stand_dev_60', 'Close_Mean_250', 'Stand_dev_250']

t_model.fit(t_train[new_var] , t_train['Target'])

def tech_model(data) :
  data.dropna(inplace=True)
  t_train = data.iloc[:-250]
  t_test = data.iloc[-250:]
  data = data.iloc[-250:]

  new_var = ['Open', 'High', 'Low', 'Close', 'vix', 'Weekday', 'RSI', 'MACD', 'Return', 'Close_Mean_2',
       'Stand_dev_2', 'Close_Mean_5', 'Stand_dev_5', 'Close_Mean_60',
       'Stand_dev_60', 'Close_Mean_250', 'Stand_dev_250']


  prediction = t_model.predict_proba(data[new_var])[: , 1]
  prediction[prediction >= 0.6] = 1
  prediction[prediction < 0.6] = 0

  prediction = pd.Series(prediction , index=t_test.index)

  preci_score = precision_score(t_test['Target'] , prediction )
  accuracy = accuracy_score(t_test['Target'] , prediction)

  reality = t_test['Target'].sum()
  comparison = prediction.sum()

  return print(f'real number of days up {reality}')  , print(f'predicted day up : {comparison}')  , print(f'precision score : {preci_score}')  , print(f'Accuracy : {accuracy}')

print('energy')
tech_model(energy)
print('finance')
tech_model(finance)
print('health')
tech_model(health)
print('tech')
tech_model(tech)
print('discr')
tech_model(discr)
print('staples')
tech_model(staples)
print('commu')
tech_model(commu)
print('estate')
tech_model(estate)
print('mat')
tech_model(mat)
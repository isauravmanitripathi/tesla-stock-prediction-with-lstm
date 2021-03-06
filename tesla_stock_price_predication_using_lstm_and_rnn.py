# -*- coding: utf-8 -*-
"""tesla-stock-price-predication-using-lstm-and-rnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CGpgrG5Oj_u3IfSkYnnzs9rr0RO1lPQC
"""

# Imort main libraries
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sns # for photing and viewing data
import matplotlib.pyplot as plt# plotting library
import plotly.express as px

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

"""# Read The Dataset"""

df=pd.read_csv('/kaggle/input/tesla-stock-price/TSLA.csv')

"""# Check Head And Tail of the dataset"""

df.head()

df.tail()

df.set_index('Date',inplace = True)# Set the date to be the index

# resorting the data
df.index =  pd.to_datetime(df.index,format='%Y-%m-%d')

df.head()

"""# Now PLots"""

plt.figure(figsize=(14, 10))
plt.plot(df['Volume'])

df.plot(figsize=(18,6))

df[['Open','Close','High','Low']].plot(figsize = (20,12))
plt.title('TESLA Stock at all time')

df[['Open','Close']].plot(figsize = (20,10), alpha = 1)
plt.title('TESLA Stock price action')
plt.xlabel('Date')
plt.ylabel('Stock action')

df[['Open','High']].plot(figsize = (20,10), alpha = 1)
plt.title('TESLA Stock price action')
plt.xlabel('Date')
plt.ylabel('Stock action')

df[['Low','Close']].plot(figsize = (20,10), alpha = 1)
plt.title('TESLA Stock price action')
plt.xlabel('Date')
plt.ylabel('Stock action')

df['Volume'].plot(figsize = (20,10), alpha = 1)
plt.title('TESLA Stock price action')
plt.xlabel('Date')
plt.ylabel('Stock action')

df['Adj Close'].plot(figsize = (20,10), alpha = 1)
plt.title('TSLA Stock price action')
plt.xlabel('Date')
plt.ylabel('Stock action')

Ama = df['2019':'2022']


Ama['Open'].plot(figsize = (20,10), alpha = 1)
plt.title('TESLA Stock Price Action form 2019 to 2022')

Ama[['Open','High']].plot(figsize = (20,10), alpha = 1)
plt.title('TESLA Stock Price Action form 2019 to 2022')

Ama['Adj Close'].plot(figsize = (20,10), alpha = 1)
plt.title('TESLA Stock Price Action form 2019 to 2022')

Ama['Volume'].plot(figsize = (20,10), alpha = 1)
plt.title('TESLA Stock Price Action form 2019 to 2022')

Ama.describe()

"""# Augmented Dickey Fuller Test (ADF)
ADF test is used to determine the presence of unit root in the series, and hence helps in understand if the series is stationary or not
"""

from statsmodels.tsa.stattools import adfuller

def adf_test(timeseries):
    #Perform Dickey-Fuller test:
    print ('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
       dfoutput['Critical Value (%s)'%key] = value
    print (dfoutput)

print(adf_test(df['High']))

print(adf_test(df['High'].resample('MS').mean()))

Ama_diff = Ama['Open'].resample('MS').mean() - Ama['Open'].resample('MS').mean().shift(1)
Ama_open_diff = Ama_diff.dropna()
Ama_open_diff.plot()

print(adf_test(Ama_open_diff))

"""# Kwiatkowski-Phillips-Schmidt-Shin Test (KPSS)
another test for checking the stationarity of a time series
"""

from statsmodels.tsa.stattools import kpss


def kpss_test(timeseries):
    print("Results of KPSS Test:")
    kpsstest = kpss(timeseries, regression="c", nlags="auto")
    kpss_output = pd.Series(
        kpsstest[0:3], index=["Test Statistic", "p-value", "Lags Used"]
    )
    for key, value in kpsstest[3].items():
        kpss_output["Critical Value (%s)" % key] = value
    print(kpss_output)

kpss_test(Ama['High'])

Ama["High_diff"] = Ama["High"] - Ama["High"].shift(1)
Ama["High_diff"].dropna().plot(figsize=(12, 8))

kpss_test(Ama['High_diff'].dropna())

kpss_test(Ama['High_diff'].resample('MS').mean().dropna())

kpss_test(Ama['High_diff'].resample('MS').std().dropna())

adf_test(Ama['High_diff'].dropna())

"""# Data Preprocessing"""

train_Ama = Ama['High'].iloc[:-4]

# Take ramdom  6 variables 

X_train=[]
y_train=[]

for i in range(2, len(train_Ama)):
    X_train.append(train_Ama[i-2:i])
    y_train.append(train_Ama[i])

import math
train_len = math.ceil(len(train_Ama)*0.8)
train_len

"""# For Model and apply RNN + LSTM"""

from tensorflow.keras.layers import LSTM
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout, TimeDistributed

X_train, y_train= np.array(X_train), np.array(y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

model=Sequential()
model.add(LSTM(50,activation='relu', input_shape=(X_train.shape[1],1)))
model.add(Dense(25))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.summary()
model.fit(X_train, y_train, epochs=10, batch_size=100, verbose=2)

losse = pd.DataFrame(model.history.history)
losse[['loss']].plot()

test_data = train_Ama[train_len-2:]
X_val=[]
Y_val=[] 

for i in range(2, len(test_data)):
    X_val.append(test_data[i-2:i])
    Y_val.append(test_data[i])

X_val, Y_val = np.array(X_val), np.array(Y_val)
X_val = np.reshape(X_val, (X_val.shape[0], X_val.shape[1],1))
prediction = model.predict(X_val)

from sklearn.metrics import mean_squared_error
# Know the model error accuracy | the model accuracy 
lstm_train_pred = model.predict(X_train)
lstm_valid_pred = model.predict(X_val)
print('Train rmse:', np.sqrt(mean_squared_error(y_train, lstm_train_pred)))
print('Validation rmse:', np.sqrt(mean_squared_error(Y_val, lstm_valid_pred)))

valid = pd.DataFrame(train_Ama[train_len:])
valid['Predictions']=lstm_valid_pred 
plt.figure(figsize=(16,8))
plt.plot(valid[['High','Predictions']])
plt.legend(['Validation','Predictions'])
plt.show()

"""# data frame to see the percentage of error between real and predicted

"""

variance = []
for i in range(len(valid)):
  
  variance.append(valid['High'][i]-valid['Predictions'][i])
variance = pd.DataFrame(variance)
variance.describe()

train = train_Ama[:train_len]
valid = pd.DataFrame(train_Ama[train_len:])
valid['Predictions']=lstm_valid_pred

plt.figure(figsize=(16,8))
plt.title('Model LSTM')
plt.xlabel('Date')
plt.ylabel('Amazon Price USD')
plt.plot(train)
plt.plot(valid[['High','Predictions']])
plt.legend(['Train','Val','Predictions'])
plt.show()

"""# If You Like This Notebook Please Upvote It."""


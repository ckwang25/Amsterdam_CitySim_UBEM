import pandas as pd
import numpy as np
import os
import csv
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
# from scipy.stats import norm
# from scipy.stats import contingency
# import seaborn as sns
# import psycopg2
# from scipy.optimize import curve_fit
import math
from sklearn.linear_model import LinearRegression

cwd = os.getcwd()
filesPath = cwd + '/../simulationOutputs/AOI_all/'
files = os.listdir(filesPath)

def readData():
    dfs = []
    for doc in files:
        if doc.endswith('csv'):
            year = doc[-8:-4]
            df = pd.read_csv(filesPath + str(doc), delimiter=',', index_col=False)
            df = df.iloc[:,[1,3]]
            df = df.rename(index=str, columns={"postcode": "postcode", "l_pc6_consumption_kwh_m3": str(year)})
            dfs.append(df)

    df_01 = pd.merge(dfs[0], dfs[1], on='postcode', how='outer')
    df_012 = pd.merge(df_01, dfs[2], on='postcode', how='outer')
    df_0123 = pd.merge(df_012, dfs[3], on='postcode', how='outer')
    df_01234 = pd.merge(df_0123, dfs[4], on='postcode', how='outer')
    df_012345 = pd.merge(df_01234, dfs[5], on='postcode', how='outer')
    df_measurement = df_012345
    return df_measurement

def cleanData(df_measurement):
    df = pd.DataFrame(columns=['postcode', 'year', 'EUI'])
    for row in df_measurement.values:
        postcode = row[0]
        measurements = row[1:]
        year = 2009
        for year_record in measurements:
            year += 1
            if not math.isnan(year_record):
                df = df.append({'postcode': postcode, 'year': year, 'EUI': year_record}, ignore_index=True)
    return df

def one_hot_encoding():
    df_measurement = readData()
    df = cleanData(df_measurement)
    df_encoded = pd.get_dummies(df)

    X = df_encoded.drop(['EUI','year_2010'], axis='columns')
    y = df_encoded.EUI
    return X,y


def residual():
    residuals = []
    X, y = one_hot_encoding()
    model = LinearRegression()
    model.fit(X,y)
    index = 0
    for i in X.values:
        y_i = y[index]
        index += 1
        y_hat = model.predict([i])
        res = y_i-y_hat

        residuals.append(res.tolist()[0])
    return residuals

residuals = residual()
print(residuals)
#
# import matplotlib.pyplot as plt
#
# # An "interface" to matplotlib.axes.Axes.hist() method
# n, bins, patches = plt.hist(x=residuals, bins='auto', color='#0504aa',
#                             alpha=0.7, rwidth=0.85)
# plt.grid(axis='y', alpha=0.75)
# plt.xlabel('Value')
# plt.ylabel('Frequency')
# plt.title('My Very Own Histogram')
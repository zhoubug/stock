import pandas as pd
import numpy as np


def boolinger(df, window):
    """    
    """
    close = df['close']
    ma = pd.rolling_mean(close, window)
    std = pd.rolling_std(close, window)
    
    up = ma+std
    down = ma-std
    val = (close-ma)/std
    return up, down, val


def returnize(series):
    returns = series.pct_change()
    returns[0] = 0              # change NaN to 0
    return returns


def sharpe_ratio(returns, k):
    std = returns.std()
    avg = returns.mean()
    return np.sqrt(k)*avg/std

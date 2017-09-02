import numpy as np

def moving_average(x, n, type='lin'):
    """
    compute an n period moving average.

    type is 'lin' or 'exp'

    """
    x = np.asarray(x)
    if type == 'lin':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()

    a = np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a
    
def relative_strength(prices, n=14):
    """
    compute the n period relative strength indicator
    http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
    http://www.investopedia.com/terms/r/rsi.asp
    """

    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed >= 0].sum()/n
    down = -seed[seed < 0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n - 1) + upval)/n
        down = (down*(n - 1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1. + rs)

    return rsi
    
def moving_average_convergence(x, nslow=26, nfast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = moving_average(x, nslow, type='exponential')
    emafast = moving_average(x, nfast, type='exponential')
    macd = emafast - emaslow
    ema9 = moving_average(macd, 9, type = 'exp')
    return macd, ema9
    
def pct_change(arr):
    return [100.0 * el1 / el2 - 100 for el1, el2 in zip(arr[1:], arr)]

def beta(stock, index):
    stock_pct_change = pct_change(stock)
    index_pct_change = pct_change(index)
    cov = np.cov(stock_pct_change, index_pct_change)
    var = np.var(stock)
    return (cov[0])[1] / var
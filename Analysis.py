import os
import csv
import numpy as np
import Indicators

TEMP_DIR = "temp/"
RSI_THRESHOLD = 50
MACD_THRESHOLD = 0
CROSSING_PERIOD = 3 # in days

def openCSV(fname):
    a = []
    with open(fname) as csvfile:
        csvread = csv.reader(csvfile)
        for row in csvread:
            a.append(row)
        return np.array(a)
        
def savetxtCSV(fname, obj, fmt = "%s", delimiter = ","):
    with open(fname, 'wb') as file:
        line = delimiter.join("None" if value is None else fmt % value for value in obj)
        file.write(line + '\n')        
    
def crosses(line1,line2):
    diff = line1 - line2
    if diff[0] <= 0 and diff[-1] >= 0:
        return 1
    else:
        return 0

def main():
    if 'filtered_stocks.csv' in os.listdir(TEMP_DIR + '.'):
        quandl_list = openCSV(TEMP_DIR + 'filtered_stocks.csv')
        print 'Loaded %i stocks from previously saved list.' % len(quandl_list[0])
    else:
        print 'List of stocks required.'
        
    filtered_stocks = []
    for stock in quandl_list[0]:
        try:
            stock_data = openCSV(TEMP_DIR + stock + '.csv')
        except(IOError):
            print 'Could not open %s.csv, skipping.' % stock
        price_data = [float(el) for el in stock_data[:,0]]
        if len(price_data) >= 26:
            rsi = Indicators.relative_strength(price_data[::-1])
            if rsi[-1] >= RSI_THRESHOLD:
                macd, ema9 = Indicators.moving_average_convergence(price_data[::-1])
                if macd[-1] >= 0 and (macd[-1] - ema9[-1]) >= 0:
                    filtered_stocks.append([stock, rsi[-1], macd[-1]])
        else:
            continue
    print filtered_stocks
    savetxtCSV(TEMP_DIR+'output.csv', filtered_stocks)
    
    # stock_data = openCSV(TEMP_DIR + quandl_list[0][0] + '.csv')
    # price_data = [float(el) for el in stock_data[:,0]]
    # RSI = Indicators.relative_strength(price_data[::-1])
    # MACD, ema9 = Indicators.moving_average_convergence(price_data[::-1])
    # print MACD


if __name__ == "__main__":
    main()
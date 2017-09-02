import os
import csv
import numpy as np
import requests
import datetime

TEMP_DIR = 'temp/'
REQ_SZ = 500
VOL_THRESHOLD = 5000000
PRICE_THRESHOLD = 0.4
DATE_TODAY = datetime.date.today()
START_DATE = DATE_TODAY - datetime.timedelta(days=90)
    
def filter_by_stocks(stocks_list):
    filtered_list = []
    for el in stocks_list:
        try:
            if int(el.split('/')[1]) <= 10000:
                filtered_list.append(el)
            else:
                pass
        except(ValueError):
            continue
    return [el2.split('/')[1] for el2 in filtered_list]

def get_price_data(ticker):
    url = 'https://query.yahooapis.com/v1/public/yql'
    params = {
        'q': 'select * from yahoo.finance.quotes where symbol in (%s)' % ticker,
        'format': 'json',
        'env': 'store://datatables.org/alltableswithkeys',
    }
    cache_timeout = 0.5*60 # in seconds
    try:
        r = requests.get(url,params=params)
    except requests.exceptions.Timeout:
        return 0
    if r.headers['Content-Type'].startswith('text/html'):
        # 404 not found
        return 0
    else:
        return r.json()['query']['results']['quote']
        
def get_detailed_data(ticker, start_date, end_date):
    url = 'https://www.quandl.com/api/v3/datasets/HKEX/' + ticker + '/data.json'
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'api_key': 'CqRnybn2soNJPpEGZCy8',
    }
    cache_timeout = 1*60 # in seconds
    try:
        r = requests.get(url,params=params)
    except requests.exceptions.Timeout:
        return 0
    if r.headers['Content-Type'].startswith('text/html'):
        # 404 not found
        return 0
    else:
        return r.json()['dataset_data']['data']
        
def fetch_detailed_data(quandl_list):
    for stock in quandl_list:
        toSave = get_detailed_data(stock, START_DATE.isoformat(), DATE_TODAY.isoformat())
        saveCSV(TEMP_DIR + stock + '.csv',[row[1:] for row in toSave])
    return 1

def filter_by_price_and_volume(stocks_list):
    filtered_list =[]
    tickers =[]
    for i in range(len(stocks_list) / REQ_SZ + 1):
        ticker = ''
        for el in stocks_list[REQ_SZ*i:REQ_SZ*(i+1)]:
            ticker += '"' + parse_ticker_for_yahoo(el) + '", '
        tickers.append(ticker[:-2])
    for el in tickers:
        for el2 in get_price_data(el):
            try:
                Open_price = float(el2['Open'])
                Open_volume = int(el2['Volume'])
                if Open_price <= PRICE_THRESHOLD and Open_volume >= VOL_THRESHOLD:
                    filtered_list.append(el2['symbol'])
                else:
                    continue
            except(IndexError, TypeError):
                continue
    return filtered_list

def parse_ticker_for_yahoo(ticker):
    num = str(int(ticker))
    return '0'*(4-len(num)) + num +'.HK'
    
def parse_ticker_for_quandl(ticker):
    id = ticker.split('.')[0]
    return '0'*(5-len(id)) + id
    
def saveCSV(fname, obj, fmt = "%.3f", delimiter = ","):
    with open(fname, 'wb') as file:
        for row in obj:
            line = delimiter.join("None" if value is None else fmt % value for value in row)        
            file.write(line + '\n')

def savetxtCSV(fname, obj, fmt = "%s", delimiter = ","):
    with open(fname, 'wb') as file:
        line = delimiter.join("None" if value is None else fmt % value for value in obj)
        file.write(line)

def openCSV(fname):
    a = []
    with open(fname) as csvfile:
        csvread = csv.reader(csvfile)
        for row in csvread:
            a.append(row)
        return np.array(a)

def main():
    if 'filtered_stocks.csv' in os.listdir(TEMP_DIR + '.'):
        quandl_list = openCSV(TEMP_DIR + 'filtered_stocks.csv')
        print 'Loaded %i stocks from previously saved list.' % len(quandl_list[0])
    else:
        print 'Filtered list not found. Creating list...'
        ticker_list = openCSV(TEMP_DIR + 'HKEX-datasets-codes.csv')
        stocks_list = filter_by_stocks(ticker_list[:,0])
        price_filtered_list = filter_by_price_and_volume(stocks_list)
        quandl_list = [parse_ticker_for_quandl(ticker) for ticker in price_filtered_list]
        savetxtCSV(TEMP_DIR + 'filtered_stocks.csv', quandl_list)
        print 'Refreshed filtered stocks list with %i stocks.' % len(quandl_list)
        quandl_list = openCSV(TEMP_DIR + 'filtered_stocks.csv')
        
    print "Downloading previous 90 day data."
    if fetch_detailed_data(quandl_list[0]):
        print "Successfully downloaded all data."
    else:
        print "An error occured."
    
if __name__ == '__main__':
    main()
#coding=utf-8

'''
    The stock data analysis is from http://q.stock.sohu.com

    Note:
        1. chinese

    Manual steps:
        import numpy as np
        import pandas as pd
        import json
        import urllib
        import time
        from datetime import datetime
        ff = open("./data/002509.json",'r')
        data_str = ff.read()
        data_nonascii = ''.join([i if ord(i)<128 else 'x' for i in data_str])
        data = json.loads(data_nonascii[21:-2])
        data_hq = pd.DataFrame(data[0]['hq'],columns=['date','start','end','incr','incr_rate','lowest','highest','amount','sum','turnover_rate'])
        data = data_hq.set_index('date')
        data['incr_rate'] = data['incr_rate'].apply(lambda x:float(x[:-1])/100)
        data.loc[stddata['incr_rate'] > 0.101, 'incr_rate'] = 0
        data.loc[stddata['incr_rate'] < -0.101, 'incr_rate'] = 0

    CopyRight:
        By liqinglu 2018
'''

import sys,getopt
import numpy as np
import pandas as pd
import json
import urllib
import time
from datetime import datetime


stock_list = None
FILE = None
start_date = '20000101'
end_date = time.strftime('%Y%m%d',time.localtime(time.time()))
datapath = "./data/"
stocklistname = "stock_list.csv"
stockanalysername = "stock_analyser.csv"
columname = ['date','start','end','incr','incr_rate','lowest','highest','amount','sum','turnover_rate']

stock_piece1 = "http://q.stock.sohu.com/hisHq?code="
stock_piece2 = "&start="
stock_piece3 = "&end="
stock_piece4 = "&stat=1&order=D&period=d&callback=historySearchHandler&rt=jsonp&r=0.8391495715053367&0.9677250558488026"

def rm_nonascii(s):
    return ''.join([i if ord(i)<128 else 'x' for i in s])

def colfilter(s):
    return float(s[:-1])/100

def regulardata(data):
    zs = False
    if data[data[columname[-1]].isin(['-'])].shape[0] > 0:
        zs = True

    for col in data.columns:
        if col == columname[0]:
            data = data.set_index(col)
        elif col == columname[4]: 
            tmpcol = data[col]
            data[col] = tmpcol.apply(colfilter)
        elif col == columname[-1] and zs == True:
            data[columname[-1]] = float(0)
        elif col == columname[-1] and zs == False:
            tmpcol = data[col]
            data[col] = tmpcol.apply(colfilter)
        else:
            tmpcol = data[col]
            data[col] = tmpcol.astype(float)

    return data

def dataStandardize(stocklink):
    stddata = None

    data_str = urllib.urlopen(stocklink).read()
    data_nonascii = rm_nonascii(data_str)
    data = json.loads(data_nonascii[21:-2])
    try:
        data_hq = pd.DataFrame(data[0]['hq'],columns=columname)
        stddata = regulardata(data_hq).sort_index()
    except (KeyError, UnboundLocalError), e:
        print "%s failed: %s"%("func dataStandardize",e.message)
    finally:
        return stddata

def dataStandardizeFile(stockfile):	 # json format file, 000001.json or 600868.json etc
    stddata = None

    with open(stockfile,'r') as f:
        data_str = f.read()
        data_nonascii = rm_nonascii(data_str)
        data = json.loads(data_nonascii[21:-2])
        try:
            data_hq = pd.DataFrame(data[0]['hq'],columns=columname)
            stddata = regulardata(data_hq).sort_index()
        except (KeyError, UnboundLocalError), e:
            print "%s failed: %s" % ("func dataStandardizeFile", e.message)
        finally:
            if (stddata is not None):
                stddata.loc[stddata['incr_rate'] > 0.101, 'incr_rate'] = 0
                stddata.loc[stddata['incr_rate'] < -0.101, 'incr_rate'] = 0

            return stddata

def dataSaveFile(stocklink, stockfile):
    with open(stockfile,"w") as f:
        f.write(urllib.urlopen(stocklink).read())
    
    print "Generated %s" % stockfile

def getLink(name):
    namestr = None
    if name == "000001" or name == "399001":
        namestr = "zs_%s" % (name)
    else:
        namestr = "cn_%s" % (name)

    return "%s%s%s%s%s%s%s" % (stock_piece1, namestr, stock_piece2, start_date, stock_piece3, end_date, stock_piece4)

# calculate the gain rate during the period that selected
def cumprodresult(fid, stock, data):
    cumprslt = (1+data['incr_rate']).cumprod()[-1]
    print "  Cumprod : [%s]" % (cumprslt)
    fid.write(",%s"%(cumprslt))

    return

# calculate vibrate rate, highest - lowest / lowest
def vibrate(fid, stock, data):
    result = (data['highest']-data['lowest'])/data['lowest']
    print "  Vibrate : [%s] [%s] [%s]" % (result.max(),result.min(),result[-1])
    fid.write(",%s,%s,%s"%(result.max(),result.min(),result[-1]))

    return

# calculate ratio between current price and mean price of the lowest 30 days price
def mins(fid, stock, data):
    curvalue = data['end'][-1]
    if stock == "000001" or stock == "399001":
        print "  Mins : [%s] [%s] [%s]"%(0, 0, curvalue)
        fid.write(",%s,%s,%s"%(0, 0, curvalue))
    else:
        datamean = data['end'].sort_values()[:30].mean()

        minsratio = curvalue / datamean
        print "  Mins : [%s] [%s] [%s]"%(datamean, minsratio, curvalue)
        fid.write(",%s,%s,%s"%(datamean, minsratio, curvalue))

    return

def byear(fid, stock, data):
    byearindex = data.index
    strplist = [ datetime.strptime(x,"%Y-%m-%d") for x in byearindex ]
    byear = strplist[0].year
    print "  BYear : [%s]"%byear
    fid.write(",%s"%byear)

    return

methods = {"accumulativeprofit":cumprodresult,"vib":vibrate,"mins":mins,"beginyear":byear}

def getstockfid():
    global FILE
    datafile = stockanalysername
    FILE = open(datafile,'w')

    for keys in methods.keys():
        if keys == 'vib':
            FILE.write(",%s,%s,%s"%("vib_max", "vib_min", "vib_cur"))
        elif keys == 'mins':
            FILE.write(",%s,%s,%s"%("mins_mean_30", "mins_ratio", "cur_price"))
        else:
            FILE.write(",%s"%keys)

    FILE.write("\n")
    return FILE

def closestockfid(f):
    f.close()

    return

def outputtbhead(fid, stock):
    if stock == "000001":
        fid.write("%s%s" % ("SH", stock))
    elif stock == "399001":
        fid.write("%s%s" % ("SZ", stock))
    elif stock[0] == "0" or stock[0] == "3":
        fid.write("%s%s" % ("SZ", stock))
    else:
        fid.write("%s%s" % ("SH", stock))

def mainfile():
    suffix = ".json"
    data = None

    FILE = getstockfid()

    for stock in stock_list:
        stockname = "%s%s%s"%(datapath, stock,suffix)
        data = dataStandardizeFile(stockname)

        if data is None:
            continue

        print "Stock [%s] :" % (stock)
        outputtbhead(FILE, stock)
        for method in methods.keys():
            methods[method](FILE, stock, data)

        FILE.write("\n")
        data = None

    closestockfid(FILE)

def mainlink():
    data = None

    FILE = getstockfid()

    for stock in stock_list:
        stockstr = getLink(stock)
        data = dataStandardize(stockstr)

        if data is None:
            continue

        print "Stock [%s] :" % (stock)
        outputtbhead(FILE, stock)
        for method in methods.keys():
            methods[method](FILE, stock, data)

        FILE.write("\n")
        data = None

    closestockfid(FILE)

def mainsavefile():
    suffix = ".json"
    for stock in stock_list:
        stockname = "%s%s%s" % (datapath, stock, suffix)
        stockstr = getLink(stock)
        dataSaveFile(stockstr, stockname)

def getstocklist():
    global stock_list
    configurefile = stocklistname
    slist = None

    with open(configurefile,"r") as f:
        slist = f.read()

    stock_list = slist.split()
    #print stock_list

def main(argv):
    try:
        opts,args = getopt.getopt(argv[1:],"hlw")
    except getopt.GetoptError,e:
        print e.msg
        sys.exit(1)

    for opt,arg in opts:
        if opt == '-h':
            print "python %s [-lw]"%(argv[0])
            sys.exit(0)
        elif opt == '-w':
            print "Processing from link(only save file):"
            mainsavefile()
            print "Done."
            sys.exit(0)
        elif opt == '-l':
            print "Processing from link:"
            mainlink()
            print "Done."
            sys.exit(0)
        else:
            pass

    print "Processing from file:"
    mainfile()
    print "Done."

if __name__ == "__main__":
    getstocklist()
    main(sys.argv)

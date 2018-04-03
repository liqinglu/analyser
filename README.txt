# man page
python analyser.py -h
python analyser.py -l  -- proceed data from link
python analyser.py -w  -- save data from link to file
python analyser.py     -- proceed data from file


# csv file
stock_list.csv      -- configuration file, stock list is in it
stock_analyser.csv  -- output file, stock analyser data is in it



## manual steps:
In [1]: import numpy as np

In [2]: import pandas as pd

In [3]: import json

In [4]: import urllib

In [5]: import time

In [6]: from datetime import datetime

In [7]: ff = open("./data/002509.json",'r')

In [8]: data_str = ff.read()

In [9]: data_nonascii = ''.join([i if ord(i)<128 else 'x' for i in data_str])

In [10]: data = json.loads(data_nonascii[21:-2])

In [11]: data_hq = pd.DataFrame(data[0]['hq'],columns=['date','start','end','incr','incr_rate','lowest','highest','amount','sum','turnover_rate'])

In [12]:

import numpy as np
import pandas as pd
import json
import sys
import urllib
import time
import re
import os
from datetime import datetime

print "in this version, no more update"

datafile = None
pattern = re.compile(r'\d+')
yourwant = raw_input("Input a six digit stock number:\n")
m = pattern.match(yourwant)
if m is not None:
    datafile = "%s%s%s" % ( "./data/", m.group(0), ".json" )
else:
    print "Input error!"
    sys.exit()

ff = open(datafile, 'r')
data_str = ff.read()
data_nonascii = ''.join([i if ord(i) < 128 else 'x' for i in data_str])
data = json.loads(data_nonascii[21:-2])
data_hq = pd.DataFrame(data[0]['hq'],columns=['date', 'start', 'end', 'incr', 'incr_rate', 'lowest', 'highest', 'amount', 'sum', 'turnover_rate'])
data = data_hq.set_index('date')
data['incr_rate'] = data['incr_rate'].apply(lambda x: float(x[:-1]) / 100)
data.loc[stddata['incr_rate'] > 0.101, 'incr_rate'] = 0
data.loc[stddata['incr_rate'] < -0.101, 'incr_rate'] = 0

# (1+data['incr_rate']).cumprod()[-1]
## add 11111
## add 22222
### add 33333
## add by another man in dev

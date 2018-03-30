import numpy as np
import pandas as pd
import json
import urllib
import time
from datetime import datetime

ff = open("./data/002509.json", 'r')
data_str = ff.read()
data_nonascii = ''.join([i if ord(i) < 128 else 'x' for i in data_str])
data = json.loads(data_nonascii[21:-2])
data_hq = pd.DataFrame(data[0]['hq'],columns=['date', 'start', 'end', 'incr', 'incr_rate', 'lowest', 'highest', 'amount', 'sum', 'turnover_rate'])
data = data_hq.set_index('date')
data['incr_rate'] = data['incr_rate'].apply(lambda x: float(x[:-1]) / 100)
data.loc[stddata['incr_rate'] > 0.101, 'incr_rate'] = 0
data.loc[stddata['incr_rate'] < -0.101, 'incr_rate'] = 0

# (1+data['incr_rate']).cumprod()[-1]
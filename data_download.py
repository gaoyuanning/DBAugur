import requests
import pandas as pd
import datetime
import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO

url = 'http://skyserver.sdss.org/log/en/traffic/x_sql.asp'
query_key = {
    "cmd": "",
    "format": "",
}

headers = {
    "Upgrade-Insecure-Requests": "1",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
}

begin = datetime.date(2019,3,26)
end = datetime.date(2019,3,31)
for i in range((end - begin).days+1):
    day = begin + datetime.timedelta(days=i)
    query_key['format'] = 'csv'
    query_key['cmd'] = "select * from SqlLog where yy=2019 and mm={} and dd={}".format(int(day.month), int(day.day))
    print('down load data of', str(day))

    r = requests.post(url, data=query_key, headers=headers)

    # data_type = {"yy":int, "mm":int, "dd":int, "hh":int, "mi":int, "ss":int, "seq":int, "theTime":str, 
    # "logID":int, "clientIP":str, "requestor":str, "server":str, "dbname":str, "access":str, 
    # "elapsed": float, "busy":str, "rows":int, "statement":str, "error":int, "errorMessage":str, "isvisible":int}
    # dataset = pd.read_csv(StringIO(r.text), sep=',', header=0, dtype=data_type, error_bad_lines=False)
    dataset = pd.read_csv(StringIO(r.text), sep=',', header=0, error_bad_lines=False)
    dataset.to_csv('data/' + str(day) + '.csv', index=False)
    

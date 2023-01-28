import threading
import time
import requests
import pandas as pd
import datetime
import sys
import argparse
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

threadLock = threading.Lock()
current_date = datetime.date(2020, 1, 1) 
end_date = datetime.date(2020, 12, 31) 

class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print ("Thread" + self.name)
        download_data(self.name)

def download_data(threadName):
    global current_date
    global end_date
    while True:
        threadLock.acquire()
        if current_date <= end_date:
            query_key['format'] = 'csv'
            query_key['cmd'] = "select * from SqlLog where yy=2019 and mm={} and dd={}".format(int(current_date.month), int(current_date.day))
            down_date = current_date
            current_date = current_date + datetime.timedelta(days=1)
        else:
            threadLock.release()
            return
        threadLock.release()
        print(threadName, "download the data of", down_date.date())
        r = requests.post(url, data=query_key, headers=headers)
        dataset = pd.read_csv(StringIO(r.text), sep=',', header=0, error_bad_lines=False)
        dataset.to_csv(str(down_date.date()) + '.csv', index=False)

def start_download(num_threads, start_date, _end_date):
    global current_date
    global end_date
    current_date = datetime.datetime.strptime(start_date, '%Y-%m-%d') 
    end_date = datetime.datetime.strptime(_end_date, '%Y-%m-%d') 
    threads = []

    for i in range(int(num_threads)):
        new_thread = myThread(i, "Thread-"+str(i))
        new_thread.start()
        threads.append(new_thread)

    for t in threads:
        t.join()

    print ("Finish")

if __name__ == '__main__':
    aparser = argparse.ArgumentParser(description='Download SQL Logs')
    aparser.add_argument('--num_threads', help='Number of Threads', default='10')
    aparser.add_argument('--start_date', help='Start Date of the Log', default='2019-01-01')
    aparser.add_argument('--end_date', help='End Date of the Log', default='2019-12-31')
    args = vars(aparser.parse_args())

    start_download(args['num_threads'], args['start_date'], args['end_date'])
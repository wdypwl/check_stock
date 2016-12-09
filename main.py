import sys

from urllib import request
import parserMoney

from parserMoney import parser_stock_text
import py_util
import config
import time
from py_util import connect_mysql
import datetime
url = "http://hq.sinajs.cn/list=sz880471"

# filePath = "d:\\炒股\\program\\log\\log.txt"
# text = request.urlopen(url).read()

connect_mysql()
for i in range(1, 2):
    print(i)

# py_util.get_history_data_by_html(600000)
# text = "sg%06.0f" %(12)
# print(text)
# py_util.get_all_stock_history_data()
# text = "sh123456"
# print(text[2:])
#print(datetime.datetime.today().)
date_format = datetime.datetime.now().strftime("%Y%m%d")
print(date_format)
text = "he heh"
makeTime = (2016,4,1,16,41,10,0,0,0)
print(time.mktime((2016,4,1,16,41,10,0,0,0)))
print(time.time())
year = time.strftime('%H-%M', time.localtime(time.time()))
print(year)
print("test datetime")
anyday= datetime.datetime(2016,12, 8).weekday() #strftime("%w");
print (3000 << 32)
dYear= year.split("-")
print(dYear)
print(int(dYear[0]))
x=text.split()
print(''.join(x))
common = input("input common 1,get today_all_Info 2, get all history info, 3 check stock from local, common =  ")
common = int(common)
#print( py_util.get_all_stock_today_volume())
if common == 1:
    py_util.get_all_stock_today_data()
elif common == 2:
    py_util.get_all_stock_history_data(config.ALL_YEARS)
elif common == 3:
    py_util.get_all_stock_history_data(config.LAST_SEASON)
elif common == 4:
    py_util.dynamic_check_stock_info()
elif common == 5:
    # stock_number = input("input stock number =")
    check_list = ["sh600188", "sh600267","sh600559","sh601688", "sh601318",
                  "sh601928", "sh600839", "sh601328", "sh600096", "sh600036",
                  "sz000031", "sz000861", "sh600022", "sh600784"]
    for i in check_list:
        parserMoney.check_a_stock_month_data(i)
elif common == 6:
    result = py_util.get_data_by_day("sh601318", 20160101, 20160130)
    print(result)
elif common == 7:
    #nowDay = time.strftime('%Y%m%d', time.localtime(time.time()))
    now = datetime.datetime.now()
    begin_time = now - datetime.timedelta(20)
    py_util.get_all_stock_total_volumn(begin_time, now)
elif common == 8:
    py_util.check_stock_in_months_for_least_price()
elif common == 9: #不断的获取今天的stock的所有交易量，如果超过3点，就将数据保存
    getSave=True
    while(True):
        nowTime = time.strftime('%H%M', time.localtime(time.time()))
        nowTime = int(nowTime)
        if nowTime > 1510 and getSave:
            py_util.get_all_stock_today_data()
            getSave=False
        elif nowTime < 1510 and not getSave:
            getSave=True

        total = py_util.get_all_stock_today_volume()
        print(nowTime, "  ", total)
        time.sleep(300)

else:
    print("error not find the common ", common)

# fp = open(filePath,"w")
# fp.write(content)

# fp.close()
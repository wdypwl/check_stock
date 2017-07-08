import sys

from urllib import request
import parserMoney

from parserMoney import parser_stock_text
import py_util
import config
import time
from py_util import connect_mysql
import datetime
import math
import mgr_pe
from datetime import date
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
makeTime = (2016, 4, 1, 16, 41, 10, 0, 0, 0)
print(time.mktime((2016, 4, 1, 16, 41, 10, 0, 0, 0)))
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
# for test
lastUpdateDate = py_util.get_last_update_date("sh601688")
print("lastUpdateDate is ", lastUpdateDate)
lastYear =  math.floor(lastUpdateDate/10000)
print("lastYear is", lastYear)
last_month = int((lastUpdateDate - lastYear * 10000)/100)
print("last_month is", last_month)
lastSeason = math.ceil(last_month / 3)
print("lastSeason is", lastSeason)
common = input("input common 1,get today_all_Info 2, get all history info, 3 check stock from local, common =  ")
common = int(common)


if common == 1:
    py_util.get_all_stock_today_data()
elif common == 2:
    py_util.get_all_stock_history_data(config.ALL_YEARS)
elif common == 3:
    py_util.get_all_stock_history_data(config.LAST_SEASON)
elif common == 4:
    py_util.dynamic_check_stock_info()
elif common == 5:
    py_util.check_one_stock_least_price("sz000046", 20170208, 20170707)
elif common == 6:
     py_util.get_stock_history_data("sz000046", config.LAST_YEAR)
elif common == 7:
    #nowDay = time.strftime('%Y%m%d', time.localtime(time.time()))
    now = datetime.datetime.now()
    begin_time = now - datetime.timedelta(20)
    py_util.get_all_stock_total_volumn(begin_time, now)
elif common == 8:
    py_util.check_stock_in_months_for_least_price()
elif common == 10: #更新特定的stock，并检查是否满足特定的条件
    py_util.update_given_stocks_and_check_condition(config.given_list)
elif common == 11: # 获取stock 的profit数据
    mgr_pe.get_all_stock_pe_data()
elif common == 12: # 获取stock 的profit数据
    mgr_pe.check_all_stock_pe()
else:
    print("error not find the common ", common)

# fp = open(filePath,"w")
# fp.write(content)

# fp.close()
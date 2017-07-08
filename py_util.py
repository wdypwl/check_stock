__author__ = 'Administrator'


from mysql import connector
from urllib import request
import parserMoney
import re
import os
import time
from Stock import Stock
import config
import math
import datetime
import mgr_pe
conn_price = 0  # 价格表的数据库链接


def connect_mysql():
    global conn_price
    conn_price = connector.connect(user='wdy', passwd='wdy', host='localhost', db='money_data')
    # create_table("中601390")

def get_conn_price():
    global conn_price
    return conn_price
def check_price_table_is_exist(name):
    global conn_price
    cursor = conn_price.cursor()
    is_exist = " select count(*) from information_schema.tables  where table_name = '%s';" %(name)
    cursor.execute(is_exist)
    [(exists,)] = cursor.fetchall()
    # print(exists)
    if exists > 0:
        # print(name, 'is Exist')
        return True
    return False


# 创建stock表，每一个stock对应一个表
def create_table(name):
    global conn_price
    cursor = conn_price.cursor()
    # is_exist = " select count(*) from information_schema.tables  where table_name = '%s';" %(name)
    # # print(is_exist)
    # cursor.execute(is_exist)
    # [(exists,)] = cursor.fetchall()
    # # print(exists)
    # if exists > 0:
    #     # print(name, 'is Exist')
    #     return
    if check_price_table_is_exist(name):
        return
    create_table_str = "create TABLE %s (date int primary key, name varchar(60) CHARACTER SET utf8,  lastPrice float, todayBeginPrice float,todayPrice float, todayMaxPrice float, todayMinPrice float, volume int, totalMoney int, rate float, isWarn int );" %(name)
    # print(create_table_str)
    cursor.execute(create_table_str)
    conn_price.commit()

# 将数据保存到数据库
def save_data(stock_number, save_info):
    create_table(stock_number)
    save_data_no_check_table(stock_number, save_info)
    # print(save_info)
    # print(save_info[1])

def change_all_name(stock_number, save_info):
    try:
        global conn_price
        cursor = conn_price.cursor()
        #tempInfo = (stock_number,) + save_in`fo[1]
        excut_str="update %s set name='%s';" % (stock_number, save_info[1])
        print(excut_str)
        cursor.execute(excut_str)
        conn_price.commit()
    except Exception as e:
        print('error  change_all_name = ', stock_number, "error = ", e)

    # 先判断是否已经保存了
def save_data_no_check_table(stock_number, save_info):

    # temp = "sg %s %s %d" % tempTuple
    # print(temp)
    try:
        global conn_price
        cursor = conn_price.cursor()
        #先判断是否有该日期记录
        is_exist = " select count(*) from %s  where date = '%s';" %(stock_number,save_info[0])
        cursor.execute(is_exist)
        [(exists,)] = cursor.fetchall()
        # print(exists)
        if exists > 0:
            insertInfo = (stock_number,) + save_info[2:] + (save_info[0],)
            #print(insertInfo)
            upOrIn_str = "update %s set  lastPrice=%.3f,todayBeginPrice=%.3f,todayPrice=%.3f,todayMaxPrice=%.3f,todayMinPrice=%.3f,volume=%d,totalMoney=%d,rate=%.3f,isWarn=%d where date=%d;" % insertInfo
        else:
            tempInfo = (stock_number,) + save_info
            upOrIn_str = "insert into %s(date,name,lastPrice,todayBeginPrice,todayPrice,todayMaxPrice,todayMinPrice,volume,totalMoney,rate,isWarn) values(%d, '%s', %.3f, %.3f, %.3f, %.3f, %.3f, %d, %d, %.3f, %d);" % tempInfo
        #print(upOrIn_str)
        cursor.execute(upOrIn_str)
        conn_price.commit()
    except Exception as e:
        print('error  stock_number = ', stock_number, "error = ", e)
#获取最近的一个工作日日期
def get_close_work_day(date):
    year = int(date /10000)
    month = int((date - year * 10000)/100)
    day = int(date - (year * 10000 + month * 100))
    date_time = datetime.datetime(year, month, day)
    oneday = datetime.timedelta(days=1)
    date_time = date_time - oneday
    date = date_time.year * 10000 + date_time.month * 100 + date_time.day
    week_day = date_time.weekday()
    if week_day == 5:  #周六
        oneday = datetime.timedelta(days=1)
        date_time = date_time - oneday
        date = date_time.year * 10000 + date_time.month * 100 + date_time.day
    else:
        #是否周日
        if week_day == 6:
            twoday = datetime.timedelta(days=2)
            date_time = date_time - twoday
            date = date_time.year * 10000 + date_time.month * 100 + date_time.day

    return date

# 从新浪获取历史数据
def get_history_data_by_html(stock_number, stockName,year,season):
    url = "http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/%s.phtml?year=%d&jidu=%d" %(stock_number[2:],year,season)
    print(url)
    while(True):
        try:
            text = request.urlopen(url).read()
            break
        except Exception as e:
            print("error get_history_data_by_html number = ",stock_number, "request.urlopen exception error =", e)
            time.sleep(120)

    text = text.decode('gb2312')

    reg = r"<a target='_blank'\s+href='http://vip.stock.finance.sina.com.cn/quotes_service/view/vMS_tradehistory.php\?symbol=\w{8}&date=\d{4}-\d{2}-\d{2}'>\s*([^\s]+)\s+</a>\s*</div></td>\s*<td[^\d]*([^<]*)</div></td>\s+<td[^\d]*([^<]*)</div></td>\s+<td[^\d]*([^<]*)</div></td>\s+<td[^\d]*([^<]*)</div></td>\s+<td[^\d]*([^<]*)</div></td>\s+<td[^\d]*([^<]*)</div></td>\s+"
    pattern = re.compile(reg)
    reg_list = pattern.findall(text)
    #print(reg_list)
  #  stock_number= "sh%s" %(stock_number)
    # 先创建表
    create_table(stock_number)
    length = len(reg_list)

    for index in range(0, length):
        i = reg_list[index]
        date = i[0]
        date = int(date.replace('-', ""))
        last_price = 0
        if stock_number == "sh601688":
            print(i)
        try:
            if (index + 1) < length:
                last_price = float(reg_list[index+1][3])
            else:
                last_work_day = get_close_work_day(date)
                last_price = get_one_date_closing_price(stock_number,last_work_day)
                if not last_price:
                    last_work_day = get_close_work_day(date)
                    last_price = get_one_date_closing_price(stock_number,last_work_day )
                if not last_price:
                    last_price = 0.1
        except Exception as e:
            print("error get_history_data_by_html not get last price = ", date, "exception is ", e )
        try:
            begin_price = float(i[1])
            max_price = float(i[2])
            now_price = float(i[3])
            min_price = float(i[4])
            volumes = int(i[5])
            total_money = int(i[6])
            rate = (now_price - last_price)/last_price * 100
            save_info = date, stockName, last_price, begin_price, now_price, max_price, min_price, volumes, total_money, rate, 0
            save_data_no_check_table(stock_number, save_info)
        except Exception as e:
            print("error get_history_data_by_html number = ",stock_number, "date = ", date, " error =", e )
def get_stock_history_data(stock_number, option):
    url = "http://hq.sinajs.cn/list=%s" %(stock_number)
    #print("get_stock_history_data url = ", url)
    while(True):
        try:
            text = request.urlopen(url).read()
            break
        except Exception as e:
            print("error get_stock_history_data number = ", stock_number, "request.urlopen exception error =", e)
            time.sleep(120)

    text = text.decode('gb2312')
    pos = text.find('"', 1)
    if stock_number == "sh601688":
        print(stock_number)
    # print(text)
    if pos == 0:#没有内容
        return
    else:
        #print("get_stock_history_data text = ", text, "get_stock_history_data pos = ", pos)
        text = text[pos+1:]
        if len(text) < 10:
            return
        #print("get_stock_history_data leave text", text)
        text = text.split(',')
        nowYear = time.strftime('%Y', time.localtime(time.time()))
        month = time.strftime('%m', time.localtime(time.time()))
        if option == config.ALL_YEARS:
            lastUpdateDate = get_last_update_date(stock_number)
            if lastUpdateDate > 0:
                lastYear =  math.floor(lastUpdateDate/10000)
                last_month = int((lastUpdateDate - lastYear * 10000)/100)
                lastSeason = math.ceil(last_month / 3)
                # if lastSeason >= 4:
                #     lastYear=lastYear+1
                #     lastSeason=1
            else:
                lastYear = 2006
                lastSeason = 1
            if stock_number == "sh601688":
                print("sh601688 year is", lastYear, "last season is ", lastSeason)
            for year in range(lastYear,int(nowYear)+1):
                for season in range(lastSeason, 5):
                    get_history_data_by_html(stock_number, text[0], year, season)
        elif option == config.LAST_SEASON:
            season = math.ceil(int(month)/3)
            get_history_data_by_html(stock_number, text[0], int(nowYear), season)
        elif option == config.LAST_YEAR:
            date_format = datetime.datetime.now().strftime("%Y")
            lastYear = int(date_format) - 1
            lastSeason = 1
            for year in range(lastYear,int(nowYear)+1):
                for season in range(lastSeason, 5):
                    get_history_data_by_html(stock_number, text[0], year, season)

def get_all_stock_history_data(option):
    for i in range(1,1000):
        stock_number = "sz%06.0f" %(i)
        get_stock_history_data(stock_number, option)

    # 泸市A股
    for i in range(600000, 604000):
        stock_number = "sh%d" %(i)
        get_stock_history_data(stock_number, option)


# 根据网址获得数据
def get_stock_text_by_url(stock_number):
    url = "http://hq.sinajs.cn/list=%s" % (stock_number)
    while(True):
        try:
            text = request.urlopen(url).read()
            break
        except Exception as e:
            print("get_stock_text_by_url stockNumber =", stock_number, " get url have exception = ", e)
            time.sleep(20)
    text = text.decode('gb2312')
    pos = text.find('"', 1)
    # print(text)
    if pos == 0:
        return None
    else:
        # print("now_get_stock_data text = ", text, "now_get_stock_data pos = ", pos)
        text = text[pos+1:]
        if len(text) < 10:
            return None

        # print("now_get_stock_data leave  text", text)
        return text.split(',')


# 获取今天所有stock的数据并且保存
def get_all_stock_today_data():
    def for_each_stock(stock_number):
        text = get_stock_text_by_url(stock_number)
        if text:
            result = parserMoney.parser_stock_text(text)
            #change_all_name(stock_number, result)
            save_data(stock_number, result)
    for i in range(1, 1000):
        temp = "sz%06.0f" %(i)
        for_each_stock(temp)
    for i in range(600000, 604000):
        temp = "sh%d" %(i)
        for_each_stock(temp)
#从数据库获取某天所有stock的数据

# 获取历史某天所有stock的数据并且保存
def get_all_stock_total_volumn(beginDate, endDate):
    # for iDate in range(beginDate, endDate):
    iDate = beginDate
    while(iDate <= endDate):
        totoal_value = 0
        date = int(iDate.strftime("%Y%m%d"))
        for i in range(1, 1000):
            temp = "sz%06.0f" %(i)
            value_info = get_all_valume_by_one_date(temp, date)
            length = len(value_info)
            if length > 0:
                totoal_value = totoal_value + value_info[0][7]
        for i in range(600000, 604000):
            temp = "sh%d" %(i)
            value_info = get_all_valume_by_one_date(temp, date)
            length = len(value_info)
            if length > 0:
                totoal_value = totoal_value + value_info[0][7]
        print(date, totoal_value/10000)

        iDate = iDate + datetime.timedelta(1)



# 从数据库查询一段时间内的数据
def get_data_by_day(stock_number, beginDate, EndDate):
    select_str = "select * from %s where date >= %d and date <= %d" % (stock_number, beginDate, EndDate)
   # print(select_str)
    cursor = conn_price.cursor()
    try:
        cursor.execute(select_str)
        allData = cursor.fetchall()
    except Exception as e:
       # print("error get_data_by_day, exception = ", e)
        return []
    # 将所有的交易量转为万
    # for i in allData:
    #     i[7] = i[7]/10000
    return allData

def get_all_valume_by_one_date(stock_number, date):

    select_str = "select * from %s where date = %d" % (stock_number, date)
    # print(select_str)
    cursor = conn_price.cursor()
    try:
        cursor.execute(select_str)
        allData = cursor.fetchall()
    except Exception as e:
        #print("error get_data_by_day, exception = ", e)
        return []
    # 将所有的交易量转为万
    # for i in allData:
    #     i[7] = i[7]/10000
    return allData

#查询某个stock的某个日期的收盘价
def get_one_date_closing_price(stock_number, date):
    select_str = "select todayPrice from %s where date=%d" %(stock_number, date)
    cursor = conn_price.cursor()
    try:
        cursor.execute(select_str)
        data = cursor.fetchall()
        length = len(data)
        if length > 0:
            return data[0][0]
        else:
            return 0
    except Exception as e:
        print("error get_last_update_date, exception = ", e)
    return 0
def get_last_update_date(stock_number):
    #---获取上次更新的日期----
   # is_exist = " select count(*) from information_schema.tables  where table_name = '%s';" %(name)
    select_str = "select max(date) from %s" %(stock_number)

    cursor = conn_price.cursor()
    try:
        cursor.execute(select_str)
        data = cursor.fetchall()
        length = len(data)
        if length > 0 and data[0] and data[0][0]:
            return data[0][0]
        else:
            return 0
    except Exception as e:
        print("error get_last_update_date stock number =", stock_number, " exception = ", e)
    return 0


def check_all_stock():
    begin_date = 20150616
    end_date = 201506117
    for i in range(1, 1000):
        stock_number = "sz%06.0f" %(i)
        parserMoney.get_stock_info_by_some_condition(stock_number, begin_date, end_date, True)

    for i in range(600000, 604000):
        stock_number = "sh%d" %(i)
        parserMoney.get_stock_info_by_some_condition(stock_number, begin_date, end_date, True)


def dynamic_check_stock_info():
    #check_list = "sh600022", "sh601928", 'sh600036', "sh600096", "sh601328", 'sh601328', "sh601318", "sh600839", "sz000031", "sz000861", "sh600030"
    check_list="sh601318","sh601328"
    stock_list = {}
    # 上证号码 'sh000001'
    for i in check_list:
        stock_list[i] = Stock(i, 20150617, 501506184)
    is_continue = True
    while is_continue:
        time.sleep(0.1)  # 睡眠两秒
        cls=os.system('clear')
        for (k, v) in stock_list.items():
            is_continue = v.get_and_print()
            if not is_continue:
                break

# 获取今天所有stock的交易量
def get_all_stock_today_volume():
    all_volume = 0
    def for_each_stock(stock_number,totalNum):
        text = get_stock_text_by_url(stock_number)
        if text:
            return totalNum + int(text[8])
        else:
            return totalNum
           # result = parserMoney.parser_stock_text(text)
    for i in range(1, 1000):
        temp = "sz%06.0f" %(i)
        all_volume =  for_each_stock(temp, all_volume)
    for i in range(600000, 604000):
        temp = "sh%d" %(i)
        all_volume = for_each_stock(temp, all_volume)

    return all_volume

#check all stock， get least stock between six month
#检查那个stock到底半年的最低点
def check_stock_in_months_for_least_price():
    now = datetime.datetime.now()
    begin_time = now - datetime.timedelta(360)
    # end = int(now.strftime("%Y%m%d"))
    begin = int(begin_time.strftime("%Y%m%d"))
    # for_each_stock("sh601318", begin, end)
    for stock_code in get_next_stock_number():
        text = get_stock_text_by_url(stock_code)
        if text:
            result = parserMoney.parser_stock_text(text)
            #change_all_name(stock_number, result)
            now_price = result[4]
            save_data(stock_code, result)
            end = result[0]
            if mgr_pe.check_condition_pe_pb(stock_code, now_price, 20, 10, 10, 3):
                check_one_stock_least_price(stock_code, begin, end)

def check_one_stock_least_price(stock_number, begin_date, end_date):
    text = get_data_by_day(stock_number, begin_date, end_date)
    length = len(text)
    now_price = 0
    # date_format = datetime.datetime.now().strftime("%Y%m%d")
    now_date = end_date
    # print(length)
    if length > 0:
        min = text[0][4]
        min_day = text[0][0]
        for i in text:
            # print(i[0], i[1], i[4])
            if i[0] == now_date:
                now_price = i[4]
            if i[4] > 0.1 and i[4] < min:
                min = i[4]
                min_day = i[0]
        # if stock_number == "sh601688":
        #     print("now_price= ", now_price, "min =", min)
        if now_price > 0:
            min_rate = 1.05
            if now_price <= (min * min_rate):
                print(stock_number, " ", text[0][1], " now price =", now_price, " min price = ", min, " min day =",
                      min_day)




"""    for i in range(1, 1000):
        temp = "sz%06.0f" %(i)
        for_each_stock(temp)
    for i in range(600000, 604000):
        temp = "sh%d" %(i)
        for_each_stock(temp)
        """


def update_given_stocks_and_check_condition(list):
    now = datetime.datetime.now()
    begin_time = now - datetime.timedelta(config.TIME_MID_YEAR)
    end = int(now.strftime("%Y%m%d"))
    begin = int(begin_time.strftime("%Y%m%d"))
    for i in list:
        get_stock_history_data(i, config.ALL_YEARS)
        check_one_stock_least_price(i, begin, end)


# 检测某个stock是否存在
def check_stock_exist(stock_name):
    # 暂时使用该方法
    text = get_stock_text_by_url(stock_name)
    if text:
        return True
    return False

def get_next_stock_number():
    for i in range(1,1000):
        stock_number = "sz%06.0f" %(i)
        yield stock_number
    # 泸市A股
    for i in range(600000, 604000):
        stock_number = "sh%d" %(i)
        yield stock_number










__author__ = 'Administrator'
from urllib import request
import py_util
import re
import os
import time
import parserMoney
# 获取stock的pe，profit

pe_table_name = "all_stock_now_pe"
TOTAL_CAPITAL_INDEX = 0
MGJZC_INDEX = 1
STOCK_STATE_INDEX = 2
PROFIT_INDEX = 3
PROFIT_FOUR_INDEX = 4
CAPITAL_UNIT = 10000
PROFIT_UINT = 100000000

# 创建stock利润，流通股数表
def create_now_pe_table():
    global pe_table_name
    name = pe_table_name
    if py_util.check_price_table_is_exist(name):
        return
    conn_price = py_util.get_conn_price()
    cursor = conn_price.cursor()
    # stock_code  代号
    # lastfive //过去5个交易日平均每分钟成交量
    # totalcapital 总股本
    # currcapital 流通股本
    # mgjzc    //最近报告的每股净资产
    # stock_state //个股状态（0:无该记录; 1:上市正常交易; 2:未上市; 3:退市）
    # profit //最近年度净利润
    # profit_four //最近四个季度净利润
    # stockname  //股票名称
    create_table_str = "create TABLE %s (stock_code  varchar(30) CHARACTER SET utf8 primary key, lastfive float, totalcapital  float, currcapital  float, mgjzc float, stock_state int, profit float, profit_four float, stockname varchar(50) CHARACTER SET utf8, business_scope varchar(100) CHARACTER SET utf8);" %(name)
    # print(create_table_str)
    cursor.execute(create_table_str)
    conn_price.commit()

# 从网站获取某个stock的数据
def get_stock_now_pe(stock_code):
    url = "http://finance.sina.com.cn/realstock/company/%s/nc.shtml" %(stock_code)
    print(url)
    text = ''
    while(True):
        try:
            text = request.urlopen(url).read()
            break
        except Exception as e:
            #print("error get_stock_now_pe number = ",stock_code, "request.urlopen exception error =", e)
            if e.__str__() == "HTTP Error 404: Not Found":  #如果改stock不存在，直接返回
                return None
            print("error get_stock_now_pe number = ",stock_code, "request.urlopen exception error =", e)
            time.sleep(30)

    text = text.decode('gbk', 'ignore')
    #print(text)
    reg = r"\nvar lastfive = (.*);.*\n.*\nvar totalcapital = (.*);.*\nvar currcapital = (.*);.*\n"
    pattern = re.compile(reg)
    match = pattern.search(text)
    lastfive = float(match.group(1))
    totalcapital = float(match.group(2))
    currcapital = float(match.group(3))
    #print(match.group(), match.end(match.lastindex),match.endpos)
    #reg_1 = r"\nvar mgjzc = (.*);"
    reg_1 = r"\nvar mgjzc = (.*);.*\nvar stock_state = (.*);//.*\n.*\nvar profit = (.*);.*\nvar profit_four = (.*);.*\n.*\nvar stockname = '(.*)';"
    pattern_1 = re.compile(reg_1)
    match = pattern_1.search(text, match.end(match.lastindex))
    mgjzc = float(match.group(1))  # 最近报告的每股净资产
    stock_state = int(match.group(2))  # 个股状态（0:无该记录; 1:上市正常交易; 2:未上市; 3:退市）
    profit = float(match.group(3))
    profit_four = float(match.group(4))
    stockname = match.group(5)
    reg_2 = r"\n<a.*target='_blank'>(.*)</a> \n</p>"
    pattern_2 = re.compile(reg_2)
    match = pattern_2.search(text)
    business_scope = match.group(1)
    # print(lastfive, totalcapital, currcapital, mgjzc, stock_state, profit, profit_four, stockname)
    return lastfive, totalcapital, currcapital, mgjzc, stock_state, profit, profit_four, stockname, business_scope

    # 先判断是否已经保存了
def save_pe_data(stock_code, save_info):
    global pe_table_name
    # temp = "sg %s %s %d" % tempTuple
    # print(stock_code, save_info)
    upOrIn_str = ''
    try:
        conn_price = py_util.get_conn_price()
        cursor = conn_price.cursor()
        #先判断是否有该日期记录
        is_exist = " select count(*) from %s  where stock_code = '%s';" %(pe_table_name,stock_code)
        cursor.execute(is_exist)
        [(exists,)] = cursor.fetchall()
        # print(exists)
        if exists > 0:
            insertInfo = (pe_table_name,) + save_info + (stock_code,)
            # stock_code  varchar(30) primary key, lastfive float, totalcapital  float, currcapital  float, mgjzc float, stock_state int, profit float, profit_four int, stockname varchar(50) )
            upOrIn_str = "update %s set  lastfive=%.3f,totalcapital=%.3f,currcapital=%.3f,mgjzc=%.3f,stock_state=%d,profit=%.3f,profit_four=%.3f,stockname='%s',business_scope='%s' where stock_code='%s';" % insertInfo
        else:
            tempInfo = (pe_table_name,) + (stock_code,) + save_info
            upOrIn_str = "insert into %s (stock_code,lastfive,totalcapital,currcapital,mgjzc,stock_state,profit,profit_four,stockname,business_scope) values('%s', %.3f, %.3f, %.3f, %.3f, %d, %.3f, %.3f, '%s', '%s');" % tempInfo
        #print(upOrIn_str)
        cursor.execute(upOrIn_str)
        conn_price.commit()
    except Exception as e:
        print('save_pe_data error  stock_number = ', stock_code, "error = ", e, " upOrIn_str = ", upOrIn_str)


def get_all_stock_pe_data():
    # 先创建数据库
    create_now_pe_table()
    for stock_code in py_util.get_next_stock_number():
        pe_info = get_stock_now_pe(stock_code)
        if pe_info:
            save_pe_data(stock_code, pe_info)

            # total_share = price * total_capital * 10000
            # if profit_four > 0:
            #     pe = total_share / profit_four / 100000000


def get_pe_pb(stock_code):
    select_str = "select totalcapital, mgjzc, stock_state, profit, profit_four from %s where stock_code='%s'" %(pe_table_name, stock_code)
    conn_price = py_util.get_conn_price()
    cursor = conn_price.cursor()
    try:
        cursor.execute(select_str)
        data = cursor.fetchall()
        length = len(data)
        if length > 0:
            total_capital = data[0][0]
            mgjzc = data[0][1]
            stock_state = data[0][2]
            profit = data[0][3]
            profit_four = data[0][4]
            return total_capital, mgjzc, stock_state, profit, profit_four
        else:
            return None
    except Exception as e:
        print("stock_code = ", stock_code, " error check_less_pe, exception = ", e)
    return None


def check_profit_growth_rate(now_profit, last_profit, campare_rate=0):
    # 如果相等，就可能是第一季报还没有出来，直接返回true
    if now_profit == last_profit or not campare_rate == 0:
        return True
    rate = (now_profit - last_profit)/last_profit *100
    if rate >= campare_rate:
        return True
    return False
def check_condition_pe_pb(stock_code, price, check_pe, check_pe_min=0, profit_grouth=None, check_pb=None):
    data = get_pe_pb(stock_code)
    if not data:
        return False
    total_share = price * data[TOTAL_CAPITAL_INDEX] * CAPITAL_UNIT
    # 盈利才计算，小于0就亏本了
    if data[PROFIT_FOUR_INDEX] <= 0:
        return False
    total_profit = data[PROFIT_FOUR_INDEX] * PROFIT_UINT
    pe = total_share/total_profit
    pro_grouth = profit_grouth or 10
    # 要判断今天是否比上一年的利润增多10
    is_grouth = check_profit_growth_rate(data[PROFIT_FOUR_INDEX], data[PROFIT_INDEX], pro_grouth)
    if not is_grouth:
        return False
    if check_pb:
            if data[MGJZC_INDEX] <= 0:
                return False
            pb = price/data[MGJZC_INDEX]
            if check_pe_min < pe <= check_pe and pb <= check_pb:
                return True
    else:
        if check_pe_min < pe <= check_pe:
            return True
    return False


def check_all_stock_pe():
    for stock_code in py_util.get_next_stock_number():
        text = py_util.get_stock_text_by_url(stock_code)
        if text:
            result = parserMoney.parser_stock_text(text)
            now_price = result[4]
            if now_price > 0 and check_condition_pe_pb(stock_code, now_price, 10):
                print(result[1], now_price, stock_code)




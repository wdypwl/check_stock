__author__ = 'Administrator'
import py_util
from datetime import date
import datetime


def parser_stock_text(text):

    now_price = float(text[3])
    last_price = float(text[2])
    today_begin_price = float(text[1])
    if last_price <= 0:
        last_diff = now_price
    else:
        last_diff = (now_price - last_price) / last_price * 100
    if today_begin_price == 0:
        today_diff = now_price
    else:
        today_diff = (now_price - today_begin_price) / today_begin_price * 100

    # last_diff = last_diff / last_price
    # today_diff = today_diff / today_begin_price
    # print('now time is  ',  text[31],  'numbers = ', text[8], 'total gold =', text[9])
    # print(text[0], '\n')
    # print('now price = ', now_price, ' last day price = ', last_price, ' today begin price = ', today_begin_price, '\n')
    # print('price: ', now_price, ' ', 'lastPer = ', last_diff, ' ', 'todayPer=', today_diff, ' \n')
    # print('price: ', text[3], '\n')
    # print(text[3])
    # print(text[0])
    new_str = text[30].replace('-',"")
    int_date = int(new_str)
    # print(int_date)
    return int_date, text[0], last_price, today_begin_price, now_price, float(text[4]), float(text[5]), int(text[8]), int(float(text[9])), last_diff, 0

def parser_stock_and_print(stock_number, text):
    now_price = float(text[3])
    last_price = float(text[2])
    diff = (now_price - last_price) / last_price * 100
    print(text[0], stock_number, "now price = ", now_price, "diff = ", diff, "total money = ",  text[9], "total volumes = ", text[8] )
    return True

def get_stock_info_and_save(stock_number):
    url = "http://hq.sinajs.cn/list=%s" %(stock_number)



def get_stock_info_by_some_condition(stock_number, begin_date, end_date, isReduce, ):
    allData = py_util.get_data_by_day(stock_number, begin_date, end_date)
    # print("get_stock_info_by_some_condition begindate  = ", begin_date, "end date =", date)
    if isReduce:
        today_max_rise_and_last_reduce(allData)
        # if check_is_reduce_condition(allData):
        #     print("finish find stock ", stock_number, allData[0][1], allData[0][4])
def today_max_rise_and_last_reduce(text):
    length = len(text)
    if length <= 0:
        return False
    # text是从数据库取出的近来n天的数据
    text = sorted(text, key=lambda data: data[0], reverse=True)
    if text[0][9] >= 9.5 and text[1][9] >= -3 and text[1][9] <= 0:
        for i in text:
            print(i[0], i[1], i[4], i[9])

def check_is_reduce_condition(text):
    length = len(text)
    if length <= 0:
        return False
    # text是从数据库取出的近来n天的数据
    text = sorted(text, key=lambda data: data[0], reverse=True)
    reduce = 0
    total_money = 0
    total_volumes = 0
    length = len(text)
    for i in text:
        rate = i[9]

        if rate >= (-2) and rate <= 1.5:
            total_money = total_money + i[8]
            total_volumes = total_volumes + i[7]
            pass
        else:
            # print("rate no perfi rate =", rate)
            return False
    average_volume = total_volumes / length
    if (total_money / length) > 500000000 and text[0][7] < (average_volume*0.9):
        print("average_volumes = ", average_volume*0.8)
        return True
    else:
        # print(length, "\n", text)
        # print(" money or volumes no perif averge money = ", (total_money / length), " average volumes = ", text[0][7], " allow volume = ", (average_volume*0.9))
        return False

def check_is_rise_condition(text):
        # text是从数据库取出的近来几天天的数据
    length = len(text)
    if length <= 0:
        return
    sort_list = sorted(text, key=lambda data: data[0], reverse = True)
    rise = 0
    for i in text:
        rate = rate + i[9]
    if rate / len(text) >= 4:
        return True
    else:
        return False


def analysis_stock_data(text):

    if len(text) <= 0:
        return False
    # text是从数据库取出的近来n天的数据
    text = sorted(text, key=lambda data: data[0], reverse=True)


    def print_average_info(data_str, day_numbers):
        total_money = 0
        total_price = 0
        total_rate = 0
        total_volumes = 0
        for index in range(0, day_numbers):
            data = data_str[index]
            total_volumes += data[7]
            total_money += data[8]
            total_price += data[4]
        last_price = data_str[day_numbers][4]
        total_rate = (data_str[0][4] - last_price)/last_price * 100
        temp_str = "%d day price = %f average : volumes = %d money = %d price = %f total_rate = %f" % (day_numbers, last_price, total_volumes/day_numbers/10000, total_money/day_numbers/10000,total_price/day_numbers,total_rate)
        print(temp_str)
    print_list = [len(text) - 1, 22, 10, 5, 3, 1]
    for i in print_list:
        print_average_info(text, i)

def check_a_stock_month_data(stock_number):
    end_date = date.today()
    end_str = str(end_date)
    begin_date = month_get(end_date)

    end_date = end_str.replace("-", "")
    print("now day =", end_date)
    end_date = int(end_date)

    text = py_util.get_data_by_day(stock_number, begin_date, end_date)
    if len(text) == 0:
        print("error not find date by stock_number = ", stock_number)
        return
    print("check stock number =", stock_number)
    print("check stock =", text[1][1])
    analysis_stock_data(text)
    print_days_data(stock_number)

def month_get(d):
    month = d.month - 2
    if d.month <= 0:
        return (d.year-1) * 10000 + (12 - month) * 100 + d.day
    else:
        return d.year * 10000 + month*100 + d.day
def print_days_data(stock_number):
    end_date = date.today()
    end_str = str(end_date)
    end_date = end_str.replace("-", "")
    end_date = int(end_date)
    begin_date = 20150612
    text = py_util.get_data_by_day(stock_number, begin_date, end_date)
    for i in text:
        print("date = ", i[0], " volumes = ", i[7]/10000, " money = ", i[8]/10000, " price = ", i[4], " rate = ", i[9])


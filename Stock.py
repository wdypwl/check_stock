__author__ = 'wdy'

import py_util
import parserMoney


class Stock(object):
    def __init__(self, stock_number, begin_date, end_date):
        self.stock_number = stock_number
        self.text=[]
       # self.text = py_util.get_data_by_day(stock_number, begin_date, end_date)
        if len(self.text) == 0:
            print("error not find date by stock_number = ", stock_number)



        # print("check stock =", self.text[1][1])
        # parserMoney.analysis_stock_data(self.text)
    def get_and_print(self):
        text = py_util.get_stock_text_by_url(self.stock_number)
        # print(text)
        return parserMoney.parser_stock_and_print(self.stock_number, text)

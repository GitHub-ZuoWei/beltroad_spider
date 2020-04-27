import os

import xlrd
import pymysql
import requests
from bs4 import BeautifulSoup

db = pymysql.connect("192.168.10.222", "root", "123456", "db_belt_road")
cursor = db.cursor()
cursor.execute('select series_codes from br_config')
series_codes = cursor.fetchall()
url_list = []
for item in eval(series_codes[0][0]):
    execute_num = cursor.execute("select * from br_worldbank where series_code = '" + item + "'")
    print(item, execute_num)
    if execute_num == 0:
        url_list.append(item)


def get_all_url():


    excel = xlrd.open_workbook('resource/API_SP.POP.3034.FE.5Y_DS2_zh_excel_v2_985790.xls')
    sheet = excel.sheet_by_name('Data')
    rows = sheet.nrows
    cols = sheet.ncols
    data_list = []
    for i in range(4, rows):
        series_name = pymysql.escape_string(sheet.cell(i, 2).value)
        series_code = sheet.cell(i, 3).value
        country_name = pymysql.escape_string(sheet.cell(i, 0).value)
        country_code = sheet.cell(i, 1).value
        for j in range(4, cols):
            value_str = sheet.cell(i, j).value
            year_str = sheet.cell(3, j).value
            data_list.append(tuple([series_name, series_code, country_name, country_code, value_str, year_str]))
    cursor.executemany(
        "insert into br_worldbank (series_name,series_code,country_name,country_code,value,year) values (%s,%s,%s,%s,%s,%s)",
        data_list)
    db.commit()
    os.remove('resource/API_SP.POP.3034.FE.5Y_DS2_zh_excel_v2_985790.xls')
    db.close()


if __name__ == '__main__':
    get_all_url()
    pass

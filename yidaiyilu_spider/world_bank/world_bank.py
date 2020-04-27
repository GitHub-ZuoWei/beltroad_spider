import os

import pymysql
import requests
import xlrd
from bs4 import BeautifulSoup

db = pymysql.connect("192.168.10.222", "root", "123456", "db_belt_road")
cursor = db.cursor()


def get_all_url():
    home_url = 'https://data.worldbank.org.cn/indicator?tab=all'
    response = requests.get(home_url)
    soup = BeautifulSoup(response.text, 'lxml')
    all_item = soup.find_all('section', attrs={'class': 'nav-item'})
    all_url = []
    for item in all_item:
        all_li = item.find_all('li')
        for li in all_li:
            href = li.find('a').get('href')
            series_code = href.split('?')[0].split('/')[-1]
            url = 'http://api.worldbank.org/v2/zh/indicator/' + series_code + '?downloadformat=excel'
            if url not in all_url:
                all_url.append(url)

    print('total number : ', len(all_url))
    for url in all_url:
        real_url = url.replace('\n', '')
        series_code = real_url.split('?')[0].split('/')[-1]
        retry_number = 0
        while retry_number < 3:
            try:
                each_response = requests.get(real_url, timeout=20)
                retry_number = 666
            except:
                retry_number += 1
                if retry_number == 3:
                    with open('resource/error_info.txt', 'wb') as f:
                        f.write(real_url)
                    break
                continue

            if each_response.status_code == 200:
                with open('resource/' + series_code + '.xls', 'wb') as f:
                    f.write(each_response.content)
                excel = xlrd.open_workbook('resource/' + series_code + '.xls')
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
                        data_list.append(
                            tuple([series_name, series_code, country_name, country_code, value_str, year_str]))
                cursor.executemany(
                    "insert into br_worldbank (series_name,series_code,country_name,country_code,value,year) values (%s,%s,%s,%s,%s,%s)",
                    data_list)
                db.commit()
                os.remove('resource/' + series_code + '.xls')
            print(real_url)

    db.close()


if __name__ == '__main__':
    get_all_url()

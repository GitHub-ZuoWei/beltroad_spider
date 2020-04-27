import re
import sys
import time

sys.path.append(r'/export/python/yq_data_spider/')

import pymysql
import requests
from lxml import etree
from utils.fanyi import fanyi

from selenium import webdriver
# browser = webdriver.Firefox()

from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

"""
      ┏┛ ┻━━━━━┛ ┻┓
      ┃　　　　　　 ┃
      ┃　　　━　　　┃
      ┃　┳┛　  ┗┳　┃
      ┃　　　　　　 ┃
      ┃　　　┻　　　┃
      ┃　　　　　　 ┃
      ┗━┓　　　┏━━━┛
        ┃　　　┃   神兽保佑
        ┃　　　┃   代码无BUG！
        ┃　　　┗━━━━━━━━━┓
        ┃　　　　　　　    ┣┓
        ┃　　　　         ┏┛
        ┗━┓ ┓ ┏━━━┳ ┓ ┏━┛
          ┃ ┫ ┫   ┃ ┫ ┫
          ┗━┻━┛   ┗━┻━┛
"""

option = ChromeOptions()
# # linux
# option.add_argument('--disable-extensions')
# option.add_argument('--headless')
# option.add_argument('--disable-gpu')
# option.add_argument('--no-sandbox')
#
# option.add_experimental_option('excludeSwitches', ['enable-automation'])

chrome_driver = r"I:\Softwares\Python\Anaconda3\Lib\site-packages\selenium\webdriver\chrome\chromedriver.exe"

# linux
# chrome_driver = '/usr/bin/chromedriver'

browser = webdriver.Chrome(options=option, executable_path=chrome_driver)
# browser.set_page_load_timeout(20)

conn = pymysql.connect("192.168.10.222", "root", "123456", "db_belt_road")
cursor = conn.cursor()


def world_bank_menu():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
    response = requests.get('https://data.worldbank.org.cn/indicator?tab=all', headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        etree_html = etree.HTML(response.text)
        html_news_href = etree_html.xpath('//*[@id="main"]/div[2]/*')
        all_data_list = []
        all_href_list = []
        for html_href in html_news_href[1:]:
            # 分类
            classify = html_href.xpath('h3/a/text()')
            ul_xpath = html_href.xpath('ul[2]/*')
            if not ul_xpath:
                ul_xpath = html_href.xpath('ul[1]/*')
            for ul in ul_xpath:
                # 标识码
                series_code = ul.xpath('a/@href')[0].split('/')[2].split('?')[0]
                # 维度名称
                series_name = ul.xpath('a/text()')
                execute_num = cursor.execute(
                    "select * from br_worldbank_menu where series_code = '" + series_code + "'")
                if execute_num == 0:
                    all_data_list.append(tuple([classify, series_code, series_name]))
                    all_href_list.append('https://data.worldbank.org.cn' + ul.xpath('a/@href')[0])

        cursor.executemany(
            "insert into br_worldbank_menu (classify,series_code,series_name) values (%s,%s,%s)", all_data_list)
        conn.commit()
        # conn.close()
        yidaiyilu_country(all_href_list)


def yidaiyilu_country(all_href_list):
    # 最大5页
    browser.get('https://data.worldbank.org.cn/indicator/AG.LND.TOTL.RU.K2?view=chart')
    for href in all_href_list:
        browser.get(href)
        retry = 0
        while retry < 6:
            try:
                WebDriverWait(browser, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@class="button secondary openinnew"]')))
            except:
                browser.get(href)
                retry += 1
                continue
            retry = 666

        # 全部点击后，取所有页面内容 解析
        browser.find_element_by_xpath("//*[@class='button secondary openinnew']").click()
        source = browser.page_source.encode("utf-8", "ignore").decode("utf-8")
        etree_html = etree.HTML(source)
        description = ''.join(etree_html.xpath("//*[@class='share  details']/div/div/div/div/p/text()"))
        if not is_chinese(description):
            description = fanyi(description)
        series_code = href.split('/')[-1].split('?')[0]

        print(href)
        print(href.split('/')[-1].split('?')[0])
        print(description)

        cursor.execute(
            "UPDATE br_worldbank_menu SET description = '" + description + "' WHERE series_code='" + series_code + "'")
        conn.commit()
    conn.close()
    browser.quit()  # 退出浏览器


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar[:2].replace(' ', '').encode('UTF-8').isalpha():
        return False
    else:
        return True


if __name__ == '__main__':
    # pass
    world_bank_menu()

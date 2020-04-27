# -*- coding:utf-8 -*-
# Author      : ZuoWei<zuowei@yuchen.net.cn>
# Datetime    : 2020-02-17 15:06
# User        : ZuoWei
# Product     : PyCharm
# Project     : SpiderSelenium
# File        : demo
# Description : 文件说明
import os
import re
import sys

import requests

sys.path.append(r'/export/python/yq_data_spider')

import pymysql
from lxml import etree
from selenium import webdriver
# browser = webdriver.Firefox()

import win32api
import win32con
import win32clipboard
from ctypes import *
import time

from urllib.request import urlretrieve
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

wait = WebDriverWait(browser, 20)

conn = pymysql.connect("192.168.10.222", "root", "123456", "db_belt_road")
cursor = conn.cursor()


def yidaiyilu_country():
    # 最大5页
    browser.get('https://www.lieguozhi.com/skwx_lgz/countrylist?SiteID=45#country_datalist')
    browser.get('https://www.lieguozhi.com/skwx_lgz/countrylist?SiteID=45#country_datalist')
    # 全部点击后，取所有页面内容 解析
    try:
        source = browser.page_source.encode("utf-8", "ignore").decode("utf-8")
    except:
        browser.close()
    etree_html = etree.HTML(source)
    # 文章标题
    all_country_href = etree_html.xpath("//*[@id='countryList']/a/@href")
    for country_href in all_country_href:
        country_details = requests.get(country_href)
        if country_details.status_code == 200:
            country_details.encoding = 'utf-8'
            country_html = etree.HTML(country_details.text)
            # 国家名称
            country_name = ''.join(country_html.xpath("//*[@class='country_profile']/h1/text()")).strip()
            # 国旗
            national_flag = ''.join(country_html.xpath("//*[@class='country_logo fl']/a[1]/img/@src"))
            # 国徽
            national_emblem = ''.join(country_html.xpath("//*[@class='country_logo fl']/a[2]/img/@src"))

            if (national_flag and national_emblem).startswith('http'):
                # 下载图片
                national_flag_response = requests.get(national_flag)
                if national_flag_response.status_code == 200:
                    open('./resource/' + ''.join(national_flag.split('/')[-4:]), 'wb').write(
                        national_flag_response.content)
                national_emblem_response = requests.get(national_emblem)
                if national_emblem_response.status_code == 200:
                    open('./resource/' + ''.join(national_emblem.split('/')[-4:]), 'wb').write(
                        national_emblem_response.content)

                cursor.execute("UPDATE br_country_copy1 SET national_flag = '" + ''.join(
                    national_flag.split('/')[-4:]) + "',national_emblem='" + ''.join(
                    national_emblem.split('/')[-4:]) + "' WHERE country_name='" + country_name + "'")
                conn.commit()

            else:
                print(country_href)

            print(country_name)

    conn.close()
    browser.close()
    browser.quit()  # 退出浏览器


if __name__ == '__main__':
    yidaiyilu_country()

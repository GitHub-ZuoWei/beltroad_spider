# -*- coding:utf-8 -*-
# Author      : ZuoWei<zuowei@yuchen.net.cn>
# Datetime    : 2020-02-17 15:06
# User        : ZuoWei
# Product     : PyCharm
# Project     : SpiderSelenium
# File        : demo
# Description : 文件说明
import os
import sys

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
    browser.get('https://www.yidaiyilu.gov.cn/info/iList.jsp?cat_id=10038')
    # browser.get('https://www.yidaiyilu.gov.cn/info/iList.jsp?cat_id=10038')
    time.sleep(5)
    now_window = browser.window_handles[0]
    # 全部点击后，取所有页面内容 解析
    all_Handles = browser.window_handles
    print(len(all_Handles))
    try:
        source = browser.page_source.encode("utf-8", "ignore").decode("utf-8")
    except:
        browser.close()
    etree_html = etree.HTML(source)

    # 文章标题
    ul_xpath = etree_html.xpath("//div[@class='slideTxtBox13']//div[@class='bd']/*")
    all_image_href = []
    for ul in ul_xpath[:2]:
        image_href = ul.xpath('li/img/@src')
        country_name = ul.xpath('li/div/a/h3/text()')
        country_overview = ul.xpath('li/div/a/p/text()')
        for name, overview, href in zip(country_name, country_overview, image_href):
            cursor.execute("UPDATE br_country_copy1 SET survey = '" + overview + "',scenery='" + href.split('/')[
                -1] + "' WHERE country_name='" + name + "'")
            conn.commit()
        for image in image_href:
            all_image_href.append('https://www.yidaiyilu.gov.cn' + image)

    for iamge_url in all_image_href:
        browser.get(iamge_url)
        browser.maximize_window()
        time.sleep(2)
        # 获取页面title作为文件名
        # 设置路径为：当前项目的绝对路径+文件名
        path = (os.path.dirname(os.path.realpath(__file__)) + "\\resource\\" + iamge_url.split('/')[-1])

        # 将路径复制到剪切板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(path)
        win32clipboard.CloseClipboard()

        # 按下ctrl+s
        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x53, 0, 0, 0)
        win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)

        # 鼠标定位输入框并点击
        windll.user32.SetCursorPos(700, 510)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(1)

        # 按下ctrl+a
        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x41, 0, 0, 0)
        win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)

        # 按下ctrl+v
        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x56, 0, 0, 0)
        win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)

        # 按下回车
        win32api.keybd_event(0x0D, 0, 0, 0)
        win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)

    conn.close()
    browser.close()
    browser.quit()  # 退出浏览器


if __name__ == '__main__':
    yidaiyilu_country()

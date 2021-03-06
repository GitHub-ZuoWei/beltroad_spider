# -*- coding:utf-8 -*-
# Author      : ZuoWei<zuowei@yuchen.net.cn>
# Datetime    : 2020-02-17 15:06
# User        : ZuoWei
# Product     : PyCharm
# Project     : SpiderSelenium
# File        : demo
# Description : 一带一路 政策法规
import datetime
import json
import os
import re
import sys
import zipfile
import requests

from utils.ftp_upload import FtpConnect, FtpUpload

sys.path.append(r'/export/python/yq_data_spider')

import pymysql
from lxml import etree
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

# 跳过webdriver检测
option.add_experimental_option('excludeSwitches', ['enable-automation'])
# 不加载图片,加快访问速度
option.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

chrome_driver = r"I:\Softwares\Python\Anaconda3\Lib\site-packages\selenium\webdriver\chrome\chromedriver.exe"

# linux
# chrome_driver = '/usr/bin/chromedriver'

browser = webdriver.Chrome(options=option, executable_path=chrome_driver)
# browser.set_page_load_timeout(20)

wait = WebDriverWait(browser, 20)

conn = pymysql.connect("192.168.10.222", "root", "123456", "db_belt_road")
cursor = conn.cursor()


def bilateral_documents():
    # 最大18页
    for num in range(0, 2):
        browser.get(
            'https://www.yidaiyilu.gov.cn/info/iList.jsp?site_id=CMSydylgw&cat_id=10009&cur_page=' + str(num))
        now_window = browser.window_handles[0]
        # 每一页有10项
        for a in range(1, 31):
            try:
                page = browser.find_element_by_xpath("//*[@class='commonList_dot']/li[%d]/a" % a)
                print('page', num, page)
                page.click()
            except:
                pass

        # 全部点击后，取所有页面内容 解析
        all_Handles = browser.window_handles
        print(len(all_Handles))
        save_data_tuple = []
        for pay_window in all_Handles:
            if pay_window != now_window:
                browser.switch_to.window(pay_window)
                try:
                    source = browser.page_source.encode("utf-8", "ignore").decode("utf-8")
                except:
                    browser.close()
                    continue
                etree_html = etree.HTML(source)
                # 文章标题
                title = browser.find_element_by_xpath("//*[@class='main_content_title']").text
                try:
                    publish_date = browser.find_element_by_xpath(
                        "//*[@class='szty']//*[@class='main_content_date'][1]").text.replace('发布时间：', '')
                except:
                    publish_date = browser.find_element_by_xpath("//*[@class='main_content_date szty1 ']").text.replace(
                        '发布时间：', '')
                try:
                    source = browser.find_element_by_xpath(
                        "//*[@class='szty']//*[@class='main_content_date'][2]").text.replace('来源：', '')
                except:
                    source = browser.find_element_by_xpath("//*[@class='main_content_date szty2']").text.replace('来源：',
                                                                                                                 '')

                content = etree_html.xpath("//*[@class='info_content']/*")
                if not content or len(content) < 2:
                    content = etree_html.xpath("//*[@class='info_content']/div/*")
                    if not content or len(content) < 2:
                        content = etree_html.xpath("//*[@class='info_content']/div/div/*")
                        if not content or len(content) < 2:
                            content = etree_html.xpath("//*[@class='info_content']/div/div/div/*")
                            if not content or len(content) < 2:
                                content = etree_html.xpath("//*[@class='info_content']/div/div/div/div/*")
                # 不带样式
                text = etree_html.xpath("string(//*[@class='info_content'])")
                # 带样式
                full_content = ''
                if len(content) == 2:
                    for index, item in enumerate(content[0]):
                        if '<Element table' not in str(item):
                            if index + 1 == 1:
                                content_title = '<strong>' + (''.join(item.xpath("string(.)"))).strip() + '</strong>'
                            else:
                                content_title = '<span>' + (''.join(item.xpath("string(.)"))).strip() + '</span>'
                            if (''.join(item.xpath("string(.)"))).strip():
                                full_content += content_title
                    content_first = content[1].xpath("./*")
                    for item in content_first if len(content_first) > 1 else content[1].xpath("./div/*"):
                        if '<Element table' not in str(item):
                            p_content = '<p>' + (''.join(item.xpath("text()"))).strip() + '</p>'
                            full_content += p_content
                else:
                    for item in content:
                        if '<Element table' not in str(item):
                            if item.xpath("strong"):
                                if item.xpath("strong/text()"):
                                    strong_content = '<strong>' + (
                                        ''.join(item.xpath("strong/text()"))).strip() + '</strong>'
                                    if ''.join(item.xpath("strong/text()")).strip():
                                        full_content += strong_content
                            elif item.xpath("span"):
                                if item.xpath("span/text()"):
                                    span_content = '<strong>' + (
                                        ''.join(item.xpath("span/text()"))).strip() + '</strong>'
                                    if not span_content:
                                        span_content = '<span>' + (
                                            ''.join(item.xpath("span/span/text()"))).strip() + '</span>'
                                    if ''.join(item.xpath("span/text()")).strip():
                                        full_content += span_content
                            else:
                                if (''.join(item.xpath("text()"))).strip():
                                    p_content = '<p>' + (''.join(item.xpath("text()"))).strip() + '</p>'
                                    full_content += p_content
                print(browser.current_url)

                # 增量
                execute_num = cursor.execute("select * from br_news_info where url = '" + browser.current_url + "'")
                if execute_num == 0:
                    save_data_tuple.append(
                        tuple([title, full_content, text, publish_date, source, '政策法规', browser.current_url, '1', 'CHN',
                               '1']))
                    file_sql = "insert into br_news_info (title,content,text,news_date,source,type,url,status,country_code,language) values %s ;" % (
                        str(tuple(
                            [title, full_content.replace(u'\u3000', u' '), text, publish_date, source, '政策法规',
                             browser.current_url, '1', 'CHN', '1'])))

                    open("zip_policies/data.sql", "a+", encoding="utf-8").write(file_sql + '\n')

                browser.close()
        cursor.executemany(
            "insert into br_news_info (title,content,text,news_date,source,type,url,status,country_code,language) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            save_data_tuple)
        conn.commit()
        browser.switch_to.window(now_window)
    conn.close()
    browser.quit()  # 退出浏览器

    file_path = "zip_policies/data.sql"
    # 压缩文件
    if os.path.exists(file_path):
        zip_path = "zip_policies_package/" + str(datetime.datetime.now())[:10] + '.zip'
        zp = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
        zp.write(file_path, 'data.sql')  # 如果不添加arcname参数，则压缩后，会出现一堆路径上的目录文件夹
        zp.close()
        # 将压缩的文件上传FTP 服务器
        connect = FtpConnect('223.223.177.101', 'internet-data', 'yqjc47ftp*')
        # connect = FtpConnect('192.168.10.216', 'ftptest10', '987654321')
        # 清空FTP服务器的所有文件
        # FtpDeleteAll(connect)
        FtpUpload(connect, '/belt_road/' + str(datetime.datetime.now())[:10] + '.zip', zip_path)
        # 判断文件是否存在
        if (os.path.exists(file_path)):
            os.remove(file_path)
            print("File deleted successfully")

        # 调用JAVA 接口增量
        java_response = requests.get('http://192.168.10.197:8091/beltRoad/handle/news')
        if java_response.status_code == 200:
            print("Java request success")
            java_response.close()


if __name__ == '__main__':
    bilateral_documents()

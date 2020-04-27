# -*- coding:utf-8 -*-
# Author      : ZuoWei<zuowei@yuchen.net.cn>
# Datetime    : 2020-02-17 15:06
# User        : ZuoWei
# Product     : PyCharm
# Project     : SpiderSelenium
# File        : demo
# Description : 文件说明
import re
import sys

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
option.add_argument('--disable-extensions')
option.add_argument('--headless')
option.add_argument('--disable-gpu')
option.add_argument('--no-sandbox')

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


def yidaiyilu_country():
    # 最大5页
    for num in range(0, 6):
        browser.get(
            'https://www.yidaiyilu.gov.cn/info/iList.jsp?cat_id=10037&cur_page=' + str(num))
        now_window = browser.window_handles[0]
        # 每一页有10项
        for a in range(1, 31):
            try:
                page = browser.find_element_by_xpath("/html/body/div[8]/div/div[2]/ul/li[%d]/a" % a)
                print('page', num, page)
                page.click()
            except:
                pass

        # 全部点击后，取所有页面内容 解析
        all_Handles = browser.window_handles
        print(len(all_Handles))
        for pay_window in all_Handles:
            if pay_window != now_window:
                browser.switch_to.window(pay_window)
                if browser.current_url == 'https://www.yidaiyilu.gov.cn/gbjg/gbgk/77073.htm':
                    browser.close()
                    continue
                try:
                    source = browser.page_source.encode("utf-8", "ignore").decode("utf-8")
                except:
                    browser.close()
                    continue
                etree_html = etree.HTML(source)
                save_data_tuple = []
                # 文章标题
                title = browser.find_element_by_xpath("//*[@id='zoom']/h1").text
                country_num = cursor.execute(
                    'select country_code3 from br_country where country_name = ' + "'" + title + "'")
                country_id = cursor.fetchall()
                if country_num > 0:
                    country_id = country_id[0][0]
                else:
                    country_id = 0

                content = etree_html.xpath("//*[@class='info_content']/*")
                try:
                    other_content = content[2].xpath("//*[@id='content']/*")
                except:
                    try:
                        other_content = content[1].xpath("//*[@id='content']/*")
                    except:
                        try:
                            other_content = content[0].xpath("//*[@id='content']/*")
                        except:
                            browser.close()
                            print('Gun')
                            continue
                try:
                    other_other_content = content[3].xpath("//*[@id='content']/*")
                except:
                    other_other_content = ''

                # 最近更新时间
                re_content = etree_html.xpath("string(//*[@class='info_content'])")
                print(browser.current_url)
                update_time = re.findall('更新时间.*?([0-9]{4}年[0-9]{1,2}月)', re_content)
                # format_update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(update_time, "%Y年%m月%d日"))
                if not update_time:
                    print('-------------')
                else:
                    update_time = update_time[0]
                print(update_time)

                full_content = ''
                last_key = ''

                # 带有id 的内容
                if other_content or other_other_content:
                    for other_item in other_content:
                        # 排除带有table 内容的标签
                        if 'table' not in str(other_item):
                            every_p_content = other_item.xpath("string(.)").strip()
                            re_key = re.findall('【(.*?)】', every_p_content)
                            # 没有数据
                            if re_key:
                                if full_content:
                                    save_data_tuple.append(tuple([country_id, update_time, last_key[0].replace(' ', ''),
                                                                  re.sub('【(.*?)】', '', full_content)]))
                                    full_content = ''
                                full_content += ('<p>' + every_p_content + '</p>')
                                last_key = re_key
                            elif not re_key and full_content:
                                full_content += ('<p>' + every_p_content + '</p>')

                # 不带有id 的内容
                for item_xpath in content[3:]:
                    # 排除带有table 内容的标签
                    if 'table' not in str(item_xpath):
                        every_p_content = item_xpath.xpath("string(.)").strip()
                        re_key = re.findall('【(.*?)】', every_p_content)
                        # 没有数据
                        if re_key:
                            if full_content:
                                save_data_tuple.append(tuple([country_id, update_time, last_key[0].replace(' ', ''),
                                                              re.sub('【(.*?)】', '', full_content)]))
                                full_content = ''
                            full_content += ('<p>' + every_p_content + '</p>')
                            last_key = re_key
                        elif not re_key and full_content:
                            full_content += ('<p>' + every_p_content + '</p>')
                    else:
                        if re_key:
                            save_data_tuple.append(tuple([country_id, update_time, last_key[0].replace(' ', ''),
                                                          re.sub('【(.*?)】', '', full_content)]))

                cursor.executemany(
                    "insert into br_country_survey (country_code,last_change,series_name,series_value) values (%s,%s,%s,%s)",
                    save_data_tuple)
                conn.commit()

                browser.close()
        browser.switch_to.window(now_window)
    conn.close()
    browser.quit()  # 退出浏览器


if __name__ == '__main__':
    yidaiyilu_country()

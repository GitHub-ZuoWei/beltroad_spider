import sys
import time

sys.path.append(r'/export/python/yq_data_spider/')

import pymysql
import requests
from lxml import etree
from utils.fanyi import fanyi

# https://www.cia.gov/library/publications/the-world-factbook/fields/331.html
# 获取新闻网页所有链接
conn = pymysql.connect("192.168.10.222", "root", "123456", "db_belt_road")
cursor = conn.cursor()


def world_factbook():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
    # for num in range(330, 335):
    for num in range(330, 335):
        news_details = requests.get(
            'https://www.cia.gov/library/publications/the-world-factbook/fields/' + str(num) + '.html',
            headers=headers)
        if news_details.status_code == 200:
            news_details.encoding = 'utf-8'
            etree_html = etree.HTML(news_details.text)
            tbody_xpath = etree_html.xpath('//tbody/*')
            # 判断是否有多条鸭
            check_status = etree_html.xpath("//*[@id='field-military-expenditures']/div[1]/span[1]")
            # 类别
            title = ''.join(etree_html.xpath("//*[@id='fieldListing']/thead/tr/th[2]/text()"))
            title_translate = fanyi(title)
            for tr_xpath in tbody_xpath:
                tr_country = ''.join(tr_xpath.xpath("td/a/text()"))
                tr_content = ''
                content_translate = ''
                if check_status:
                    for span_xpath in tr_xpath.xpath("td/div/*"):
                        content_en = span_xpath.xpath("string(.)").strip().replace('  ', '').replace('\n', '')
                        tr_content += '<p>' + content_en + '</p>'
                        content_translate += '<p>' + fanyi(content_en) + '</p>'
                else:
                    content = (''.join(tr_xpath.xpath("string(td[2])"))).strip().replace('  ', '').replace('\n', '')
                    tr_content = '<p>' + content + '</p>'
                    content_translate = '<p>' + fanyi(content) + '</p>'

                number = cursor.execute(
                    "SELECT country_code3 FROM `br_country` WHERE country ='" + pymysql.escape_string(tr_country) + "'")
                if number > 0:
                    country_code = cursor.fetchall()[0][0]
                else:
                    print(tr_country)
                    country_code = None

                cursor.execute(
                    "insert into br_world_factbook (country_code,country_name,title,title_translation,content,content_translation) values (%s,%s,%s,%s,%s,%s)",
                    (
                        country_code, tr_country, pymysql.escape_string(title), pymysql.escape_string(title_translate),
                        pymysql.escape_string(tr_content), pymysql.escape_string(content_translate)))
                conn.commit()

    conn.close()


if __name__ == '__main__':
    world_factbook()

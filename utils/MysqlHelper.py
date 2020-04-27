# -*- coding:utf-8 -*-
# Author      : suwei<suwei@yuchen.net.cn>
# Datetime    : 2019-07-18 13:40
# User        : suwei
# Product     : PyCharm
# Project     : Demo_BI
# File        : MysqlHelper.py
# Description : 数据库连接工具类
import pymysql

import conf


class MySqlHelper:

    def __init__(self, sql_info=conf.sql_info):
        # 连接数据库
        self.connect_database(sql_info)

    def connect_database(self, sql_info=conf.sql_info):
        try:
            self.conn = pymysql.connect(sql_info['ip'], sql_info['user'],
                                        sql_info['pwd'], sql_info['database'])
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print('database connection failed ：', e)
            return False

    def execute_sql(self, sql):
        try:
            self.conn.ping(reconnect=True)
            self.cursor.execute(sql)
            self.conn.commit()  # Temp
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            print('SQL execute failed：', e, '\n\t\t', sql)

    def execute_many_sql(self, sql, l):
        try:
            self.conn.ping(reconnect=True)
            self.cursor.executemany(sql, l)
            self.conn.commit()
            return True
        except Exception as e:
            print('SQL execute failed：', e, '\n\t\t', sql)

    def close(self):
        if self.conn:
            # self.conn.commit()
            self.cursor.close()
            self.conn.close()

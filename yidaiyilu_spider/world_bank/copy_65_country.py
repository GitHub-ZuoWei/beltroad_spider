import pymysql

country_cn_name_list = ['蒙古国', '新加坡', '马来西亚', '印度尼西亚', '缅甸', '泰国', '老挝', '柬埔寨', '越南', '文莱', '菲律宾', '伊朗', '伊拉克', '土耳其',
                        '叙利亚', '约旦', '黎巴嫩', '以色列', '巴勒斯坦', '沙特阿拉伯', '也门', '阿曼', '阿联酋', '卡塔尔', '科威特', '巴林', '希腊', '塞浦路斯',
                        '埃及', '印度', '巴基斯坦', '孟加拉国', '阿富汗', '斯里兰卡', '马尔代夫', '尼泊尔', '不丹', '哈萨克斯坦', '乌兹别克斯坦', '土库曼斯坦',
                        '塔吉克斯坦', '吉尔吉斯斯坦', '俄罗斯', '乌克兰', '白俄罗斯', '格鲁吉亚', '阿塞拜疆', '亚美尼亚', '摩尔多瓦', '波兰', '立陶宛', '爱沙尼亚',
                        '拉脱维亚', '捷克', '斯洛伐克', '匈牙利', '斯洛文尼亚', '克罗地亚', '波黑', '黑山', '塞尔维亚', '阿尔巴尼亚', '罗马尼亚', '保加利亚',
                        '马其顿']

db_rs = pymysql.connect("192.168.10.222", "root", "123456", "rs")
cursor_rs = db_rs.cursor()

db_br = pymysql.connect("192.168.10.222", "root", "123456", "belt_road")
cursor_br = db_br.cursor()

for country_cn_name in country_cn_name_list:
    sql_select_country_en_name = "select countryCode from  hs_country_new where internetName = '%s'" % country_cn_name
    cursor_rs.execute(sql_select_country_en_name)
    country_code = cursor_rs.fetchall()[0][0]
    sql_select_world_bank = "select seriesname,seriescode,countryname,countrycode,value,year from br_worldbank_all where countrycode ='%s'" % country_code
    cursor_br.execute(sql_select_world_bank)
    world_bank_list = cursor_br.fetchall()
    for world_bank in world_bank_list:
        seriesname = pymysql.escape_string(world_bank[0])
        seriescode = world_bank[1]
        countryname = world_bank[2]
        countrycode = world_bank[3]
        value = world_bank[4]
        year = world_bank[5]
        sql_insert_into_br = "insert into br_worldbank_65 (seriesname,seriescode,countryname,countrycode,value,year) values ('%s','%s','%s','%s','%s','%s')"%(seriesname,seriescode,countryname,countrycode,value,year)
        print(sql_insert_into_br)
        cursor_br.execute(sql_insert_into_br)
db_br.commit()
db_br.close()
db_rs.close()

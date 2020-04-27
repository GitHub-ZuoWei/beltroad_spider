import requests
import json, hashlib, time


def fanyi(keyword):
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&sessionFrom=null'

    # 定义请求参数
    salt = str(int(time.time() * 1000))

    client = 'fanyideskweb'
    a = "rY0D^0'nM0}g5Mm1z%1G4"
    md5 = hashlib.md5()
    digStr = client + keyword + salt + a
    md5.update(digStr.encode('utf-8'))
    sign = md5.hexdigest()

    # 构建请求对象
    data = {
        'i': keyword,
        'from': 'AUTO',
        'to': 'AUTO',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': salt,
        'sign': sign,
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTIME',
        'typoResult': 'true'
    }
    # 发送请求，抓取信息
    res = requests.post(url, data=data)
    # 解析结果并输出
    str_json = res.content.decode('utf-8')  # 获取响应的json字串
    all_result = ''
    try:
        myjson = json.loads(str_json, strict=False)  # 把json转字典
        info = myjson['translateResult']
        for items in info:
            if items:
                for item in items:
                    result = item['tgt']
                    if result:
                        all_result += result
        return all_result
    except:
        return ''


# print(fanyi('青铜峡旅游区'))

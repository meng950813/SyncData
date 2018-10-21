import pytesseract

from PIL import Image
import requests
import io
import os
import time
import datetime
import xml.etree.ElementTree as ET
import csv

import urllib3
urllib3.disable_warnings()

import sys
sys.path.append("..")

from helper import Codeconfig as info
from helper import DBhelper as DB

default_headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Host": "isisn.nsfc.gov.cn",
    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0',
    'Referer': 'https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list',
}


CONTENT = []
YEAR = 2018
TOTAL = 1


def WriteFile(context,dirpath):
    context.insert(0, ["项目批准号", "申请代码", "项目名称","项目负责人", "依托单位", "批准金额", "项目起止年月","项目批准时间","项目类型"])
    # dirpath = './data/优秀青年科学基金项目'
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    f = open(dirpath + "/_"+str(YEAR)+".csv", 'w', encoding='utf8')
    f.write('\ufeff')
    file = csv.writer(f, dialect='excel')
    for ls in context:
        # print( type(ls))
        file.writerow(ls)
    f.close()


def parseXML(xml,year,grantCode):
    global CONTENT, TOTAL

    doc = ET.fromstringlist(xml)
    rows = doc.findall('row')

    if TOTAL == 1:
        TOTAL = int(doc.find('total').text)
        print("set TOTAL = ", TOTAL)

    if 0 == TOTAL:
        return False

    for row in rows:
        desc = []
        for cell in row.findall('cell'):
            desc.append(cell.text)
        desc.append(year)
        desc.append(grantCode)

        CONTENT.append(desc)
    print("success Write")


def once(page, grantCode, year):
    s = requests.Session()

    def getVaildata():
        time = str(datetime.datetime.now().timestamp())
        url = "https://isisn.nsfc.gov.cn/egrantindex/validatecode.jpg?date="+time
        # print(url)

        try:
            res = s.get(url, headers=default_headers.copy(), verify=False)
        except Exception as e:
            # raise e
            return None
        # print('req done')

        if res.status_code == 200:
            img = Image.open(io.BytesIO(res.content))
            # print('open done')
            # 转化到灰度图
            imgry = img.convert('L')

            # imgry.show()
            # tessdata_dir_config = ""
            code = pytesseract.image_to_string(imgry)

            return code
        else:
            return None

    def postCode(code):
        url = 'https://isisn.nsfc.gov.cn/egrantindex/funcindex/validate-checkcode'
        headers = default_headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["X-Requested-With"] = "XMLHttpRequest"
        body = 'checkCode=%s' % (code)

        try:
            res = s.post(url, headers=headers, data=body, verify=False)

        except Exception as e:
            return False

        if res.status_code == 200 and res.content.decode('utf8') != 'error':
            return True
        else:
            return False

    def getlist(code, grantCode, page, year):
        url = 'https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list?flag=grid&checkcode=%s' % (code)

        headers = default_headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["X-Requested-With"] = "XMLHttpRequest"
        searchString = 'resultDate^:prjNo%3A%2Cctitle%3A%2CpsnName%3A%2CorgName%3A%2CsubjectCode%3A%2Cf_subjectCode_hideId%3A%2CsubjectCode_hideName%3A%2CkeyWords%3A%2Ccheckcode%3A' + \
            code + '%2CgrantCode%3A'+grantCode+'%2CsubGrantCode%3A%2ChelpGrantCode%3A%2Cyear%3A' + \
            year+'[tear]sort_name1^:psnName[tear]sort_name2^:prjNo[tear]sort_order^:desc'
        body = '_search=false&nd=%d000&page=%d&rows=%d&searchString=%s&sidx=&sord=desc' % (
            datetime.datetime.now().timestamp(),
            page,
            10000,
            searchString,
        )

        try:
            res = s.post(url, headers=headers, data=body, verify=False)
            # pass
        except Exception as e:
            return None

        if res.status_code == 200:
            return res.content.decode('utf8')
        else:
            print('ERR', res.content.decode('utf8'))
            return None

    code = getVaildata().replace(" ", "")

    print('code:', code)

    while code is None or len(code) != 4:
        code = getVaildata().strip()
        # print('code:', code)

    f = postCode(code)
    # print('post code:', f)
    if f:
        ls = parseXML(getlist(code, grantCode, page, year),year,grantCode)
        if ls == False:
            return False

        return True
    else:
        return False

def main():
    for item in info.config:
        # 考虑到往年数据不会变化，因此只需爬今年的数据
        YEAR = datetime.datetime.now().year

        # while YEAR >= 1997: #
        #
        x = 1
        while x <= TOTAL:
            success = once(x, item['grantCode'], str(YEAR))
            if success:
                x += 1
                # 休眠10s
                print("sleep 10s")
                time.sleep(10)

            print(CONTENT)

            if 0 != TOTAL:
                # WriteFile(CONTENT,"../data/"+item['name'])
                DB.save_to_db(CONTENT)
                # exit()
                # pass



            CONTENT = []
            YEAR -= 1
            TOTAL = 1

if __name__ == '__main__':
    main()

    # trun_to_json.getDataFromDir(info)

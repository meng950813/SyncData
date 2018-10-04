#-*- coding:utf-8 -*-

from scrapy import cmdline

import datetime

# cmdline.execute("scrapy crawl NSFCSpider".split())

time = datetime.datetime.now()

str_time = str(datetime.datetime.strftime(time, "%a %b %d %Y %X")) + " GMT+0800 (中国标准时间)"
print(str_time)
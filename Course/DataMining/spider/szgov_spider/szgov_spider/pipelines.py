# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# 去重
from scrapy.exceptions import DropItem

# import pymysql
import MySQL_config as mysql_config

class SzgovSpiderPipeline(object):

    def __init__(self):
        # self.config = mysql_config
        self.conn = None
        self.cursor = None
        #用于去重
        self.ids_seen = set()
        
    # def  open_spider(self,spider):
    #     try:
    #         self.conn = mysql.connector.connect(**config)
    #     except mysql.connector.Error as e:
    #         print('connect fails!{}'.format(e))
    #         self.cursor = self.conn.cursor()

    # def close_spider(self,spider):
    #     self.cursor.close()
    #     self.conn.close()

    def process_item(self, item, spider):

        # print("this is in item line : ",item['file_name'].encode('utf-8'))

        if item['file_name'] in self.ids_seen:
            print(" file_name repeat! ")
            pass
        else:
            # print("ready to write : ",item['file_name'].encode('utf-8'))
            self.ids_seen.add(item['file_name'])
            with open('./download/'+item['file_name']+".txt","w") as f:
                f.write(item['content'].encode('utf-8'))
        return item

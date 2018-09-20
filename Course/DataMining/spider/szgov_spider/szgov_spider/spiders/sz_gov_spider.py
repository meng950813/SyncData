# -*- coding: utf-8 -*-
import scrapy
from szgov_spider.items import SzgovSpiderItem as szgovItem
import re


class SzGovSpiderSpider(scrapy.Spider):
    name = 'sz_gov_spider'
    allowed_domains = ['sipac.gov.cn']
    # start_urls = ['http://www.sipac.gov.cn/dept/kjhxxhj/tzgg/']
    start_urls = ['http://www.sipac.gov.cn/dept/kjhxxhj/tzgg/']

    # 2017-08-22 15:22
    getTime = re.compile(r"(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2})")
    # 清除标签，获取标签中的内容
    clearTag = re.compile(r"<？^[>]*>?(^[<]*)<?^[>]*>?")

    pageIndex = 0

    def getFileLinkList(self,response):
        file_list = response.xpath("//div[@class='contAll']//div[@class='listBox']//ul//li")

        print("in getFileLinkList,is file_list == [] : ",file_list == [])
        
        for item in file_list:
            link_url = item.xpath(".//a[1]/@href").extract()
            if not ("http" in link_url):
                # link_url[2:] 目的是去掉代表相对路径的 ./
                link_url = self.start_urls[0]+(link_url[0].strip())[2:]

                print("in FileList,link_url： ",link_url)
            # # link_list.append(link_url)
            # if not (link_url in self.start_urls):
            #     self.start_urls.append(link_url)
            
            yield scrapy.Request(link_url, callback=self.parse)

    
    def getContext(self,response):
        txt = response.xpath("//div[@class='contAll']")
        # print("getContext ,txt : ",txt)
        data = szgovItem()
        # print(data)
        data['file_name'] = txt.xpath(".//div[@class='contR_cont']//h1/text()").extract_first()
        time_str = str(txt.xpath(".//div[@class='contR_cont']//div[@class='c_d_info']//span/text()").extract())
        # print("this is time : ",time_str,type(time_str))

        # TODO date is None
        try:
            data['date'] = self.getTime.search(time_str).group(0)
        except Exception as e:
            pass

        # print(data['file_name'],data['date'])

        # TODO file_context is []
        file_context = txt.xpath(".//div[@class='TRS_Editor']//p[@class='MsoNormal']//text()").extract()

        print("data&file_context : ",file_context)
        text = ""
        for con in file_context:
            # con = con.encode('utf-8')
            # print("in getContext,con:  ",con," \n after encode : ",con.encode('utf-8'))
            text += str(con).encode('utf-8')
        data['content'] = text
        
        print("in getContext,content : ",data['file_name'],text)

        yield data

    def parse(self, response):
        # print(response.text)
        next_link = response.xpath("//div[@class='pageBar']").extract()
        
        print("in parse,next_link, is [] : ",next_link == [], self.pageIndex)

        # 处于文件列表页
        if next_link != []:
            yield self.getFileLinkList(response)

            self.pageIndex += 100

            # print(self.start_urls[0]+"index_"+str(self.pageIndex)+".htm")

            # 访问下一页列表
            yield scrapy.Request(self.start_urls[0]+"index_"+str(self.pageIndex)+".htm", callback=self.parse)

        # 访问到了详细内容页面
        elif response.xpath("//div[@class='contR_detail']").extract() != []:
            print("Request File Context,response.url : ",response.url)
            
            yield self.getContext(response)

        else:
            # print(response.xpath("//div[@class='contR_detail']").extract())
            print("Bad Request!")
            
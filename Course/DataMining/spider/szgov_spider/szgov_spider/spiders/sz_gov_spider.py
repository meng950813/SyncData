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

    def parse(self, response):
        # print(response.text)
        next_link = response.xpath("//div[@class='pageBar']").extract()
        
        # print("in parse,next_link, is [] : ",next_link == [], self.pageIndex)

        # 处于文件列表页
        if next_link != []:
            # yield self.getFileLinkList(response)
            file_list = response.xpath("//div[@class='contAll']//div[@class='listBox']//ul//li")

            for item in file_list:
                
                time = str(item.xpath(".//span[1]/text()").extract_first())[:4]
                if time != "2018":
                    break

                link_url = item.xpath(".//a[1]/@href").extract()
                if not ("http" in link_url):
                    # link_url[2:] 目的是去掉代表相对路径的 ./
                    link_url = self.start_urls[0]+(link_url[0].strip())[2:]

                yield scrapy.Request(link_url, callback=self.parse)

            self.pageIndex += 1

            # 访问下一页列表
            yield scrapy.Request(self.start_urls[0]+"index_"+str(self.pageIndex)+".htm", callback=self.parse)

        # 访问到了详细内容页面
        elif response.xpath("//div[@class='contR_detail']").extract() != []:
            # self.getContext(response)
            txt = response.xpath("//div[@class='contAll']")

            data = szgovItem()

            data['file_name'] = txt.xpath(".//div[@class='contR_cont']//h1/text()").extract_first()
            time_str = str(txt.xpath(".//div[@class='contR_cont']//div[@class='c_d_info']//span/text()").extract())

            try:
                data['date'] = self.getTime.search(time_str).group(0)
            except Exception as e:
                pass

            response.text.replace("<p>","\r\n <p>")
            # file_context
            data['content'] = "".join(txt.xpath(".//div[@class='TRS_Editor']//p[@class='MsoNormal']//text()").extract())

            yield data
            # print(response.text,data['content'].encode('utf-8'))

        else:
            print("Bad Request!")
            
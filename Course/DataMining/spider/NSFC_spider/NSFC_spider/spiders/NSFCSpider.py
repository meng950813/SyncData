# -*- coding: utf-8 -*-
import scrapy

from pytesser import *

import urllib2
import json
# im = Image.open('validatecode.jpg')

# text = image_to_string(im)

# print("*"*100)
# print("this is test : ",type(im),text)
# print("*"*100)

class NsfcspiderSpider(scrapy.Spider):
	name = 'NSFCSpider'
	allowed_domains = ['isisn.nsfc.gov.cn']
	start_urls = ['https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list']

	POSTURL = start_urls[0]+"/egrantindex/funcindex/pub-project-query"

	pageNum = 1

	header = {
		'Accept': 'application/xml, text/xml, */*; q=0.01',
		"Accept-Encoding": "gzip, deflate, br",
		"Accept-Language": "zh-CN,zh;q=0.9",
		"Connection": "keep-alive",
		"Content-Length": "452",
		"Content-Type": "application/x-www-form-urlencoded",
		"Cookie": "sessionidindex=QSnKb1kRgThxbhvyswp5dKWv1rZB6hQvyd0L9wsZkLSwl4kNFJTQ!-1567179947!NONE; test=44721941; isisn=98184645; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN; JSESSIONID=QrBPiI0i6gvsIUGhyGiSQ2DirvpYdSz6Zmbls2ztJOVGBiDgOjnX!1158236721",
		"Host": "isisn.nsfc.gov.cn",
		"Origin": "https://isisn.nsfc.gov.cn",
		"Referer": "https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
		"X-Requested-With": "XMLHttpRequest"
	}

	def parse(self, response):
		# 若是 None ,表示本页是搜索页
		isSearch = response.xpath("//input[@id='resultDate']/@value").extract_first()

		img_validata = response.xpath("//img[@id='img_checkcode']/@src").extract_first()
		v_code = (self.readValidate(img_validata))[:4]
		
		print("*"*50)
		print(isSearch)
		print("*"*50)

		# 位于搜索页
		if not isSearch:
			print("*"*50)
			print("this is search page and v_code = ",v_code)
			print("*"*50)
			# scrapy.FormRequest\
			data = {
	                'checkcode':v_code,
					'grantCode':'429',
					'subGrantCode':"",
					'helpGrantCode':"",
					'year':'2017&checkcode='+v_code
	            }

			yield scrapy.Request(
	            url = self.start_urls[0]+"?flag=grid&checkcode=",
	            method = "POST",
	            # headers = self.header,
	            body=json.dumps(data),
	            callback=self.post_parse
	        )

		# 位于内容页
		else:
			print("*"*50)
			print("内容页：验证码 = ",v_code)
			print("*"*50)
			print(response.text)


	def readValidate(self,src):

		print("src: ",src)
		src = "https://isisn.nsfc.gov.cn" + str(src)

		# print("this is readValidate and src = ",src)
		# 获取验证码图片
		img = urllib2.urlopen(src)
		
		# 写入本地
		with open("validatecode.jpg","wb") as f:
			f.write(img.read())

		# 打开图片
		im = Image.open('validatecode.jpg')
		
		# im.show()
		# print("readValidate : ",type(im))

		# 返回验证码内容
		return image_to_string(im)



	def post_parse(self,response):
		print("="*50)
		print(response)
		# print("="*50)
		# print(response.body)
		# print("="*50)
		print(response.status)
		
		img_validata = response.xpath("//img[@id='img_checkcode']/@src").extract_first()
		print(img_validata)
		v_code = (self.readValidate(img_validata))[:4]

		print(v_code)
		# data = {
		# 		"_search": 'false',
		# 		'nd': '1538619439464',
		# 		'rows': '10',
		# 		'page': '2',
		# 		'sidx': '',
		# 		'sord': 'desc',
		# 		'searchString': 'resultDate:prjNo:,ctitle:,psnName:,orgName:,subjectCode:,f_subjectCode_hideId:,subjectCode_hideName:,keyWords:,checkcode:6d25,grantCode:429,subGrantCode:,helpGrantCode:,year:2017'
		# 	}

		# data = "_search=false&nd=1538576944008&rows=10&page=1&sidx=&sord=desc&searchString=prjNo:,ctitle:,psnName:,orgName:,subjectCode:,f_subjectCode_hideId:,subjectCode_hideName:,keyWords:,checkcode:n8a2,grantCode:429,subGrantCode:,helpGrantCode:,year:2017"
		data = "_search=false&nd=1538576944008&rows=10&page=1&sidx=&sord=desc&searchString=resultDate%5E%3AprjNo%253A%252Cctitle%253A%252CpsnName%253A%252CorgName%253A%252CsubjectCode%253A%252Cf_subjectCode_hideId%253A%252CsubjectCode_hideName%253A%252CkeyWords%253A%252Ccheckcode%253Aw46b%252CgrantCode%253A429%252CsubGrantCode%253A%252ChelpGrantCode%253A%252Cyear%253A2017%5Btear%5Dsort_name1%5E%3ApsnName%5Btear%5Dsort_name2%5E%3AprjNo%5Btear%5Dsort_order%5E%3Adesc"
		yield scrapy.Request(
			url="https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list?flag=grid&checkcode=",
			method='POST',
			headers = self.header,
			body = data,
			callback = self.getXml
		)
		print("="*50)

	def getXml(self,response):
		print("+"*50)
		print(response.body)
		print("+"*50)

# resultDate=prjNo:,
# 	ctitle:,
# 	psnName:,
# 	orgName:,
# 	subjectCode:,
# 	f_subjectCode_hideId:,
# 	subjectCode_hideName:,
# 	keyWords:,
# 	checkcode:67xf,
# 	grantCode:429,
# 	subGrantCode:,
# 	helpGrantCode:,
# 	year:2017&checkcode=67xf


# sessionidindex=QSnKb1kRgThxbhvyswp5dKWv1rZB6hQvyd0L9wsZkLSwl4kNFJTQ!435439981!1768389381; path=/egrantindex; HttpOnly
# sessionidindex=QSnKb1kRgThxbhvyswp5dKWv1rZB6hQvyd0L9wsZkLSwl4kNFJTQ!1768389381!435439981; path=/egrantindex; HttpOnly
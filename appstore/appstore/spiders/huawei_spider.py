import scrapy
import re
from scrapy.selector import Selector
from appstore.items import AppstoreItem

class HuaweiSpider(scrapy.Spider):
	name = "huawei"
	allowed_domains = ["huawei.com"]
	
	start_urls = [
		"http://appstore.huawei.com/more/recommend/1",
		"http://appstore.huawei.com/more/soft/1",
		"http://appstore.huawei.com/more/game/1",
		"http://appstore.huawei.com/more/newPo/1",
		"http://appstore.huawei.com/more/newUp/1",
	]
	
	initial_urls = [
		"http://appstore.huawei.com/more/all/",
	]
	for url in initial_urls:
		for i in range(1, 41):
			start_urls.append(("").join([url, str(i)]))
	
	'''
	def find_next_page(self, url):
		try:
			page_num_str = url.split('/')[-1];
			page_num = int(page_num_str) + 1
			#limit page count for testing
			#if page_num>1: crawl only specified number of pages
			#return google.com
			url = url[:-len(page_num_str)] + str(page_num)
			return url
		except ValueError:
			print "## page cannot be handled: ",
			print url
			return "http://google.com"
	'''
	
	def parse(self, response):
		page = Selector(response)
		hrefs = page.xpath('//h4[@class="title"]/a/@href')
		for href in hrefs:
			url = href.extract()
			yield scrapy.Request(url, self.parse_item, meta={
				'splash': {
					'endpoint': 'render.html',
					'args': {'wait':0.5}
				}			
			})
	
	def parse_item(self, response):
		page = Selector(response)
		item = AppstoreItem()
		print page 
		item['title'] = page.xpath('.//ul[@class="app-info-ul nofloat"]/li/p/span[@class="title"]/text()').extract_first().encode('utf-8')
		item['url'] = response.url
		appid = re.match(r'http://.*/(.*)', item['url']).group(1)
		item['appid'] = appid
		item['intro'] = page.xpath('.//meta[@name="description"]/@content').extract_first().encode('utf-8')
		
		divs = page.xpath('//div[@class="open-info"]')
		recomm = ""
		for div in divs:
			url = div.xpath('./p[@class="name"]/a/@href').extract_first()
			recommended_appid = re.match(r'http://.*/(.*)', url).group(1)
			name = div.xpath('./p[@class="name"]/a/text()').extract_first().encode('utf-8')
			recomm += "{0}:{1},".format(recommended_appid, name)
		item['recommended'] = recomm
		
		item['thumbnailurl'] = page.xpath('.//ul[@class="app-info-ul nofloat"]/li[@class="img"]/img[@class="app-ico"]/@src').extract_first()
		yield item
		
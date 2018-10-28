# -*- coding: utf-8 -*-
import scrapy
import os
import json
from scrapy import cmdline

if __name__ == '__main__':
    # 输出csv格式
    os.remove('lianjia.csv')
    cmdline.execute("scrapy crawl chengjiao -o lianjia.csv --loglevel=INFO".split())
    # 输出json格式
    # cmdline.execute("scrapy crawl chengjiao --loglevel=INFO".split())


class ChengjiaoSpider(scrapy.Spider):
    name = 'chengjiao'
    allowed_domains = ['gz.lianjia.com']
    # scrapy shell "https://gz.lianjia.com/chengjiao/baiyun/"
    start_urls = ['https://gz.lianjia.com/chengjiao/baiyun/']

    # 解析入口url页面（首页），得到总页数，遍历所有页面
    def parse(self, response):
        page_json_str = response.css('div.house-lst-page-box::attr(page-data)').extract_first()
        page_json = json.loads(str(page_json_str))
        page_url = response.css('div.house-lst-page-box::attr(page-url)').extract_first()
        for i in range(page_json['totalPage']):
            next_page = str(page_url).replace('{page}', str(i + 1))
            yield response.follow(next_page, callback=self.parse_changjiao_record)

    # 遍历成交记录，请求成交记录详情页
    def parse_changjiao_record(self, response):
        data = {}
        for li in response.css('ul.listContent li'):
            url = li.css('div.title a::attr(href)').extract_first()
            request = scrapy.Request(url, callback=self.parse_house)
            request.meta['data'] = data
            yield request

    # 解析房子成交详情
    def parse_house(self, response):
        data = response.meta['data']
        data['title'] = response.css('div.house-title h1::text').extract_first()
        data['成交时间'] = response.css('div.house-title span::text').extract_first()
        data['成交价格(万)'] = response.css('div.price span.dealTotalPrice i::text').extract_first()
        data['成交单价(元/每平)'] = response.css('div.price b::text').extract_first()
        # 其他成交信息
        for span in response.css('div.info div.msg span'):
            data[span.xpath('text()').extract_first()] = span.css('label::text').extract_first()

        # 房屋基本属性
        for li in response.css('div.introContent div.content li'):
            data[li.css('span::text').extract_first()] = li.xpath('text()').extract_first()

        # 房屋交易属性
        for li in response.css('div.introContent div.transaction li'):
            data[li.css('span::text').extract_first()] = li.xpath('text()').extract_first()

        data['房屋详情网址'] = response.url
        yield data

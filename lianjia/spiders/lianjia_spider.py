# -*- coding: utf-8 -*-
import scrapy
import json
import os
from scrapy import cmdline

if __name__ == '__main__':
    # 输出csv格式
    # os.remove('lianjia.csv')
    # cmdline.execute("scrapy crawl lianjia -o lianjia.csv --loglevel=INFO".split())
    # 输出json格式
    cmdline.execute("scrapy crawl lianjia --loglevel=INFO".split())


class LianjiaSpiderSpider(scrapy.Spider):
    name = 'lianjia'
    allowed_domains = ['gz.lianjia.com']
    # scrapy shell "https://gz.lianjia.com/xiaoqu/baiyun/"
    start_urls = ['https://gz.lianjia.com/xiaoqu/baiyun/']

    # 解析入口url页面（首页），得到总页数，遍历所有页面
    def parse(self, response):
        page_json_str = response.css('div.house-lst-page-box::attr(page-data)').extract_first()
        page_json = json.loads(str(page_json_str))
        page_url = response.css('div.house-lst-page-box::attr(page-url)').extract_first()
        for i in range(page_json['totalPage']):
            next_page = str(page_url).replace('{page}', str(i + 1))
            yield response.follow(next_page, callback=self.parse_xiaoqu)

    # 解析每个页面上的小区，拿到小区信息，暂存到data对象中
    def parse_xiaoqu(self, response):
        for xiaoqu in response.css('li.xiaoquListItem'):
            data = {
                '小区名称': xiaoqu.css('div.title a::text').extract_first(),
                '均价': xiaoqu.css('div.totalPrice span::text').extract_first(),
                '在售二手房(套)': xiaoqu.css('div.xiaoquListItemSellCount span::text').extract_first()
            }

            # 销售状态
            house_info = ''
            for position in xiaoqu.css('div.houseInfo a::text'):
                house_info += position.extract()
            data['销售状态'] = house_info

            # 小区商圈
            position_info = ''
            for position in xiaoqu.css('div.positionInfo a::text'):
                position_info += position.extract()
            data['商圈'] = position_info

            # 进入小区详情页面查询其他信息
            detail_url = xiaoqu.css('div.title a::attr(href)').extract_first()
            detail_request = scrapy.Request(detail_url, callback=self.parse_xiaoqu_detail)
            detail_request.meta['data'] = data
            yield detail_request

    # 获取小区详细信息，然后进入小区成交记录页
    def parse_xiaoqu_detail(self, response):
        data = response.meta['data']
        for info in response.css('div.xiaoquInfoItem'):
            data[info.css('span.xiaoquInfoLabel::text').extract_first()] = info.css(
                'span.xiaoquInfoContent::text').extract_first()
        data['详细地址'] = response.css('div.detailDesc::text').extract_first()
        data['小区详情网址'] = response.url

        # 进入小区成交记录页面查找成交记录
        changjiao_record_url = response.css('div.xiaoquMainContent a.btn-large::attr(href)').extract_first()
        if changjiao_record_url:
            changjiao_record_request = scrapy.Request(changjiao_record_url, callback=self.parse_changjiao_record_pages)
            changjiao_record_request.meta['data'] = data
            yield changjiao_record_request

    # 解析小区成交记录首页，得到总页数，遍历所有页面
    def parse_changjiao_record_pages(self, response):
        page_json_str = response.css('div.house-lst-page-box::attr(page-data)').extract_first()
        if page_json_str:
            page_json = json.loads(str(page_json_str))
            page_url = response.css('div.house-lst-page-box::attr(page-url)').extract_first()
            data = response.meta['data']
            for i in range(page_json['totalPage']):
                next_page = str(page_url).replace('{page}', str(i + 1))
                request = response.follow(next_page, callback=self.parse_changjiao_record)
                request.meta['data'] = data
                yield request

    # 遍历成交记录，请求成交记录详情页
    def parse_changjiao_record(self, response):
        data = response.meta['data']
        for li in response.css('ul.listContent li'):
            url = li.css('div.title a::attr(href)').extract_first()
            request = scrapy.Request(url, callback=self.parse_house)
            request.meta['data'] = data
            yield request

    # 解析房子成交详情
    def parse_house(self, response):
        data = response.meta['data']
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

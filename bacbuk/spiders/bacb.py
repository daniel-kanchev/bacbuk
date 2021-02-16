import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bacbuk.items import Article


class BacbSpider(scrapy.Spider):
    name = 'bacb'
    start_urls = ['https://www.bacb.co.uk/news']

    def parse(self, response):
        links = response.xpath('//a[@class="news-item"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@aria-label="Next page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//h2[@class="text-white font-italic"]/text()').get().split()[-1]
        if date:
            date = datetime.strptime(date.strip(), '%d/%m/%Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="bg-white py-5"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()

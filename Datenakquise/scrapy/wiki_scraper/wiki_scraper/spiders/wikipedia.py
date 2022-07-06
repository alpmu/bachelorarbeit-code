import scrapy


class WikipediaSpider(scrapy.Spider):
    name = 'wikipedia'
    allowed_domains = ['de.wikipedia.com']
    start_urls = [
        'https://de.wikipedia.org/wiki/Spezial:Zuf%C3%A4llige_Seite' for i in range(1000)
     ]

    def parse(self, response):
        title = response.xpath('//h1/text()').extract_first()
        with open('log.txt', 'a') as f:
            f.write(f'Title: {title}, URL: {response.url}\n')

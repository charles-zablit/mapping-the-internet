import scrapy
from wikipedia_mapper.items import WikipediaPage


class WikipediaSpider(scrapy.Spider):
    name = "wikipedia"
    allowed_domains = ["en.wikipedia.org"]
    start_urls = ["https://en.wikipedia.org/wiki/Main_Page"]

    def parse(self, response):
        page = WikipediaPage()
        page["title"] = response.xpath("//title/text()").get()
        page["url"] = response.url
        links = []
        for link in response.css("a::attr(href)").getall():
            if link.startswith("/wiki/") and ":" not in link:
                links.append(link[6:])
        page["links"] = links
        yield page

        for link in links:
            yield response.follow(link, callback=self.parse)

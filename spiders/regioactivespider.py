import scrapy
from eventscraper.items import RegioaActiveScraperItem
from scrapy.loader import ItemLoader
import re

class RegioActiveSpider(scrapy.Spider):
    name = "regioactive"
    start_urls = ['https://www.regioactive.de/events/20600/mannheim/veranstaltungen-party-konzerte/2022-02-02']

    # split url, take third element of path and capitalize it
    base_url = re.findall('(\w+)://([\w\-\.]+)', start_urls[0])[0][1]
    city = re.findall('(\w+)://([\w\-\.]+)/(\w+).(\w+).(\w+)', start_urls[0])[0][-1].capitalize()
    counter = 0
    counter_date = 0
    event_list = []

    custom_settings = {
        'FEEDS' :{ 
            'regioActive_items.csv': {
                'format': 'csv',
                'fields': ["date", "city", "loc_name", "street", "postal_code", "latitude", "longitude", "category", "name_event", "start_time", "end_time", "description_short", "link_event", "link_image", "website"],
            },
        }
    }


    def parse(self, response):
        events = response.css('.hcont')

        num = 0
        for event in events:
            l = ItemLoader(item=RegioaActiveScraperItem(), selector=event)

            l.add_css('name_event', 'span.summary::text')
            l.add_xpath('date', './/span[contains(concat(" ", normalize-space(@class), " "), " dtstart ")]/@content')
            l.add_xpath('start_time', './/span[contains(concat(" ", normalize-space(@class), " "), " dtstart ")]/@content')
            l.add_xpath('end_time', './/span[contains(concat(" ", normalize-space(@class), " "), " dtend ")]/@content')

            # location

            l.add_xpath('latitude', './/meta[@itemprop="latitude"]/@content')
            l.add_xpath('longitude', './/meta[@itemprop="longitude"]/@content')
            l.add_xpath('loc_name', './/span[contains(concat(" ", normalize-space(@class), " "), " location ")]/span[@itemprop="name"]/text()')
            
            # Address

            l.add_xpath('street', './/span[@itemprop="streetAddress"]/text()')
            l.add_xpath('postal_code', './/span[@itemprop="postalCode"]/text()')
            l.add_value('city', self.city)

            l.add_css('category', '.muted.hbmargin::text')
            l.add_css('description_short', '.smaller.notmargin::text')
            l.add_xpath('link_event', './/p[contains(concat(" ", normalize-space(@class), " "), " smaller notmargin ")]//a[@class="more"]/@href')
            l.add_xpath('link_image', './/div[contains(concat(" ", normalize-space(@class), " "), " media-object ")]//img/@src')
            
            l.add_value('website', self.base_url.split(".")[1].capitalize())
            yield l.load_item()

        # the numbers of the links do not change equally after the fives day (starting from today(!!)) -> after that, it's alsways the fifth link I need for the next day
        if self.counter < 5:
            self.counter_date = self.counter
        else:
            self.counter_date = 5

        next_page = response.xpath('.//li[contains(concat(" ", normalize-space(@class), " "), " ncurrent ")]//@href').getall()[self.counter_date]
        self.event_list.append(response.xpath('.//li[contains(concat(" ", normalize-space(@class), " "), " ncurrent ")]//@href').getall())

        if next_page is not None and self.counter < 10:
            self.counter += 1
            print(next_page)
            print("COUNTER: ", self.counter)
            yield response.follow(next_page, callback=self.parse)
        else:
            print(self.event_list)

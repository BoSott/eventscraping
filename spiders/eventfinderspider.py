import scrapy
from scrapy.loader import ItemLoader
from eventscraper.items import EventFinderScraperItem
import re

class TheLoader(ItemLoader):
    """ Extended Loader
    for Selector resetting.
    """
    def reset(self, selector=None, response=None):
        if response is not None:
            if selector is None:
                selector = self.default_selector_class(response)
            self.selector = selector
            self.context.update(selector=selector, response=response)
        elif selector is not None:
            self.selector = selector
            self.context.update(selector=selector)


class EventFinderSpider(scrapy.Spider):
    name = 'eventfinder'
    start_urls = ['https://www.eventfinder.de/veranstaltungen-mannheim.php']
    counter = 2
    base_url = re.findall('(\w+)://([\w\-\.]+)', start_urls[0])[0][1]

    custom_settings = {
        'FEEDS' :{ 
            'eventFinder_items.csv': {
                'format': 'csv',
                'fields': ["date", "city", "loc_name", "street", "postal_code", "latitude", "longitude", "category", "name_event", "start_time", "end_time", "description_short", "link_event", "link_image", "website"],
            },
        }
    }


    def parse(self, response):        
        # get event container
        events = response.css('div[id^="\/veranstaltung"]')

        for event in events:
            l = ItemLoader(item=EventFinderScraperItem(), selector=event)
            l.add_xpath('date', './/time[@class="tmtime"]/span[2]//text()')
            l.add_xpath('start_time', './/time[@class="tmtime"]/span[1]//text()')
            l.add_xpath('loc_name', './/*[contains(@class, "col-sm-8")]//a/text()')
            l.add_xpath('description_short', './/div[@class="col-sm-7"]/p/text()')
            l.add_xpath('link_event', './/section[@class="linked"]/a/@href')
            l.add_xpath('link_image', './/*[contains(@class, "event-image-container")]/img/@src')
            
            l.add_value('website', self.base_url.split(".")[1].capitalize())

            # link event location
            # get coordinates
            # city
            # postal code
            # street address
            eventlocationpage = event.xpath('.//*[contains(@class, "col-sm-8")]//@href').get()

            # get category
            eventpage = event.xpath('.//section[@class="linked"]/a/@href').get()
            
            event_item = l.load_item()
            yield response.follow(
                eventlocationpage,
                self.parse_eventlocation,
                meta={'event_item' : event_item, 'event_page': eventpage},
                dont_filter = True
            )

        next_page = f'{self.start_urls[0]}?page={self.counter}'
        if next_page is not None and self.counter < 15:
            print(next_page)
            print("COUNTER: ", self.counter)
            self.counter += 1
            yield response.follow(next_page, callback=self.parse, dont_filter=True)

 
    def parse_eventpage(self, response):
        loader = response.meta['loader']        
        loader.add_xpath('name_event', './/h2[@class="no-margin-bottom"]/text()')
        v = response.xpath('.//ul[contains(concat(" ", normalize-space(@class), " "), " blog-tags ")]/li[2]/a/text()').get()
        loader.add_value('category', v)
        yield loader.load_item()



    def parse_eventlocation(self, response):
        event_item = response.meta['event_item']
        event_page = response.meta['event_page']
        loader = ItemLoader(item=event_item, response=response)
        loader.add_xpath('latitude','.//script[contains(., "lat=")]/text()')
        loader.add_xpath('longitude','.//script[contains(., "lat=")]/text()')
        loader.add_xpath('street', './/h3[@class="margin-bottom-25"]/span/text()')
        loader.add_xpath('postal_code', './/h3[@class="margin-bottom-25"]/span[2]/text()')
        loader.add_xpath('city', './/h3[@class="margin-bottom-25"]/span[3]/text()')
        yield response.follow(event_page, callback = self.parse_eventpage, meta={'loader' : loader, 'event_page': event_page}, dont_filter = True) 

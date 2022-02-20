from scrapy.exceptions import DropItem
import logging

class EventscraperPipelineDefault:
    def process_item(self, item, spider):

        item.setdefault('name_event', 'Here Could Be A Name')
        item.setdefault('start_time', 'undefiniert')
        item.setdefault('end_time', 'undefiniert')
        item.setdefault('loc_name', 'undefiniert')

        item.setdefault('street', 'undefiniert')
        item.setdefault('postal_code', 'undefiniert')
        item.setdefault('city', 'undefiniert')

        item.setdefault('category', 'Sonstige')
        item.setdefault('description_short', 'Es gibt leider keine Kurzbeschreibung')
        item.setdefault('link_event', 'https://www.giybf.com/')
        item.setdefault('link_image', 'https://image.shutterstock.com/image-photo/concept-image-business-acronym-eod-260nw-332349266.jpg')
        return item

class DropIfEmptyFieldPipeline(object):

    def process_item(self, item, spider):
        try:
            if not(item["longitude"]) or not(item["latitude"]):
                raise DropItem()
            else:
                return item
        except KeyError as err:
            print(f"Drop item {item['name_event']}")
            raise DropItem()
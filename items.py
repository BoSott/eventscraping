import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags
import requests
import datetime
import re


def remove_whitespace(value):
    return value.strip()


def string_to_float(value):
    try:
        value = float(value)
    except:
        return None
    return value

def string_to_int(value):
    try:
        value = int(value)
    except:
        return None
    return value


def simplify_category(value):
    return value.replace("/", " ").split(" ")[0]


def check_image_url(value):
    """ 
        check if image response is 200, otherwise turn to None
        scontent and static proved to be the ones not working
        will be resolved with default image through the pipeline
    """
    if not(("scontent" in value) or ("static" in value)):
        return value
    try:
        r = requests.head(value,verify=False,timeout=5) # it is faster to only request the header
        if r.status_code == 200:
            return value
        else:
            return None
    except:
        return None


def only_get_time(value):
    """Create datetime object of date column, only containing the time."""
    try:
        t = datetime.datetime.fromisoformat(value)
    except:
        return None
    return datetime.datetime.strftime(t, '%H:%M')


def only_get_date(value):
    """Create datetime object of date column, only containing the date."""
    try:
        t = datetime.datetime.fromisoformat(value)
    except:
        return None
    return datetime.datetime.strftime(t, '%Y-%m-%d')

def extend_link_event(value):
    '''Check if value exists, if yes: add preface'''
    if value:
        return f'https://www.regioactive.de{value}'


# @dataclass
class RegioaActiveScraperItem(scrapy.Item):
    """Class defines scrapy items, their input- and output_processors"""

    name_event = scrapy.Field(input_processor = MapCompose(remove_tags, remove_whitespace), output_processor = TakeFirst())
    date = scrapy.Field(input_processor = MapCompose(remove_tags, only_get_date), output_processor = TakeFirst())
    start_time = scrapy.Field(input_processor = MapCompose(remove_tags, only_get_time), output_processor = TakeFirst())
    end_time = scrapy.Field(input_processor = MapCompose(remove_tags, only_get_time), output_processor = TakeFirst())

    # location
    latitude = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    longitude = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    loc_name = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())

    # Address
    street = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    postal_code = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    city = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())

    category = scrapy.Field(input_processor = MapCompose(remove_tags, simplify_category), output_processor = TakeFirst())
    description_short = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    link_event = scrapy.Field(input_processor = MapCompose(remove_tags, extend_link_event), output_processor = TakeFirst())
    link_image = scrapy.Field(input_processor = MapCompose(remove_tags, check_image_url), output_processor = TakeFirst())
    website = scrapy.Field()


def get_latitude(value):
    '''Find the latitude in the given string indicated with "lat=" '''
    return re.findall('lat=(\d+.\d+)', value)[0]


def get_longitude(value):
    '''Find the longitude in the given string indicated with "lat=" '''
    return re.findall('lng=(\d+.\d+)', value)[0]


def extend_image_url(value):
    if value:
        value.startswith('/bilder')
        return 'https://www.eventfinder.de' + value
    else:
        return None

def change_date(value):
    return value.replace('.', '/')

def simplify_category(value):
    return value.replace("/", " ").split(" ")[0]

def simplify_cat_eventfinder(value):
    simple_cat = value.strip().replace("/", "").split(" ")[0].strip()
    return simple_cat


class EventFinderScraperItem(scrapy.Item):
    """Class defines scrapy items, their input- and output_processors"""

    name_event = scrapy.Field(input_processor = MapCompose(remove_tags, remove_whitespace), output_processor = TakeFirst())
    date = scrapy.Field(input_processor = MapCompose(remove_tags, change_date), output_processor = TakeFirst())
    start_time = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    end_time = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())

    # location
    latitude = scrapy.Field(input_processor = MapCompose(remove_tags, get_latitude), output_processor = TakeFirst())
    longitude = scrapy.Field(input_processor = MapCompose(remove_tags, get_longitude), output_processor = TakeFirst())
    loc_name = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())

    # Address
    street = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    postal_code = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    city = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())

    category = scrapy.Field(input_processor = MapCompose(remove_tags, simplify_cat_eventfinder), output_processor = TakeFirst()) #simplify_cat_eventfinder
    description_short = scrapy.Field(input_processor = MapCompose(remove_tags)) #, output_processor = TakeFirst())
    link_event = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    link_image = scrapy.Field(input_processor = MapCompose(remove_tags, extend_image_url), output_processor = TakeFirst())

    website = scrapy.Field()

import scrapy

class JobItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    company_description = scrapy.Field() 
    posted_date = scrapy.Field()
    description = scrapy.Field() 
    skills = scrapy.Field()
    job_type = scrapy.Field()
    category = scrapy.Field()
    country = scrapy.Field()
    scrape_timestamp = scrapy.Field()
    salary = scrapy.Field()
    logo_url = scrapy.Field()
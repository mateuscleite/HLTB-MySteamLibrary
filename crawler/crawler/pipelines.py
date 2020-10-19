# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class CrawlerPipeline:
    def process_item(self, item, spider):
        item['game_name'] = item['game_name'].replace("®", "")
        item['game_name'] = item['game_name'].replace("\"", "")
        print("Item:" + item['game_name'])
        return item

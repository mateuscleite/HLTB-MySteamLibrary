import scrapy
import json
from ..items import CrawlerItem

class SteamGamesSpider(scrapy.Spider):
    name = 'steam_games'
    start_urls = [
            'https://steamcommunity.com/id/mcasleite/games/?tab=all'
        ]

    item = CrawlerItem()

    def parse(self, response):

        item = CrawlerItem()
        
        # the games are stored in a javascript object inside a <script> tag
        # this pattern is used to find the object and its content
        pattern = r'\bvar\s+rgGames\s*=\s*(\[{.*?\}])\s*;\s*\n'
        json_data = response.css('script::text').re_first(pattern)
        all_games = json.loads(json_data)
        for game in all_games:
            game_name = game['name']
            item['game_name'] = game_name
            yield item
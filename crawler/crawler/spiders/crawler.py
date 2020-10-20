import scrapy
import json
import re
from scrapy.http import FormRequest 
from scrapy.utils.response import open_in_browser
from ..items import CrawlerItem

class SteamGamesSpider(scrapy.Spider):
    name = 'steam_games'

    def __init__(self, username='', id='', *args, **kwargs):
        super(SteamGamesSpider, self).__init__(*args, **kwargs)
        self.username = username
        self.id = id
        self.hltb_start_url = 'https://howlongtobeat.com/'

    def start_requests(self):
        url_username = 'https://steamcommunity.com/id/' + self.username + '/games/?tab=all'
        url_profile_id = 'https://steamcommunity.com/profiles/'+ self.id + '/games/?tab=all'
        
        if(self.username != ''):
            yield scrapy.Request(url=url_username, callback=self.parse)
        else:
            yield scrapy.Request(url=url_profile_id, callback=self.parse)
                
    def parse(self, response):   
        # the games are stored in a javascript object inside a <script> tag
        # this pattern is used to find the object and its content
        pattern = r'\bvar\s+rgGames\s*=\s*(\[{.*?\}])\s*;\s*\n'
        json_data = response.css('script::text').re_first(pattern)
        if json_data is not None:
            all_games = json.loads(json_data)
            for game in all_games:
                game['name'] = game['name'].replace("®", "")
                game['name'] = game['name'].replace("™", "")
                game['name'] = game['name'].replace("&", "and")
                game['name'] = game['name'].replace("\"", "")
                game['name'] = re.sub(r"\(\w+\)", "", game['name'])
                print("'"+game['name']+"'")
                yield response.follow(self.hltb_start_url, cb_kwargs={'item': game}, callback=self.searchHLTB)
            
    def searchHLTB(self, response, item):
        return FormRequest(url="https://howlongtobeat.com/search_results?page=1", formdata={
            "queryString" : item['name'],
            "t": "games",
            "sorthead": "name",
            "sortd": "Normal Order",
            "plat": "",
            "length_type": "main",
            "length_min": "",
            "length_max": "",
            "detail": ""
        }, cb_kwargs={"item": item} ,callback=self.scrapeGame)

    def scrapeGame(self, response, item):
        print(item['name'])
        first_result = response.css('.search_list_details_block')
        if len(first_result) > 0:
            first_result = response.css('.search_list_details_block')[0]
            data = first_result.css('.search_list_tidbit.center.time_100::text').get()
            
            game_data = CrawlerItem()
            game_data['game_name'] = item['name']
            game_data['length_main_story'] = data
            yield game_data

        
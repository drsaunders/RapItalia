# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from w3lib.html import remove_tags
from tutorial.items import TutorialItem
import os.path

class AngolotestiSpider(CrawlSpider):
    name = 'angolotesti'
    allowed_domains = ['www.aztesti.it']
#    start_urls = ['http://www.angolotesti.it/A/']
    start_urls = ['http://www.aztesti.it/top-artisti/']
    rules = (
         Rule(LinkExtractor(restrict_xpaths=["//*[@class='top-100']"]), follow=True),
         Rule(LinkExtractor(restrict_xpaths=["//*[@class='albums']"],deny=[".*altri-testi-album.*"]), callback='parse_album', follow=True),
         Rule(LinkExtractor(restrict_xpaths=["//*[@class='lyrics-album']"]), process_links='only_first_link', callback='parse_song', follow=True),
    )
    def parse_album(self, response):
		title, year = response.xpath("//div[@class='content album']//h1").re("\t([^\t\n]+)\n")
		tracks = response.xpath("//*[@class='lyrics-album']").re("href=\"\/([^\/]*)\/")
		with open('albuminfo.txt', 'a') as f:
			for t in tracks:
				f.write('%s\t%s\t%s\n' % (title,year[1:-1],t))
		
    def parse_song(self, response):
        filename = 'lyrics/' + response.url.split("/")[-2] + '.txt'
        with open(filename, 'wb') as f:
            lyricsstring = remove_tags(response.xpath("//div[@class='lyrics-content']").extract()[0])
            f.write(lyricsstring.encode('utf-8'))

    def only_first_link(self,links):
        filename = 'lyrics/' + links[0].url.split("/")[-2] + '.txt'
        if os.path.isfile(filename):
            self.logger.info('Skipped ' + links[0].url)
            return []
        else:
            return [links[0]]
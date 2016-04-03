#encoding:utf8 

#scaray import
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from kbook.items import KbookItem

#base import 
import os, sys, logging, time, string
from urlparse import urljoin
from urllib import unquote, quote_plus


#plugin import 
import dbhandle

logging.basicConfig(level=logging.INFO)

reload(sys)  
sys.setdefaultencoding( "utf-8" )


class KanSpider(CrawlSpider):

    name = "kankindle"
    allowed_domains = ["kankindle.com"]
    start_urls = [
        "http://kankindle.com/"
    ]
    rules = [
        Rule(LinkExtractor(allow = ("http://kankindle.com/catalogue/")), callback="parse_typeindex")
        ]

    #debug
    DEBUG = True

        
    def _get_downhref(self , reponse):
        sel = Selector(reponse)
        href = sel.xpath("//p[@class='yanshi_xiazai']/a/@href").extract()[0]
        kbook = reponse.meta["kbook"]
        kbook["downurl"] = href
        return kbook


    def parse_typeindex(self, reponse):
        sel = Selector(reponse)

        url = reponse.url
        book_type = string.split(string.split(reponse.url, "/")[-1], ".")[0] 

        #page num 
        pagejujump = sel.xpath("//div[@class='hero-unit']/a//@href").extract()
        pagenum = len(pagejujump)

        if pagenum > 5:
            pagenum = int(string.split(sel.xpath("//div[@class='hero-unit']/a/@href").extract()[pagenum-1], "/")[-1])

        for i in range(1, pagenum+1):
            #====debug=====
            if self.DEBUG:
                if i > 1:
                    break
            pageurl = string.split(url, ".html")[0] + "/" + str(i)
            req = Request(pageurl, self.parse_booklist_page, meta = dict(booktype = unquote(book_type)))
            yield req 


    def parse_booklist_page(self, response):
        sel = Selector(response)
        books = sel.xpath("//div[@class='hero-unit']/table/tr")[1:]

        #tag
        '''
        tagdetail = book.xpath("td[1]/a")[:-1]
        tags = []
        for tag in tagdetail:
            ret = tag.xpath("text()").extract()[0].decode("utf8").encode("GBK", "ignore")
            tags.append(ret)
        '''

        booktype = response.meta["booktype"]

        items = []
        index = 0
        for book in books:

            #====debug=====
            if self.DEBUG:
                if index >= 1:
                    return

            item  = KbookItem()
            #book titlte
            name  = book.xpath("td[1]//b/text()").extract()[0].strip()

            #anchor
            try:
                anchor= book.xpath("td[4]/a[1]/text()").extract()[0]
            except:
                anchor="unknow"

            #size
            try:
                size  = book.xpath("td[2]/text()").extract()[0]
            except:
                sizse = "unkonw"

            #text format
            try:
                format= book.xpath("td[4]/a[2]/text()").extract()[0]
            except:
                format= "unkonw"

            item["name"] = name
            item["anchor"] = anchor
            item["size"] = size
            item["format"] = format
            item["booktype"] = booktype

            # item["downurl"] = downurl  #store by req
            url = book.xpath("td[1]//@href").extract()[0]
            req = Request(url, self._get_downhref)
            req.meta["kbook"] = item

            yield req
            index = index + 1

    def closed(self, reson):
        print (reson, "reson======??????")
        if reson == "finished":

            #down all file
            func_download = dbhandle.batch_download

            dbhandle.downpath = "/root/download/kindlebook/"

            #chk douban start
            dbhandle.chk_doubanscore(func_download)

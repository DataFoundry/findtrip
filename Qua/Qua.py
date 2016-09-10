#!/usr/bin/env python
# -*- coding:utf-8 -*-
from selenium import webdriver
import time
from random import choice
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from lxml import etree
from urllib import urlencode
import pymongo 
#from washctrip import wash
import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def strunicode2unicode(strunicode):
    return str(strunicode).replace('u\'','\'').decode("unicode-escape")

def parse_pages(driver):
    origin_page = driver.page_source
    origin_html = etree.HTML(origin_page)
    pages = origin_html.xpath('//div[@class="m-page"]/div[@class="container"]//a[@data-pager-pageno]/text()')
    return pages

def parse_airline(driver,dep_date):
    origin_page = driver.page_source
    origin_html = etree.HTML(origin_page)
    base_xpath="//div[@class='mb-10']//div[@class='m-airfly-lst']/div[@class='b-airfly']/div[@class='e-airfly']"
    items=origin_html.xpath(base_xpath)
    airline=[]
    #for index,each in enumerate(items):
    for item in items:
        airline_item={}
        airline_item['search_date'] = datetime.date.today().strftime("%Y-%m-%d") 
        airline_item['dep_date'] = dep_date
        airline_item['company'] = item.xpath( ".//div[@class='air']//span/text()")[0]
        airline_item['airline_num'] = item.xpath('.//div[@class="num"]//span[1]/text()')[0]
        airline_item['airplane'] = item.xpath('.//div[@class="num"]//span[2]/text()')[0]
        airline_item['start_time'] = item.xpath('.//div[@class="sep-lf"]/h2/text()')[0]
        airline_item['start_airport'] = item.xpath( './/div[@class="sep-lf"]/p/span[1]/text()')[0]
        try:
            airline_item['start_terminal'] = item.xpath( './/div[@class="sep-lf"]/p/span[2]/text()')[0]
        except Exception, e:
            print e
            airline_item['start_terminal'] = ''

        airline_item['duration'] = item.xpath('.//div[@class="sep-ct"]/div[@class="range"]/text()')[0]
        airline_item['arrive_time'] = item.xpath('.//div[@class="sep-rt"]/h2/text()')[0]
        airline_item['arrive_airport'] = item.xpath('.//div[@class="sep-rt"]/p/span[1]/text()')[0]
        try:
            airline_item['arrive_terminal'] = item.xpath('.//div[@class="sep-rt"]/p/span[2]/text()')[0]
        except Exception, e:
            print e
            airline_item['arrive_terminal'] = ''
        try:
            airline_item['discount'] = item.xpath( '//div[@class="col-price"]//span[@class="v dis"]/text()')[0]
        except Exception, e:
            print e
            airline_item['discount'] = ''
        airline_item = str(airline_item).replace('u\'','\'')
        airline_item = airline_item.decode("unicode-escape")
        airline_item = eval(airline_item)
        airline.append(airline_item)
    return airline

def findTrip(fromCode,fromCity,toCode,toCity,dep_date,arr_date):
    url_head = "http://flight.qunar.com/site/oneway_list.htm?"
    url_param={"searchDepartureAirport": fromCity,
               "searchArrivalAirport": toCity,
               "searchDepartureTime": dep_date,
               "searchArrivalTime": arr_date,
               "nextNDays": '0',
               "startSearch": 'true' ,
               "fromCode": fromCode,
               "toCode": toCode ,
               "from": "qunarindex",
               "lowestPrice": "null"}
    url = url_head + urlencode(url_param)
    print "url_param: ",url_param
    ua_list = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.0.2564.82 Chrome/48.0.2564.82 Safari/537.36",
            "Mozilla/5.0 (Windows NT 9.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 9.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)"
            ]

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.resourceTimeout"] = 20 
    dcap["phantomjs.page.settings.loadImages"] = False
    
    for i in range(0,3):
        try:
            driver = webdriver.PhantomJS(executable_path='/usr/bin/phantomjs',desired_capabilities=dcap)
            driver.set_window_size(1440, 900) 
        except  Exception, e:
            print e
            time.sleep(10)
            if i<2:
                continue
            else:
                return []

    for i in range(0,3):
        try:
            dcap["phantomjs.page.settings.userAgent"] = choice(ua_list)
            print "phantomjs_settings: ",dcap
            print "try:", i, "times for url: ",url
            driver.get(url)
            break
        except  Exception, e:
            print e
            time.sleep(60)
            pass

    driver.implicitly_wait(5)

    try:
        driver.find_element_by_xpath("//div[@class='filterbox']/div[@class='item item-direct']/label").click()
        menu=driver.find_element_by_xpath("//div[@class='m-condition']/div[@class='e-filter']/div[@class='filterbox']/div[@class='item']//span[contains(text(),'舱位')]/parent::div")
        input=driver.find_element_by_xpath("//div[@class='m-condition']/div[@class='e-filter']/div[@class='filterbox']/div[@class='item']//span[contains(text(),'舱位')]/parent::div/parent::div/div[@class='list']//li[2]/label")
        ActionChains(driver).move_to_element(menu).click(input).perform()
    except  Exception, e:
        print e
        pass

    pages = parse_pages(driver)
    print "pages: ",pages
    airline = parse_airline(driver,dep_date) 
    for page in pages: 
        print "get page: ",page,"of pages: ",pages
        try:
            driver.find_element_by_xpath("//div[@class='m-page']/div[@class='container']/a[@data-pager-pageno='" + str(page) + "']").click()
        except Exception, e:
            print "can't click pages"
            continue
        airline = airline + parse_airline(driver,dep_date) 
    return airline
    

if __name__ == '__main__':
    city_list=['CAN:广州', 'PEK:北京', 'SHA:上海', 'PVG:上海', 'CSX:长沙', 'CTU:成都', 'HAK:海口',
               'CKG:重庆', 'SZX:深圳', 'HGH:杭州', 'DLC:大连', 'URC:乌鲁木齐', 'WUH:武汉', 'NKG:南京',
               'SYX:三亚', 'KMG:昆明', 'SHE:沈阳', 'SIA:西安', 'HRB:哈尔滨', 'XMN:厦门']
    #city_list=['SHA:上海', 'CAN:广州']

    
    mongo_client = pymongo.MongoClient('mongodb://jsmith:' + 'password' + '@10.173.32.103')
    mongo_db = mongo_client['airline_data']  
    #mongo_collect = mongo_db['airline_data']
    #mongo_collect = mongo_db['airline_test']
    mongo_collect = mongo_db[sys.argv[3]]
    now=datetime.date.today()
      
    for fromCity in city_list:
        for toCity in city_list:
            if(fromCity.split(':')[1] == toCity.split(':')[1]):
                continue
            for i in range(int(sys.argv[1]), int(sys.argv[2])): 
                date = now + datetime.timedelta(days = i)
                dep_date = date.strftime("%Y-%m-%d")
                date = now + datetime.timedelta(days = (i+9))
                arr_date = date.strftime("%Y-%m-%d")
                print dep_date 
                print "get data .........." 
                airline={}
                airline = findTrip(fromCity.split(':')[0],
                         fromCity.split(':')[1],
                         toCity.split(':')[0],
                         toCity.split(':')[1],
                         dep_date,
                         arr_date)     
                 
                if airline <> []:
                    print "save data .........." 
                    post_res = mongo_collect.insert_many(airline)
                    print post_res
                
                else:
                    print "no data ............"

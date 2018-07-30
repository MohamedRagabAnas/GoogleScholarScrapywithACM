# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re
import sys
import csv


class GooglescholarSpider(scrapy.Spider):
    name = 'googlescholar'
    allowed_domains = ['scholar.google.com']
    topic='description_logic'
    start_urls = ['https://scholar.google.com.eg/citations?view_op=search_authors&hl=en&mauthors=label:lod']

    chromeOptions = webdriver.ChromeOptions()
    prefs={'disk-cache-size': 4096 }
    chromeOptions.add_experimental_option('prefs', prefs)
        
    def getURL(self,Prev_Next_url):
        url=Prev_Next_url
        url=url.replace("\\x3d","=")
        url=url.replace("\\x26","&")
        url=url.replace("&oe=ASCII","")
        url=url.replace("window.location='","https://scholar.google.com.eg")
        url=url.replace("'","")
        return url
    			
    def parse(self, response):
        authors=response.xpath('//*[@class="gsc_1usr gs_scl"]')
        
        ACM_BASE_URL = 'https://dl.acm.org/'
        ACM_SEARCH_URL = ACM_BASE_URL + "results.cfm?within=owners.owner%3DGUIDE&srt=_score&query=persons.authors.personName:"
        
        driver = webdriver.Chrome(chrome_options=self.chromeOptions) # wen need to check Phantom js which is hidden and may be faster...

        for author in authors:
            name= author.xpath('.//h3[@class="gsc_oai_name"]/a/text()').extract_first()
            link= author.xpath('.//h3[@class="gsc_oai_name"]/a/@href').extract_first()
            Afflst=[] 
            Afflst.append(author.xpath('.//*[@class="gsc_oai_aff"]/text()').extract_first())
            email=author.xpath('.//*[@class="gsc_oai_eml"]/text()').extract_first()
            email=str(email).replace('Verified email at ', '')
            citedby=author.xpath('.//*[@class="gsc_oai_cby"]/text()').extract_first()
            citedby=str(citedby).replace('Cited by ', '')
            topics=author.xpath('.//*[@class="gsc_oai_one_int"]/text()').extract()
            
            
            driver.get(ACM_SEARCH_URL+""+name)
            try:
                link = driver.find_element_by_link_text(name)
                link.click()
                affHistElems=driver.find_elements_by_xpath("/html/body/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/div/a")
                affHist=[]
                for aff in affHistElems:
                    affHist.append(aff.text)
                Afflst.append(affHist)
            except:
                print ('Link to be clicked cannot be found!')

            yield{'Name':name,'Affiliation':Afflst,'Email':email,'CitedBy':citedby,'Topics':topics}    
            #yield{'Affiliation':Afflst}

        Prev_Next =response.xpath("//button[@type='button'][@aria-label='Next']/@onclick").extract()
        if(len(Prev_Next)>0):
            Prev_Next_url=str(Prev_Next[0])
            Prev_Next_url=self.getURL(Prev_Next_url)
            yield scrapy.Request(url=Prev_Next_url, dont_filter=True)
        
            			
			

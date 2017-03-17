# -*- coding: utf-8 -*-
"""
@author: yevhenkolodko
"""

from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import urllib.request 
import requests

     
class TagParser:    
    """
    Inherit from this class if calendar is just shown on the page.
    """
    
    def __init__(self, url):
        req = urllib.request.Request(url, 
                                     headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
        self.soup = BeautifulSoup(html, 'lxml')
        self._get_days_from_soup()
         
    def _check_if_url_correct(self, url, supported_site):
        try:
            assert urlsplit(url)[1] == supported_site
        except AssertionError:
            print("This class doesn't support your URL")
                    
    def _get_days_from_soup(self):
        try:
            self.days = self.soup.findAll(self.day_tag_info[0],
                                          attrs=self.day_tag_info[1]) 
            assert self.days != []                                     
        except AssertionError:
            print('Could not parse a url, because day_tag_info or date_string \
is invalid. Check the page source code for correct value of tag')   

    def _check_if_flags_valid(self):
        
        try:
            assert self.soup.find(attrs=
                                 {'class':self.unavailable_flags}) != None
            assert self.soup.find(attrs={'class':self.no_info_flags}) != None
        except AssertionError:
            print('Invalid status flags used. Check the page source for\
actual values')                           
                             
    def make_calendar(self):
        self.calendar = []
                                     
        for day in self.days:
            date = self.get_date(day)
            status = self.check_day_status(day)
            
            self.calendar.append((date,status))
                  
    def check_day_status(self, day):        
        
        if 'class' in day.attrs.keys(): #available dates can be blank tag

            if any(flag in day.attrs['class'] for flag in self.no_info_flags):
                status = 'NO INFO'
                
            elif any(flag in day.attrs['class'] for flag in 
                                                      self.unavailable_flags):
                status = 'Unavailable'
            
            else:
                status = 'Available'
                
        else:
            status = 'Available'  
        return status
 
          
class JsonParser:
    """
    Inherit from this class if calendar is sent as json file via request.
    """
    def __init__(self, req_type, link , data):        
        if req_type == 'post':
            self.response = requests.post(link, data)
        elif req_type == 'get':
            self.response = requests.get(link, data)
        else:
            raise AttributeError('Provided type of request is not supported')

        self.response.raise_for_status()
    
    def _check_if_url_correct(self, url, supported_site):
        try:
            assert urlsplit(url)[1] == supported_site
        except AssertionError:
            print("This class doesn't support your URL")    
               
    def make_calendar(self):
        self.calendar = self.response.json()
        
##############################################################################        
       
class OktvParser(TagParser):
   
    def __init__(self,url):
        self._check_if_url_correct(url, 'oktv.ua')
        self.unavailable_flags = ['bron']
        self.no_info_flags = ['old']   
        self.date_string = 'data-time-default'
        self.day_tag_info = ('div', {self.date_string:True})
        super().__init__(url)
        self._check_if_flags_valid()
             
    def get_date(self, day):
        try:
            date = day.attrs[self.date_string]
        except KeyError:
            print('Invalid date_string value. Check the page source for \
actual values')
        return date
 

class DobovoParser(JsonParser):
    
    def __init__(self, url, start_date='2017-03-01'):
       self._check_if_url_correct(url, 'www.dobovo.com') 
       req_type = 'post' 
       post_link = 'http://www.dobovo.com/dobovo/apt/ajax.php?\
                           action=getCalendar&lang=en' 
       data = {'id':self._get_id(url),'date':start_date}
       super().__init__(req_type, post_link, data)

       
    def _get_id(self,url):
        return urlsplit(url).path.replace('.','-').split('-')[-2]       


class AirbnbParser(JsonParser):
    
    def __init__(self, url, month_to_start='3', count='3'):
        self._check_if_url_correct(url, 'www.airbnb.com') 
        req_type = 'get'
        get_link = 'https://www.airbnb.com/api/v2/calendar_months'
        data = {'key':'d306zoyjsyarp7ifhu67rjxn52tv0t20', 
                'listing_id': self._get_id(url), 
                'month': month_to_start, 
                'count': count}
        super().__init__(req_type, get_link, data)
        
    def _get_id(self, url):     
        return url.split('/')[-1]
               
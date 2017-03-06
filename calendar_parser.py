# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 03:33:37 2017

@author: polka
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlsplit
import time
import calendar
import datetime
import sys


def month_to_number(month):
    month_numbers = {v: k for k,v in enumerate(calendar.month_name)}
    number = str(month_numbers[month])
    if len(number) == 1:
        number = '0' + number
    return number


def calendar_parser(url):
    """
    Parse a site to get a booking calendar.
    
    input: string
        URL of a page with wanted flat.
    
    output: list of tuples
        Returns list of tuples, where each tuple is the information about a 
        day. 
        First element of tuple is a string with date. If constructed by the 
        program,
        the string is "YYYY-MM-DD' format, else it can have a format provided
        by site, for example 'DD.MM.YYYY'.
        Second element is a status string with three possible values.
            'Available' -- the flat is available for selected date.
            
            'Unavailable' -- the flat is already booked for selected date.
            
            'NO INFO' -- information is not provided for this date, e.g. 
            the date is last or the program constructed unexisting date like 
            '2017-02-31'. Typically, date with this status must be filtered out
            
        NOTE: sometimes, sites show info about some months multiple times, like 
        www.tripadvisor.com does. It can be filtered by using set() function.
        
    If user wants to add a new site to parser, he must examine the source code 
    of page and assign parameter variables:
    
    click: boolean
        True, if the page shows calendar only after clicking on button or 
        input form.
        
    click_id: string
        Id of an element that must be clicked.
        
    date_type: {'by_date_str', 'by_construction_from_tags'}
        The way date information is provided by page.
            'by_date_str' -- site provides date as an attribute of an element 
            with day.

            'by_construction_from_tags' -- date information is displayed for 
            each month as a header of calendar in a word form, 
            e.g. 'March 2017'. If year info is not provided, it's filled with a 
            value of current year.
            
    tag_with_days: string
        Name of a tag, that contains info about a single day. Common values 
        are 'div','td'.
    
    tag_with_days_attrs: dictionary
        All possible attributes of tags with day info. The keys are the 
        attributes name, e.g. {'class':'calendar_month_day'}. If there are 
        multiple attributes, the value of dict is a list of strings, 
        e.g. {'class':['available', 'booked']}.
        
    unavailable_flag: list of strings
        Attributes of a tag with day info that show the flat is already booked 
        for the date. If there's no such attribute, the flat is considered as 
        available.
        
    no_info_flag: list of strings
        Attributes of a tag with day that show there's no information about 
        booking. Used for blank cells in calendar, for last days or cells of 
        other month.
   
    The next parameters are used if user chose by_construction_from_tags' 
    value of date_str.
    
    prev_tag_to_find_month: string or False if there's no such tag.
        A tag located upper than day tag, that contains information about 
        month.
        
    attr_to_find_month: dictionary
        Attributes of tag with month info.
        
    prev_tag_to_find_year: string or False if there's no such tag.
        A tag located upper than day tag, that contains information about year.
        If there's no such info, the program will fill it with a value of a 
        current year.
        
    attr_to_find_year: dictionary
        Attributes of tag with year info.
        
    Sometimes, prev_tag_to_find_month and prev_tag_to_find_year can be the 
    same tag with information in a form, e.g. 'March 2017'. The program will 
    split that string and convert it to number with month_to_number() function.
    
    Example of using:
    
    >>> calendar_parser('https://www.airbnb.com/rooms/16435808')
    
    [('2017-03-', 'NO INFO'),
     ('2017-03-', 'NO INFO'),
     ('2017-03-', 'NO INFO'),
     ('2017-03-1', 'Unavailable'),
     ('2017-03-2', 'Unavailable'),
     ('2017-03-3', 'Unavailable'),
     ('2017-03-4', 'Unavailable'),
     ('2017-03-5', 'Unavailable'),
     ('2017-03-6', 'Unavailable'),
     ('2017-03-7', 'Available'),
     ('2017-03-8', 'Available'),
     ...
     
    """
    
    sites_added = ['www.dobovo.com',
                   'oktv.ua',
                   'www.partnerguesthouse.com',
                   'www.airbnb.com',
                   'www.tripadvisor.com',
                   'www.9flats.com',
                   'www.wimdu.com']
    
    site = urlsplit(url)[1]
    if site in sites_added:
        if site == 'oktv.ua':
            click = False
            click_id = ''
            date_type = 'by_date_str'
            date_str = 'data-time-default'
            tag_with_days = 'div'
            tag_with_days_attrs = {date_str:True}
            unavailable_flag = ['bron']
            no_info_flag = ['old']
            prev_tag_to_find_month = False
            attr_to_find_month = {}
            prev_tag_to_find_year = False
            attr_to_find_year = {}

        elif site == 'www.dobovo.com':
            click = False
            click_id = ''
            date_type = 'by_date_str'
            date_str = 'date'
            tag_with_days = 'div'
            tag_with_days_attrs = {date_str:True}
            unavailable_flag = ['is-inactive']
            no_info_flag = ['is-last-days']
            prev_tag_to_find_month = False
            attr_to_find_month = {}
            prev_tag_to_find_year = False
            attr_to_find_year = {}

        elif site == 'www.airbnb.com':
            click = True
            click_id = 'datespan-checkin' 
            date_type = 'by_construction_from_tags'
            date_str = False
            tag_with_days = 'td'
            tag_with_days_attrs = {}
            unavailable_flag = ['ui-state-disabled']
            no_info_flag = ['ui-datepicker-other-month']
            prev_tag_to_find_month = True
            attr_to_find_month = {'class':'ui-datepicker-month'}
            prev_tag_to_find_year = True
            attr_to_find_year = {'class':'ui-datepicker-year'}

        elif site == 'www.partnerguesthouse.com':
            click = False
            click_id = '' 
            date_type = 'by_construction_from_tags'
            date_str = False
            tag_with_days = 'span'
            tag_with_days_attrs = {'class':['calender__booking', 
                                            'js-open-popupcal']}
            unavailable_flag = ['calender__booking']
            no_info_flag = ['']
            prev_tag_to_find_month = 'h3'
            attr_to_find_month = {}
            prev_tag_to_find_year = False
            attr_to_find_year = {}

        elif site == 'www.tripadvisor.com':
            click = False
            click_id = '' 
            date_type = 'by_construction_from_tags'
            date_str = False
            tag_with_days = 'td'
            tag_with_days_attrs = {'class':['available', 'booked', 
                                            'vr-detail-cal-checkout', 
                                            'vr-detail-cal-checkin']}
            unavailable_flag = ['booked','vr-detail-cal-checkin']
            no_info_flag = ['past']
            prev_tag_to_find_month = 'div'
            attr_to_find_month = {'class':'caption'}
            prev_tag_to_find_year = 'div'
            attr_to_find_year = {'class':'caption'}

        elif site == 'www.9flats.com':
            click = False
            click_id = '' 
            date_type = 'by_date_str'
            date_str = 'data-day'
            tag_with_days = 'div'
            tag_with_days_attrs = {'class':'place__calendar__month__day'}
            unavailable_flag = \
                ['place__calendar__month__day__status_unavailable']
            no_info_flag = ['place__calendar__month__day_gone', 
                            'place__calendar__month__day_out']
            prev_tag_to_find_month = 'caption'
            attr_to_find_month = {'class':'place__calendar__month__header'}
            prev_tag_to_find_year = 'caption'
            attr_to_find_year = {'class':'place__calendar__month__header'}   

        elif site == 'www.wimdu.com':
            click = True
            click_id = 'booking_checkin_date' 
            date_type = 'by_construction_from_tags'
            date_str = False
            tag_with_days = 'td'
            tag_with_days_attrs = {'class':['g','ui-datepicker-unselectable']}
            unavailable_flag = ['ui-state-disabled']
            no_info_flag = ['ui-datepicker-other-month']
            prev_tag_to_find_month = 'span'
            attr_to_find_month = {'class':'ui-datepicker-month'}
            prev_tag_to_find_year = 'span'
            attr_to_find_year = {'class':'ui-datepicker-year'}       

        """
        #Uncomment this part and complete assignments to add new site

        elif site == '':
            click = False / True
            click_id = '' 
            date_type = 'by_date_str' / 'by_construction_from_tags'
            date_str = False / True
            tag_with_days = ''
            tag_with_days_attrs = {'class':''}
            unavailable_flag = ['']
            no_info_flag = ['']
            prev_tag_to_find_month = '' / False
            attr_to_find_month = {'class':''}
            prev_tag_to_find_year = '' / False
            attr_to_find_year = {'class':''}    
        """
           
    else:
        print('Please, add this site to parser before scraping')
        return
    
    browser = webdriver.PhantomJS()
    browser.set_window_size(1366, 768)
    browser.get(url)
    
    if click:
        browser.find_element_by_id(click_id).click()
        time.sleep(1) # wait for calendar to download
        
    page_source = browser.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    browser.quit()
      
    result = []
    days = soup.findAll(tag_with_days, attrs=tag_with_days_attrs)
    for day in days:

        if date_type == 'by_date_str':
            date = day.attrs[date_str]
            
        elif date_type == 'by_construction_from_tags':
            day_number = day.getText()
            if len(day_number) == 1:
                day_number = '0' + day_number
                
            # split is used in cases like 'March 2017'
            month = month_to_number(
                        day.find_previous(prev_tag_to_find_month, 
                        attrs=attr_to_find_month).getText().split()[0]) 
            
            if prev_tag_to_find_year:
                year = day.find_previous(attrs=attr_to_find_year).getText()
            else:
                year = str(datetime.datetime.now().year)
                
            if len(year.split()) == 2:
                year = year.split()[1]
                   
            date =  ''.join((year,'-',month,'-',day_number)) 
            
        #sometimes available days are just empty tags
        if 'class' in day.attrs.keys(): 

            if any(flag in day.attrs['class'] for flag in no_info_flag):
                status = 'NO INFO'
                
            elif any(flag in day.attrs['class'] for flag in unavailable_flag):
                status = 'Unavailable'
            
            else:
                status = 'Available'
                
        else:
            status = 'Available'
        
        result.append((date,status))
        
    return result
    
if __name__ == '__main__':
    result = calendar_parser(sys.argv[1])
    for day in result:
        print(day)
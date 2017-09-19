#!/bin/python
from bs4 import BeautifulSoup as bs
import lxml
from os import _exit
from os.path import expanduser, exists
from termcolor import colored, cprint
import asyncio
import async_timeout
import aiohttp
import concurrent.futures
import math
from dateutil.parser import parse
import logging

"""

Craigraker! A really cool Craigslist scraper!

This file contains the functions used in craigraker.py. Make sure this file is in the same directory so that craigraker can run. 

Craigraker reads from the config file ~/.craigrakerrc which is where craigraker gets location data. 

Craigraker is able to produce highlighted output for readability, as well as sort listings by price, location (alphabetically), or date posted.

Output is formatted so that it can be written to a csv for spreadsheet use.

AUTHOR:Ethan Henderson 
https://github.com/ethan626

"""

async def fetch(url, params=None):
    """ Grabs a url  """
    
    async with aiohttp.request('GET', url, params=params) as response:
        return await response.text()
    
async def scrape_ad_page(url, params=None):    
    """ Returns the info from a cl-ad page. """
    
    try:
        response = await fetch(url, params=params)
        soup = bs(response, "lxml")
        
    except Exception as e:
        logging.debug(e)

    else:
        page_text = soup("section",{"id":"postingbody"})[0].text
        page_text = page_text.replace('\n\nQR Code Link to This Post\n\n\n','') # Remove the junk
        page_text = page_text.replace(',','')
        page_text = page_text.replace('\n','')
        
        date = soup("time", class_="date timeago")[0].text
                
        for contact_link in soup('a', {'id':'replylink'}):
            contact_link = ''.join([local_cl_url, contact_link['href']])
                                    
        contact_email, contact_phone = await get_contact_info(contact_link)
        
        return page_text, date, contact_email, contact_phone

async def get_contact_info(url, params=None):
    """ Visits the contact info page """
        
    try:
        response = await fetch(url, params=params)
        soup = bs(response, "lxml")
        
    except Exception as e:
        logging.debug(e)
        
    else:
        email_address, phone_number = "N/A","N/A"

        for email in soup('p', class_='anonemail'):
            email_address = email.text
            email_address = email_address.replace(',','')

        for phone in soup('p', class_='reply-tel-number'):
            phone_number = phone.text
            phone_number = phone_numbe.replace(',','')

        return email_address, phone_number

async def scrape_search_page(url, params=None, verbose=False, wanted=False, max_results=120):

    """ 
        Returns (ad title, price, neighborhood,link) or if verbose (ad title, price, neighborhood, ad text, link)

        verbose: Verbose output, the function will visit every ad and extract the text from within the ad.

       """    

    try:
        response = await fetch(url, params=params)
        soup = bs(response, 'lxml')

    except Exception as e:
        logging.debug(e)
        
    else:
        results = []

        for link, counter in zip(soup("p",{"class":"result-info"}), range(max_results)):
            price, hood = "N/A", "N/A" # Incase of none

            if wanted:              # Ignore wanted ads
                if 'wanted' in link.text.lower():
                    continue
                
            for price in link("span",{"class":"result-price"}):                    
                price = price.text
                price = price.strip()
                price = price.replace("(","")
                price = price.replace(")","")
                price = price.replace("$","")
                price = price.replace(',','') 
                price = price.replace('\n','')
                price = float(price)

            for hood in link("span",{"class":"result-hood"}):                    
                hood = hood.text
                hood = hood.strip()
                hood = hood.replace(",","")
                hood = hood.replace("(","")
                hood = hood.replace(")","")
                hood = hood.replace('\n','')

            for link_text in link("a",{"class":"result-title hdrlnk"}):
                ad_title = link_text.text
                ad_title = ad_title.strip()
                ad_title = ad_title.replace('\n','')
                ad_title = ad_title.replace(',','')
                ad_url = ''.join([local_cl_url, link_text['href']]) # Individual ad page url

            for date in link('time',{"class","result-date"}):                    
                date_updated = parse(date['datetime'])

            if verbose:
                full_url = ''.join([local_cl_url, link_text['href']]) # Individual ad page url

                try:
                    page_text, date_posted, contact_email, contact_phone = await scrape_ad_page(full_url)

                except Exception as e:
                    logging.debug(e)

                results.append((ad_title, price, hood, page_text, contact_email, contact_phone, ad_url, date_updated, date_posted))

            else:
                results.append((ad_title, price, hood, ad_url, date_updated))
                
        return results
        
async def get_total_results(url, params=None):
    """ Returns the total number of search results"""

    try:
        response = await fetch(url, params=params)
        soup = bs(response, 'lxml')
        return int(soup('span',class_='totalcount')[0].text)

    except Exception as e:
        logging.debug(e)

def print_result(result, color=False):    
    """ """

    if len(result) == 9:
        if color:
            print("{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(colored(result[0],'white'),colored(result[1],'red'),colored(result[2],'yellow'), 
                                                               colored(result[3],'green'),colored(result[4],'blue'), colored(result[5], 'cyan'), colored(result[6], 'magenta'), colored(result[7], 'white'), colored(result[8],'red')))
        else:
            print("{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(*result))
                  
        return None

    if len(result) == 6:
        if color:
            print("{0},{1},{2},{3},{4},{5}".format(colored(result[0],'white'),colored(result[1],'red'),colored(result[2],'yellow'), 
                                               colored(result[3],'green'),colored(result[4],'blue'), colored(result[5], 'cyan')))
        else:
            print("{0},{1},{2},{3},{4},{5}".format(*result))
                  
        return None
    
    if len(result) == 5:
        
        if color:
            print("{0},{1},{2},{3},{4}".format(colored(result[0],'white'),colored(result[1],'red'),colored(result[2],'yellow'), 
                                               colored(result[3],'green'), colored(result[4],'cyan')))
        else:
            print("{0},{1},{2},{3},{4}".format(*result))
                  
        return None

    if len(result) == 4:
        if color:
            print("{0},{1},{2},{3}".format(colored(result[0],'white'),colored(result[1],'red'),colored(result[2],'yellow'), 
                                            colored(result[3],'green')))
        else:
            print("{0},{1},{2},{3}".format(*result))

        return None
          
def parse_section(user_choice):
    """ Returns the appropiate resource id for the section of Craiglist """
    
    if user_choice.lower() == "for sale":
        return "sss"
    
    if user_choice.lower() == "personals":
        return "ppp"
    
    if user_choice.lower() == "community":
        return "ccc"
    
    if user_choice.lower() == "gigs":
        return "ggg"
    
    if user_choice.lower() == "housing":
        return "hhh"
    
    if user_choice.lower() == "jobs":
        return "jjj"
    
    if user_choice.lower() == "resumes":
        return "rrr"
    
    if user_choice.lower() == "services":
        return "bbb"

def scrape(url, query, max_results=120, verbose=False, wanted=False):
    """ Main driver """
    
    try:
        tasks = [asyncio.ensure_future(get_total_results(url, params={'query': query, 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}))] # Get the max number of results for this query
        completed, _ = LOOP.run_until_complete(asyncio.wait(tasks))

        total_results = [i.result() if not max_results else max_results for i in completed if i.result()][0]        

        parameters = [{"s": i, "query": query, "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36" } for i in range(0,total_results,120)]    

       
        tasks = [asyncio.ensure_future(scrape_search_page(url, params=param, max_results=max_results, verbose=verbose, wanted=wanted))
                 for param in parameters]        

        completed, _ = LOOP.run_until_complete(asyncio.wait(tasks))    
        results = []
        _ = [results.extend(key.result()) for key in completed if key.result()]
        
        return results
    
    except Exception as e:
        print("No results")
        _exit(status=0)         # No results so exit the script

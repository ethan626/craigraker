#!/bin/python
import math
import traceback
from os import _exit
import asyncio
from dateutil.parser import parse

import aiohttp
from bs4 import BeautifulSoup as bs
import lxml
from termcolor import colored, cprint

from craigraker import LOOP 

""" 

Craigraker! A really cool Craigslist scraper!

Functions used in craigraker.py and craigraker_gui.py. 

Author: Ethan Henderson 
https://github.com/ethan626

"""

async def fetch(url, params=None):
    """ Fetches a url. Returns an awaitable. """
    async with aiohttp.request('GET', url, params=params) as response:
        return await response.text()

async def get_contact_info(url, params=None):
    """ Gets the email address and phone number in the ad. Return a tuple. """
    try:
        response = await fetch(url, params=params)
        soup = bs(response, "lxml")

        email_address, phone_number = "N/A","N/A"

        for email in soup('p', class_='anonemail'):
            email_address = email.text
            email_address = email_address.replace(',','')

        for phone in soup('p', class_='reply-tel-number'):
            phone_number = phone.text
            phone_number = phone_numbe.replace(',','')

        return email_address, phone_number

    except Exception:
        print(traceback.format_exc())

async def get_total_results(url, params=None):
    """ Returns the total number of search results"""
    try:
        response = await fetch(url, params=params)
        soup = bs(response, 'lxml')
        return int(soup('span',class_='totalcount')[0].text)

    except Exception:
        print(traceback.format_exc())

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

    else:
        print("Please choose a valid section of Craigslist, such as \"for sale\" ")
        return ""

def print_result(result, color=False):    
    """ Print the scraped data colored with ANSI colors """
    if len(result) == 9:
        if color:
            print("{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(colored(result[0],'white'),
                                                               colored(result[1],'red'),
                                                               colored(result[2],'yellow'), 
                                                               colored(result[3],'green'),
                                                               colored(result[4],'blue'),
                                                               colored(result[5], 'cyan'),
                                                               colored(result[6], 'magenta'),
                                                               colored(result[7], 'white'),
                                                               colored(result[8],'red')))
        else:
            print("{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(*result))

    if len(result) == 6:
        if color:
            print("{0},{1},{2},{3},{4},{5}".format(colored(result[0],'white'),
                                                   colored(result[1],'red'),
                                                   colored(result[2],'yellow'), 
                                                   colored(result[3],'green'),
                                                   colored(result[4],'blue'),
                                                   colored(result[5], 'cyan')))
        else:
            print("{0},{1},{2},{3},{4},{5}".format(*result))
                  
    if len(result) == 5:
        if color:
            print("{0},{1},{2},{3},{4}".format(colored(result[0],'white'),
                                               colored(result[1],'red'),
                                               colored(result[2],'yellow'), 
                                               colored(result[3],'green'),
                                               colored(result[4],'cyan')))
        else:
            print("{0},{1},{2},{3},{4}".format(*result))
                  
    if len(result) == 4:
        if color:
            print("{0},{1},{2},{3}".format(colored(result[0],'white'),
                                           colored(result[1],'red'),
                                           colored(result[2],'yellow'), 
                                           colored(result[3],'green')))
        else:
            print("{0},{1},{2},{3}".format(*result))

    return None

def scrape(url, local_cl_url, query, max_results=120, verbose=False, wanted=False):
    """ Executes a scrape of craigslist. Returns a list of the results. """
    try: # Get the max number of results for this query
        tasks = [asyncio.ensure_future(
                                       get_total_results(url,
                                                params={'query': query,
                                                        'User-Agent': """Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)
                                                         AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"""}))]

        completed, _ = LOOP.run_until_complete(asyncio.wait(tasks))
        total_results = [i.result() if not max_results or i.result() < max_results
                         else max_results for i in completed if i.result()][0] # Getting the max number of results

        parameters = [{"s": result_count, "query":
                       query, "User-Agent": """Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)
                              AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/538.36"""}
                      for result_count in range(0, total_results, 120)] # Each page is 120 results or less 

        tasks = [asyncio.ensure_future(scrape_search_page(url,
                                                          local_cl_url,
                                                          params=param,
                                                          max_results=total_results,
                                                          verbose=verbose,
                                                          wanted=wanted))
                                                          for param in parameters]        

        completed, _ = LOOP.run_until_complete(asyncio.wait(tasks))    
        results = []
        _ = [results.extend(key.result()) for key in completed if key.result()]

        return results

    except IndexError as e:
        # print(traceback.format_exc())
        print("Sorry, no results.")
        _exit(status=0)         # No results so exit the script

    except Exception: 
        print(traceback.format_exc())
        _exit(status=0) 

async def scrape_ad_page(url, local_cl_url, contact_info=False, params=None):    
    """ Scrapes a Craigslist ad page. Returns a tuple of the page text, date, contact email, and contact phone number. """ 
    try:
        response = await fetch(url, params=params)
        soup = bs(response, "lxml")

        page_text = soup("section",{"id":"postingbody"})[0].text
        page_text = page_text.replace('\n\nQR Code Link to This Post\n\n\n','') # Remove the junk
        page_text = page_text.replace(',','')
        page_text = page_text.replace('\n','')
        date = soup("time", class_="date timeago")[0].text

        for contact_link in soup('a', {'id':'replylink'}):
            contact_link = local_cl_url + contact_link["href"]

        if contact_info:
            contact_email, contact_phone = "N/A", "N/A"
            try:
                contact_email, contact_phone = await get_contact_info(contact_link)

            except Exception:              # Ignore pages we can't get info from.
                print("Could not gather contact information from {}".format(url))
                # print(traceback.format_exc())

        return page_text, date, contact_email, contact_phone

    except Exception:
        print("Could not scrape {}".format(url))
        # print(traceback.format_exc())

async def scrape_search_page(url, local_cl_url, params=None, verbose=False, wanted=False, max_results=120):
    """ Scrape the page of a craigslist search. 

        Returns [ad_title, price, neighborhood,link] or 

        if verbose: 
            [ad_title, price, neighborhood, ad text, link]

        Kwargs:
            params -- params for the http request.
            verbose -- Verbose output, the function will visit every ad and extract the text from within the ad.
            wanted -- Ignore ads with wanted in the title if set to True.
            max_results -- The maximum number of results to keep.
    """
    try:
        response = await fetch(url, params=params)
        soup = bs(response, 'lxml')

    except Exception:
        print("Could not scrape {}".format(url))
        # print(traceback.format_exc())

    results = []

    for ad, counter in zip(soup("p",{"class":"result-info"}), range(max_results)):
        if wanted:              # Ignore wanted ads
            if 'wanted' in ad.text.lower():
                continue

        for price in ad("span",{"class":"result-price"}):                    
            price = price.text
            price = price.strip()
            price = price.replace("(","")
            price = price.replace(")","")
            price = price.replace("$","")
            price = price.replace(',','') 
            price = price.replace('\n','')
            price = float(price)

        for hood in ad("span",{"class":"result-hood"}):                    
            hood = hood.text
            hood = hood.strip()
            hood = hood.replace(",","")
            hood = hood.replace("(","")
            hood = hood.replace(")","")
            hood = hood.replace('\n','')

        for link_text in ad("a",{"class":"result-title hdrlnk"}):
            ad_title = link_text.text
            ad_title = ad_title.strip()
            ad_title = ad_title.replace('\n','')
            ad_title = ad_title.replace(',','')
            ad_url = link_text["href"] 

        for date in ad('time',{"class","result-date"}):                    
            date_updated = parse(date['datetime'])

        if verbose:
            full_url = link_text["href"] # Link text still exists  
            
            try:            
                page_text, date_posted, contact_email, contact_phone = await scrape_ad_page(full_url, local_cl_url)

            except Exception:
                print("Could not extract the data (verbose) for {}".format(url))
                # print(traceback.format_exc())

        local_vars = locals()   # This is used in the list comprehension below to check if certain variables exist. 
        result = [local_vars[ad_data] for ad_data in ["ad_title", "price", "hood", "page_text",
                                                        "contact_email", "contact_phone", "ad_url",
                                                        "date_updated", "date_posted"] if ad_data in local_vars]
        if result != []:
            results.append(result)

    return results


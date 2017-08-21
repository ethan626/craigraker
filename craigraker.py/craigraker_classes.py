#!/bin/python
import requests
from bs4 import BeautifulSoup as bs
import lxml
import argparse
from os.path import expanduser,exists
from termcolor import colored, cprint
import configparser
from math import ceil 

"""

This file is a scaper for craigslist. It searches for a user specified item.

AUTHOR:Ethan Henderson 
https://github.com/ethan626

"""

############ Parsing Arguments ############

parser = argparse.ArgumentParser(description="A craigslist.org scraper. Allows for sorting by location and price as well as specifying how many results you would like.  ",epilog="Author: Ethan Henderson https://github.com/ethan626")

#parser.add_argument("query",help="The search term, if there are spaces this must be surrounded by quotes. Example \"this search has spaces\" ")
parser.add_argument("-q","--query",help="The search term")
parser.add_argument("-p","--price",help="Turn on sort by price",action='store_true')
parser.add_argument("-l","--location",help="Turn on sort by location",action='store_true')
parser.add_argument("-f","--first",help="Search only the first page of craigslist for results", action='store_true')
parser.add_argument("-a","--all",help="Search all pages. If not specified, just the first page of 120 results will be returned",action='store_true')
parser.add_argument("-m","--maxresults",help="The maximum number of results to display")
parser.add_argument("-r","--reverse",help="Reverse order of sorted output",action='store_true')
parser.add_argument("-c","--color",help="Color the output - uses asni colors. ",action='store_true')
parser.add_argument("-w","--where",help="Which Craigslist location to use ")
parser.add_argument("-v","--verbose",help="Verbose output. Craigraker will go into each ad and retrieve the text from within the posting.",action='store_true')
args = parser.parse_args()

############### Config ####################

config = configparser.ConfigParser()

# if path does not exist, create the config file in the home directory
if not exists(expanduser('~/.craigrakerrc')):
    
    config['DEFAULT'] = {'city':'seattle'}
    
    with open(expanduser('~/.craigrakerrc'),'w+') as configfile:        
        config.write(configfile)
        
config.read(expanduser('~/.craigrakerrc')) # Read in config values 

##### Location Preprocessing #######
  
if args.where:
    city = args.where
else:    
    city = config['DEFAULT']['city']

class CraigScraper:
    ""
    
    def __init__(self):
        ""
        self.parameters = {"sort":"rel","query":args.query,"s":0}
        self.local_cl_url =  "".join(["https://",city,".craigslist.org/"])
        self.local_cl_search_url = "".join(["https://",city,".craigslist.org/search"])
        self.resp = requests.get(self.local_cl_search_url,params=self.parameters)
        self.soup = bs(self.resp.content,"lxml")
        self.max_results = 120        
        
    def open_ad_page(self,url):
        """ Returns the text from a cl-ad page"""
        response = requests.get(url)
        page_content = response.content
        local_soup = bs(page_content,"lxml")

        return local_soup("section",{"id":"postingbody"})[0].text #Only need the first bit of text

    def load_next_search_page(self):
        "Loads the page of the search"
        self.parameters["s"] += 120
        new_page_response = requests.get(self.local_cl_search_url,parameters)
        new_page_content = new_page_response.content
        self.soup(new_page_content,"lxml")       

    def scrape_search_page(self,soup,verbose=False,color=False): # split this up into two functions so that open_ad_page is not called for everypage regardless of max number of results

        """ Main driver for scraping. Pending awesome documentation!

        Yields tuples of the cl ads title, price, neighborhood, and the link.
        This function extracts this data from the bs4 object passed in as an argument """

        for link in self.soup.find_all("p",{"class":"result-info"}):        
            if "wanted" in link.text.lower(): # Ignore wanted ads
                continue

            for price in link.find_all("span",{"class":"result-price"}):
                for hood in link.find_all("span",{"class":"result-hood"}):
                    for link_text in link.find_all("a",{"class":"result-title hdrlnk"}):

                        hood = hood.text
                        hood = hood.replace("(","")
                        hood = hood.replace(")","")
                        hood = hood.strip()

                        price = price.text
                        price = price.replace("(","")
                        price = price.replace(")","")
                        price = price.replace("$","")                    
                        price = price.strip()

                        urllink = link_text['href']
                        full_url = "".join([self.local_cl_url, urllink])
                        ad_title = link_text.text

                        if color: # color the output if arg flag is set
                            ad_title = colored(ad_title,'white')
                            hood = colored(hood,'yellow')
                            price = colored(price,"red")

                            if verbose:
                                page_text = self.open_ad_page(full_url)
                                yield(ad_title, price, hood, page_text,full_url)

                            else:
                                yield(ad_title, price, hood, full_url)


                        else:       # If color flag is not set

                            if verbose:

                                page_text = self.open_ad_page(full_url)
                                print(page_text)

                                yield(ad_title,price,hood,page_text,full_url)

                            else:
                                yield(ad_title,price,hood,full_url)
    def scrape(self, max_results=120, color=False, verbose=False):
        ""
        results = self.scrape_search_page(self.soup, color=color, verbose=verbose)
        for result,counter in zip(results,range(1,max_results+1)):
            
            if counter > 0 and counter % 120 == 0: # 120 results per page, so after 120 results load the next page and update the soup object
                self.load_next_search_page()
                
            yield result 

s=CraigScraper()

########### Main Program Logic ################                        
# if __name__ == '__main__':

#     # if args.query:        
#     # results = [i for i in scrape_search_page(soup,verbose=args.verbose,color=args.color)]

#     if args.first:
#         max_results = 120

#     if args.all:
#         max_results = num_of_results

#     if args.maxresults:
#         max_results = int(args.maxresults)
        
#     pages = scrape_search_page(soup,verbose=args.verbose,color=args.color)
#     results = [page for page,counter in zip(pages,range(max_results))]

#     pages_to_scrape = ceil(num_of_results/120)

       
#     # multi page generator
            
    
#     # [pages.__next__() for i in range(max_results)] 
#     # results = []
#     # while parameters["s"] < max_results:
#     #     parameters["s"] += 1
#     #     pages = scrape_search_page(soup,verbose=args.verbose,color=args.color) 
           
#     #     results.append(pages.__next__())

#     #     if parameters["s"] % 120 == 0: # at the end of the search page
#     #         resp = requests.get(local_cl_search_url,params=parameters)
#     #         soup = bs(resp.content,"lxml")
#     #         results = scrape_search_page(soup,verbose=args.verbose,color=args.color)                

#     if args.price:
#         results.sort(key=lambda x: x[1],reverse=args.reverse)

#         # if args.location:
#         #     results.sort(key=lambda x: x[2].strip())
#             # results = results[:max_results]

#     # if args.location and not args.maxresults and not args.all:
#     if args.location:
#         results.sort(key=lambda x: x[2].strip(),reverse=args.reverse)

# ##### Printing the results to the console #####
# if 'results' not in globals():
#     raise Exception("I have no results. Maybe you forgot to enter a search query") # results will not be created unless there is a search query 

# for result in results:        
#     print("{0}, {1}, {2} ".format(*result))

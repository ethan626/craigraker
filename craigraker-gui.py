#!/bin/python
import argparse
import configparser
from gooey import Gooey
from craigraker_functions import *

"""

Craigraker! A really cool Craigslist scraper! GUI Version!

This file is the file to be called to run the script. Make sure craigraker_functions.py is in the same directory. 

Craigraker reads from the config file ~/.craigrakerrc which is where craigraker gets location data. 

Craigraker is able to produce highlighted output for readability, as well as sort listings by price, location (alphabetically), or date posted.

Output is formatted so that it can be written to a csv for spreadsheet use.

AUTHOR:Ethan Henderson 
https://github.com/ethan626

"""

LOOP = asyncio.get_event_loop()

@Gooey
def main():
    """ Call this to start scraping """
    parser = argparse.ArgumentParser()
    parser.add_argument("-q","--query", help="The search term, if there are spaces this must be surrounded by quotes or escaped with \. Example \"this search has spaces\" ")
    parser.add_argument("-F","--file", help="The file to which Craigraker will write the output. If the file exists, Craigraker will append to the end of the file.")
    parser.add_argument("-f","--firstpage", help="Only scrape the first page of the search results", action='store_true')
    parser.add_argument("-P","--sortpricemax", help="Turn on sort by price with the maximum price first", action='store_true')
    parser.add_argument("-p","--sortpricemin", help="Turn on sort by price with the minimum price first", action='store_true')
    parser.add_argument("-l","--sortlocation", help="Turn on sort by location", action='store_true')
    parser.add_argument("-d","--sortpast", help="Sort by date posted with the most recent last", action='store_true')
    parser.add_argument("-D","--sortrecent", help="Sort by date posted with the most recent first", action='store_true')
    parser.add_argument("-a","--allresults", help="Search all pages. If not specified, just the first page of 120 results will be returned",
                        action='store_true')
    parser.add_argument("-m","--maxresults", help="The maximum number of results to display")
    parser.add_argument("-w","--where", help="Which Craigslist location to use.")
    parser.add_argument("-W","--sublocation", help="Which sublocation to use")
    parser.add_argument("-v","--verbose", help="Verbose output. Craigraker will go into each ad and retrieve the text from within the posting. The date returned will be the date the ad was posted",
                        action='store_true')

    parser.add_argument("-i","--ignorewanted",help="Ignore ads with \"wanted\" in the title.", action='store_true')
    parser.add_argument("-s","--section",help="Which section to search in, for example \"for sale\" or \"personals\"")
    args = parser.parse_args()

    """ Location specific configuration """ 

    config = configparser.ConfigParser()

    if not exists(expanduser('~/.craigrakerrc')): # if path does not exist, create the config file in the home directory
        config['DEFAULT'] = {'city':'seattle'}

        with open(expanduser('~/.craigrakerrc'),'w+') as configfile:        
            config.write(configfile)

    config.read(expanduser('~/.craigrakerrc')) # Read in config values 

    """ Location Preprocessing """
    if args.where:
        city = args.where
    else:    
        city = config['DEFAULT']['city']

    local_cl_url =  "".join(["https://",city, ".craigslist.org"])
    search_url = "".join(["https://", city, ".craigslist.org/search/"])    

    """ Main Program Logic """
    max_results = 2500
                                       
    if args.firstpage:           
        max_results = 120
        
    if args.maxresults:         # Max number of results the user wishes to have as output
        max_results = int(args.maxresults)
        
        if max_results > 2500:
            max_results = 2500

    if args.sublocation:
        search_url += args.sublocation + '/'

    if args.section:
        search_url = ''.join([search_url, parse_section(args.section),"?"])

    if not args.section:        # Default to for sale
        search_url = ''.join([search_url, "sss/","?"])

     """ This is where we scrape CL """ 

    results = [result for result in scrape(search_url, local_cl_url, args.query, max_results=max_results, verbose=args.verbose, wanted=args.ignorewanted)]

    if args.sortlocation:
        results.sort(key=lambda x: x[2])

    if args.sortpricemin:
        results.sort(key=lambda x: x[1])
        
    if args.sortpricemax:
        results.sort(key=lambda x: x[1], reverse=True)

    if args.sortpast:
        results.sort(key=lambda x: x[-1])
        
    if args.sortrecent:
        results.sort(key=lambda x: x[-1], reverse=True)

    print('Title, Price, Location, Posting Information, Email, Phone, Url, Updated, Posted') # Headers for csv columns

    for result in results:
        result

    if args.file:
        with open(args.file, 'a+') as f:
            for result in results:
                f.write(', '.join([str(r) for r in result]))
                f.write('\n')
        
    LOOP.close()

if __name__ == "__main__":
    main()

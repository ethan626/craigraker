#!/bin/python
import argparse
import configparser
from gooey import Gooey, GooeyParser
from craigraker_functions import *

"""

Craigraker! A really cool Craigslist scraper! GUI Version!

This file is the file to be called to run the script. Make sure craigraker_functions.py is in the same directory. 

Craigraker reads from the config file ~/.craigrakerrc which is where craigraker gets location data. 

Output is formatted so that it can be written to a csv for spreadsheet use.

Author: Ethan Henderson 
https://github.com/ethan626

"""

LOOP = asyncio.get_event_loop()

@Gooey
def main():
    """ Call this to start scraping """
    parser = GooeyParser(description="Craigraker")
    parser.add_argument("-Query", help="The search term, if there are spaces this must be surrounded by quotes or escaped with \. Example \"this search has spaces\" ")
    parser.add_argument("-File", help="The file to which Craigraker will write the output. If the file exists, Craigraker will append to the end of the file.")
    parser.add_argument("-Scrape Only the First Page", help="Only scrape the first page of the search results", action="store_true")
    # parser.add_argument("Sort", help="Choose a sorting function", widget="Listbox")
    parser.add_argument("-Sort by Price, Decending", help="Turn on sort by price with the maximum price first", action="store_true")
    parser.add_argument("-Sort by Price, Ascening", help="Turn on sort by price with the minimum price first", action="store_true")
    parser.add_argument("-Sort by Location, Alphabetically", help="Turn on sort by location", action="store_true")
    parser.add_argument("-Sort by Date Posted, Ascending", help="Sort by date posted with the most recent last", action="store_true")
    parser.add_argument("-Sort by Date, Descending", help="Sort by date posted with the most recent first", action="store_true")
    parser.add_argument("-Do Not Sort", help="Do not sort. Overrides local config.", action="store_true")
    parser.add_argument("-Search all Pages", help="Search all pages. If not specified, just the first page of 120 results will be returned",
                        action="store_true")
    parser.add_argument("-Maximum Number of Results", help="The maximum number of results to display")
    parser.add_argument("-Location", help="Which Craigslist location to use. Example: Seattle")
    parser.add_argument("-Sublocation", help="""Which sublocation to use.
                                                You may have to refer to Craigslist to find your specific sublocation. 
                                                If not provided Craigraker will read from the default config, 
                                                or search based on the location. Example: Tac""")
    parser.add_argument("-Get Full Ad", help="Get the text of the Craigslist ad, not just the title.", action="store_true")
    parser.add_argument("-Ignore Wanted Ads", help="Ignore ads with \"wanted\" in the title.", action="store_true")
    parser.add_argument("-Section", help="Which section to search in, for example \"for sale\" or \"personals\"")
    args = parser.parse_args()
    
    """ Loading/Creating the users config file. """

    config = configparser.ConfigParser()

    if not exists(expanduser("~/.craigrakerrc")): # if path does not exist, create the config file in the home directory
        config["DEFAULT"] = {"city":"seattle", "sublocation":"", "section": "", "maxresults": 2500, "firstpage": False, "sort": False}

        with open(expanduser("~/.craigrakerrc"),"w+") as configfile:        
            config.write(configfile)

    config.read(expanduser("~/.craigrakerrc")) # Read in config values 

    """ Fill in the values from the users config and/or command line arguments. """
    if args.where:
        city = args.where

    if not args.where:
        city = config["DEFAULT"]["city"]

    if args.sublocation:
        sublocation = args.sublocation

    if not args.sublocation:
        sublocation = config["DEFAULT"]["sublocation"]

    if args.section:
        section = args.section

    if not args.section:        # Default to for sale
        section = "sss?"

    local_cl_url = "https://" + city + ".craigslist.org" + sublocation
    search_url = "https://" + city + ".craigslist.org/search/" + sublocation + "/" + section

    if args.maxresults:
        max_results = int(args.maxresults)
        if max_results > 2500:
            max_results = 2500

    if not args.maxresults:
        max_results = 2500

    if args.firstpage:           
        max_results = 120

    if args.sortlocation:
        sort = {"key": lambda x: x[2]}

    if args.sortpricemin:
        sort = {"key": lambda x: x[1]}
        
    if args.sortpricemax:
        sort = {"key": lambda x: x[1], "reverse": True}

    if args.sortpast:
        sort = {"key": lambda x: x[-1]}
    
    if args.sortrecent:
        sort = {"key": lambda x: x[-1], "reverse": True}

    if args.donotsort:
        sort = dict()
        
    if args.donotsort:
        sort = False

    if not args.sortlocation and not args.sortpricemin and not args.sortpricemax and not args.sortpast and not args.sortrecent and not args.donotsort:
       if config["DEFAULT"]["sort"].lower() == "false":
           sort = False
       else:
           try:
                sort = exec(config["DEFAULT"]["sort"])

           except Exception:
               print("Sort found in config file is not valid. ")
               sort = False

    """ This is where we scrape CL """ 
    results = [result for result in scrape(search_url,
                                           local_cl_url,
                                           args.query,
                                           max_results=max_results,
                                           verbose=args.verbose,
                                           wanted=args.ignorewanted)]

    if sort:
        results.sort(**sort)

    if not args.quiet and len(results) > 0: 
        print_result(['Title', 'Price', 'Location', 'Posting Information',
                      'Email', 'Phone', 'Url', 'Updated', 'Posted'], color=args.color) # Headers for csv columns

        for result in results:
            print_result(result, color=args.color)

    if args.file:                
        with open(args.file, 'a+') as f:
            for result in results:
                f.write(result)
                f.write('\n')

    LOOP.close()

if __name__ == "__main__":
    main()

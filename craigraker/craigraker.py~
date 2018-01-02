#!/bin/python
import argparse
import configparser
import traceback
from os.path import expanduser, exists
from craigraker_functions import *
from os import _exit

"""

Craigraker! A really cool Craigslist scraper!

This file is the file to be called to run the script. Make sure craigraker_functions.py is in the same directory. 

Craigraker reads from the config file ~/.craigrakerrc which is where craigraker gets location data unless supplied as command line args. 

Craigraker is able to produce highlighted output for readability, as well as sort listings by price, location (alphabetically), or date posted.

Output is formatted so that it can be written to a csv for spreadsheet use.

AUTHOR:Ethan Henderson 
https://github.com/ethan626

"""

LOOP = asyncio.get_event_loop()  

def main():
    """ Call this to start Craigraker """
    parser = argparse.ArgumentParser()
    parser.add_argument("-q","--query", help="The search term, if there are spaces this must be surrounded \
                                              by quotes or escaped with \. Example \"this search has spaces\" ")
    parser.add_argument("-Q","--quiet", help="Do not print output", action="store_true")
    parser.add_argument("-F","--file", help="The file to which Craigraker will write the output. \
                                             If the file exists Craigraker will append to the end of the file")
    parser.add_argument("-f","--firstpage", help="Only scrape the first page of the search results", action="store_true")
    parser.add_argument("-P","--sortpricemax", help="Turn on sort by price with the maximum price first", action="store_true")
    parser.add_argument("-p","--sortpricemin", help="Turn on sort by price with the minimum price first", action="store_true")
    parser.add_argument("-l","--sortlocation", help="Turn on sort by location", action="store_true")
    parser.add_argument("-d","--sortpast", help="Sort by date posted with the most recent last", action="store_true")
    parser.add_argument("-S", "--donotsort", help="Do not sort. Overrides local config.", action="store_true")
    parser.add_argument("-D","--sortrecent", help="Sort by date posted with the most recent first", action="store_true")
    parser.add_argument("-a","--allresults", help="Search all pages. \
                                                   If not specified, just the first page of 120 results will be returned", action="store_true")
    parser.add_argument("-m","--maxresults", help="The maximum number of results to display")
    parser.add_argument("-c","--color", help="Color the output - uses ansi colors. ", action="store_true")
    parser.add_argument("-w","--where", help="Which Craigslist location to use.")
    parser.add_argument("-W","--sublocation", help="Which sublocation to use")
    parser.add_argument("-v","--verbose", help="""Verbose output. Craigraker will go into each ad \
                                                  and retrieve the text from within the posting.
                                                  The date returned will be the date the ad was posted""",
                                                action="store_true")
    parser.add_argument("-i","--ignorewanted",help="Ignore ads with \"wanted\" in the title.", action="store_true")
    parser.add_argument("-s","--section",help="Which section to search in, for example \"forsale\" or \"personals\"")
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

    """ This section is where we scrape CL """
    try:
        results = [result for result in scrape(search_url,
                                               local_cl_url,
                                               args.query,
                                               max_results=max_results,
                                               verbose=args.verbose,
                                               wanted=args.ignorewanted)]

    except TypeError as e:      # Most likely caused by results being None and thus not iterable. No results will be printed later in the script
        # print(traceback.format_exc()) 
        results = [] # No results. Variable name is referenced later so we need results in scope 

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
        
    LOOP.close()                # Close asyncio event 

if __name__ == "__main__":
    main()

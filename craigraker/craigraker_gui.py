#!/bin/python
import asyncio
import configparser
from gooey import Gooey, GooeyParser
from os.path import expanduser, exists
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
    parser.add_argument("-Query", help="The search term")
    parser.add_argument("-File", help="The file to which Craigraker will write/append the output.")
    parser.add_argument("-Sort", choices=["Do Not Sort", "Price Descending", "Price Ascending", "Location", "Date Descending", "Date Ascending"],
                                            help="Click the dropdown menu to select a sorting method or not to sort.")
    parser.add_argument("-Results", type=int, help="The maximum number of results to display")
    parser.add_argument("-Location", help="Which Craigslist location to use. Example: Seattle")
    parser.add_argument("-Sublocation", help="""Which sublocation to use.
                                                You may have to refer to Craigslist to find your specific sublocation.
                                                If not provided Craigraker will read from the default config,
                                                or search based on the location. Example: Tac""")
    parser.add_argument("-Verbose", help="Get the text of the Craigslist ad, not just the title.", action="store_true")
    parser.add_argument("-Section", help="Default is \"For Sale\".")
    args = parser.parse_args()

    """ Loading/Creating the users config file. """

    config = configparser.ConfigParser()

    if not exists(expanduser("~/.craigrakerrc")):  # if path does not exist, create the config file in the home directory
        config["DEFAULT"] = {"city": "seattle", "sublocation": "", "section": "", "maxresults": 2500, "firstpage": False, "sort": False}

        with open(expanduser("~/.craigrakerrc"), "w+") as configfile:
            config.write(configfile)

    config.read(expanduser("~/.craigrakerrc")) # Read in config values

    """ Fill in the values from the users config and/or command line arguments. """
    if args.Location:
        city = args.Location.lower()

    if not args.Location:
        city = config["DEFAULT"]["city"].lower()

    if args.Sublocation:
        sublocation = args.Sublocation.lower()

    if not args.Sublocation:
        sublocation = config["DEFAULT"]["sublocation"].lower()

    if args.Section:
        section = args.Section.lower()

    if not args.Section:        # Default to for sale
        section = "sss?"

    local_cl_url = "https://" + city + ".craigslist.org" + sublocation

    if sublocation:
        search_url = "https://" + city + ".craigslist.org/search/" + sublocation + "/" + section

    else:
        search_url = "https://" + city + ".craigslist.org/search/" + section

    if args.Results:
        max_results = args.Results
        if max_results > 2500:
            max_results = 2500

    if not args.Results:
        max_results = 2500

    if args.Sort == "Location":
        sort = {"key": lambda x: x[2]}

    if args.Sort == "Price Descending":
        sort = {"key": lambda x: x[1]}

    if args.Sort == "Price Ascending":
        sort = {"key": lambda x: x[1], "reverse": True}

    if args.Sort == "Date Ascending":
        sort = {"key": lambda x: x[-1]}

    if args.Sort == "Date Descending":
        sort = {"key": lambda x: x[-1], "reverse": True}

    if args.Sort == "Do Not Sort":
        sort = False

    if not args.Sort:
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
                                           args.Query,
                                           max_results=max_results,
                                           verbose=args.Verbose,
                                           wanted=False)]

    if sort:
        results.sort(**sort)

    if len(results) > 0:
        print(print_result(["Title", "Price", "Location", "Posting Information",
                            "Email", "Phone", "Url", "Updated", "Posted"]))  # Headers for csv columns

        for result in results:
            print(print_result(result))
            print()

    if args.File:
        with open(args.File, "a+") as f:
            for result in results:
                f.write(print_result(result))
                f.write("\n")

    LOOP.close()


if __name__ == "__main__":
    main()

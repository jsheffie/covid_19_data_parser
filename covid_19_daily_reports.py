#!/usr/bin/env python3

import os
import sys

# look for libraries that are configured by './build.sh'
cwd = os.getcwd()

# Add `/lib` to the path to pick up our pip installed 3rd party requirements
sys.path[0:0] = ["{}/lib".format(cwd)]

# Add '/huvr_api_client' to the path to make this runnable out of the source tree
sys.path[0:0] = ["{}/covid_19_data_parser".format(cwd)]

from covid_19_data_parser import Client, DailyReportsParser

if __name__ == '__main__':
    """
    so here we want to agressivly cache the data ( since it wont change after a file has been fetched )
    """
    base_url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports" # 03-27-2020.csv
    daily_data_dir = 'daily_data'

    daily_parser = DailyReportsParser()

    # TODO: make this fancy with datetime, and calendar later.. or not
    date_range = [ 
                   # "03-01-2020", 
                   # "03-02-2020",
                   # "03-03-2020",
                   # "03-04-2020",
                   # "03-05-2020",
                   # "03-06-2020",
                   # "03-07-2020",
                   # "03-08-2020",
                   # "03-09-2020",
                   # "03-10-2020",
                   # "03-11-2020",
                   # "03-12-2020",
                   # "03-13-2020",
                   # "03-14-2020",
                   # "03-15-2020",
                   # "03-16-2020",
                   # "03-17-2020",
                   # "03-18-2020",
                   # "03-19-2020",
                   # "03-20-2020",
                   # "03-21-2020",
                   "03-22-2020",  # New Data Format ( more detailed data )
                   "03-23-2020",
                   "03-24-2020",
                   "03-25-2020",
                   "03-26-2020",
                   "03-27-2020",
                   "03-28-2020"]
                   # "03-29-2020",
                   # "03-30-2020",
                   # "03-31-2020" ]

    # Download the data
    for date_str in date_range:
        filename = "{}/{}.csv".format(daily_data_dir, date_str)
        download_url = "{}/{}.csv".format(base_url, date_str)
        daily_parser.set_cachefile(filename)
        if not daily_parser.cached_csv():
            print("Fetching csv file from {}".format(filename))
            client = Client()
            ( res_code, data ) = client.get(download_url)
            if res_code == 200:
                print("Successfully Downloaded data {}".format(len(data)))
                res = daily_parser.write_csv_file(filename, data)
                if res:
                    print("Successfully Wrote datafile {}".format(filename))
            else:
                print("ERROR: {}".format(res_code))
                print(data)

    # Up to 3/21/2020 the format was this
    # Province/State,Country/Region,Last Update,Confirmed,Deaths,Recovered,Latitude,Longitude
    # on 3/22 it change to this
    # FIPS,Admin2,Province_State,Country_Region,Last_Update,Lat,Long_,Confirmed,Deaths,Recovered,Active,Combined_Key
    # 48453,Travis,Texas,US
    # 48491,Williamson,Texas,US
    # needle_array = 
    needle_arrays = [['48453', 'Travis', 'Texas', 'US'],
                     ['48491', 'Williamson', 'Texas', 'US'],
                     ['48113', 'Dallas', 'Texas', 'US'],
                     ['36059', 'Nassau', 'New York', 'US'],
                     ['36103', 'Suffolk', 'New York', 'US'],
                     ['36061', 'New York City', 'New York', 'US'],
                     ['22071', 'Orleans', 'Louisiana', 'US']
                     ]
    for needle_array in needle_arrays:
        daily_parser = DailyReportsParser()
        # loop thought them again, this time calcaliting the data
                            # FIPS  Admin2    State   Country
        for date_str in date_range:
            filename = "{}/{}.csv".format(daily_data_dir, date_str)
            daily_parser.parse(date_str, needle_array, filename )

        daily_parser.remove_csv_file(needle_array)
        daily_parser.write_csv(needle_array)

    # import json
    # print(json.dumps(daily_parser.parsed_lines, indent=4))

#!/usr/bin/env python3

import os
import sys

# look for libraries that are configured by './build.sh'
cwd = os.getcwd()

# Add `/lib` to the path to pick up our pip installed 3rd party requirements
sys.path[0:0] = ["{}/lib".format(cwd)]

# Add '/huvr_api_client' to the path to make this runnable out of the source tree
sys.path[0:0] = ["{}/covid_19_data_parser".format(cwd)]

from covid_19_data_parser import DailyReportsParser

if __name__ == '__main__':
    base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports"  # 03-27-2020.csv
    daily_data_dir = 'daily_data'

    daily_parser = DailyReportsParser()

    # TODO: make this fancy with datetime, and calendar later.. or not
    date_range = ["03-22-2020",  # New Data Format ( more detailed data )
                  "03-23-2020",
                  "03-24-2020",
                  "03-25-2020",
                  "03-26-2020",
                  "03-27-2020",
                  "03-28-2020",
                  "03-29-2020",
                  "03-30-2020",
                  "03-31-2020",
                  "04-01-2020"]

    for date_str in date_range:
        filename = "{}/{}.csv".format(daily_data_dir, date_str)
        download_url = "{}/{}.csv".format(base_url, date_str)
        daily_parser.get_data(download_url, filename)

    # The data formats are covered in this issue ( format changed on 03/21/2020 )
    # https://github.com/jsheffie/covid_19_data_parser/issues/1
    needle_arrays = [['48453', 'Travis', 'Texas', 'US'],
                     ['48491', 'Williamson', 'Texas', 'US'],
                     ['48201', 'Harris', 'Texas', 'US'],
                     ['48113', 'Dallas', 'Texas', 'US'],
                     ['36059', 'Nassau', 'New York', 'US'],
                     ['36103', 'Suffolk', 'New York', 'US'],
                     ['36061', 'New York City', 'New York', 'US'],
                     ['22071', 'Orleans', 'Louisiana', 'US']
                     ]
    for needle_array in needle_arrays:
        daily_parser = DailyReportsParser()
        for date_str in date_range:
            filename = "{}/{}.csv".format(daily_data_dir, date_str)
            daily_parser.parse(date_str, needle_array, filename)

        daily_parser.remove_csv_file(needle_array)
        daily_parser.write_csv(needle_array)

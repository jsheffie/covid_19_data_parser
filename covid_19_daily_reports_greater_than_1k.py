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
        if date_str == date_range[-1]:
            # grab the latest day, and build up a needle array of any cases of more than 1k 'Confirmed'
            needle_arrays = daily_parser.build_needle_array(Country_Region='US', column='Confirmed', high_watermark=1000)

    for needle_array in needle_arrays:
        daily_parser = DailyReportsParser()
        for date_str in date_range:
            filename = "{}/{}.csv".format(daily_data_dir, date_str)
            daily_parser.parse(date_str, needle_array, filename)

        daily_parser.remove_csv_file(needle_array)
        daily_parser.write_csv(needle_array)

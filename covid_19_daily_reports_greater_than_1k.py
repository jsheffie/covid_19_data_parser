#!/usr/bin/env python3

import os
import sys
from datetime import date, timedelta

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

    start_date = date(2020,3,22) # This is the day that the 'New Data Format' started for more detailed data.
    todays_date = date.today()
    delta = todays_date - start_date
    date_range = []
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        date_range.append("{:02d}-{:02d}-{:4d}".format(day.month, day.day, day.year))

    # TODO: re-work a bit for genericy ( currently expect the last file downloaded to be the one ... does not handle no-downloaded file)
    for date_str in date_range:
        filename = "{}/{}.csv".format(daily_data_dir, date_str)
        download_url = "{}/{}.csv".format(base_url, date_str)
        res_code = daily_parser.get_data(download_url, filename)
        # if res_code == 200:
        if date_str == date_range[-1]:
          # grab the latest day, and build up a needle array of any cases of more than 1k 'Confirmed'
          needle_arrays = daily_parser.build_needle_array(Country_Region='US', column='Confirmed', high_watermark=1000)

    if not ['48453', 'Travis', 'Texas', 'US'] in needle_arrays:
      needle_arrays.append(['48453', 'Travis', 'Texas', 'US'])
    if not ['48491', 'Williamson', 'Texas', 'US'] in needle_arrays:
      needle_arrays.append(['48491', 'Williamson', 'Texas', 'US'])

    for needle_array in needle_arrays:
        daily_parser = DailyReportsParser()
        for date_str in date_range:
            filename = "{}/{}.csv".format(daily_data_dir, date_str)
            daily_parser.parse(date_str, needle_array, filename)

        daily_parser.remove_csv_file(needle_array)
        daily_parser.write_csv(needle_array)

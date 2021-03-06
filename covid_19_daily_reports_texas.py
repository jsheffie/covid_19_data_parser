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

    daily_parser = DailyReportsParser(verbose=True)

    start_date = date(2020,3,22) # This is the day that the 'New Data Format' started for more detailed data.
    todays_date = date.today()
    # todays_date = date(2020,4,6)
    delta = todays_date - start_date
    date_range = []
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        date_range.append("{:02d}-{:02d}-{:4d}".format(day.month, day.day, day.year))

    downloaded_date_range = []
    for date_str in date_range:
        filename = "{}/{}.csv".format(daily_data_dir, date_str)
        download_url = "{}/{}.csv".format(base_url, date_str)
        res_code = daily_parser.get_data(download_url, filename)
        if int(res_code) < 300:
            downloaded_date_range.append(date_str)

    # print(downloaded_date_range)
    # sys.exit(0)

    # grab the latest day, and build up a needle array of any cases of more than 1k 'Confirmed'
    needle_arrays = daily_parser.build_needle_array(Country_Region='US', column='Confirmed', high_watermark=100, Province_State='Texas')


    cumlutive_data_confirmed_just_texas = ['name,'+','.join(downloaded_date_range)]


    for needle_array in needle_arrays:
        daily_parser = DailyReportsParser()
        for date_str in downloaded_date_range:
            filename = "{}/{}.csv".format(daily_data_dir, date_str)
            daily_parser.parse(date_str, needle_array, filename)

        daily_parser.remove_csv_file(needle_array)
        daily_parser.write_csv(needle_array)

        new_line=needle_array[1]+" "+needle_array[2]+","+",".join([i.split(",")[1] for i in daily_parser.parsed_lines[1:]])  # so much magic ( this is confirmed cases )

        if 'texas' in needle_array[2].lower():
            cumlutive_data_confirmed_just_texas.append(new_line)

    covid_csv_file = "{}/observablehq_covid_19_confirmed_all_texas.csv".format(daily_parser.data_directory)
    daily_parser.update_csv_file(covid_csv_file, cumlutive_data_confirmed_just_texas)


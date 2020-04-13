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
    needle_arrays = daily_parser.build_needle_array(Country_Region='US', column='Confirmed', high_watermark=1000)

    if not ['48453', 'Travis', 'Texas', 'US'] in needle_arrays:
      needle_arrays.append(['48453', 'Travis', 'Texas', 'US'])
    if not ['48491', 'Williamson', 'Texas', 'US'] in needle_arrays:
      needle_arrays.append(['48491', 'Williamson', 'Texas', 'US'])
    if not ['25015', 'Hampshire', 'Massachusetts', 'US'] in needle_arrays:
      needle_arrays.append(['25015', 'Hampshire', 'Massachusetts', 'US'])

    cumlutive_data_confirmed = ['name,'+','.join(downloaded_date_range)]
    cumlutive_data_confirmed_no_ny = ['name,'+','.join(downloaded_date_range)]
    cumlutive_data_new_cases = ['name,'+','.join(downloaded_date_range)]
    cumlutive_data_new_cases_no_ny = ['name,'+','.join(downloaded_date_range)]

    # Well crap the death's and recoverd data is not in the daily data ~~ sigh ~~
    # cumlutive_data_combined = ['name,'+','.join(downloaded_date_range)]  # confirmed - (deaths + recovered )
    cumlutive_data_deaths = ['name,'+','.join(downloaded_date_range)]
    cumlutive_data_deaths_no_ny = ['name,'+','.join(downloaded_date_range)]

    for needle_array in needle_arrays:
        daily_parser = DailyReportsParser()
        for date_str in downloaded_date_range:
            filename = "{}/{}.csv".format(daily_data_dir, date_str)
            daily_parser.parse(date_str, needle_array, filename)

        daily_parser.remove_csv_file(needle_array)
        daily_parser.write_csv(needle_array)

        new_line=needle_array[1]+" "+needle_array[2]+","+",".join([i.split(",")[1] for i in daily_parser.parsed_lines[1:]])  # so much magic ( this is confirmed cases )
        new_line_nc=needle_array[1]+" "+needle_array[2]+","+",".join([i.split(",")[5] for i in daily_parser.parsed_lines[1:]])  # so much magic ( this is new cases i.e. +increase )
        # new_line_combined=needle_array[1]+" "+needle_array[2]+","+",".join([str(int(i.split(",")[1]) - (int(i.split(",")[2])+ int(i.split(",")[3]))) for i in daily_parser.parsed_lines[1:]])  # so much magic (  )
        new_line_deaths=needle_array[1]+" "+needle_array[2]+","+",".join([i.split(",")[2] for i in daily_parser.parsed_lines[1:]])  # so much magic (  )
        cumlutive_data_confirmed.append(new_line)
        cumlutive_data_new_cases.append(new_line_nc)
        # cumlutive_data_combined.append(new_line_combined)
        cumlutive_data_deaths.append(new_line_deaths)

        if 'new york' not in needle_array[2].lower():
            cumlutive_data_confirmed_no_ny.append(new_line)
            cumlutive_data_new_cases_no_ny.append(new_line_nc)
            cumlutive_data_deaths_no_ny.append(new_line_deaths)

    covid_csv_file = "{}/observablehq_covid_19_confirmed.csv".format(daily_parser.data_directory)
    daily_parser.update_csv_file(covid_csv_file, cumlutive_data_confirmed)

    covid_csv_file = "{}/observablehq_covid_19_confirmed_no_ny.csv".format(daily_parser.data_directory)
    daily_parser.update_csv_file(covid_csv_file, cumlutive_data_confirmed_no_ny)

    covid_csv_file = "{}/observablehq_covid_19_new_cases.csv".format(daily_parser.data_directory)
    daily_parser.update_csv_file(covid_csv_file, cumlutive_data_new_cases)

    covid_csv_file = "{}/observablehq_covid_19_new_cases_no_new_york.csv".format(daily_parser.data_directory)
    daily_parser.update_csv_file(covid_csv_file, cumlutive_data_new_cases_no_ny)

    # covid_csv_file = "{}/observablehq_covid_19_confirmed-deaths_plus_recovered.csv".format(daily_parser.data_directory)
    # daily_parser.update_csv_file(covid_csv_file, cumlutive_data_combined)

    covid_csv_file = "{}/observablehq_covid_19_deaths.csv".format(daily_parser.data_directory)
    daily_parser.update_csv_file(covid_csv_file, cumlutive_data_deaths)

    covid_csv_file = "{}/observablehq_covid_19_deaths_no_ny.csv".format(daily_parser.data_directory)
    daily_parser.update_csv_file(covid_csv_file, cumlutive_data_deaths_no_ny)

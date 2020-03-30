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

    date_range = ["03-26-2020"]

    for date_str in date_range:
        filename = "{}/{}.csv".format(daily_data_dir, date_str)
        download_url = "{}/{}.csv".format(base_url, date_str)
        daily_parser.get_data(download_url, filename)
        if date_str == date_range[-1]:
            # grab the latest day, and build up a needle array of any cases of more than 1k 'Confirmed'
            # needle_arrays = daily_parser.build_needle_array(Country_Region='US', column='Confirmed', high_watermark=1, Province_State='New York')
            needle_arrays = daily_parser.build_needle_array(Country_Region='US', column='Confirmed', high_watermark=1)

    counts = []
    for needle_array in needle_arrays:
        daily_parser = DailyReportsParser()
        for date_str in date_range:
            filename = "{}/{}.csv".format(daily_data_dir, date_str)
            daily_parser.parse_lat_long_counts(date_str, needle_array, filename)

        # import json
        # print(json.dumps(daily_parser.parsed_lat_lng_lines, indent=4))
        for lat_lng in daily_parser.parsed_lat_lng_lines.keys():
            # {location: new google.maps.LatLng(37.782, -122.447), weight: 0.5},
            elem = daily_parser.parsed_lat_lng_lines[lat_lng]
            counts.append(int(elem['count']))
            if int(elem['count']) > 1:
                print("{" + "location: new google.maps.LatLng({}, {}), weight: {}".format(elem['lat'], elem['lng'], elem['count']) + "},", end='')
            else:
                print("new google.maps.LatLng({},{}),".format(elem['lat'], elem['lng']), end='');
          # if False:
          #   if int(elem['count']) > 300:
          #     for i in range(0, 300):
          #       print("new google.maps.LatLng({},{}),".format(elem['lat'], elem['lng']), end='');
          #     print("{" + "location: new google.maps.LatLng({}, {}), weight: {:.1f}".format(elem['lat'], elem['lng'], int(elem['count'])/1000) + "},", end='')
          #   else:
          #     for i in range(0, int(elem['count'])):
          #       print("new google.maps.LatLng({},{}),".format(elem['lat'], elem['lng']), end='');

        # daily_parser.remove_csv_file(needle_array)
        # daily_parser.write_csv(needle_array)
    # counts.sort()
    # for cnt in counts:
    #   print(cnt)

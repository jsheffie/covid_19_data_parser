#!/usr/bin/env python3

import os
import sys
from datetime import datetime
import random
import string

# look for libraries that are configured by './build.sh'
cwd = os.getcwd()

# Add `/lib` to the path to pick up our pip installed 3rd party requirements
sys.path[0:0] = ["{}/lib".format(cwd)]

# Add '/huvr_api_client' to the path to make this runnable out of the source tree
sys.path[0:0] = ["{}/covid_19_data_parser".format(cwd)]

from covid_19_data_parser import DailyReportsParser, Client

if __name__ == '__main__':
    base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports"  # 03-27-2020.csv
    daily_data_dir = 'daily_data'

    daily_parser = DailyReportsParser()

    date_range = ["03-30-2020"]

    for date_str in date_range:
        filename = "{}/{}.csv".format(daily_data_dir, date_str)
        download_url = "{}/{}.csv".format(base_url, date_str)
        daily_parser.get_data(download_url, filename)
        if date_str == date_range[-1]:
            # grab the latest day, and build up a needle array of any cases of more than 1k 'Confirmed'
            # needle_arrays = daily_parser.build_needle_array(Country_Region='US', column='Confirmed', high_watermark=1, Province_State='New York')
            needle_arrays = daily_parser.build_needle_array(Country_Region='US', column='Confirmed', high_watermark=30)


    print(len(needle_arrays))
    # sys.exit()

    counts = []
    data_batch = []
    count = 0
    firebase_client = Client(verbose=True)
    for needle_array in needle_arrays:
        if needle_array[1].lower() != 'unassigned' and (needle_array[1] and needle_array[2]):
            print("needle_array: {} count: {}".format(needle_array[1], count))
            daily_parser = DailyReportsParser()
            for date_str in date_range:
                filename = "{}/{}.csv".format(daily_data_dir, date_str)
                daily_parser.parse_lat_long_counts(date_str, needle_array, filename)

            # import json
            # print(json.dumps(daily_parser.parsed_lat_lng_lines, indent=4))
            for lat_lng in daily_parser.parsed_lat_lng_lines.keys():
                # {location: new google.maps.LatLng(37.782, -122.447), weight: 0.5},
                elem = daily_parser.parsed_lat_lng_lines[lat_lng]
                # for i in range(0, int(elem['count'])):
                # print("{"+" 'lat': {}, 'lng': {} 'weight': {}".format(elem['lat'], elem['lng'], elem['count']) + "}")

                if True:
                    if elem['count'] < 31:
                        detailed_data = { 'lat': float(elem['lat']), 'lng': float(elem['lng']) }
                    else:
                        detailed_data = { 'lat': float(elem['lat']), 'lng': float(elem['lng']), 'weight': elem['count'] }
                    detailed_data['sender'] = "t6eCnfpYUMPJgPvIBKWt9J9j1Kk2"  # anonymous
                    # detailed_data['sender'] = "xiMiIFIFbkTL7ZOD2Iso8R0zxlM2"  # jeff.sheffield
                    detailed_data['timestamp'] = int(datetime.now().strftime("%s%f"))/1000
                    data_batch.append(detailed_data)
                count += 1
                if len(data_batch) > 50:
                    response = firebase_client.post('https://my-project-jeffield.firebaseio.com/clicks.json', data=data_batch)
                    if response.status_code != 200:
                        print("ERROR: invalid status")
                        import json
                        print(json.dumps(response.text, indent=4))
                        response.raise_for_status()
                    data_batch = []

                # if count > 100:
                #     sys.exit()
    print(count)
    response = firebase_client.post('https://my-project-jeffield.firebaseio.com/clicks.json', data=data_batch)
    if response.status_code != 200:
        print("ERROR: invalid status")
        import json
        print(json.dumps(response.text, indent=4))
        response.raise_for_status()

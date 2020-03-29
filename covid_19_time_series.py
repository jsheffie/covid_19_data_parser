#!/usr/bin/env python3

import os
import sys

# look for libraries that are configured by './build.sh'
cwd = os.getcwd()

# Add `/lib` to the path to pick up our pip installed 3rd party requirements
sys.path[0:0] = ["{}/lib".format(cwd)]

# Add '/huvr_api_client' to the path to make this runnable out of the source tree
sys.path[0:0] = ["{}/covid_19_data_parser".format(cwd)]

from covid_19_data_parser import TimeSeriesParser

if __name__ == '__main__':
    download_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    filename = 'downloads/confirmed_global_data.csv'
    ts_parser = TimeSeriesParser(use_cachfile=False)
    ts_parser.get_data(download_url, filename)

    print("Parsing Time Series CSV data")
    ts_parser.parse('US')

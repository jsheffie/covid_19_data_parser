"""Main module."""

import csv
import io
import os

import requests
import json
from datetime import datetime

class Client(object):
    """
    A thin wrapper to the python requests library
    """
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.client = requests.Session()

    def get(self, url, params=None):

        headers = {
            # TODO: figure out how to properly single source __version__ from __init__.py
            'User-Agent': 'covid-19-dat-parser/{}'.format('0.1.0'),  # python-requests/2.22.0
        }

        response = self.client.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return (200, response.text)
        else:
            return (response.status_code, response.text)
        return response

    def post(self, url, data={}):
        """
        Override the requests.put handler so that we can dynamically enable
        logging, with our verbose flag.
        """
        headers = {
            # TODO: figure out how to properly single source __version__ from __init__.py
            'User-Agent': 'covid-19-dat-parser/{}'.format('0.1.0'),  # python-requests/2.22.0
        }

        if self.verbose:
            print("Putting {}".format(url))
            print(json.dumps(data, indent=4))
        response = self.client.post(url, json=data, headers=headers)
        if self.verbose:
            print("Put {} {}".format(response.request.method, response.url))
        return response



class Parser(object):
    def __init__(self, verbose=None):
        self.verbose = verbose
        self.data_directory = 'data_output'
        self.CSV_LOOKUP_3232020 = {
            'FIPS': 0,
            'Admin2': 1,
            'Province_State': 2,
            'Country_Region': 3,
            'Last_Update': 4, 
            'Lat': 5,
            'Long': 6,
            'Confirmed': 7,
            'Deaths': 8,
            'Recovered': 9,
            'Active': 10,
            'Combined_Key': 11
        }

    def makedirs(self, filename):
        toks = filename.split('/')
        dir_name = "/".join(toks[:-1])
        if dir_name and not os.path.exists(dir_name):
            print("Making Directory: [{}]".format(dir_name))
            os.makedirs(dir_name)

    def cached_csv(self):
        return os.path.isfile(self.data_file)

    def write_csv_file(self, filename, data):

        self.makedirs(filename)
        with io.open(filename, 'w', encoding="utf-8") as outfile:
            outfile.write(data)
            print("Wrote to file {}".format(filename))
            return True

        return False

    def update_csv_file(self, filename, lines):
        """
        A thin wrapper to write_csv_file
        """
        if os.path.isfile(filename):
            os.unlink(filename)
        data = ""
        for line in lines:
            data += "{}\n".format(line)

        self.write_csv_file(filename, data)


    def set_cachefile(self, filename):
        if os.path.isfile(filename):
            self.data_file = filename
            return True

        return False

    def get_data(self, download_url, filename):
        res_code = 100
        filename = self.sanitize_filename(filename)
        file_exists = self.set_cachefile(filename)
        if not self.cached:
            # Force-refetching
            if os.path.isfile(filename):
                os.unlink(filename)
                file_exists = False

        if not file_exists:
            print("Fetching csv file from {}".format(filename))
            self.client = Client()
            (res_code, data) = self.client.get(download_url)
            if res_code == 200:
                print("Successfully Downloaded data {}".format(len(data)))
                res = self.write_csv_file(filename, data)
                if res:
                    self.set_cachefile(filename)
                    print("Successfully Wrote datafile {}".format(filename))
            else:
                print("ERROR: {}".format(res_code))
                print(data)

        return res_code

    def sanitize_filename(self, filename):
        return '_'.join(filename.split(' '))


class TimeSeriesParser(Parser):

    def __init__(self, verbose=None, use_cachfile=True):
        super().__init__(verbose=verbose)
        self.client = None
        self.cached = use_cachfile

    def calculate_new_cases(self, data_array, today_index, yesterday_index, index_range):
        if today_index > index_range:
            return int(data_array[today_index]) - int(data_array[yesterday_index])
        else:
            return 0

    def calculate_multiplication_factor(self, data_array, today_index, yesterday_index, index_range):
        if today_index > index_range:
            return int(data_array[today_index]) / int(data_array[yesterday_index])
        else:
            return 0

    def parse(self, country_region, data_offset=3):
        with open(self.data_file, newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter='+', quotechar='|')
            cnt = 0
            final_csv_data = ""
            header_row = ""
            filename = '{}/{}.csv'.format(self.data_directory, country_region)
            for row in datareader:
                if cnt == 0:
                    final_csv_data = "date,count,new_cases,multiplication_factor\n"
                    # final_csv_data = "date,count,new_cases\n"
                    header_row = row[0].split(',')
                else:
                    try:
                        data_array = row[0].split(',')
                        if data_array[1].lower() == country_region.lower():
                            index_range = [i for i in range(360) if i > data_offset]
                            for index in index_range:
                                month = int(header_row[index].split('/')[0])
                                day = int(header_row[index].split('/')[1])
                                new_cases = self.calculate_new_cases(data_array, index, index - 1, index_range[0])
                                multiplication_factor = self.calculate_multiplication_factor(data_array, index, index - 1, index_range[0])
                                final_csv_data += "{}-{:02d}-{:02d},{},+{},{:.3f}\n".format("2020", month, day, data_array[index], new_cases, multiplication_factor)
                                # final_csv_data += "{}-{:02d}-{:02d},{}\n".format("2020", month, day, data_array[index])
                                # final_csv_data += "{},{},+{},{:.3f}\n".format(datetime(2020, month, day).isoformat(), data_array[index], new_cases, multiplication_factor)
                    except IndexError:
                        pass
                cnt += 1
            self.write_csv_file(filename, final_csv_data)


class DailyReportsParser(Parser):
    """
    This module agressivly cache's the data ( via filesystem csv files)
    Since the daily data won't ( in theory ) change after a file has been fetched.
    There is a module init attribure 'use_cachfile' to change the default behavior.
    However, the nice thing to do is use cache.
    """

    def __init__(self, verbose=None, use_cachfile=True):
        super().__init__(verbose=verbose)
        self.parsed_lines = []
        self.parsed_lat_lng_lines = {}
        self.client = None
        self.cached = use_cachfile

    def add_line(self, date='Date', confirmed='Confirmed', deaths='Deaths', recovered='Recovered', active='Active', new_cases='Confirmed New Cases', multiplication_factor='Confirmed multiplication factor'):
        try:
            self.parsed_lines.append("{},{},{},{},{},+{},{:.3f}".format(date, confirmed, deaths, recovered, active, new_cases, multiplication_factor))
        except ValueError:
            self.parsed_lines.append("{},{},{},{},{},{},{}".format(date, confirmed,  deaths, recovered, active, new_cases, multiplication_factor))

    def calculate_new_cases(self, today_cnt, yesterday_cnt):
        return int(today_cnt) - int(yesterday_cnt)

    def calculate_multiplication_factor(self, today_cnt, yesterday_cnt):
        if int(yesterday_cnt) > 0:
            return int(today_cnt) / int(yesterday_cnt)
        else:
            return 0

    def parse(self, date_str, needle_array, filename):
        """ needle_array is the thing we are looking for """
        filename = self.sanitize_filename(filename)
        confirmed_index = self.CSV_LOOKUP_3232020['Confirmed']
        deaths_index = self.CSV_LOOKUP_3232020['Deaths']
        recovered_index = self.CSV_LOOKUP_3232020['Recovered']
        active_index = self.CSV_LOOKUP_3232020['Active']
        if len(self.parsed_lines) == 0:
            self.add_line()  # add the header line

        if os.path.isfile(filename):
            with open(filename, newline='') as csvfile:
                datareader = csv.reader(csvfile, delimiter='+', quotechar='|')
                for row in datareader:
                    try:
                        data_array = row[0].split(',')
                        found_it = True
                        indexes = range(1,len(needle_array)-1)  # skip the FIPS number ( some of the data is missing it )
                        for index in indexes:
                            if data_array[index] != needle_array[index]:
                                found_it = False
                        if found_it:
                            yesterdays_cnt = 0
                            new_cases = 0
                            multiplication_factor = 0
                            if len(self.parsed_lines) > 1:
                                yesterdays_cnt = self.parsed_lines[-1].split(',')[1]
                                new_cases = self.calculate_new_cases(data_array[confirmed_index], yesterdays_cnt)
                                multiplication_factor = self.calculate_multiplication_factor(data_array[confirmed_index], yesterdays_cnt)
                            self.add_line(date_str, data_array[confirmed_index], data_array[deaths_index], data_array[recovered_index], data_array[active_index], new_cases, multiplication_factor)

                    except IndexError:
                        pass
        else:
            print("Filename: {} Not found".format(filename))

    def parse_lat_long_counts(self, date_str, needle_array, filename):
        filename = self.sanitize_filename(filename)
        confirmed_index = self.CSV_LOOKUP_3232020['Confirmed']
        offset_to_lat = self.CSV_LOOKUP_3232020['Lat']
        offset_to_lng = self.CSV_LOOKUP_3232020['Long']

        with open(filename, newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter='+', quotechar='|')
            for row in datareader:
                try:
                    data_array = row[0].split(',')
                    found_it = True
                    indexes = range(len(needle_array))
                    for index in indexes:
                        if data_array[index] != needle_array[index]:
                            found_it = False
                    if found_it:
                        # TODO: remove magic
                        unique_key = "_".join([str(data_array[offset_to_lat]), str(data_array[offset_to_lng])])
                        if unique_key in self.parsed_lat_lng_lines:
                            self.parsed_lat_lng_lines[unique_key]['count']+= int(data_array[confirmed_index])
                        else:
                            if data_array[offset_to_lat] and  data_array[offset_to_lng] and data_array[confirmed_index]:
                                self.parsed_lat_lng_lines[unique_key] = { 'lat': data_array[offset_to_lat], 
                                                                          'lng': data_array[offset_to_lng], 
                                                                          'count': int(data_array[confirmed_index])}

                except IndexError:
                    pass


    def remove_fips_element(self, needle_array):
        return needle_array[1:]

    def write_csv(self, filename_tokes):
        filename_tokes = self.remove_fips_element(filename_tokes)
        final_data = ""
        for line in self.parsed_lines:
            final_data += "{}\n".format(line)

        filename = "_".join(filename_tokes)
        filename = self.sanitize_filename(filename)
        self.write_csv_file("{}/{}.csv".format(self.data_directory, filename), final_data)

    def remove_csv_file(self, filename_tokes):
        filename_tokes = self.remove_fips_element(filename_tokes)
        filename = "_".join(filename_tokes)
        filename = self.sanitize_filename(filename)
        filename = "{}/{}.csv".format(self.data_directory, filename)
        if os.path.isfile(filename):
            os.unlink(filename)

    def build_needle_array(self, Country_Region='US', column='Confirmed', high_watermark=1000, Province_State=None):
        # Some example needles
        # needle_arrays = [['48453', 'Travis', 'Texas', 'US'],
        #                  ['48491', 'Williamson', 'Texas', 'US']]
        needle_arrays = []
        # self.data_file
        if os.path.isfile(self.data_file):
            with open(self.data_file, newline='') as csvfile:
                datareader = csv.reader(csvfile, delimiter='+', quotechar='|')
                for row in datareader:
                    try:
                        data_array = row[0].split(',')
                        found_it = False
                        if Province_State:  # the more detailed filter
                            if data_array[3] == Country_Region and data_array[2] == Province_State:
                                found_it = True
                        else:
                            if data_array[3] == Country_Region:
                                found_it = True
                        if found_it:
                            # What's its count
                            offset_to_count = self.CSV_LOOKUP_3232020[column]
                            if int(data_array[offset_to_count]) >= int(high_watermark):
                                needle_arrays.append([data_array[0], data_array[1], data_array[2], data_array[3]])
                    except IndexError:
                        pass
        else:
            print("build_needle_array: Filename {} not found".format(self.data_file))
        return needle_arrays


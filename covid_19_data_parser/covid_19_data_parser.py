"""Main module."""

import csv
import io
import os

import requests


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


class Parser(object):
    def __init__(self, verbose=None):
        self.verbose = verbose
        self.data_directory = 'data_output'

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

    def set_cachefile(self, filename):
        self.data_file = filename

    def get_data(self, download_url, filename):
        filename = self.sanitize_filename(filename)
        self.set_cachefile(filename)
        if not self.cached:
            # Force-refetching
            if os.path.isfile(filename):
                os.unlink(filename)

        if not self.cached_csv():
            print("Fetching csv file from {}".format(filename))
            self.client = Client()
            (res_code, data) = self.client.get(download_url)
            if res_code == 200:
                print("Successfully Downloaded data {}".format(len(data)))
                res = self.write_csv_file(filename, data)
                if res:
                    print("Successfully Wrote datafile {}".format(filename))
            else:
                print("ERROR: {}".format(res_code))
                print(data)

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
                    final_csv_data = "date,count,new cases,multiplication factor\n"
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
        self.client = None
        self.cached = use_cachfile

    def add_line(self, date='date', count='confirmed', new_cases='new cases', multiplication_factor='multiplication factor'):
        try:
            self.parsed_lines.append("{},{},+{},{:.3f}".format(date, count, new_cases, multiplication_factor))
        except ValueError:
            self.parsed_lines.append("{},{},{},{}".format(date, count, new_cases, multiplication_factor))

    def calculate_new_cases(self, today_cnt, yesterday_cnt):
        return int(today_cnt) - int(yesterday_cnt)

    def calculate_multiplication_factor(self, today_cnt, yesterday_cnt):
        return int(today_cnt) / int(yesterday_cnt)

    def parse(self, date_str, needle_array, filename):
        """ needle_array is the thing we are looking for """
        filename = self.sanitize_filename(filename)

        if len(self.parsed_lines) == 0:
            self.add_line()  # add the header line

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
                        offset_to_confirmed = 7
                        yesterdays_cnt = 0
                        new_cases = 0
                        multiplication_factor = 0
                        if len(self.parsed_lines) > 1:
                            yesterdays_cnt = self.parsed_lines[-1].split(',')[1]
                            new_cases = self.calculate_new_cases(data_array[offset_to_confirmed], yesterdays_cnt)
                            multiplication_factor = self.calculate_multiplication_factor(data_array[offset_to_confirmed], yesterdays_cnt)
                        self.add_line(date_str, data_array[offset_to_confirmed], new_cases, multiplication_factor)

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

    def build_needle_array(self, country='US', column='Confirmed', high_watermark=1000):
        # Some example needles
        # needle_arrays = [['48453', 'Travis', 'Texas', 'US'],
        #                  ['48491', 'Williamson', 'Texas', 'US']]
        needle_arrays = []
        num_lookup = {
            'Confirmed': 7,
            'Deaths': 8,
            'Recovered': 9
        }
        self.data_file
        with open(self.data_file, newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter='+', quotechar='|')
            for row in datareader:
                try:
                    data_array = row[0].split(',')
                    found_it = False
                    if data_array[3] == country:
                        found_it = True
                    if found_it:
                        # What's its count
                        offset_to_count = num_lookup[column]
                        if int(data_array[offset_to_count]) >= int(high_watermark):
                            needle_arrays.append([data_array[0], data_array[1], data_array[2], data_array[3]])
                except IndexError:
                    pass
        return needle_arrays

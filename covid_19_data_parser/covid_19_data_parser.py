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


class TimeSeriesParser(Parser):

    def __init__(self, confirmed_data_file=None, verbose=None):
        # super().__init__()
        self.data_file = confirmed_data_file

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
            filename = '{}.csv'.format(country_region)
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

    def __init__(self, verbose=None):
        super().__init__(verbose=verbose)
        self.parsed_lines = []

    def set_cachefile(self, filename):
        self.data_file = filename

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

    def write_csv(self, filename_tokes):
        final_data = ""
        for line in self.parsed_lines:
            final_data += "{}\n".format(line)

        filename = "_".join(filename_tokes)
        self.write_csv_file("{}.csv".format(filename), final_data)

    def remove_csv_file(self, filename_tokes):
        filename = "_".join(filename_tokes)
        filename = "{}.csv".format(filename)
        if os.path.isfile(filename):
            os.unlink(filename)

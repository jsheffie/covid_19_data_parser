"""Main module."""

import requests
import io
import os
import csv


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
            return (response.status_code, json.loads(response.text))
        return response


class Parser(object):

    def __init__(self, confirmed_data_file=None, verbose=None):
        self.confirmed_data_file = confirmed_data_file

    def makedirs(self, filename):
        toks = filename.split('/')
        dir_name = "/".join(toks[:-1])
        if dir_name and not os.path.exists(dir_name):
            print("Making Directory: [{}]".format(dir_name))
            os.makedirs(dir_name)

    def cached_csv(self):
        return os.path.isfile(self.confirmed_data_file)

    def write_csv_file(self, filename, data):

        self.makedirs(filename)
        with io.open(filename, 'w', encoding="utf-8") as outfile:
            outfile.write(data)
            print("Wrote to file {}".format(filename))
            return True

        return False
    def calculate_new_cases(self, data_array, today_index, yesterday_index, index_range):
        if today_index > index_range:
            return int(data_array[today_index]) - int(data_array[yesterday_index])
        else:
            return 0

    def calculate_multiplication_factor(self, data_array, today_index, yesterday_index, index_range):
        if today_index > index_range:
            return int(data_array[today_index])/int(data_array[yesterday_index])
        else:
            return 0


    def parse_time_series(self, country_region, data_offset=3):
        with open(self.confirmed_data_file, newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter='+', quotechar='|')
            cnt = 0
            final_csv_data=""
            header_row=""
            filename='{}.csv'.format(country_region)
            for row in datareader:
                if cnt == 0:
                    final_csv_data="date,count,new cases,multiplication factor\n"
                    header_row = row[0].split(',')
                else:
                    try:
                        data_array = row[0].split(',')
                        # print(data_array[0].lower())
                        # print(data_array)
                        if data_array[1].lower() == country_region.lower():
                            index_range = [i for i in range(360) if i > data_offset  ]
                            # print(index_range)
                            for index in index_range:
                                month = int(header_row[index].split('/')[0])
                                day = int(header_row[index].split('/')[1])
                                new_cases = self.calculate_new_cases(data_array, index, index-1, index_range[0])
                                multiplication_factor = self.calculate_multiplication_factor(data_array, index, index-1 index_range[0])
                                final_csv_data+="{}-{:02d}-{:02d},{},+{},{}\n".format("2020", month, day, data_array[index], new_cases, multiplication_factor)
                    except IndexError:
                        pass
                cnt+=1
            self.write_csv_file(filename, final_csv_data)

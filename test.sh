#! /bin/bash

pip3 install -r requirements_dev.txt

# Disabled the following flake errors
#          E501 line too long (89 > 79 characters)
#          E402 module level import not at top of file
flake8 --ignore E402,E501 covid_19_data_parser tests *.py

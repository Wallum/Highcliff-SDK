#!/usr/bin/env python3
import argparse
import csv
from datetime import datetime
import random
import os
import tempfile
import time


class GenerateData:

    def __init__(self) -> None:
        pass

    def _generateTemp(self) -> float:
        return round(random.uniform(35.5, 42.5), 1)

    def _generateTime(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _modCsv(self, file_name: str) -> None:
        # open file and clear existing content
        f = open(file_name, 'w')
        f.truncate(0)
        # write csv row
        c = csv.writer(f)
        c.writerow((self._generateTime(), self._generateTemp()))
        # close file
        f.close()


def parse_arguments():
    default_data_file = 'temps.csv'
    parser = argparse.ArgumentParser(description="Generate random temperatures and store them in a file.")
    parser.add_argument('--data-file', default=default_data_file, type=str, help="File path for output data.")
    return parser.parse_args()


def main():
    parameters = parse_arguments()
    # create instance of class
    genData = GenerateData()
    # infinite loop, publishing csv data
    print(f'Output data file: {parameters.data_file}')
    while True:
        genData._modCsv(parameters.data_file)
        time.sleep(20)
        


if __name__ == "__main__":
    main()

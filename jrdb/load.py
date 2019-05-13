import sys
import numpy as np
import pandas as pd
import re
import json

from abc import ABCMeta, abstractmethod 

class FileLoader():
    def __init__(self):
        self._file_name = None
        self._file_type = None

    def load(self, file_name):
        self._file_name = file_name
        self._file_type = self._get_file_type(file_name)
        loader = self._create_loader(self._file_type)
        return loader.load_file(self._file_name)

    def _get_file_type(self, file_name):
        return re.search('\.[a-z]+', file_name).group(0)[1:]

    def _create_loader(self, file_type):
        if file_type == 'txt':
            return TextLoader()
        elif file_type == 'json':
            return JsonLoader()
        elif file_type == 'sql':
            return SqlLoader()
        elif file_type == 'csv':
            return CsvLoader()

    def get_file_name(self):
        return self._file_name
    
    def get_file_type(self):
        return self._file_type

    def get_data(self):
        return self._data

class IFileLoader(metaclass = ABCMeta):
    @abstractmethod
    def load_file(self, file_name):
        pass

class TextLoader(IFileLoader):
    def load_file(self, file_name):
        try:
            return pd.read_table(file_name, encoding = 'shift_jisx0213', header = None)[0]
        except FileNotFoundError as e:
            print('FileNotFoundError', e)

class JsonLoader(IFileLoader):
    def load_file(self, file_name):
        try:
            with open(file_name, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print('JSONDecodeError', e)
        except FileNotFoundError as e:
            print('FileNotFoundError', e)

class SqlLoader(IFileLoader):
    def load_file(self, file_name):
        try:
            with open(file_name, 'r') as f:
                return f.read()
        except FileNotFoundError as e:
            print('FileNotFoundError', e)

class CsvLoader(IFileLoader):
    def load_file(self, file_name):
        try:
            return pd.read_csv(file_name)
        except FileNotFoundError as e:
            print('FileNotFoundError', e)


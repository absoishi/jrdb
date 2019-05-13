import re
import numpy as np
import pandas as pd

from jrdb import load

class JrdbDataParser():
    def __init__(self):
        self._config_path = 'jrdb/config/'
        self._loader = load.FileLoader()

    def parse(self, text_data, data_type):
        config_json_name = self._config_path + data_type + '.json'
        config_json = self._loader.load(config_json_name)
        converter = JrdbTextConverterIntoDataFrame(text_data, config_json)
        df = converter.convert_text_into_dataframe()
        formater = JrdbDataFrameFormatter(df, config_json)
        return formater.format_dataframe()

class JrdbTextConverterIntoDataFrame():
    def __init__(self, text_data, config_json):
        self._text_data      = text_data
        self._config_json    = config_json
        self._keys           = config_json.keys()

    def convert_text_into_dataframe(self):
        df = self._generate_dataframe_for_data_strage()
        return self._store_data(df)

    def _generate_dataframe_for_data_strage(self):
        data_list = [['' for column in range(len(self._keys))] for row in range(len(self._text_data))]
        return pd.DataFrame(data_list, columns = self._keys)

    def _store_data(self, df):
        for key in self._keys:
            for row in range(len(df)):
                encode_text = self._text_data[row].encode(encoding = 'shift_jisx0213')
                df.at[row, key] = encode_text[self._config_json[key]['start_ind_b'] : self._config_json[key]['end_ind_b']].decode(encoding = 'shiftjisx0213')
        return df

def validate_blank(text):
    if re.search('^\s+$', text):
        return True
    else:
        return False

def remove_blank(text):
    """
    Remove whitespace from string

    Example
    --------
    >>> remove_blank('  6')
        '6'
    """
    if validate_blank(text):
        return None 
    return re.sub('\s', '', text)

def bring_to_head_sign(text):
    """
    Move forward plus or minus sign

    Example
    --------
    >>> bring_to_head_sign(' -6')
        '- 6'
    """
    symbol_ind = re.search('-|\+', text).start()
    text = list(text)
    text[0], text[symbol_ind] = text[symbol_ind], text[0]
    text = ''.join(text)
    return text

def blank_to_zero(text):
    """
    Fill in blanks with zeros.

    Example
    --------
    >>> blank_to_zero('  6')
        '006'
    """
    if validate_blank(text):
        return None 
    else:
        return re.sub('\s', '0', text)

def str_to_float(text):
    """
    Convert a string that type 999 in JRDB data to a float.

    Example
    --------
    >>> str_to_float('123')
        12.3
    >>> str_to_float(' 23')
        2.3
    """
    if validate_blank(text):
        return None
    else:
        try:
            text = bring_to_head_sign(text)
        except:
            pass
        text = blank_to_zero(text)
        return float(text[0:2]) + float(text[2])/10

def time_to_seconds(text):
    """
    Convert a string that type 9999 in JRDB data to seconds

    Example
    --------
    >>> time_to_seconds('1345')
        94.5
        (1:34.5)
    """
    if validate_blank(text):
        return None
    else:
        text = blank_to_zero(text)
        text_len = len(text)
        return float(text[0])*60 + float(text[1:3]) + float(text[3])/10


class JrdbDataFrameFormatter():
    def __init__(self, dataframe, config_json):
        self._data           = dataframe
        self._config_json    = config_json
        self._keys           = config_json.keys()

    def format_dataframe(self):
        ret_dataframe = self._data.copy()
        for key in self._keys:
            target_series = JrdbCorrectStrSeries(self._data[key])
            target_var_function = self._config_json[key]['var_function']
            target_var_type = self._config_json[key]['var_type']
            ret_dataframe[key] = target_series.correct_str_series(target_var_function, target_var_type)
        return ret_dataframe

class JrdbCorrectStrSeries():
    def __init__(self, series):
        self._series = series

    def correct_str_series(self, var_function, var_type):
        ret_series = self._series.copy()
        try:
            if var_function == 'remove_blank_series':
                ret_series = self._remove_blank_series(ret_series)
            elif var_function == 'blank_to_zero_series':
                ret_series = self._blank_to_zero_series(ret_series)
            elif var_function == 'str_to_float_series':
                ret_series = self._str_to_float_series(ret_series)
            elif var_function == 'time_to_seconds_series':
                ret_series = self._time_to_seconds_series(ret_series)
        except:
            pass
        ret_series = self._convert_var_type(ret_series, var_type)
        return ret_series

    def _remove_blank_series(self, series):
        return series.map(remove_blank)

    def _blank_to_zero_series(self, series):
        return series.map(blank_to_zero)

    def _str_to_float_series(self, series):
        return series.map(str_to_float)

    def _time_to_seconds_series(self, series):
        return series.map(time_to_seconds)

    def _convert_var_type(self, series, var_type):
        ret_series = series
        type_converted_series = ret_series.fillna(0).astype(var_type)
        ret_series.loc[ret_series.notnull()] = type_converted_series
        return ret_series
        


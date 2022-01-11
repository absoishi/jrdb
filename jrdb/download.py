import io
import os
import re
import zipfile
import lhafile
from abc import ABCMeta, abstractmethod

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth


class JrdbDownloader():
    def __init__(self, username=None, password=None):
        self._file_name = None
        self._file_type = None
        self._jrdb_user = os.environ['JRDB_USERNAME'] if os.environ['JRDB_USERNAME'] else username
        self._jrdb_pass = os.environ['JRDB_PASSWORD'] if os.environ['JRDB_USERNAME'] else password

    def load(self, file_name):
        self._file_name = file_name
        self._file_type = self._get_file_type(file_name)
        loader = self._create_loader(self._file_type)
        return loader.load_file(self._file_name, self._jrdb_user, self._jrdb_pass)

    def _get_file_type(self, file_name):
        return re.search(r'\.[a-z]+', file_name).group(0)[1:]

    def _create_loader(self, file_type):
        if file_type == 'zip':
            return ZipLoader()
        elif file_type == 'lzh':
            return LzhLoader()
        else:
            print('Unexpected file type: %s' % (file_type))
            raise SystemExit()


class IFileLoader(metaclass=ABCMeta):
    def load_file(self, file_name, jrdb_user, jrdb_pass):
        try:
            # Try to download ZIP file from JRDB with username and password.
            url = self.base_url + self._generate_url_strings(file_name)
            res = requests.get(url, auth=HTTPBasicAuth(jrdb_user, jrdb_pass))
        except requests.exceptions as e:
            # Exception error handling
            print('Request is failure: Name, server or service not known')
            print('RequestsExceptions', e)
            raise SystemExit()

        # Response Status Confirmation
        if res.status_code not in [200]:
            # HTTP Response is not 200 (Normal)
            print('Request to ' + url + ' has been failure: ' + str(res.status_code))
            raise SystemExit()

        return self._uncompress_file(res.content)

    def _generate_url_strings(self, file_name):
        # Extract category from file_name (ex. SED220110.zip -> Sed)
        category = re.search(r'[A-Z]{3}', file_name).group(0).capitalize()

        # Extract year from file_name and add it to url if the file_name is single data section (単体データコーナー)
        # if you point year pack section (年度パックコーナー), url is not required year directory.
        if re.search(r'[A-Z]{3}\d{6}.zip', file_name):
            short_year = re.search(r'\d{6}', file_name).group(0)[0:2]
            year = "20" + short_year if short_year != "99" else "19" + short_year
            # Add year directory to file_name (ex. 2022/SED220110.zip)
            file_name = year + "/" + file_name

        # Concat category and file_name (ex. Sed/2022/SED220110.zip, Sed/SED_2021.zip)
        return category + "/" + file_name

    @abstractmethod
    def _uncompress_file(self, content):
        pass


class ZipLoader(IFileLoader):
    def __init__(self):
        self.base_url = 'http://www.jrdb.com/member/datazip/'

    def _uncompress_file(self, content):
        # Create Zip Object from response strings
        zip_object = zipfile.ZipFile(io.BytesIO(content))

        # Uncompress ZIP files & union all files
        # if the Zip file has many text files, the script integrate files to single file.
        records = list()
        for file_name in zip_object.namelist():
            if not re.search(r'(SRA|SRB)\d{6}.txt', file_name):
                txt = zip_object.open(file_name).read()
                records.extend(txt.decode('ms932').splitlines())

        return pd.DataFrame(records)


class LzhLoader(IFileLoader):
    def __init__(self):
        self.base_url = 'http://www.jrdb.com/member/data/'

    def _uncompress_file(self, content):
        # Create Lzh Object from response strings
        lha_object = lhafile.Lhafile(io.BytesIO(content))

        # Uncompress Lzh files & union all files
        # if the Lzh file has many text files, the script integrate files to single file.
        records = list()
        for file_info in lha_object.infolist():
            if not re.search(r'(SRA|SRB)\d{6}.txt', file_info.filename):
                txt = lha_object.read(file_info.filename)
                records.extend(txt.decode('ms932').splitlines())

        return pd.DataFrame(records)

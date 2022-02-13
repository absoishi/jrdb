# jrdb: JRDB(JRA horse racing database) data parser and feature creater
----------------------

### What is this?
----------------------
**jrdb** is a python package for parsing JRDB(http://www.jrdb.com/) data. In addition, it helps to create some features from parsed data(future work).  
JRDB contains so many types of data. For example, not only the race results but also training, odds, jockeys and trainers data. These data will be very useful for thinking about horse racing from the data analysis side, but is given in text format. You have to parse!! **jrdb** will help you.  
<!--
Parsed data will be stored in the database. This package contains sql files for creating tables.  
When creating features, extract data from the database and process it. **jrdb** assumes that the database is postgreSQL. (In the future, **jrdb** will be improved to work with other databases.) 
-->
### Dependencies
----------------------
- [NumPy](https://www.numpy.org)
- [pandas](https://pandas.pydata.org/)
- [re]()
- [requests](https://docs.python-requests.org/en/latest/)
- [lhafile](https://github.com/FrodeSolheim/python-lhafile/)
- [bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
<!--
- [psycopg2]()
- [sqlalchemy]()
- [postgreSQL]()
-->
### Usage
----------------------
To parse JRDB data and insert to DB.
```py
# import modules
from jrdb import load
from jrdb import parse

# load text data (ex. SED)
loader = load.FileLoader()
text_data = loader.load('file_path/SEDyymmdd.txt')

# parse
parser = parse.JrdbDataParser()
df = parser.parse(text_data, 'SED')   # return pandas DataFrame
```  
  
#### Direct data load from JRDB
If you would like to download data from JRDB directorly, you can use `JrdbLoader` intead of `FileLoader`.  
NOTE:  
- **JRDB username and password are required** for script execution.
- The script support **only separated data** (個別データ). Not support integrated data pack (JRDBデータパック).  
- The script support daily data section (単体データコーナー) and yearly data section (年度パックコーナー).  
- The script **not** support SRA/SRB data set download which is included SED data data set.
- The script support `zip` and `lzh` file format.  
- If you avoid to set username and password in source code, you can use envrionemnt variables (JRDB_USERNAME/JRDB_PASSWORD). In this case, The script skip the `load` method username and password parameters.  
```py
# import modules
from jrdb import download
from jrdb import parse

# Download data from JRDB web site (ex. SED)
loader = load.JrdbDownloader()
text_data = loader.load('SEDyymmdd.zip', 'JRDB_USERNAME', 'JRDB_PASSWORD')

# parse
parser = parse.JrdbDataParser()
df = parser.parse(text_data, 'SED')   # return pandas DataFrame
```  

#### Bulk load option
If you would like to bulk download or latest file download from JRDB, you can use `file_names` method.  
- If you collect only latest data, please delete `bulk=True` option from `file_names` method arguments.
```py
# Download data from JRDB web site (ex. SED)
loader = load.JrdbDownloader()
text_data_all = []
# Listing target data type files and loop it.
for file_name in loader.file_names('SED', bulk=True):
    text_data = loader.load(file_name, 'JRDB_USERNAME', 'JRDB_PASSWORD')
    text_data_all = text_data_all.append(text_data)
    time.sleep(5)
# Gathering loaded data
text_data_all = pd.concat(text_data_all)
```
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
- [pandas]()
- [re]()
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
import pandas as pd

# load text data (ex. SED)
loader = load.FileLoader()
text_data = loader.load('file_path/SEDyymmdd.txt')

# parse
parser = parse.JrdbDataParser()
df = parser.parse(text_data, 'SED')   # return pandas DataFrame
```




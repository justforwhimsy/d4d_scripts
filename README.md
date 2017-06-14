# d4d_scripts
These scripts were used to assist in the Data for Democracy issues https://github.com/Data4Democracy/just-politics/issues/8 and https://github.com/Data4Democracy/just-politics/issues/9

Some files were used to test out a package or API. Some scripts require tokens or authentication information.

# us_counties_full.csv
This file contains a list of 3142 counties in the United States.

According to Wikipedia, there are 3144 counties, but when you look at their page listing all counties, it says there are 3142.

A couple of states have cities that do not belong to a county, but operate as a county.

Alaska has boroughs instead of counties while Louisiana has Parishes.

The list of counties and cities can be found on this Wikipedia page - https://en.wikipedia.org/wiki/List_of_United_States_counties_and_county_equivalents

# find_county_pages.py
Overview:
Search Facebook Pages - Using facepy and reading us_counties.csv, the script searches Facebook for each county.

Verify each page's location - Using the Facebook location provided in each page and Google's map API, the script tries to verify what true county the page is related to. There are several states that have the same county, so searching for Clark County can return results for several states.

Store the results - Once the county has been verified, the page ID, name, URL, state, Google verified county, and search county are stored into a database.

Wait a minute to make another request so Facebook doesn't block us.

The script will run through a max of 4 pages of Facebook results which is about 100 pages.

Packages used:
- facepy (used to query facebook)
- requests (used to make requests to the google API)
- csv (used to read the list of counties)
- time (used to break between county queries)
- logging
- json (not necessary for basic functionality)
- _mysql (this package was used since I wrote this on Windows. There are other packages that may work better depending on OS) http://mysql-python.sourceforge.net/MySQLdb.html

Google API - This is used to verify the address of a Facebook page. There is a 50k daily request limit. Data is returned in a dictionary of array values that will not always have the same structure. This has resulted in some values being incorrect. If there is a more reliable tool or package that can be downloaded, that may be a better solution.

# public_county_pages_fb_pages.sql
This is as far as the script got before the Google API said 'Stawp giving us requests today!' This made it through the Alabama counties and some of the Alaskan boroughs. Some of the data is stored wrong. This may be due to the way information is collected from the google API.

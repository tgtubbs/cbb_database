# cbb school index scraper

'''
Notes:

Some of the location strings (City, State) are incorrect and need to be set manually.
'''

from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import pandas
import requests

# scrape school index from bbref
url = "http://www.sports-reference.com/cbb/schools/"
soup = BeautifulSoup(requests.get(url).text)
team_hrefs = [a["href"] for a in soup.find_all("tbody")[0].find_all("a")]
bbref_ids = [href[13:-1] for href in team_hrefs]
table_headers = [th.text for th in soup.find_all("tbody")[0].find_all("th")][1:18]
table_rows = soup.find_all("tbody")[0].find_all("tr", attrs={"class": ""})
row_data = [[td.text for td in table_rows[i].find_all("td")[1:]] for i in range(0, len(table_rows))]

# fill dataframe
team_index_df = pandas.DataFrame(row_data, columns=table_headers)
team_index_df["bbref_id"] = bbref_ids
column_names = team_index_df.columns.tolist()
column_names = column_names[-1:] + column_names[:-1]
team_index_df = team_index_df[column_names]

# get geographical coordinates
geolocator = Nominatim()
latitude = []
longitude = []
for i in range(len(team_index_df["City, State"])):
    location = geolocator.geocode(team_index_df["City, State"][i])
    latitude.append(location.raw["lat"])
    longitude.append(location.raw["lon"])
    print(team_index_df["School"][i] + ": " + location.raw["lat"] + ", " + location.raw["lon"])
team_index_df["latitude"] = latitude
team_index_df["longitude"] = longitude

team_index_df.to_csv("/Users/travistubbs/Desktop/cbb_database/data/team_index.txt", sep="\t", index=False)

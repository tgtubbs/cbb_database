
from bs4 import BeautifulSoup
import pandas
import requests

# scrape bbref team ids and school index
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

# Some team_index_df["City, State"] data are incorrect. Modify manually
# before running geocoder.

team_index_df.to_csv("/Users/travistubbs/cbb_database/data/teams.txt", sep="\t", index=False)

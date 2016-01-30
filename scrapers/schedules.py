
from bs4 import BeautifulSoup
import pandas
import requests
# from time import sleep


def format_url(bbref_team_id, year):
    return("http://www.sports-reference.com/cbb/schools/" + bbref_team_id + "/" + str(year) + "-schedule.html")


def get_schedule(url):
    soup = BeautifulSoup(requests.get(url).text)
    headers = [th.text for th in soup.find_all("table", attrs={"id": "schedule"})[0].find_all("th")]
    rows = soup.find_all("table", attrs={"id": "schedule"})[0].find_all("tbody")[0].find_all("tr", attrs={"class": ""})
    row_data = [[td.text for td in rows[i].find_all("td")] for i in range(len(rows))]
    return(headers[0:16], row_data)


teams = pandas.read_csv('Users/travistubbs/cbb_database/data/teams.txt', sep="\t")
years_array = [2015]
url = format_url(teams["bbref_id"][0], 2015)
headers, row_data = get_schedule(url)
schedule_array = []
for year in years_array:
    for team_id in teams["bbref_id"]:
        print(team_id + " - " + str(year))
        url = format_url(team_id, year)
        try:
            schedule_headers, schedule_data = get_schedule(url)
            schedule_df = pandas.DataFrame(schedule_data, columns=schedule_headers)
            schedule_df["team"] = team_id
            schedule_array.append(schedule_df)
        except IndexError:  # teams without schedules for that year will raise IndexError
            next
    schedules = pandas.concat(schedule_array)
    schedules["year"] = str(year)
    file_path = "/Users/travistubbs/cbb_database/data/schedules" + str(year) + ".txt"
    schedules.to_csv(file_path, sep="\t", index=False)

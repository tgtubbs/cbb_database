# cbb boxscore scraper

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas
import requests
from time import sleep

'''
TO DO:
- Download school index
- Do I need to scrape each team's schedule to get game location?
- What other info do I need before I run this in full?

'''


def date_range(start_string, end_string): # start_string TO end_string, not THROUGH end_string
    start = datetime.strptime(start_string, "%m/%d/%Y")
    end = datetime.strptime(end_string, "%m/%d/%Y")
    for num_days in range(0, (end - start).days):
        yield((start + timedelta(num_days)))


def get_game_links(date):
    # expects datetime object input
    url = "http://www.sports-reference.com/cbb/boxscores/index.cgi?" + date.strftime(format="month=%-m&day=%-d&year=%Y")
    soup = BeautifulSoup(requests.get(url).text)
    game_links = ["http://www.sports-reference.com" + a["href"] for a in soup.find_all("a", text="Final")]
    return(game_links)


def _parse_team_ids(soup):
    team_hrefs = [a["href"] for a in soup.find_all("div", attrs={"class": "margin_top padding_top"})[0].find_all("a")]
    bbref_team_ids = [team_hrefs[i] for i in range(0, len(team_hrefs)) if "schools" in team_hrefs[i]]
    bbref_team_ids = [team[13:-10] for team in bbref_team_ids]  # [away_team, home_team] 
    return(bbref_team_ids)


def _parse_boxscore_stats(soup, team):
    basic_rows = soup.find_all("table", attrs={"id": team})[0].find_all("tr")[1:]
    basic_data = [[td.text for td in basic_rows[i].find_all("td")] for i in range(0, len(basic_rows)-1)]
    advanced_rows = soup.find_all("table", attrs={"id": team + "_advanced"})[0].find_all("tr")[1:]
    advanced_data = [[td.text for td in advanced_rows[i].find_all("td")] for i in range(0, len(advanced_rows)-1)]
    return(basic_data, advanced_data)


def _fill_boxscore_df(basic_data, advanced_data, basic_headers, advanced_headers, team, home_or_away):
    basic_df = pandas.DataFrame(basic_data, columns=basic_headers)
    advanced_df = pandas.DataFrame(advanced_data, columns=advanced_headers)
    try:
        df = pandas.merge(basic_df, advanced_df, on=["Starters", "MP"], how="inner")
    except KeyError:
        df = pandas.merge(basic_df, advanced_df, on=["Player", "MP"], how="inner")
        df.rename(columns={"$Player": "Starters"}, inplace=True)
    if home_or_away == "home":
        df["home"] = True
    else:
        df["home"] = False
    df["bbref_team_id"] = team
    return(df)


def get_boxscore(game_link, date):
    # expects datetime object input
    soup = BeautifulSoup(requests.get(game_link).text)
    away_team, home_team = _parse_team_ids(soup)
    basic_headers = [th.text for th in soup.find_all("table", attrs={"id": away_team})[0].find_all("th")[2:25]]
    advanced_headers = [th.text for th in soup.find_all("table", attrs={"id": away_team + "_advanced"})[0].find_all("th")[2:18]]
    away_basic_data, away_advanced_data = _parse_boxscore_stats(soup, away_team)
    home_basic_data, home_advanced_data = _parse_boxscore_stats(soup, home_team)
    away_df = _fill_boxscore_df(away_basic_data, away_advanced_data, basic_headers, advanced_headers, away_team, "away")
    home_df = _fill_boxscore_df(home_basic_data, home_advanced_data, basic_headers, advanced_headers, home_team, "home")
    boxscore = pandas.concat([away_df, home_df])
    boxscore["date"] = date.strftime(format="%-m/%-d/%Y")
    boxscore["game_id"] = away_team + "@" + home_team + "|" + date.strftime(format="%m%d%Y")
    matchup = away_team + " @ " + home_team + "   " + date.strftime(format="%-m-%-d-%Y")
    return(boxscore, matchup)


# -------------------------
start_string = "11/13/2015"
end_string = "11/14/2015"
SLEEP_TIME = 1
# -------------------------

date_generator = date_range(start_string, end_string)
boxscore_array = []
for date in date_generator:
    game_links = get_game_links(date)
    if game_links:
        for i in range(0, len(game_links)):
            boxscore, matchup = get_boxscore(game_links[i], date)
            boxscore_array.append(boxscore)
            print(matchup)
            sleep(SLEEP_TIME)
boxscores = pandas.concat(boxscore_array)
boxscores = boxscores.drop(boxscores.index[0:4])  # I don't understand why this is necessary, but it is
boxscores.to_csv("/Users/travistubbs/Desktop/boxscore_test.txt", sep="\t", index=False)



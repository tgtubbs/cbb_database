
from geopy.geocoders import Nominatim
import pandas

teams = pandas.read_csv('/Users/travistubbs/cbb_database/data/teams.txt', sep="\t")

geolocator = Nominatim()
latitude = []
longitude = []
for i in range(len(teams["City, State"])):
    location = geolocator.geocode(teams["City, State"][i])
    latitude.append(location.raw["lat"])
    longitude.append(location.raw["lon"])
    print(teams["School"][i] + ": " + location.raw["lat"] + ", " + location.raw["lon"])
teams["latitude"] = latitude
teams["longitude"] = longitude

teams.to_csv("/Users/travistubbs/cbb_database/data/teams.txt", sep="\t", index=False)

# clean and combine schedule data

library(data.table)
library(dplyr)

setwd("~/cbb_database/data/schedules/")
schedule_files <- list.files()
schedules <- lapply(schedule_files, read.delim, sep="\t")
lapply(schedules, dim)


# remove and rename columns
new_names <- c(
  "game_id",
  "date",
  "type",
  "site_operator",
  "conference",
  "points_for",
  "points_against",
  "overtime",
  "arena",
  "opponent_name",
  "team_name",
  "season"
)
names_to_remove <- c(
  "Time",
  "Network",
  "W",
  "L",
  "X.1",
  "Opponent",
  "Streak"
)
for (i in 1:length(schedules)) {
  schedules[[i]]$Opponent <- as.character(schedules[[i]]$Opponent)
  schedules[[i]]$opponent_bbref_id <- as.character(schedules[[i]]$opponent_bbref_id)
  for (j in 1:nrow(schedules[[i]])) {
    if (is.na(schedules[[i]]$opponent_bbref_id[j])) {
      id <- gsub(" ", "-", tolower(schedules[[i]]$Opponent[j]))
      id <- gsub("\\(", "", id)
      schedules[[i]]$opponent_bbref_id[j] <- gsub("\\)", "", id)
    }
  }
  schedules[[i]] <- schedules[[i]][, -which(names(schedules[[i]]) %in% names_to_remove)]
  colnames(schedules[[i]]) <- new_names
}
games <- as.data.frame(rbindlist(schedules))


# clean date
games$date <- as.character(games$date)
games$date <- substr(games$date, 6, nchar(games$date))
games$date <- as.Date(games$date, format="%b %d, %Y")


# subset conference affiliations
confs <- games %>%
  group_by(season, opponent_name) %>%
  summarize(
    conference = conference[1]
  )
write.table(confs, "~/cbb_database/data/conferences.txt", row.names=FALSE, col.names=TRUE, sep="\t")


# remove duplicate games
games$temp_id <- NA
games$team_name <- as.character(games$team_name)
games$opponent_name <- as.character(games$opponent_name)
games$date <- as.character(games$date)
for (i in 1:nrow(games)) {
  teams <- c(games$team_name[i], games$opponent_name[i])
  teams <- teams[order(teams)]
  games$temp_id[i] <- paste(teams[1], teams[2], games$date[i], sep="")
  print((i/nrow(games))*100)
}
length(unique(games$temp_id))/nrow(games)  # 0.5212 (slightly over 50% expected)
games <- games[!duplicated(games$temp_id),]
games <- games[,-which(colnames(games)=="temp_id")]


# home/away formatting
games[, 13:16] <- NA
colnames(games)[13:16] <- c(
  "home_team",
  "away_team",
  "home_points",
  "away_points"
)
for (i in 1:nrow(games)) {
  if (games$site_operator[i]=="@") {
    games$home_team[i] <- games$opponent_name[i]
    games$home_points[i] <- games$points_against[i]
    games$away_team[i] <- games$team_name[i]
    games$away_points[i] <- games$points_for[i]
  } else {
    games$home_team[i] <- games$team_name[i]
    games$home_points[i] <- games$points_for[i]
    games$away_team[i] <- games$opponent_name[i]
    games$away_points[i] <- games$points_against[i]
  }
}


# final clean-up
games <- games[, c(
  "game_id",
  "date",
  "season",
  "arena",
  "type",
  "home_team",
  "away_team",
  "home_points",
  "away_points",
  "overtime"
)]
games <- games[order(games$date), ]
games$overtime <- games$overtime=="OT"
game_ids <- 1:nrow(games)
games$game_id <- game_ids
write.table(games, "~/cbb_database/data/schedules/schedules_compiled.txt", sep="\t", row.names=FALSE)

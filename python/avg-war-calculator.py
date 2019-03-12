import csv
import statistics

with open('data/exclusives-avg-war.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    team = 'Rangers'
    team_seasons = 0
    team_war = 0
    player_wars = []

    teams = []

    for row in reader:
        if row['team'] == team:
            team_seasons += int(row['seasons'])
            team_war += float(row['war'])
            player_wars.append(float(row['war/season']))
        elif row['team'] != team:
            current_team = {
                "team": team,
                "total_seasons": team_seasons,
                "avg_war_per_season": round((team_war / team_seasons), 2),
                "median_war": round(statistics.median(player_wars), 2)
            }
            teams.append(current_team)

            team = row['team']
            team_seasons = int(row['seasons'])
            team_war = float(row['war'])
            player_wars = []
            player_wars.append(float(row['war/season']))
        elif row['name'] == reader[-1]['name']:
            current_team = {
                "team": team,
                "total_seasons": team_seasons,
                "avg_war_per_season": round((team_war / team_seasons), 2),
                "median_war": round(statistics.median(player_wars), 2)
            }
            teams.append(current_team)

    keys = teams[0].keys()

    with open('data/avg-war-per-team.csv', 'a') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(teams)
        output_file.close()

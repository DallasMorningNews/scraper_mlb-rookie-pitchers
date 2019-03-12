import pprint
import requests
import time
import csv
import random

from bs4 import BeautifulSoup, Comment

HEADERS = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'),
       'referer': 'https://stats.nba.com/players/traditional/'
      }

#todo:
# go through all_pitcher_list and pluck out pitchers who didn't play with the team they signed with first
# then collect stats for the pitchers who did play with that team

# create a list of all pitchers drafted by that team in that year that made the majors
all_pitcher_list = []

exclusive_pitchers = []

def get_pitchers(team):

    # for specified team in each draft from 2006 to 2018
    for year in range(2014, 2015):
        time.sleep(random.randint(3, 6))
        # get that team's draft results
        print(year)
        draft_request = requests.get("https://www.baseball-reference.com/draft/?team_ID={0}&year_ID={1}&query_type=franch_year&from_type_jc=0&from_type_hs=0&from_type_4y=0&from_type_unk=0".format(team, year))
        # parse the request with beautiful soup
        if draft_request.status_code != 200:
            print('ERROR!', draft_request.status_code)
            with open('data/missed.txt', 'a') as output_file:
                missed_year = team + " " + str(year)
                output_file.write(missed_year)
                output_file.close()


        request_content = BeautifulSoup(draft_request.text, "html.parser")
        # find the draft results table
        draft_table = request_content.find("table", {"id": "draft_stats"})
        # find all the rows in that table
        try:
            draft_rows = draft_table.find("tbody").findAll("tr")
        except AttributeError:
            continue

        # iterate over the rows
        for row in draft_rows:
            # find all the cells for each row
            player_cells = row.findAll("td")
            # find the links in the "name" column. two links indicates the player has a
            # major league details page on baseball reference
            links = player_cells[6].findAll("a")

            # check if player made majors (2 links), has "HP" in his position column, and "Y"
            # in his signed column
            if len(links) == 2 and len(player_cells[14].text) > 0:
                # create a dict for that pitcher and populate it with top line info
                pitcher = {}
                pitcher["name"] = links[0].text
                if team == "ANA":
                    pitcher["short_team"] = "LAA"
                elif team == "TBD":
                    pitcher["short_team"] = "TBR"
                elif year >= 2009 and team == "FLA":
                    pitcher["short_team"] = "MIA"
                else:
                    pitcher["short_team"] = team
                pitcher["team"] = player_cells[4].text
                pitcher["drafted"] = year
                pitcher["url"] = links[0]["href"]
                pitcher["handed"] = player_cells[7].text

                # add that pitcher to the list of all pitchers
                all_pitcher_list.append(pitcher)

def find_exclusives(pitcher):

    player_url = "https://www.baseball-reference.com" + pitcher['url']
    pitcher_request = requests.get(player_url)
    pitcher_content = BeautifulSoup(pitcher_request.text, "html.parser")
    pitcher_stats_table = pitcher_content.find("table", {"id": "pitching_standard"})
    try:
        pitcher_rows = pitcher_stats_table.find("tbody").findAll("tr")
    except AttributeError:
        pitcher_rows = []

    mlb_rows = []
    value_rows = []

    for item in pitcher_content.find_all(text=lambda text:isinstance(text, Comment)):
        data = BeautifulSoup(item,"html.parser")
        pitcher_value_table = data.find_all("table", {"id": "pitching_value"})
        if len(pitcher_value_table) > 0:
            pitcher_value_rows = pitcher_value_table[0].findAll('tr', {"class": "full"})
            for row in pitcher_value_rows:
                value_rows.append(row)

    for row in pitcher_rows:
        cells = row.findAll('td')
        team_links = cells[1].findAll('a')
        if len(team_links) >= 1:
            mlb_rows.append(row)

    pitcher_meta = pitcher_content.find('div', {'id': 'meta'})

    try:
        pitcher_graphs = pitcher_meta.findAll("p")
    except AttributeError:
        pitcher_graphs = []

    for graph in pitcher_graphs:
        if 'Position' in graph.text:
            graph_text = graph.text.split(':')

        if 'Draft:' in graph.text:
            draft_text = graph.text.split('Draft')

    if len(mlb_rows) > 0 and 'Pitcher' in graph_text[1] and pitcher["team"] in draft_text[len(draft_text) - 2]:
        rookie_cells = mlb_rows[0].findAll("td")
        print(pitcher["team"])
        print(pitcher["short_team"])
        print(rookie_cells[1].text)
        if pitcher["short_team"] in rookie_cells[1].text:
            pprint.pprint("WE HIT A PLAYER!!!!!")
            wins = 0
            losses = 0
            games = 0
            games_started = 0
            whole_innings_pitched = 0
            partial_innings_pitched = 0
            hits = 0
            runs = 0
            earned_runs = 0
            home_runs = 0
            base_on_balls = 0
            strikeouts = 0
            war = 0

            for row in mlb_rows:
                season_cells = row.findAll("td")
                if pitcher["short_team"] in season_cells[1].text:
                    wins += int(season_cells[3].text)
                    losses += int(season_cells[4].text)
                    games += int(season_cells[7].text)
                    games_started += int(season_cells[8].text)
                    whole_innings_pitched += float(season_cells[13].text.split(".")[0])
                    partial_innings_pitched += float(season_cells[13].text.split(".")[1])
                    hits += int(season_cells[14].text)
                    runs += int(season_cells[15].text)
                    earned_runs += int(season_cells[16].text)
                    home_runs += int(season_cells[17].text)
                    base_on_balls += int(season_cells[18].text)
                    strikeouts += int(season_cells[20].text)
                elif "TOT" in season_cells[1].text:
                    continue
                else:
                    break

            for row in value_rows:
                print(row)
                season_value_cells = row.findAll("td")
                print(season_value_cells)
                if pitcher["short_team"] in season_value_cells[1].text:
                    try:
                        war += float(season_value_cells[17].text)
                    except ValueError:
                        war += 0

            pitcher["W"] = wins
            pitcher["L"] = losses
            pitcher["G"] = games
            pitcher["GS"] = games_started

            innings_pitched = whole_innings_pitched + (partial_innings_pitched / 3)
            pitcher["IP"] = innings_pitched
            pitcher["H"] = hits
            pitcher["R"] = runs
            pitcher["ER"] = earned_runs

            if innings_pitched == 0 and earned_runs > 0:
                pitcher["ERA"] = "inf"
            else:
                pitcher["ERA"] = round(((earned_runs / innings_pitched) * 9), 2)
            pitcher["HR"] = home_runs
            pitcher["BB"] = base_on_balls
            pitcher["K"] = strikeouts
            pitcher["war"] = round(war, 1)

            pprint.pprint(pitcher)
            exclusive_pitchers.append(pitcher)



# teams=["ANA", "HOU", "OAK", "TOR", "ATL", "MIL", "STL", "CHC", "TBD", "ARI", "LAD", "SFG",
#         "CLE", "SEA", "FLA", "NYM", "WSN", "BAL", "SDP", "PHI", "PIT", "TEX", "BOS", "CIN", "COL",
#         "KCR", "DET", "MIN", "CHW", "NYY",]
teams=["MIN"]
# teams=["TEX"]

for team in teams:
    print(team)
    get_pitchers(team)

    for pitcher in all_pitcher_list:
        print(pitcher["name"])
        find_exclusives(pitcher)
        time.sleep(random.randint(3, 5))

    toCSV = exclusive_pitchers
    keys = toCSV[0].keys()


    with open('data/exclusives-war.csv', 'a') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(toCSV)
        output_file.close()

    exclusive_pitchers = []
    all_pitcher_list = []

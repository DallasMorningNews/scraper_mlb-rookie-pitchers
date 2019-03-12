import pprint
import csv
import math

team_totals = []

with open('./data/exclusives-war.csv', mode='r') as pitchers:
    reader = csv.reader(pitchers)



    teams=["LAA", "HOU", "OAK", "TOR", "ATL", "MIL", "STL", "CHC", "TBR", "ARI", "LAD", "SFG",
            "CLE", "SEA", "FLA", "NYM", "WSN", "BAL", "SDP", "PHI", "PIT", "TEX", "BOS", "CIN", "COL",
            "KCR", "DET", "MIN", "CHW", "NYY"]

    for team in teams:
        team_totaled = {}
        team_totaled["team"] = team
        team_totaled["total"] = 0
        team_totaled["games"] = 0
        team_totaled["gs"] = 0
        team_totaled["ip"] = 0
        team_totaled["w"] = 0
        team_totaled["l"] = 0
        team_totaled["h"] = 0
        team_totaled["r"] = 0
        team_totaled["er"] = 0
        team_totaled["era"] = 0
        team_totaled["k"] = 0
        team_totaled["bb"] = 0
        team_totaled["hr"] = 0
        team_totaled["war"] = 0

        for row in reader:
            if row[16] == team or (team == "FLA" and row[16] == "MIA"):
                team_totaled["total"] += 1
                team_totaled["games"] += int(row[4])
                team_totaled["gs"] += int(row[2])
                team_totaled["ip"] += float(row[6])
                team_totaled["w"] += int(row[14])
                team_totaled["l"] += int(row[8])
                team_totaled["h"] += int(row[7])
                team_totaled["r"] += int(row[12])
                team_totaled["er"] += int(row[18])
                team_totaled["k"] += int(row[17])
                team_totaled["bb"] += int(row[1])
                team_totaled["hr"] += int(row[11])
                team_totaled["war"] += float(row[10])

        print(row, team, team_totaled['ip'], team_totaled['er'])
        team_totaled['ip'] = math.floor(team_totaled['ip'] * 10) / 10
        team_totaled['era'] = round(9 * (team_totaled["er"] / team_totaled["ip"]), 2)
        print(team_totaled)
        team_totals.append(team_totaled)
        pitchers.seek(0)

    print(team_totals)

    keys = team_totals[0].keys()

    with open('data/totals.csv', 'a') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(team_totals)
        output_file.close()

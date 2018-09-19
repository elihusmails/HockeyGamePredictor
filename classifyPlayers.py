import csv
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import json

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

def normalize(data):
    for i, f in data.iterrows():
        data.set_value(i, 'Goals', 60 * f[4] / f[9])
        data.set_value(i, 'Assists', 60 * f[5] / f[9])
        data.set_value(i, 'Points', 60 * f[6] / f[9])
        data.set_value(i, 'PM', 60 * f[7] / f[9])
        data.set_value(i, 'PIM', 60 * f[8] / f[9])
        data.set_value(i, 'Blocks', 60 * f[10] / f[9])
        data.set_value(i, 'Hits', 60 * f[11] / f[9])

    means = [np.mean(data['Goals']), np.mean(data['Assists']),
             np.mean(data['Points']), np.mean(data['PM']),
             np.mean(data['PIM']), np.mean(data['Blocks']),
             np.mean(data['Hits'])]
    std_dev = [np.std(data['Goals']), np.std(data['Assists']),
               np.std(data['Points']), np.std(data['PM']),
               np.std(data['PIM']), np.std(data['Blocks']),
               np.std(data['Hits'])]

    for i, f in data.iterrows():
        data.set_value(i, 'Goals', (f[4] - means[0]) / std_dev[0])
        data.set_value(i, 'Assists', (f[5] - means[1]) / std_dev[1])
        data.set_value(i, 'Points', (f[6] - means[2]) / std_dev[2])
        data.set_value(i, 'PM', (f[7] - means[3]) / std_dev[3])
        data.set_value(i, 'PIM', (f[8] - means[4]) / std_dev[4])
        data.set_value(i, 'Blocks', (f[10] - means[5]) / std_dev[5])
        data.set_value(i, 'Hits', (f[11] - means[6]) / std_dev[6])

    return data


def import_goalies(goalieFile):
    
    with open(goalieFile) as gf:
        gfResults = json.load(gf)
        data = gfResults['data']

    goalieData = json.dumps(data)
    goalieDataFrame = pd.read_json(goalieData)

    goalies = []
    for i, r in goalieDataFrame.iterrows():

        wins = r['wins']
        games = r['gamesPlayed']

        row = [
            r['playerName'], 
            r['playerTeamsPlayedFor'], 
            float(r['savePctg']),
            float(r['goalsAgainstAverage']), 
            float(r['shutouts']), 
            float(r['timeOnIce']),
            float(r['wins']),
            float(r['gamesPlayed']),
            float( wins / games)
        ]
        goalies.append(row)

    title = ['player', 'team', 'savePctg', 'gaa', 'so', 'toi', 'wins', 'games', 'winPct']
    goalie_df = pd.DataFrame(goalies, columns=title)
    dims = goalie_df[['savePctg', 'gaa', 'so', 'toi', 'wins', 'games']]
    k_means = KMeans(n_clusters=3).fit(dims)
    centers = k_means.cluster_centers_

    mapping = [0,0,0]
    max_toi = 0
    toi_index = 0
    max_wins = 0
    wins_index = 0
    max_games = 0
    games_index = 0

    for i, center in enumerate(centers):
        # if center[0] > max_sp:
        #     max_sp = center[0]
        #     sp_index = 1
        # if center[1] > max_gaa:
        #     max_gaa = center[1]
        #     gaa_index = 1
        # if center[2] > max_so:
        #     max_so = center[2]
        #     so_index = 1
        if center[3] > max_toi:
            max_toi = center[3]
            toi_index = 1
        if center[4] > max_wins:
            max_wins = center[4]
            wins_index = 1
        if center[5] > max_games:
            max_games = center[5]
            games_index = 1

    mapping[toi_index] = 0
    mapping[wins_index] = 1
    mapping[games_index] = 2

    # 0:toi, 1:wins, 2:games
    goalie_df['Type'] = list(map(lambda x: mapping[x], k_means.labels_))

    # print( goalie_df.to_string())

    starters = goalie_df[goalie_df['Type'] == 0]
    # starters = starters[starters['wins'] > 20]
    return starters.sort_values(by='winPct', ascending=False)

def import_player_file(playerStatsFile, addlStatsFile):

    with open(playerStatsFile) as psf:
        psfResults = json.load(psf)
        data = psfResults['data']

    psfData = json.dumps(data)
    psfDataFrame = pd.read_json(psfData)

    with open(addlStatsFile) as addlStatsJson:
        addStatsResults = json.load(addlStatsJson) 
        addlData = addStatsResults['data']
    
    theData = json.dumps(addlData)
    addlDataFrame = pd.read_json(theData)

    forwards = []
    defence = []

    # for row in reader:
    row = {}

    for i, r in psfDataFrame.iterrows():
        try:
            row['gp'] = float(r['gamesPlayed'])  # games played
            row['goals'] = float(r['goals'])  # goals
            row['assists'] = float(r['assists'])  # assists
            row['points'] = float(r['points'])  # points
            row['plus'] = float(r['plusMinus'])  # plus minus
            row['pim'] = float(r['penaltyMinutes'])  # penalty minutes
            row['toi'] = float(r['timeOnIcePerGame'])  # time on ice

            player = addlDataFrame[addlDataFrame['playerId'] == r['playerId']]
            if player.empty:
                continue

            if player.shape[0] > 1:
                player = player.iloc[0]

            # row[blocks] = float(row[blocks])  # blocks
            # row[hits] = float(row[hits])  # hits
            row['blocks'] = float(player['blockedShots'])
            row['hits'] = float(player['hits'] )
            row['team'] = player['playerTeamsPlayedFor'].iloc[0]
            row['name'] = player['playerName'].iloc[0]
            row['pos'] = player['playerPositionCode'].iloc[0]
            row['gp'] = float(player['gamesPlayed'])

            # if nat != 0:
            #     row[nat] = float(row[nat])  # nat
            row['nat'] = float(0)
        except ValueError:
            continue

        rr = [row['team'], row['name'], row['pos'], row['gp'], row['goals'], row['assists'], row['points'],
                row['plus'], row['pim'], row['toi'], row['blocks'], row['hits']]

        # if (row['gp'] > 10) & (('nat' == 0) | (row['nat'] == 0) | (row['nat'] == 2)) & ('D' not in row['pos']):
        #     forwards.append(rr)
        # elif (row['gp'] > 10) & (('nat' == 0) | (row['nat'] == 0) | (row['nat'] == 2)) & ('D' in row['pos']):
        #     defence.append(rr)

        if 'D' not in rr[2]:
            forwards.append(rr)
        elif 'D' in rr[2]:
            defence.append(rr)

    title = ['Team', 'Player', 'Pos', 'GP', 'Goals', 'Assists', 'Points', 'PM', 'PIM', 'TOI', 'Blocks', 'Hits']
    forward_df = normalize(pd.DataFrame(forwards, columns=title))
    dims = forward_df[['Goals', 'Assists', 'PM', 'PIM', 'Blocks', 'Hits']]
    k_means = KMeans(n_clusters=4).fit(dims)
    centers = k_means.cluster_centers_

    # top-line = 0, second = 1, def = 2, phys = 3
    mapping = [0, 0, 0, 0]
    max_goals = 0
    goals_index = 0
    max_blocks = 0
    blocks_index = 0
    max_hits = 0
    hits_index = 0
    max_hits_2 = 0
    hits_index_2 = 0
    for i, center in enumerate(centers):
        if center[0] > max_goals:
            max_goals = center[0]
            goals_index = i
        if center[4] > max_blocks:
            max_blocks = center[4]
            blocks_index = i
        if center[5] > max_hits:
            max_hits_2 = max_hits
            hits_index_2 = hits_index
            max_hits = center[5]
            hits_index = i
        elif center[5] > max_hits_2:
            max_hits_2 = center[5]
            hits_index_2 = i

    if hits_index == blocks_index:
        blocks_index = hits_index_2

    assert goals_index != blocks_index
    assert goals_index != hits_index
    assert hits_index != blocks_index
    second_index = 0
    for j in range(4):
        if (j == goals_index) | (j == hits_index) | (j == blocks_index):
            continue
        else:
            second_index = j
            break
    mapping[goals_index] = 0
    mapping[second_index] = 1
    mapping[blocks_index] = 2
    mapping[hits_index] = 3
    forward_df['Type'] = list(map(lambda x: mapping[x], k_means.labels_))
    defence_df = normalize(pd.DataFrame(defence, columns=title))
    dims = defence_df[['Points', 'PM', 'PIM', 'Blocks', 'Hits']]
    k_means = KMeans(n_clusters=4).fit(dims)
    centers = k_means.cluster_centers_
    # offencive = 0, defencive = 1, average = 2, phys = 3
    mapping = [0, 0, 0, 0]
    max_points = 0
    points_index = 0
    max_blocks = 0
    blocks_index = 0
    max_hits = 0
    hits_index = 0
    max_hits_2 = 0
    hits_index_2 = 0
    for i, center in enumerate(centers):
        if center[0] > max_points:
            max_points = center[0]
            points_index = i
        if center[3] > max_blocks:
            max_blocks = center[3]
            blocks_index = i
        if center[4] > max_hits:
            max_hits_2 = max_hits
            hits_index_2 = hits_index
            max_hits = center[4]
            hits_index = i
        elif center[4] > max_hits_2:
            max_hits_2 = center[4]
            hits_index_2 = i

    if hits_index == blocks_index:
        blocks_index = hits_index_2

    assert points_index != blocks_index
    assert points_index != hits_index
    assert hits_index != blocks_index
    average_index = 0
    for j in range(4):
        if (j == points_index) | (j == hits_index) | (j == blocks_index):
            continue
        else:
            average_index = j
            break
    mapping[points_index] = 0
    mapping[blocks_index] = 1
    mapping[average_index] = 2
    mapping[hits_index] = 3
    defence_df['Type'] = list(map(lambda x: mapping[x], k_means.labels_))
    # print(defence_df)

    return {'forward': forward_df.sort_values(by='GP', ascending=False),
            'defence': defence_df.sort_values(by='GP', ascending=False)}




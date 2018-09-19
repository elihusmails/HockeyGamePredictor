import pandas as pd
import json
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
#from sklearn.datasets import make_classification
import matplotlib.pyplot as plt
from HockeyTeam import Team
from sklearn import tree
import classifyPlayers as cp

teams = dict()
data = []
teamGameHistoryWindow = 5

players = {'2017': cp.import_player_file('player-summary-20172018.json', 'player-bks_hits.json')}

# print( type(players) )
# print( players )

with open('2017-18-game-results.json') as results:
    resultsData = json.load(results)
    data = resultsData['data']
    
#############################
####  Load the Team data  ###
#############################

# Sort the data list based on gameId
sortedList = sorted(data, key=lambda k: k['gameId'])

for d in sortedList:
    # print(d['gameId'])
    teamName = d['teamAbbrev']
    opponentName = d['opponentTeamAbbrev']

    if teamName in teams:
        team = teams[teamName]
    else:
        team = Team(teamName)

    if opponentName in teams:
        opponent = teams[opponentName]
    else:
        opponent = Team(opponentName)

    # Goals
    team.goalsFor.append(d['goalsFor'])
    team.goalsAgainst.append(d['goalsAgainst'])

    # Update shots count
    team.teamShotsFor.append(d['shotsFor'])
    opponent.teamShotsFor.append(d['shotsAgainst'])
    team.teamShotsAgainst.append(d['shotsAgainst'])
    opponent.teamShotsAgainst.append(d['shotsAgainst'])

    # Update faceoff count
    team.teamFaceoffWon.append(d['faceoffsWon'])
    opponent.teamFaceoffWon.append(d['faceoffsLost'])
    team.teamFaceoffLost.append(d['faceoffsLost'])
    opponent.teamFaceoffLost.append(d['faceoffsWon'])
    
    # Update win/loss/OT loss
    team.updateWinLossTie(win=d['wins'], loss=d['losses'], otloss=d['otLosses'])
    opponent.updateWinLossTie(loss=d['wins'], win=d['losses'], otloss=d['otLosses']*-1)

    # Special Teams
    # Not sure how to get SH goals
    team.powerplays.append(d['ppOpportunities'])    # On PP
    opponent.powerplays.append(d['shNumTimes'])

    team.shorthanded.append(d['shNumTimes'])        # On PK
    opponent.shorthanded.append(d['ppOpportunities'])

    team.ppGoals.append(d['ppGoalsFor'])            # PP Goals
    opponent.ppGoals.append(d['ppGoalsAgainst'])

    team.shGoals.append(d['ppGoalsAgainst'])        # PK Goals given up
    opponent.shGoals.append(d['ppGoalsFor'])

    teams[teamName] = team
    teams[opponentName] = opponent

#################################
####  End Load the Team data  ###
#################################

# Calculate and print PDO values for teams
# teamPdo = dict()
# for tx in teams:
#     team = teams[tx]
#     teamPdo[tx] = team.getTeamPDO()
# print( sorted(teamPdo.items(), key=lambda kv: kv[1]) )

### Load goalie data
goalies = cp.import_goalies('2017-18_goalies.json')

### Load the player data in the team data
for t in teams:
    p = players['2017']  # players from year
    f = p['forward']    # forwards
    d = p['defence']    # defensemen
    f = f[(f['Team'] == t) | (f['Team'] == t.capitalize())]   # forwards for a team
    d = d[(d['Team'] == t) | (d['Team'] == t.capitalize())]   # defensemen for a team
    if (len(f.index) < 12) | (len(d.index) < 6):  # not enough data
        continue
        
    fTypes = f['Type']      # top-line = 0, second = 1, def = 2, phys = 3
    dTypes = d['Type']      # top-line = 0, second = 1, def = 2, phys = 3
    forwards = [0, 0, 0, 0]
    defence = [0, 0, 0, 0]
    for i, pType in enumerate(fTypes):
        if i < 12:
            forwards[pType] += 1
    for i, pType in enumerate(dTypes):
        if i < 6:
            defence[pType] += 1

    # forwards.extend(defence)
    # t.extend(forwards)
    # advancedTeams.append(t)

    team = teams[t]

    team.topLine = forwards[0]
    team.secondLine = forwards[1]
    team.defForward = forwards[2]
    team.physForward = forwards[3]
    team.offDefence = defence[0]
    team.defDefence = defence[1]
    team.avDefence = defence[2]
    team.physDefence = defence[3]

    goalie = goalies[goalies['team'] == t]
    if goalie.empty:
        print('TEAM HAS NO GOALIES == ' + t)
    else:
        goalie = goalie.iloc[0]
        # print( goalie )

        team.goalieSavePct = goalie['savePctg']
        team.goalieWins = goalie['wins']
        team.goalieGaa = goalie['gaa']

gameData = pd.DataFrame.from_dict(data, orient='columns').sort_values(by='gameId', ascending=True)

# Make sure we have an even number of games.
# There's an entry for each home and away team 
# per game.
assert len(gameData) %2 == 0

# Slice out every other game record.
theGameData = gameData.iloc[::2, :]

records = pd.DataFrame()

for index,row in gameData.iterrows():

    teamName = row['teamAbbrev']
    opponentName = row['opponentTeamAbbrev']
    if teamName in teams:
        team = teams[teamName]
    else:
        team = Team(teamName)

    if opponentName in teams:
        opponent = teams[opponentName]
    else:
        opponent = Team(opponentName)


    goalsFor = row['goalsFor']
    goalsAgainst = row['goalsAgainst']
    
    if goalsFor > goalsAgainst:
        # Home team won
        winningTeam = row['teamAbbrev']
        losingTeam = row['opponentTeamAbbrev']
        homeTeamWon = True
    else:
        winningTeam = row['opponentTeamAbbrev']
        winningTeam = row['teamAbbrev']
        homeTeamWon = False

    records = records.append({
        # 'winningTeam':winningTeam,
        # 'losingTeam': losingTeam,
        # 'goals': goalsFor - goalsAgainst,
        'fo': row['faceoffWinPctg'],
        'ppg': row['ppGoalsFor'] - row['ppGoalsAgainst'],
        'shots': row['shotsFor'] - row['shotsAgainst'],
        'ppp': row['ppPctg'],
        'ppk': row['penaltyKillPctg'],
        
        # # Team stats for the season
        'teamWinLoss': team.getWinsWindow(teamGameHistoryWindow),
        'teamWinPct': team.getTeamWinPctWindow(teamGameHistoryWindow),
        'teamShotsFor': team.getShotsForWindow(teamGameHistoryWindow),
        'teamShotsAgainst': team.getShotsAgainstWindow(teamGameHistoryWindow),
        'teamPPgoals': team.getPowerPlayGoalsWindow(teamGameHistoryWindow),
        
        'topLine': team.topLine,
        'secondLine': team.secondLine,
        'defForward': team.defForward,
        'physForward': team.physForward,
        'offDefence': team.offDefence,
        'defDefence': team.defDefence,
        'avDefence': team.avDefence,
        'physDefense': team.physDefence,

        'goalieSvPct': team.goalieSavePct,
        'goalieWins': team.goalieWins,
        'goalieGaa': team.goalieGaa,

        'pdo': team.getTeamPDO(),

        'win': np.where(goalsFor > goalsAgainst, True, False),
        # 'is_train': np.random.uniform(0, 1) <= .9
    }, ignore_index=True)

total = 0
count = 0
accuracy = []

records['is_train'] = np.random.uniform(0, 1, len(records)) <= .75   
train, test = records[records['is_train'] == True], records[records['is_train'] == False]

#print( records.head(5) )

print('Number of observations in the training data:', len(train))
print('Number of observations in the test data:', len(test))

clf = tree.DecisionTreeClassifier() #n_jobs=2, n_estimators=15, random_state=0)

features = records.columns[:22]
# print("Features: ", features)

trainWin = train['win'].apply(pd.to_numeric)
clf.fit(train[features], trainWin)

prediction = clf.predict(test[features])
# print( test['win'])
# print( prediction )
#print(clf.predict_proba(test[features]))

for i, j in zip(prediction, test['win']):
    total += 1
    if i == j:
        count += 1

ratio = count / total
print( "Percentage guess correct: {}".format(ratio) )
importances = list(zip(train[features], clf.feature_importances_))
for impt in importances:
    print( impt[0] + "\t\t" + str(impt[1]) )

# print(list(zip(train[features], clf.feature_importances_)))
print(accuracy)

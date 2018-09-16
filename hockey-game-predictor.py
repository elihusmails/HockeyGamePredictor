import pandas as pd
import json
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
import matplotlib.pyplot as plt
from HockeyTeam import Team
from sklearn import tree

teams = dict()
data = []
teamGameHistoryWindow = 5

with open('data/2017-18-game-results.json') as results:
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

    # Update shots count
    team.teamShotsFor.append(d['shotsFor'])
    opponent.teamShotsFor.append(d['shotsAgainst'])
    team.teamShotsAgainst.append(d['shotsAgainst'])
    opponent.teamShotsAgainst.append(d['shotsFor'])

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


gameData = pd.DataFrame.from_dict(data, orient='columns').sort_values(by='gameId', ascending=True)

# Make sure we have an even number of games.
# There's an entry for each home and away team 
# per game.
assert len(gameData) %2 == 0

# Slice out every other game record.
theGameData = gameData.iloc[::2, :]

records = pd.DataFrame()

for index,row in theGameData.iterrows():

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

features = records.columns[:10]
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
print( ratio )
print(list(zip(train[features], clf.feature_importances_)))
# print(accuracy)

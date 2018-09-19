# HockeyGamePredictor
Predict the winner of an NHL hockey game

Data is mostly from the nhl.com stats webpage.  

### Skater information
http://www.nhl.com/stats/rest/skaters?isAggregate=false&reportType=basic&isGame=false&reportName=skatersummary&sort=[{%22property%22:%22points%22,%22direction%22:%22DESC%22},{%22property%22:%22goals%22,%22direction%22:%22DESC%22},{%22property%22:%22assists%22,%22direction%22:%22DESC%22}]&cayenneExp=gameTypeId=2%20and%20seasonId%3E=20172018%20and%20seasonId%3C=20172018

http://www.nhl.com/stats/rest/skaters?isAggregate=true&reportType=basic&isGame=false&reportName=skatersummary&sort=[{%22property%22:%22points%22,%22direction%22:%22DESC%22}]&cayenneExp=gameTypeId=2and%20seasonId%3E=20172018and%20seasonId%3C=20172018

http://www.nhl.com/stats/rest/skaters?isAggregate=false&reportType=basic&isGame=true&reportName=skatersummary&sort=[{%22property%22:%22points%22,%22direction%22:%22DESC%22},{%22property%22:%22goals%22,%22direction%22:%22DESC%22},{%22property%22:%22assists%22,%22direction%22:%22DESC%22}]&cayenneExp=gameDate%3E=%222017-10-04%22%20and%20gameDate%3C=%222018-03-18%22%20and%20gameTypeId=2

### Blocks/hits 
http://www.nhl.com/stats/rest/skaters?isAggregate=false&reportType=basic&isGame=false&reportName=realtime&sort=[{%22property%22:%22hits%22,%22direction%22:%22DESC%22}]&cayenneExp=gameTypeId=2%20and%20seasonId%3E=20172018%20and%20seasonId%3C=20172018

### Team Summary Report
http://www.nhl.com/stats/rest/team?isAggregate=false&reportType=basic&isGame=false&reportName=teamsummary&sort=[{%22property%22:%22points%22,%22direction%22:%22DESC%22},{%22property%22:%22wins%22,%22direction%22:%22DESC%22}]&cayenneExp=gameTypeId=2%20and%20seasonId%3E=20172018%20and%20seasonId%3C=20172018

### Team game summaries
http://www.nhl.com/stats/rest/team?isAggregate=false&reportType=basic&isGame=true&reportName=franchisesummary&sort=[{%22property%22:%22points%22,%22direction%22:%22DESC%22},{%22property%22:%22wins%22,%22direction%22:%22DESC%22}]&cayenneExp=gameDate%3E=%222017-10-04%22%20and%20gameDate%3C=%222018-04-09%22%20and%20gameTypeId=2

http://www.nhl.com/stats/rest/team?isAggregate=false&reportType=basic&isGame=true&reportName=teamsummary&sort=[{%22property%22:%22points%22,%22direction%22:%22DESC%22},{%22property%22:%22wins%22,%22direction%22:%22DESC%22}]&cayenneExp=gameDate%3E=%222017-10-04%22%20and%20gameDate%3C=%222018-04-09%22%20and%20gameTypeId=2

### Single season team stats 
https://statsapi.web.nhl.com/api/v1/teams/15/stats

### Goalie stats
http://www.nhl.com/stats/rest/goalies?isAggregate=false&reportType=goalie_basic&isGame=false&reportName=goaliesummary&sort=[{%22property%22:%22wins%22,%22direction%22:%22DESC%22}]&cayenneExp=gameTypeId=2%20and%20seasonId%3E=20172018%20and%20seasonId%3C=20172018

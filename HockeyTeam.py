import math

class Team(object):

    window = 10

    def __init__(self, teamName):
        self.teamName = teamName

        # Shots
        self.teamShotsFor = []
        self.teamShotsAgainst = []

        # Faceoffs
        self.teamFaceoffWon = []
        self.teamFaceoffLost = []

        # Goals
        self.goalsFor = []
        self.goalsAgainst = []

        # Record
        self.record = []

        # Special Teams
        self.powerplays = []
        self.shorthanded = []
        self.ppGoals = []
        self.shGoals = []

        # Calculated player weights
        self.topLine = 0
        self.secondLine = 0
        self.defForward = 0
        self.physForward = 0
        self.offDefence = 0
        self.defDefence = 0
        self.avDefence = 0
        self.physDefence = 0

        # Calculated goalie weights
        self.goalieSavePct = 0
        self.goalieWins = 0
        self.goalieGaa = 0
        

    def getTeamName(self): return self.teamName

    # Win / Loss / OT Loss functions
    def getWinsWindow(self, x=window): return self.record[(x*-1):].count('w')
    def getLossesWindow(self, x=window): return self.record[(x*-1):].count('l')
    def getOtlWindow(self, x=window): return self.record[(x*-1):].count('otl')
    def getTotalWins(self): return self.record.count('w')
    def getTotalLosses(self): return self.record.count('l')
    def getTotalOtLosses(self): return self.record.count('otl')
    def getTeamWinPctWindow(self, x=window): return self.getWinsWindow(x) / x
    def getWinLossTie(self): return self.record
    def updateWinLossTie(self, win=0, loss=0, otloss=0):
        if win == 1:
            self.record.append('w')
        if loss == 1:
            self.record.append('l')
        if otloss == 1:
            self.record.append('otl')

    # Shots functions
    def getTeamShotsFor(self): return self.teamShotsFor
    def getTeamShotsAgainst(self): return self.teamShotsAgainst
    def getShotsForWindow(self, x=window): return sum(self.teamShotsFor[(x*-1):])
    def getShotsAgainstWindow(self, x=window): return sum(self.teamShotsAgainst[(x*-1):])

    # Faceoff functions
    def getTeamFaceoffWon(self): return self.teamFaceoffWon
    def getTeamFaceoffLost(self): return self.teamFaceoffLost
    def getTeamFaceoffWonWindow(self, x=window): return sum(self.teamFaceoffWon[(x*-1):])
    def getTeamFaceoffLostWindow(self, x=window): return sum(self.teamFaceoffLost[(x*-1):])
    def getFaceoffWinPctWindow(self, x=window):
        foWins = sum(self.teamFaceoffWon[(x*-1):])
        foLosses = sum(self.teamFaceoffLost[(x*-1):])
        return foWins/(foWins+foLosses)

    # Special Teams functions
    def getPowerPlayGoalsWindow(self, x=window):
        pp = sum(self.powerplays[(x*-1):])
        ppgoals = sum(self.ppGoals[(x*-1):])
        return pp/(pp+ppgoals)

    def getShorthandedGoalsWindow(self, x=window):
        sh = sum(self.shorthanded[(x*-1):])
        shgoals = sum(self.shGoals[(x*-1):])
        return sh/(sh+shgoals)

    def getSpecialTeamRateWindow(self, x=window):
        pp = sum(self.powerplays[(x*-1):])
        sh = sum(self.shorthanded[(x*-1):])
        return pp/(pp+sh)

    def getTeamPDO(self):
        totalShots = sum(self.teamShotsFor)
        totalGoals = sum(self.goalsFor)
        shootingPercentage = totalGoals / totalShots

        shotsAgainst = sum(self.teamShotsAgainst)
        goalsAgainst = sum(self.goalsAgainst)
        savePercentage = 1 - (goalsAgainst / shotsAgainst)

        pdo = shootingPercentage + savePercentage
        
        # return (pdo ** 2) * 100
        return math.log(pdo) * 1000
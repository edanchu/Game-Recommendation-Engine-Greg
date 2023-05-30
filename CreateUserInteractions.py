import pickle
import numpy as np
import pandas as pd

#Generates the user interaction matrices for use in matrix factorization. Sparse matrix is of the form
# User, Game, Rating. Dense matrix has one row per use and one column per game where the value for a cell is the rating a player
#gave to that game, or 0 if no interaction
#Ratings are estimated based on the technique here https://www.researchgate.net/publication/330249306_Estimated_Rating_Based_on_Hours_Played_for_Video_Game_Recommendation


def getCleanData(usersData, gameLocDict):
    #cleans out useless data from the database
    #removes top 2% of players by playtime for each game to get rid of outliers
    #removes all games that appear less than 20 times or have a sum total of less than 300 hours played
    #over all players
    userGameHours = []
    gameHours = {}
    gameCounts = {}
    for user, data in usersData.items():
        if data == "Private": continue
        for game, hours in data.items():
            if(game not in gameLocDict): continue
            if (game not in gameHours): gameHours[game] = 0
            if (game not in gameCounts): gameCounts[game] = 0
            gameCounts[game] += 1
            gameHours[game] += hours
    for user, data in usersData.items():
        if data == "Private": continue
        for game, hours in data.items():
            if(game not in gameLocDict or gameHours[game] < 300 or gameCounts[game] < 20): continue
            userGameHours.append((user, game, hours/60))
    df = pd.DataFrame(data=userGameHours, index=range(len(userGameHours)), columns=["user", "game", "hours"], dtype=pd.Int64Dtype)
    def Remove_Outlier_Indices(df):
        # Q1 = np.percentile(df, 0.25)
        # Q3 = np.percentile(df, 0.75)
        # IQR = Q3 - Q1
        # dropList = (df > (Q3 + 1.5 * IQR))
        return df < np.percentile(df, 90)

    grouped = df[["game", "hours"]].groupby(by="game")
    res = grouped.apply(Remove_Outlier_Indices)

    res2 = res.reset_index(level=0, drop=True)
    res2[res2["hours"] == True]["hours"].index.values
    df.drop(res2[res2["hours"] == False]["hours"].index.values, inplace=True)
    return df

def main():
    infile = open("Data\\UsersDict.pkl", "rb")
    users = pickle.load(infile)
    infile.close()

    # infile = open("Data\\GameFeatureMatrix.pkl")
    gameFeatureMatrixDF = pd.read_pickle("Data\\GameFeatureMatrix.pkl")
    # infile.close()

    gameLocs = {}
    for i, game in enumerate(gameFeatureMatrixDF.index):
        gameLocs[game] = i

    print("cleaning data")
    cleanData = getCleanData(users, gameLocs)
    groupedByUser = cleanData.groupby(by="user").apply(lambda x: x)

    #index games
    gameLocs = {}
    for i, game in enumerate(cleanData["game"].unique()):
        gameLocs[game] = i

    #index users
    userLocs = {}
    for i, user in enumerate(cleanData["user"].unique()):
        userLocs[user] = i

    print("computing game statistics")
    #dict of user -> total hours played accross all games
    userHours = {}
    #dict of game -> total hours played accross all players of this game
    gameHours = {}
    #dict of game -> list of (user, hours) for all players of this game
    gameUserLists = {}
    #list of all interactions between users and games
    userGameInteractionsList = []
    for user in userLocs:
        for game, hours in groupedByUser.loc[user][["game","hours"]].values:
            if (game not in gameHours): gameHours[game] = 0
            if(game not in gameUserLists): gameUserLists[game] = []
            if (user not in userHours): userHours[user] = 0
            userHours[user] += hours
            gameHours[game] += hours
            gameUserLists[game].append((user, hours))
            userGameInteractionsList.append((user, game))

    print("computing frequencies")
    #sort the users of each game by time played
    for game in gameUserLists:
        gameUserLists[game] = sorted(gameUserLists[game], key=lambda item:item[1], reverse=True)

    #Pre-calculate the frequency metric (from paper in header) for every user and every game
    gameFrequencyLists = {}
    for game, sortedUsers in gameUserLists.items():
        gameFrequencyLists[game] = [hours/gameHours[game] if gameHours[game] > 0 else 0 for user, hours in sortedUsers]
        gameFrequencyLists[game] = np.cumsum(gameFrequencyLists[game])

    userInteractionsDense = np.zeros((len(userLocs), len(gameLocs)))
    userInteractionsSparse = np.zeros((len(userGameInteractionsList), 3))

    print("computing dense interactions")
    i = 0
    #Compute user ratings and add them to the two output matrices
    for user, loc in userLocs.items():
        for game, hours in groupedByUser.loc[user][["game","hours"]].values:
            k = gameUserLists[game].index((user, hours))
            kSum = gameFrequencyLists[game][k]
            rating = 4*(1-kSum) + 1
            userInteractionsDense[loc][gameLocs[game]] = rating
            userInteractionsSparse[i][0] = user
            userInteractionsSparse[i][1] = game
            userInteractionsSparse[i][2] = rating
            i += 1

    userInteractionsDF = pd.DataFrame(data=userInteractionsDense, columns = list(gameLocs.keys()), index = map(int,list(userLocs.keys())))
    
    # print("computing sparse interactions")
    # for index, pair in enumerate(userGameInteractionsList):
    #     userInteractionsSparse[index][0] = pair[0]
    #     userInteractionsSparse[index][1] = pair[1]
    #     userInteractionsSparse[index][2] = userInteractionsDense[userLocs[user]][gameLocs[game]]

    userInteractionsSparseDF = pd.DataFrame(data=userInteractionsSparse, columns=["user", "appid", "score"], index=range(len(userGameInteractionsList)))

    print("writing")
    # userInteractionsDF.to_csv("Data\\userInteractionsDense.csv", sep=",")
    outfile = open("Data\\userInteractionsDense.pkl", "wb")
    pickle.dump(userInteractionsDF, outfile)
    outfile.close()

    outfile = open("Data\\userInteractionsSparse.pkl", "wb")
    pickle.dump(userInteractionsSparseDF, outfile)
    outfile.close()



if __name__ == "__main__":
    main()
import pickle
import pandas as pd
import numpy as np
import implicit
import scipy
import knn
import requests

def getUserLibrary(user, genRatings = True):
    f = open("Data\key")
    key = f.read()
    f.close()
    response = requests.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key="+key+"&steamid="+user+"&format=json&include_played_free_games=true")
    if response.status_code != 200:
        return "Private"
    dict = response.json()
    # f = open("ExampleGames")
    # dict = json.loads(f.read())
    userHours = 0
    games = {}
    if "games" not in dict["response"]:
        return "Private"
    for game in dict["response"]["games"]:
        games[game["appid"]] = game["playtime_forever"]
        userHours += game["playtime_forever"]
    if genRatings:
        for game in games:
            games[game] = games[game]/userHours
    return games

#uid = steam user id
#interactionsSparse = dataframe of games and ratings in the form: user, appid, score
#numRecs = how many games to return
#returns list of tuples of games, predicted rating sorted by recommendation strength
def getRecommendations(uid, interactionsSparse, numRecs = 100):
    userInteractionsDense = pd.read_pickle("Data\\userInteractionsDense.pkl")

    ui = userInteractionsDense.copy()

    ui.loc[76561198229940716] = 0
    for game, score in interactionsSparse[["appid", "score"]].to_numpy():
        ui.loc[76561198229940716][game] = score if score >= 3 else 0

    # loc2uid = dict(zip(range(len(ui.index.tolist())), ui.index.tolist()))
    uid2loc = dict(zip(ui.index.tolist(), range(len(ui.index.tolist()))))
    loc2appid = dict(zip(range(len(ui.columns.tolist())), ui.columns.tolist()))

    sdf = ui.astype(pd.SparseDtype("float", 0))
    ssdf = scipy.sparse.csr_matrix(sdf.sparse.to_coo())

    model = implicit.bpr.BayesianPersonalizedRanking()
    model.fit(ssdf, show_progress=False)

    apLocs, scores = model.recommend(uid2loc[uid], ssdf[uid2loc[uid]], numRecs)

    appids = [loc2appid[apLoc] for apLoc in apLocs]
    # games = [gameDict[str(appid)]["name"] for appid in appids]
    return knn.knn(uid, appids, 3, "cosine")

def main():
    userInteractionsDense = pd.read_pickle("Data\\userInteractionsDense.pkl")
    gameFeatureMatrix = pd.read_pickle("Data\\gameFeatureMatrix.pkl")
    userInteractionsSparse = pd.read_pickle("Data\\userinteractionsSparse.pkl")
    infile = open("Data\\GameDictRaw.pkl", "rb")
    gameDict = pickle.load(infile)
    infile.close()
    appids = getRecommendations(76561198199414039, userInteractionsSparse[userInteractionsSparse["user"] == 76561198199414039])
    games = [gameDict[str(appid)]["name"] for appid in appids]
    print(games)

if __name__ == "__main__":
    main()
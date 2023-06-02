import pickle
import pandas as pd
import numpy as np
import implicit
import scipy


def getRecommendations(uid, interactionsSparse, numRecs = 100):
    userInteractionsDense = pd.read_pickle("Data\\userInteractionsDense.pkl")

    ui = userInteractionsDense.copy()

    ui.loc[76561198229940716] = 0
    for game, score in interactionsSparse[["appid", "score"]].to_numpy():
        ui.loc[76561198229940716][game] = score

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
    return appids

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
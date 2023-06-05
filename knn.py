import pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

#initial_df = predsDF.sort_values(by="score", ascending=False).head(30)
#weight_selection = 0,1, or 2
#similarity_selection = "euclidian", "cosine", or "dot"
def knn(u, recs, weight_selection, similarity_selection):

    gameFeatureMatrix = pd.read_pickle("Data\\gameFeatureMatrix.pkl")
    userInteractionsSparse = pd.read_pickle("Data\\userinteractionsSparse.pkl")
    infile = open("Data\\GameDictRaw.pkl", "rb")
    gameDict = pickle.load(infile)
    infile.close()

    games_owned = userInteractionsSparse[userInteractionsSparse["user"] == u]["appid"].sort_values()

    id_list = []
    for game_id in games_owned:
        id_list.append(game_id)

    
    print(id_list)
    g = pd.DataFrame(gameFeatureMatrix, index=id_list)
    column_totals = g.sum(axis=0)
    totals_row = pd.DataFrame([column_totals.values], columns=g.columns)

    
    #Weight Labels:
    #devW = Developer Weight
    #pubW = Publisher Weight
    #plaW = Platform Weight
    #catW = Catagories / Tags Weight
    #ratW = Rating Weight
    #pltW = Average Playtime Weight
    #freW = Is Free? Weight
    

    if(weight_selection == 0):
        devW = 10
        pubW = 4
        plaW = 2
        catW = 8
        ratW = 5
        pltW = 4
        freW = 2

    elif(weight_selection == 1):
        devW = 8
        pubW = 4
        plaW = 2
        catW = 8
        ratW = 5
        pltW = 4
        freW = 2

    else:
        devW = 6
        pubW = 2
        plaW = 1
        catW = 10
        ratW = 5
        pltW = 4
        freW = 2

    #Developers
    totals_row.iloc[:, :1782] = totals_row.iloc[:, :1782] * devW
    #Publishers
    totals_row.iloc[:, 1783:3218] = totals_row.iloc[:, 1783:3218] * pubW
    #Platforms
    totals_row.iloc[:, 3219:3222] = totals_row.iloc[:, 3219:3222] * plaW
    #tags / categories
    totals_row.iloc[:, 3223:] = totals_row.iloc[:, 3223:] * catW

    
    recommendations = pd.DataFrame(gameFeatureMatrix, index = recs["appid"].tolist())
    extra_info = pd.DataFrame (gameDict, index = recs["appid"].tolist())
    #print(extra_info.iloc[0])

    findict = {}

    for i in range(recommendations.shape[0]):
        first = recommendations.iloc[i]
        
        try:
            temp = extra_info.iloc[i]
            positive = 0
            negative = 0
            avg_playtime = 0
            is_free = 0
        except:
            positive = 0
            negative = 0
            avg_playtime = 0
            is_free = 0
            
        #bias term (larger = better)
        bias = ratW*(positive/(positive+negative+1)) + pltW*(avg_playtime) + freW*(is_free)
        
        if(similarity_selection == "euclidian"):
            #euclidian norm
            rev = False
            sum_square_diff = (((first.T) - totals_row)**2).sum(axis=1)
            findict.update({recommendations.index[i]:sum_square_diff.iloc[0] - bias})
        elif(similarity_selection == "cosine"):
            #cosine similarity
            rev = False
            cosine_sim = cosine_similarity(first.values.reshape(1, -1), totals_row.values)
            similarity_score = 1 - cosine_sim
            findict.update({recommendations.index[i]: similarity_score[0][0] - bias})
        else:
            #dot similarity
            rev = True
            dot_similarity = np.dot(first, totals_row.iloc[0])
            findict.update({recommendations.index[i]: dot_similarity + bias})
    
        
    #sorted dict of key value pairs, where keys represent appid
    #sorted from best recommendation to worst
    j = {k: v for k, v in sorted(findict.items(), key=lambda item: item[1], reverse=rev)}
    sorted_keys = list(j.keys())
    return(sorted_keys)














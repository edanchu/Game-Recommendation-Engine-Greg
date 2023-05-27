import csv
import requests
import json
import pickle
import numpy as np
import os
import sys
import time
import copy
import pandas as pd

def getGameInfo(game):
    response = requests.get("https://store.steampowered.com/api/appdetails/?appids="+game+"&filters=basic,developers,publishers,platforms,categories")
    if (response.status_code != 200):
        return response.status_code
    dict = response.json()
    if (dict[game]["success"] == False):
        return "Failure"
    data = dict[game]["data"]
    if (data["type"] != "game"):
        return "Not Game"
    gameInfo = {"appid":game}
    gameInfo["name"] = data["name"] if "name" in data else None
    gameInfo["is_free"] = data["is_free"] if "is_free" in data else None
    gameInfo["about_the_game"] = data["about_the_game"] if "about_the_game" in data else None
    gameInfo["header_image"] = data["header_image"] if "header_image" in data else None
    gameInfo["developers"] = data["developers"] if "developers" in data else None
    gameInfo["publishers"] = data["publishers"] if "publishers" in data else None
    gameInfo["platforms"] = data["platforms"] if "platforms" in data else None
    gameInfo["categories"] = data["categories"] if "categories" in data else None

    response = requests.get("https://steamspy.com/api.php?request=appdetails&appid="+game)
    data = response.json()

    gameInfo["positive_reviews"] = data["positive"] if "positive" in data else None
    gameInfo["negative_reviews"] = data["negative"] if "negative" in data else None
    gameInfo["owners"] = data["owners"].split(" ..")[0] if "owners" in data else None
    gameInfo["median_playtime"] = data["median_forever"] if "median_forever" in data else None
    gameInfo["tags"] = data["tags"] if "tags" in data else None

    return gameInfo




def main():
    infile = open("Data\\UsersDict.pkl", "rb")
    users = pickle.load(infile)
    infile.close()

    ###Be very careful wil regeneration. Will take ~12 hours. Make backup before doing so
    DONOTCHANGETHISREGENERATE = False
    if (os.path.isfile("Data\\GameDictRaw.pkl") and not DONOTCHANGETHISREGENERATE):
        infile = open("Data\\GameDictRaw.pkl", "rb")
        gamesDict = pickle.load(infile)
        infile.close()
    else:
        gamesDict = {}

    gamesDictCopy = copy.deepcopy(gamesDict)
    deleted = 0
    for game in gamesDictCopy:
        if (type(gamesDict[game]) == type(3)):
            del gamesDict[game]
            deleted += 1

    
    generateDict = False if deleted == 0 else True
    if (generateDict):
        print(deleted)
        gamesList = {}
        for user in users:
            if users[user] != "Private":
                for game in users[user]:
                    if (game not in gamesList):
                        gamesList[game] = 1
                
        for game in gamesList:
            game = str(game)
            if (game not in gamesDict):
                res = getGameInfo(game)
                if (type(res) == type(3)):
                    print(res)
                    outfile = open("Data\\GameDictRaw.pkl", "wb")
                    pickle.dump(gamesDict, outfile)
                    outfile.close()
                    return(1)
                if (res == "Not Game" or res == "Failure"):
                    print(str(len(gamesDict))+"/"+str(len(gamesList)), game, res)
                    continue
                else: print(str(len(gamesDict))+"/"+str(len(gamesList)), game)
                gamesDict[game] = res
                if (len(gamesDict)%50 == 0):
                    print("dumping")
                    outfile = open("Data\\GameDictRaw.pkl", "wb")
                    pickle.dump(gamesDict, outfile)
                    outfile.close()
                time.sleep(0.3)
        print("finished regenerating")
        outfile = open("Data\\GameDictRaw.pkl", "wb")
        pickle.dump(gamesDict, outfile)
        outfile.close()

    tagsList = []
    for game in gamesDict:
        for tag in gamesDict[game]["tags"]:
            if (tag not in tagsList):
                tagsList.append(tag)
        if (gamesDict[game]["categories"] is not None):
            for category in gamesDict[game]["categories"]:
                if (category["description"] not in tagsList):
                    tagsList.append(category["description"])

    tagLocs = {}
    for index, tag in enumerate(tagsList):
        tagLocs[tag] = index

    publisherFrequencies = {}
    for game in gamesDict:
        for publisher in gamesDict[game]["publishers"]:
            if (publisher not in publisherFrequencies):
                publisherFrequencies[publisher] = 1
            else:
                publisherFrequencies[publisher] += 1

    commonPublisherLocs = {}
    i = 0
    for publisher in publisherFrequencies:
        if publisherFrequencies[publisher] > 2:
            commonPublisherLocs[publisher] = i
            i += 1


    developerFrequencies = {}
    for game in gamesDict:
        if gamesDict[game]["developers"] is not None:
            for dev in gamesDict[game]["developers"]:
                if (dev not in developerFrequencies):
                    developerFrequencies[dev] = 1
                else:
                    developerFrequencies[dev] += 1

    commonDevLocs = {}
    i = 0
    for dev in developerFrequencies:
        if developerFrequencies[dev] > 2:
            commonDevLocs[dev] = i
            i += 1

    gameLocs = {}
    for index, game in enumerate(gamesDict):
        gameLocs[game] = index
    
    platformLocs = {"windows":0, "mac": 1, "linux": 2}
    pubOffset = len(commonDevLocs)
    platOffset = pubOffset + len(commonPublisherLocs)
    tagOffset = platOffset + len(platformLocs)
    gameFeatureMatrix = np.zeros((len(gamesDict), len(commonDevLocs) + len(commonPublisherLocs) + len(platformLocs) + len(tagLocs)), dtype=np.int8)
    for game in gamesDict:
        if gamesDict[game]["developers"] is not None:
            for dev in gamesDict[game]["developers"]:
                if dev in commonDevLocs:
                    gameFeatureMatrix[gameLocs[game]][commonDevLocs[dev]] = 1
        for publisher in gamesDict[game]["publishers"]:
            if publisher in commonPublisherLocs:
                gameFeatureMatrix[gameLocs[game]][commonPublisherLocs[publisher] + pubOffset] = 1
        for platform in gamesDict[game]["platforms"]:
            if gamesDict[game]["platforms"][platform] == True:
                gameFeatureMatrix[gameLocs[game]][platformLocs[platform] + platOffset] = 1
        for tag in gamesDict[game]["tags"]:
            gameFeatureMatrix[gameLocs[game]][tagLocs[tag] + tagOffset] = 1
        if (gamesDict[game]["categories"] is not None):
            for category in gamesDict[game]["categories"]:
                gameFeatureMatrix[gameLocs[game]][tagLocs[category["description"]] + tagOffset] = 1


    colNames = list(commonDevLocs.keys())
    colNames.extend(list(commonPublisherLocs.keys()))
    colNames.extend(list(platformLocs.keys()))
    colNames.extend(list(tagLocs.keys()))
    gameFeatureMatrixDF = pd.DataFrame(data=gameFeatureMatrix, index=list(gameLocs.keys()), columns=colNames)

    print("writing")
    # gameFeatureMatrixDF.to_csv("Data\\gameFeatureMatrix.csv", sep=",")
    outfile = open("Data\\gameFeatureMatrix.pkl", "wb")
    pickle.dump(gameFeatureMatrixDF, outfile)
    outfile.close()
    





if __name__ == "__main__":
    main()
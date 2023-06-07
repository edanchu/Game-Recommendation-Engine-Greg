import requests
import pickle
import numpy as np
import os
import time
import copy
import pandas as pd

#Creates a dictionary that maps steam appids to game information (GameDictRaw.pkl) as well as a game feature matrix (gameFeatureMatrix.pkl of pandas dataframe)
#that contains a one-hot encoding for tags, top publishers and devs, and platform availability
#Information available in the main dictionary is: appid, name, is_free, about_the_game, header_image,
#developers, publishers, platforms, categories (steam), tags (steamspy), number of positive and negative steam reviews,
#owners, and median_playtime

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



#Uses cached database and dumps every 50 updates
def main():
    infile = open("Data/UsersDict.pkl", "rb")
    users = pickle.load(infile)
    infile.close()

    ###Be very careful with regeneration. Will take ~12 hours. Make backup before doing so
    ###Changing this will flush the cache and restart gathering data about all games from scratch
    DONOTCHANGETHISREGENERATE = False
    if (os.path.isfile("Data/GameDictRaw.pkl") and not DONOTCHANGETHISREGENERATE):
        infile = open("Data/GameDictRaw.pkl", "rb")
        gamesDict = pickle.load(infile)
        infile.close()
    else:
        gamesDict = {}

    #Create a copy and remove all invalid game data
    gamesDictCopy = copy.deepcopy(gamesDict)
    deleted = 0
    for game in gamesDictCopy:
        if (type(gamesDict[game]) == type(3)):
            del gamesDict[game]
            deleted += 1

    #If there was any invalid game data regenerate the dictionary for missing data
    generateDict = False if deleted == 0 else True
    if (generateDict):
        print(deleted)
        #create a list of games for which to download information based on what games our users own
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
                #If an error code was returned from getGameInfo, dump current valid data and exit
                if (type(res) == type(3)):
                    print(res)
                    outfile = open("Data/GameDictRaw.pkl", "wb")
                    pickle.dump(gamesDict, outfile)
                    outfile.close()
                    return(1)
                #If the app is not a game or has been removed from the steam store don't add it to our dictionary
                if (res == "Not Game" or res == "Failure"):
                    print(str(len(gamesDict))+"/"+str(len(gamesList)), game, res)
                    continue
                #If no error add game info to the dict
                else: print(str(len(gamesDict))+"/"+str(len(gamesList)), game)
                gamesDict[game] = res

                #Dump the dict data every 50 iterations so not much data is lost on an error
                if (len(gamesDict)%50 == 0):
                    print("dumping")
                    outfile = open("Data/GameDictRaw.pkl", "wb")
                    pickle.dump(gamesDict, outfile)
                    outfile.close()
                #sleep so that steam api doesn't block your ip
                time.sleep(0.3)
        print("finished regenerating")
        outfile = open("Data/GameDictRaw.pkl", "wb")
        pickle.dump(gamesDict, outfile)
        outfile.close()

    #create a list of all tags that have been applied to games in our dictionary
    #some tags are from steamspy and some are from steam, so this grabs both
    tagsList = []
    for game in gamesDict:
        for tag in gamesDict[game]["tags"]:
            if (tag not in tagsList):
                tagsList.append(tag)
        if (gamesDict[game]["categories"] is not None):
            for category in gamesDict[game]["categories"]:
                if (category["description"] not in tagsList):
                    tagsList.append(category["description"])

    #indexes tags
    tagLocs = {}
    for index, tag in enumerate(tagsList):
        tagLocs[tag] = index

    #Calculate how many times each publisher is in our dataset
    publisherFrequencies = {}
    for game in gamesDict:
        for publisher in gamesDict[game]["publishers"]:
            if (publisher not in publisherFrequencies):
                publisherFrequencies[publisher] = 1
            else:
                publisherFrequencies[publisher] += 1

    #Remove any publisher that has only published one or two games, since they don't provide much info
    commonPublisherLocs = {}
    i = 0
    for publisher in publisherFrequencies:
        if publisherFrequencies[publisher] > 2:
            commonPublisherLocs[publisher] = i
            i += 1

    #same as above, but for devs instead of publishers
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

    #indexes the games
    gameLocs = {}
    for index, game in enumerate(gamesDict):
        gameLocs[game] = index
    
    #creates offsets for each piece of data added to the game feature matrix so that values can be inserted into the right place
    #the order of the data is {devs, publishers, platforms, tags}
    platformLocs = {"windows":0, "mac": 1, "linux": 2}
    pubOffset = len(commonDevLocs)
    platOffset = pubOffset + len(commonPublisherLocs)
    tagOffset = platOffset + len(platformLocs)
    gameFeatureMatrix = np.zeros((len(gamesDict), len(commonDevLocs) + len(commonPublisherLocs) + len(platformLocs) + len(tagLocs)), dtype=np.int8)
    #inserts data into the matrix for each game
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


    #creates column names for the pandas dataframe based on the insertion order of data from above
    colNames = list(commonDevLocs.keys())
    colNames.extend(list(commonPublisherLocs.keys()))
    colNames.extend(list(platformLocs.keys()))
    colNames.extend(list(tagLocs.keys()))
    gameFeatureMatrixDF = pd.DataFrame(data=gameFeatureMatrix, index=map(int,list(gameLocs.keys())), columns=colNames)

    print("writing")
    # gameFeatureMatrixDF.to_csv("Data\\gameFeatureMatrix.csv", sep=",")
    outfile = open("Data/gameFeatureMatrix.pkl", "wb")
    pickle.dump(gameFeatureMatrixDF, outfile)
    outfile.close()
    





if __name__ == "__main__":
    main()
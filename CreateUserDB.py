import requests
import json
import pickle

##DO NOT RUN THIS!!!!!!##
##DO NOT RUN THIS!!!!!!##
##DO NOT RUN THIS!!!!!!##
##DO NOT RUN THIS!!!!!!##
##DO NOT RUN THIS!!!!!!##
##DO NOT RUN THIS!!!!!!##
##DO NOT RUN THIS!!!!!!##
##DO NOT RUN THIS!!!!!!##
##DO NOT RUN THIS!!!!!!##
##DO NOT RUN THIS!!!!!!##

def getFriends(key, user):
    response = requests.get("http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key="+key+"&steamid="+user+"&relationship=all")
    if response.status_code == 403:
        return []
    dict = response.json()
    # f = open("ExampleFriends")
    # dict = json.loads(f.read())
    friends = []
    if "friendslist" not in dict:
        return []
    for friend in dict["friendslist"]["friends"]:
        friends.append(friend["steamid"])
    return friends
    


def getOwnedGames(key, user):
    response = requests.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key="+key+"&steamid="+user+"&format=json&include_played_free_games=true")
    if response.status_code == 403:
        return 403
    dict = response.json()
    # f = open("ExampleGames")
    # dict = json.loads(f.read())
    games = {}
    if "games" not in dict["response"]:
        return "Private"
    for game in dict["response"]["games"]:
        games[game["appid"]] = game["playtime_forever"]
    return games

def getKey():
    f = open("Data\key")
    key = f.read()
    f.close()
    return key



def main():
    key = getKey()
    infile = open("Data\\UsersDict.pkl", "rb")
    users = pickle.load(infile)
    infile.close()
    infile = open("Data\\UncheckedUsers.pkl", "rb")
    uncheckedUsers = pickle.load(infile)
    infile.close()
    while len(users) < 45000:
        while True:
            user = uncheckedUsers.pop(0)
            if user not in users:
                break

        if (len(users) % 100 == 0):
            print("dumping")
            outfile = open("Data\\UsersDict.pkl", "wb")
            pickle.dump(users, outfile)
            outfile.close()
            outfile = open("Data\\UncheckedUsers.pkl", "wb")
            pickle.dump(uncheckedUsers, outfile)
            outfile.close()

        if (len(uncheckedUsers) < 5000):
            uncheckedUsers.extend([friend for friend in getFriends(key, user) if friend not in users])

        games = getOwnedGames(key, user)

        if (games == 403):
            print("403: Dumping")
            outfile = open("Data\\UsersDict.pkl", "wb")
            pickle.dump(users, outfile)
            outfile.close()
            outfile = open("Data\\UncheckedUsers.pkl", "wb")
            pickle.dump(uncheckedUsers, outfile)
            outfile.close()
            break

        print(len(users), "P" if games == "Private" else "N")
        users[user] = games
    outfile = open("Data\\UsersDict.pkl", "wb")
    pickle.dump(users, outfile)
    outfile.close()
    outfile = open("Data\\UncheckedUsers.pkl", "wb")
    pickle.dump(uncheckedUsers, outfile)
    outfile.close()

    
    

if __name__ == "__main__":
    main()
Files and what they do:

gui.py: Main app. Requires the output from CreateGameDB and CreateUserInteractions

CreateUserDB: Scrapes steam for user data. DON'T RUN THIS

CreateGameDB: Scrapes steam for the game data of every game that a user in our user database has played. Outputs two files: GameDictRaw.pkl which is a dump of a dictionary that maps games by appid to data about them. gameFeatureMatrix.pkl which is a dump of a pandas dataframe that holds the feature embeddings for a game (one hot encoding of developer, publisher, tags, and platforms)

CreateUserInteractions: Processes user and game data to create a user interactions matrix which maps each user to each game they own and an estimated rating for that game based on their hours played. More detailed info in the file. Outputs are userInteractionsDense.pkl and userInteractionsSparse.pkl which are both dumps of pandas dataframes.

Recommender: main module the implements recommendations using BPR and nearest neighbors.

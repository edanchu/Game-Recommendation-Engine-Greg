Files and what they do:

CreateUserDB: Scrapes steam for user data. DON'T RUN THIS

CreateGameDB: Scrapes steam for the game data of every game that a user in our user database has played. Outputs two files: GameDictRaw.pkl which is a dump of a dictionary that maps games by appid to data about them. gameFeatureMatrix.pkl which is a dump of a pandas dataframe that holds the feature embeddings for a game (one hot encoding of developer, publisher, tags, and platforms)

CreateUserInteractions: Processes user and game data to create a user interactions matrix which maps each user to each game they own and an estimated rating for that game based on their hours played. More detailed info in the file. Outputs are userInteractionsDense.pkl and userInteractionsSparse.pkl which are both dumps of pandas dataframes.

Recommender: Placeholder file that currently does nothing. Eventually this will have an interface that takes in a user's ratings and outputs a list of games and their estimated score for that user. This output will need to be passed through a second algorithm to rank the outputs for display to the user.

RecommenderProcedural: A jupyter notebook that I am using to work through how to create the matrix factorization part of the algorithm. 
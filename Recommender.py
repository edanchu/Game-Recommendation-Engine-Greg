import pickle
import pandas as pd
import numpy as np

def main():
    userInteractions = pd.read_pickle("Data\\userInteractions.pkl")
    print(userInteractions.describe(include='all'))

if __name__ == "__main__":
    main()
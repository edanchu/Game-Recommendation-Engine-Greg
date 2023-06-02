from tkinter import *
import requests
from io import BytesIO
from PIL import ImageTk, Image
import pickle
from html.parser import HTMLParser
import CreateGameDB as game
import pandas as pd

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def get_data(self):
        return ''.join(self.fed)

def strip_html(html):
    html_stripper = HTMLStripper()
    html_stripper.feed(html)
    return html_stripper.get_data()

class GREG:
    def __init__(self, root, pickle_file):
        self.uid = 1
        self.dataIndex = 1
        self.photoImage = None
        self.imgLabel = None
        self.developerLabel = None
        self.gameInfo = None
        self.publisherLabel = None
        self.positiveReviewsLabel = None
        self.root = root
        self.data = self.read_pickle(pickle_file)  
        self.ratings_df = pd.DataFrame(columns=['uid', 'appid', 'score'])
        self.choice_counter = 0  
        self.setupUI()

    def read_pickle(self, pickle_file):
        infile = open(pickle_file, "rb")
        gamesDict = pickle.load(infile)
        infile.close()
        self.gameInfo = gamesDict
        return [row for row in gamesDict]

    def setupUI(self):
        center_frame = Frame(self.root)
        center_frame.pack(side=TOP, expand=True, fill=BOTH)

        rating_frame = Frame(self.root)
        rating_frame.pack(side=BOTTOM, expand=False, fill=BOTH)

        # Inner frame to hold the stars
        stars_frame = Frame(rating_frame)
        stars_frame.pack(expand=True)

        self.photoImage = self.getImage("https://steamcdn-a.akamaihd.net/steam/apps/"+self.data[self.dataIndex]+"/header.jpg")
        self.imgLabel = Label(center_frame, image=self.photoImage)
        self.imgLabel.pack(side=TOP)

        self.name = self.get_game_name(self.data[self.dataIndex])
        self.nameLabel = Label(center_frame, text=self.name)
        self.nameLabel.pack(side=TOP)

        self.developer = self.get_game_developer(self.data[self.dataIndex])
        self.developerLabel = Label(center_frame, text="Developer: " + self.developer)
        self.developerLabel.pack(side=TOP)

        self.publisher = self.get_game_publisher(self.data[self.dataIndex])
        self.publisherLabel = Label(center_frame, text="Publisher: " + self.publisher)
        self.publisherLabel.pack(side=TOP)
        self.positiveReviews = self.get_positive_review_percent(self.data[self.dataIndex])
        self.positiveReviewsLabel = Label(center_frame, text="Positive Reviews: " + str(self.positiveReviews) + "%")
        self.positiveReviewsLabel.pack(side=TOP)

        scroll = Scrollbar(center_frame)
        scroll.pack(side=RIGHT, fill=Y)

        self.descriptionText = Text(center_frame, wrap=WORD, yscrollcommand=scroll.set, height= 7, width = 70)
        self.description = self.get_game_description(self.data[self.dataIndex])
        self.descriptionText.insert(INSERT, self.description)
        self.descriptionText.pack(side=TOP)

        self.refresh_button = Button(center_frame, text="Refresh", command=self.refresh)
        self.refresh_button.pack()
        self.refresh_button.pack_forget()
        self.refresh_button

        self.stars = [Button(stars_frame, text=" ★ ", fg="grey") for i in range(5)]
        for i in range(5):
            self.stars[i].pack(side=LEFT, padx=5)
            self.stars[i].bind("<Enter>", lambda e, i=i: self.hover(i))
            self.stars[i].bind("<Leave>", lambda e: self.reset())
            self.stars[i].bind("<Button-1>", lambda e, i=i: self.click(i))
    
    def get_game_name(self, app_id):
        return self.gameInfo[app_id]['name']
    def get_game_description(self, app_id):
        return strip_html(self.gameInfo[app_id]['about_the_game'])
    
    def get_game_developer(self, app_id):
        return ', '.join(self.gameInfo[app_id]["developers"])
    
    def get_game_publisher(self, app_id):
        
        return ', '.join(self.gameInfo[app_id]["publishers"])

    def get_positive_review_percent(self, app_id):
        positive = self.gameInfo[app_id]["positive_reviews"]
        negative = self.gameInfo[app_id]["negative_reviews"]
        total = positive + negative
        if total > 0:
            return round(positive / total * 100, 2)
        else:
            return 0

    def getImage(self, url):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return ImageTk.PhotoImage(img)

    def hover(self, star_num):
        for i in range(star_num + 1):
            self.stars[i].config(fg="orange")

    def reset(self):
        for star in self.stars:
            star.config(fg="grey")

    def refresh(self):
        self.choice_counter = 0
        self.refresh_button.pack_forget() 
        self.update()

    def click(self, star_num):
        self.choice_counter += 1
        if self.choice_counter >= 3:
            self.refresh_button.pack() 
        print(f"for game id {self.data[self.dataIndex]} user chose {star_num + 1} stars")
        self.ratings_df = self.ratings_df.append({
            'uid': self.uid,
            'appid': self.data[self.dataIndex],
            'score': star_num + 1
        }, ignore_index=True)
        self.update()

    def update(self):
        self.dataIndex += 1
        self.photoImage = self.getImage("https://steamcdn-a.akamaihd.net/steam/apps/"+self.data[self.dataIndex]+"/header.jpg")

        self.imgLabel.config(image=self.photoImage)

        self.nameLabel.config(text = self.get_game_name(self.data[self.dataIndex]))

        self.descriptionText.delete('1.0', END)  # clear the existing description
        self.description = self.get_game_description(self.data[self.dataIndex])
        self.descriptionText.insert(INSERT, self.description)
        self.descriptionText.pack(side=TOP)
        self.descriptionText.config(state= DISABLED)

        self.developer = self.get_game_developer(self.data[self.dataIndex])
        self.developerLabel.config(text="Developer: " + self.developer)

        self.publisher = self.get_game_publisher(self.data[self.dataIndex])
        self.publisherLabel.config(text="Publisher: " + self.publisher)

        self.positiveReviews = self.get_positive_review_percent(self.data[self.dataIndex])
        self.positiveReviewsLabel.config(text="Positive Reviews: " + str(self.positiveReviews) + "%")
        


def main():
    root = Tk()
    root.minsize(550,200)
    root.maxsize(550,1000)
    steamInfo = "Data\GameDictRaw.pkl"
    GREG(root, steamInfo)
    root.mainloop()

if __name__ == "__main__":
    main()

from tkinter import *
from tkinter import ttk
import requests
from io import BytesIO
from PIL import ImageTk, Image
import pickle
from html.parser import HTMLParser
import CreateGameDB as game
import pandas as pd
from tkhtmlview import HTMLLabel

# class HTMLStripper(HTMLParser):
#     def __init__(self):
#         super().__init__()
#         self.reset()
#         self.fed = []

#     def handle_data(self, data):
#         self.fed.append(data)

#     def get_data(self):
#         return ''.join(self.fed)

# def strip_html(html):
#     html_stripper = HTMLStripper()
#     html_stripper.feed(html)
#     return html_stripper.get_data()

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
        self.center_frame = None
        self.rating_frame = None
        self.refresh_frame = None
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
        self.center_frame = Frame(self.root)
        self.center_frame.pack(side=TOP, expand=True, fill=BOTH)

        self.rating_frame = Frame(self.root)
        self.rating_frame.pack(side=BOTTOM, expand=False, fill=BOTH)

        stars_frame = Frame(self.rating_frame)
        stars_frame.pack(expand=True)

        self.photoImage = self.getImage("https://steamcdn-a.akamaihd.net/steam/apps/"+self.data[self.dataIndex]+"/header.jpg")
        self.imgLabel = Label(self.center_frame, image=self.photoImage)
        self.imgLabel.pack(side=TOP)

        self.name = self.get_game_name(self.data[self.dataIndex])
        self.nameLabel = Label(self.center_frame, text=self.name, font=("Helvetica", 16))
        self.nameLabel.pack(side=TOP)

        self.developer = self.get_game_developer(self.data[self.dataIndex])
        self.developerLabel = Label(self.center_frame, text="Developer: " + self.developer, font=("Helvetica", 14))
        self.developerLabel.pack(side=TOP)

        self.publisher = self.get_game_publisher(self.data[self.dataIndex])
        self.publisherLabel = Label(self.center_frame, text="Publisher: " + self.publisher, font=("Helvetica", 14))
        self.publisherLabel.pack(side=TOP)

        self.positiveReviews = self.get_positive_review_percent(self.data[self.dataIndex])
        self.positiveReviewsLabel = Label(self.center_frame, text="Positive Reviews: " + str(self.positiveReviews) + "%", font=("Helvetica", 14))
        self.positiveReviewsLabel.pack(side=TOP)

        spacer = Label(self.center_frame, height=1)
        spacer.pack(side=TOP)

        scroll = Scrollbar(self.center_frame)
        scroll.pack(side=RIGHT, fill=Y)

        self.description = self.get_game_description(self.data[self.dataIndex])
        self.descriptionText = HTMLLabel(self.center_frame, html= self.description, wrap=WORD, yscrollcommand=scroll.set, height= 15, width = 100)
        self.descriptionText.pack(side=TOP)

        spacer = Label(self.center_frame, height=1)
        spacer.pack(side=TOP)

        self.refresh_frame = Frame(self.root)
        self.refresh_frame.pack(side=TOP, expand=True, fill=BOTH)

        self.text_above_button = Label(self.refresh_frame, text = "Generate new recommendations")
        self.refresh_button = Button(self.refresh_frame, text="Refresh", command=self.refresh, height= 3, width= 10)
        self.text_below_button = Label(self.refresh_frame, text = "Generating this might take a few seconds")


        self.stars = [Button(stars_frame, text=" ★ ", fg="grey",width= 3, height=2) for i in range(5)]
        for i in range(5):
            self.stars[i].pack(side=LEFT, padx=5)
            self.stars[i].bind("<Enter>", lambda e, i=i: self.hover(i))
            self.stars[i].bind("<Leave>", lambda e: self.reset())
            self.stars[i].bind("<Button-1>", lambda e, i=i: self.click(i))
    
    def get_game_name(self, app_id):
        return self.gameInfo[app_id]['name']
    def get_game_description(self, app_id):
        return self.gameInfo[app_id]['about_the_game']
    
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
        self.center_frame.pack(side=TOP, expand=True, fill=BOTH)
        self.rating_frame.pack(side=BOTTOM, expand=False, fill=BOTH)
        self.text_above_button.pack_forget()
        self.refresh_button.pack_forget()
        self.text_below_button.pack_forget()
        self.refresh_frame.pack_forget()
        self.update()

    def click(self, star_num):
        self.choice_counter += 1
        if self.choice_counter >= 5:
            self.refresh_frame.pack()
            self.text_above_button.pack()
            self.refresh_button.pack()
            self.text_below_button.pack()
            self.center_frame.pack_forget()
            self.rating_frame.pack_forget()

            self.refresh_button.pack() 
        print(f"for game id {self.data[self.dataIndex]} user chose {star_num + 1} stars")
        self.ratings_df.loc[self.ratings_df.shape[0]] = {
            'uid': self.uid,
            'appid': self.data[self.dataIndex],
            'score': star_num + 1
        }
        self.update()

    def update(self):
        self.dataIndex += 1
        self.photoImage = self.getImage("https://steamcdn-a.akamaihd.net/steam/apps/"+self.data[self.dataIndex]+"/header.jpg")

        self.imgLabel.config(image=self.photoImage)

        self.nameLabel.config(text = self.get_game_name(self.data[self.dataIndex]))

        self.descriptionText.delete('1.0', END) 
        self.description = self.get_game_description(self.data[self.dataIndex])
        self.descriptionText.set_html(self.description)
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
    root.minsize(150,100)
    root.maxsize(1280,720)
    steamInfo = "Data\GameDictRaw.pkl"
    GREG(root, steamInfo)
    root.mainloop()

if __name__ == "__main__":
    main()

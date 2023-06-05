from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import requests
from io import BytesIO
from PIL import ImageTk, Image
import pickle
from html.parser import HTMLParser
import CreateGameDB as game
import pandas as pd
from tkhtmlview import HTMLLabel
import Recommender as rec

class GREG:
    def __init__(self, root, starting_games):
        self.uid = 1
        self.dataIndex = 0
        self.list_len = len(starting_games)
        self.photoImage = None
        self.imgLabel = None
        self.developerLabel = None
        self.gameInfo = self.read_pickle("Data/GameDictRaw.pkl")
        self.publisherLabel = None
        self.positiveReviewsLabel = None
        self.center_frame = None
        self.rating_frame = None
        self.refresh_frame = None
        self.root = root
        self.data = starting_games
        self.ratings_df = pd.DataFrame(columns=['user', 'appid', 'score'])
        self.three_plus_star_games = []
        self.choice_counter = 0  
        self.start_screen()
        
        # self.setupUI()


    def start_screen(self):
        self.start_frame = Frame(self.root)
        self.start_frame.pack(side=TOP, expand=True, fill=BOTH)

        self.starter_label = Label(self.start_frame, text="Welcome to GREG!", font=("Helvetica", 16))
        self.starter_label.pack(side=TOP, pady=200)

        self.button_frame = Frame(self.start_frame)
        self.button_frame.pack(side=TOP)

        self.continue_button = Button(self.button_frame, text="Start From Scratch", command=self.continue_setup)
        self.continue_button.pack(side=LEFT, padx=100)  

        self.steam_id_frame = Frame(self.button_frame)
        self.steam_id_frame.pack(side=LEFT, padx=100) 

        self.steam_id_entry = Entry(self.steam_id_frame)
        self.steam_id_entry.pack(side=TOP, padx=100, pady= 5)  
        
        self.steam_id_button = Button(self.steam_id_frame, text="Enter Steam ID", command=self.enter_steam_id)
        self.steam_id_button.pack(side=TOP, padx=100)

    def continue_setup(self):
        self.start_frame.destroy()
        self.steam_id = 1
        self.setupUI()

    def enter_steam_id(self):
        self.steam_id = self.steam_id_entry.get()
        self.start_frame.destroy()
        userLib = rec.getUserLibrary(self.steam_id)
        self.ratings_df = userLib
        if isinstance(userLib, str) and userLib == "Private":
            messagebox.showwarning("Private Account","Make sure your account is public. Please try again!")
            self.start_screen()
        else:
            self.data = rec.getRecommendations(self.steam_id, userLib)
            self.setupUI()
        

    def read_pickle(self, pickle_file):
        infile = open(pickle_file, "rb")
        gamesDict = pickle.load(infile)
        infile.close()
        return gamesDict
        #self.gameInfo = gamesDict
        #return [row for row in gamesDict]

    def setupUI(self):
        self.center_frame = Frame(self.root)
        self.center_frame.pack(side=TOP, expand=True, fill=BOTH)

        self.rating_frame = Frame(self.root)
        self.rating_frame.pack(side=BOTTOM, expand=False, fill=BOTH)

        stars_frame = Frame(self.rating_frame)
        stars_frame.pack(expand=True)

        self.photoImage = self.getImage("https://steamcdn-a.akamaihd.net/steam/apps/"+str(self.data[self.dataIndex])+"/header.jpg")
        self.imgLabel = Label(self.center_frame, image=self.photoImage)
        self.imgLabel.pack(side=TOP)

        self.name = self.get_game_name(self.data[self.dataIndex])
        self.nameLabel = Label(self.center_frame, text=self.name, font=("Helvetica", 16))
        self.nameLabel.pack(side=TOP)

        self.developer = self.get_game_developer(self.data[self.dataIndex])
        self.developerLabel = Label(self.center_frame, text="Developer: " + self.developer, font=("Helvetica", 12))
        self.developerLabel.pack(side=TOP)

        self.publisher = self.get_game_publisher(self.data[self.dataIndex])
        self.publisherLabel = Label(self.center_frame, text="Publisher: " + self.publisher, font=("Helvetica", 12))
        self.publisherLabel.pack(side=TOP)

        self.positiveReviews = self.get_positive_review_percent(self.data[self.dataIndex])
        self.positiveReviewsLabel = Label(self.center_frame, text="Positive Reviews: " + str(self.positiveReviews) + "%", font=("Helvetica", 12))
        self.positiveReviewsLabel.pack(side=TOP)

        spacer = Label(self.center_frame, height=1)
        spacer.pack(side=TOP)

        scroll = Scrollbar(self.center_frame)
        # scroll.pack(side=RIGHT, fill=Y)
        border_frame = Frame(self.center_frame, borderwidth=2, relief="groove")
        border_frame.pack(side=TOP, padx=5, pady=5)

        self.description = self.get_game_description(self.data[self.dataIndex])
        self.descriptionText = HTMLLabel(border_frame, html= self.description, wrap=WORD, yscrollcommand=scroll.set, height= 15, width = 70)
        self.descriptionText.pack(side=TOP)

        spacer = Label(self.center_frame, height=1)
        spacer.pack(side=TOP)

        self.refresh_frame = Frame(self.root)
        self.refresh_frame.pack(side=TOP, expand=True, fill=BOTH)

        self.text_above_button = Label(self.refresh_frame, text = "Generate new recommendations")
        self.refresh_button = Button(self.refresh_frame, text="Refresh", command=self.refresh, height= 3, width= 10)
        self.text_below_button = Label(self.refresh_frame, text = "Generating this might take a few seconds")

        self.print_button = Button(stars_frame, text="Print 3+ Star Games", command=self.print_three_plus_star_games)
        self.print_button.pack(side=RIGHT)

        self.stars = [Button(stars_frame, text="   ★   ", fg="grey",width= 10, height=5) for i in range(5)]
        for i in range(5):
            self.stars[i].pack(side=LEFT, padx=5)
            self.stars[i].bind("<Enter>", lambda e, i=i: self.hover(i))
            self.stars[i].bind("<Leave>", lambda e: self.reset())
            self.stars[i].bind("<Button-1>", lambda e, i=i: self.click(i))
    
    def get_game_name(self, app_id):
        return self.gameInfo[str(app_id)]['name']
    
    def get_game_description(self, app_id):
        return self.gameInfo[str(app_id)]['about_the_game']
    
    def get_game_developer(self, app_id):
        return ', '.join(self.gameInfo[str(app_id)]["developers"])
    
    def get_game_publisher(self, app_id):
        
        return ', '.join(self.gameInfo[str(app_id)]["publishers"])

    def get_positive_review_percent(self, app_id):
        positive = self.gameInfo[str(app_id)]["positive_reviews"]
        negative = self.gameInfo[str(app_id)]["negative_reviews"]
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
    def print_three_plus_star_games(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        output_frame = Frame(self.root)
        output_frame.pack()

        output_text = Text(output_frame)
        output_text.insert(END, "Here are the games that you liked\n")
        for game in self.three_plus_star_games:
            output_text.insert(END, game + '\n')
        output_text.pack()

    def refresh(self):
        self.data = rec.getRecommendations(self.steam_id, self.ratings_df)
        self.choice_counter = 0
        self.dataIndex = 0
        self.center_frame.pack(side=TOP, expand=True, fill=BOTH)
        self.rating_frame.pack(side=BOTTOM, expand=False, fill=BOTH)
        self.text_above_button.pack_forget()
        self.refresh_button.pack_forget()
        self.text_below_button.pack_forget()
        self.refresh_frame.pack_forget()
        self.update()

    def click(self, star_num):
        self.choice_counter += 1
        if star_num + 1 >= 3:
            self.three_plus_star_games.append(self.get_game_name(self.data[self.dataIndex]))
        if self.choice_counter == self.list_len:
            self.refresh_frame.pack()
            self.text_above_button.pack()
            self.refresh_button.pack()
            self.text_below_button.pack()
            self.center_frame.pack_forget()
            self.rating_frame.pack_forget()

            self.refresh_button.pack() 

        self.ratings_df.loc[self.ratings_df.shape[0]] = {
            'user': self.steam_id,
            'appid': self.data[self.dataIndex],
            'score': star_num + 1
        }
        print(self.ratings_df)
        self.update()

    def update(self):
        self.dataIndex += 1
        self.photoImage = self.getImage("https://steamcdn-a.akamaihd.net/steam/apps/"+str(self.data[self.dataIndex])+"/header.jpg")

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
    starting_games = [72850, 730, 1172470, 413150, 210970, 220, 8930, 214490, 1551360, 230410, 1222670]
    root = Tk()
    root.minsize(1280,720)
    root.maxsize(1280,720)
    steamInfo = "Data/GameDictRaw.pkl"
    GREG(root, starting_games)
    root.mainloop()

if __name__ == "__main__":
    main()

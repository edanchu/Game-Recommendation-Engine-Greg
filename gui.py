from tkinter import *
import requests
from io import BytesIO
from PIL import ImageTk, Image
import pickle
from html.parser import HTMLParser

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
        self.dataIndex = 1
        self.photoImage = None
        self.imgLabel = None
        self.root = root
        self.data = self.read_pickle(pickle_file)  
        self.setupUI()

    def read_pickle(self, pickle_file):
        infile = open(pickle_file, "rb")
        gamesDict = pickle.load(infile)
        infile.close()
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

        scroll = Scrollbar(center_frame)
        scroll.pack(side=RIGHT, fill=Y)

        self.descriptionText = Text(center_frame, wrap=WORD, yscrollcommand=scroll.set, height= 7, width = 70)
        self.description = self.get_game_description(self.data[self.dataIndex])
        self.descriptionText.insert(INSERT, self.description)
        self.descriptionText.pack(side=TOP)

        self.stars = [Button(stars_frame, text=" ★ ", fg="grey") for i in range(5)]
        for i in range(5):
            self.stars[i].pack(side=LEFT, padx=5)
            self.stars[i].bind("<Enter>", lambda e, i=i: self.hover(i))
            self.stars[i].bind("<Leave>", lambda e: self.reset())
            self.stars[i].bind("<Button-1>", lambda e, i=i: self.click(i))
    
    def get_game_name(self, app_id):
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        response = requests.get(url)
        data = response.json()
        if data[str(app_id)]['success']:
            return data[str(app_id)]['data']['name']
        else:
            return None
    def get_game_description(self, app_id):
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        response = requests.get(url)
        data = response.json()
        if data[str(app_id)]['success']:
            desc_html = data[str(app_id)]['data']['about_the_game']
            return strip_html(desc_html)
        else:
            return None

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

    def click(self, star_num):
        print(f"for game id {self.data[self.dataIndex]} user chose {star_num + 1} stars")
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

 
def main():
    root = Tk()
    root.minsize(550,200)
    root.maxsize(550,1000)
    steamInfo = "Data\GameDictRaw.pkl"
    GREG(root, steamInfo)
    root.mainloop()

if __name__ == "__main__":
    main()

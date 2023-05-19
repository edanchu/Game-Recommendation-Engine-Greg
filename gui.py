import csv
from tkinter import *
import requests
from io import BytesIO
from PIL import ImageTk, Image
import numpy as np
import textwrap


class GREG:
    def __init__(self, root, csv_file, description):
        self.dataIndex = 1
        self.rating = 0
        self.photoImage = None
        self.imgLabel = None
        self.root = root
        self.data = self.read_csv(csv_file)  
        self.description = self.read_csv(description)
        self.setupUI()

    def read_csv(self, csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            return [row for row in reader]

    def setupUI(self):
        left_frame = Frame(self.root)
        left_frame.pack(side=LEFT, expand=False, fill=BOTH)

        center_frame = Frame(self.root)
        center_frame.pack(side=LEFT, expand=False, fill=BOTH)

        right_frame = Frame(self.root)
        right_frame.pack(side=LEFT, expand=False, fill=BOTH)

        self.photoImage = self.getImage("https://steamcdn-a.akamaihd.net/steam/apps/"+self.data[self.dataIndex][0]+"/header.jpg")
        self.imgLabel = Label(center_frame, image=self.photoImage)
        self.imgLabel.pack(side=TOP)

        name = self.data[self.dataIndex][1]
        self.nameLabel = Label(center_frame, text=name)
        self.nameLabel.pack(side=TOP)
        
        description = self.description[self.dataIndex][3]
        wrapped_description = "\n".join(textwrap.wrap(description, width=75))
        self.descLabel = Label(center_frame, text = wrapped_description)
        self.descLabel.pack(side=TOP)

        self.rating = int(self.data[self.dataIndex][12]) - int(self.data[self.dataIndex][13])
        self.ratingLabel = Label(center_frame, text = "Rating:" + str(self.rating))
        self.ratingLabel.pack(side=TOP)

        redButton = Button(left_frame, text="<--", command=self.disliked, bg="red",height=14, width=5)
        redButton.pack(anchor=N, expand=True)

        greenButton = Button(right_frame, text="-->", command=self.liked, bg="green",height=14, width=5)
        greenButton.pack(anchor=N, expand=True)


    def getImage(self, url):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return ImageTk.PhotoImage(img)

    def liked(self):
        self.dataIndex = (self.dataIndex + 1) % len(self.data)
        self.updateImage()

    def disliked(self):
        self.dataIndex = (self.dataIndex + 1) % len(self.data)
        self.updateImage()

    def updateImage(self):
        self.photoImage = self.getImage("https://steamcdn-a.akamaihd.net/steam/apps/"+self.data[self.dataIndex][0]+"/header.jpg")
        self.imgLabel.config(image=self.photoImage)
        self.nameLabel.config(text=self.data[self.dataIndex][1]) 
        self.descLabel.config(text=  "\n".join(textwrap.wrap(self.description[self.dataIndex][3], width=75)))
        self.ratingLabel.config(text = "Rating:" + str(int(self.data[self.dataIndex][12]) - int(self.data[self.dataIndex][13])))


def main():
    root = Tk()
    root.minsize(550,200)
    root.maxsize(550,500)
    steamInfo = "Data\steam.csv"
    descriptionInfo = "Data\steam_description_data.csv"

    GREG(root, steamInfo,descriptionInfo)
    root.mainloop()


if __name__ == "__main__":
    main()

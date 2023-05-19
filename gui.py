import csv
from tkinter import *
import requests
from io import BytesIO
from PIL import ImageTk, Image
import numpy as np

class GREG:
    def __init__(self, root, csv_file):
        self.dataIndex = 1
        self.photoImage = None
        self.imgLabel = None
        self.root = root
        self.data = self.read_csv(csv_file)  
        self.setupUI()

    def read_csv(self, csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            return [row for row in reader]

    def setupUI(self):
        print(self.data[self.dataIndex])
        self.photoImage = self.getImage("https://steamcdn-a.akamaihd.net/steam/apps/"+self.data[self.dataIndex][0]+"/header.jpg")
        self.imgLabel = Label(self.root, image=self.photoImage)
        self.imgLabel.pack(side=TOP)

        name = self.data[self.dataIndex][1]
        self.nameLabel = Label(self.root, text=name)
        self.nameLabel.pack(side=TOP)
        

        redButton = Button(self.root, text="<--", command=self.disliked, bg="red")
        redButton.pack(side=LEFT)
        greenButton = Button(self.root, text="-->", command=self.liked, bg="green")
        greenButton.pack(side=RIGHT)

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


def main():
    root = Tk()
    root.minsize(550,300)
    root.maxsize(550,300)
    steamInfo = "Data\steam.csv"
    GREG(root, steamInfo)
    root.mainloop()


if __name__ == "__main__":
    main()

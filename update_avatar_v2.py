################################################################
#
#   INTRO
#
################################################################
# # avatar maken, hangt af van deze params
# windsnelheid
# temperatuur
# bewolkte lucht of heldere

# eventueel ook: moment van dag (sunset/sunset/night/day/golden hour)
# volle maan, geen maan
# neerslag


# image:
# achtergrond: varieert tussen grijs (bewolkt) en blauw (minder bewolkt, clear sky)
# figuur: polygon waarbij de verschillende punten elkaars spiegelbeeld zijn per kwadrant
#    p1 : ~ windsnelheid
#    p2 : ~ 'inverse' van p1
#    background color van figuur: ~ temperatuur

# input van parameters
# clouds:        0 - 100
# windsnelheid:  0 - verwacht maximum: 30 a 40
# temperatuur:  onder nul tot 273 + x


################################################################
#
#   INCLUDES / REQUIRES
#
################################################################
import os
from dotenv import load_dotenv
import requests, json
import hashlib

#from libgravatar import Gravatar
from libgravatar import GravatarXMLRPC

import random
import numpy as np
import math

from PIL import Image, ImageDraw, ImageColor
import os

# https://openweathermap.org/weather-conditions
# PyGithub
# OpenWeatherMap


################################################################
#
#   CONFIG
#
################################################################
load_dotenv()
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
OPEN_WEATHER_API_KEY = os.getenv('OPEN_WEATHER_API_KEY')

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

base_url = "http://api.openweathermap.org/data/2.5/weather?"
city_name = "Bruges"

# name of the file to save
filename = "img01.png"
dim_x = 2000 * 2      # * 2 om te kunnen resizen ifv anti-alias
dim_y = 2000 * 2

base_color = (5, 210, 255)      # soort van sky blue

colors_old = [
   '#ffffff',
   '#E5F5FF',
   '#BFDEFF',
   '#05b4ff',

   '#6ca8ff',
   '#a598f9',
   '#d186e2',
   '#ef74c1',

   '#db36a4',
   '#FF6998',
   '#FF847D',

   '#FF9671',
   '#FFA967',
   '#FFC75F',
   '#F9F871'
]

colors = np.array(
   [
      ["#09BFE3","#19A5E3","#2A8BE3","#3A71E3","#4A57E3","#5A3DE3","#6B23E3","#7B09E3"],
      ["#5009C8","#5F0DC5","#6E11C3","#7D15C0","#8D1ABE","#9C1EBB","#AB22B9","#BA26B6"],
      ["#7B09E3","#8714DA","#931ED1","#9F29C8","#AB34C0","#B73FB7","#C349AE","#CF54A5"],
      ["#BA26B6","#BF36B7","#C446B9","#C956BA","#CD67BB","#D277BC","#D787BE","#DC97BF"],
      ["#CF54A5","#D4688D","#DA7C76","#DF905E","#E5A447","#EAB82F","#F0CC18","#F5E000"]
   ]
)

minTemp = 273     # ~ 0 graden celcius
maxTemp = 305     # ~ 32 graden celcius


################################################################
#
#   INITZ
#
################################################################
dim_x2 = round(dim_x / 2)               # dimensies in 2 ifv gemakkelijker berekeningen
dim_y2 = round(dim_y / 2)              
dim_x4 = round(dim_x2 / 2)
dim_y4 = round(dim_y2 / 2) 


################################################################
#
#   FUNCTIONS
#
################################################################
def create_image_weather(clouds, temp, windSpeed):
   # berekenen van waardes
   #clouds = 100 - clouds
   clouds = clouds / 100
   alpha = round(255 * clouds)
   offset = getOffsetFromWind(windSpeed)
   colorIndex = mapTemp(temp)
   colors = getColors(colorIndex)
   fgColor = colors[0]
   bgColor = colors[7]

   # achtergrond kleur op grijs zetten
   imageBg = Image.new(mode = "RGBA", size = (dim_x, dim_y), color = '#32A6F7')

   # voorgrond image aanmaken
   imageFg = Image.new(mode = "RGBA", size = (dim_x, dim_y), color = 'grey')
   imageFg.putalpha(alpha)

   # achtergrond samenvoegen met voorgrond
   imageBg.paste(imageFg, (0,0), imageFg)

   # figuur erop zetten
   draw = ImageDraw.Draw(imageBg)

   # punten berekenen
   origin = (dim_x2, dim_y2)

   print("offset     = ", offset)

   pm = (dim_x2, dim_y2)

   p1 = (dim_x4 - offset, dim_y2)
   p3 = rotate(origin, p1, np.pi / 2)
   p5 = rotate(origin, p1, np.pi)
   p7 = rotate(origin, p3, np.pi)

   p2 = (dim_x4 + offset, dim_y2)
   p2 = rotate(origin, p2, np.pi / 4)
   p4 = rotate(origin, p2, np.pi / 2)
   p6 = rotate(origin, p2, np.pi)
   p8 = rotate(origin, p4, np.pi)

   draw.polygon((p1, p2, p3, p4, p5, p6, p7, p8), fill=fgColor, outline=None)

   # now draw the triangles (hardcoded, because the points are also hardcoded from p1 to p8)
   draw.polygon((p7, p8, pm), fill=colors[1], outline=colors[0])
   draw.polygon((p8, p1, pm), fill=colors[3], outline=colors[0])
   draw.polygon((p6, p5, pm), fill=colors[2], outline=colors[0])
   draw.polygon((p1, p2, pm), fill=colors[4], outline=colors[0])
   draw.polygon((p5, p4, pm), fill=colors[5], outline=colors[0])
   draw.polygon((p2, p3, pm), fill=colors[6], outline=colors[0])
   draw.polygon((p4, p3, pm), fill=colors[7], outline=colors[0])

   # resizen om anti-alias mogelijk te maken, en saven; LANCZOS ~ anti-alias
   imageBg = imageBg.resize((dim_x2, dim_y2), resample=Image.LANCZOS)
   imageBg.save(filename)

def mapWeather(w):
   clouds = 0
   windSpeed = 0
   temp = 0

   # mss later gebruiken:
   # windDegree = 0
   # sunset = 0
   # sunrise = 0

   try:      
      clouds      = w["clouds"]["all"]
      windSpeed   = w["wind"]["speed"]
      temp        = w["main"]["feels_like"]
      #windDegree  = w["wind"]["deg"]      
      #sunrise     = w["sys"]["sunrise"]
      #sunset      = w["sys"]["sunset"]
   except:
      print("error while parsing the weather")

   return (clouds, windSpeed, temp)


def mapWind(wind):
   magicFactor = 25
   return np.tanh((wind -4) / magicFactor)

def getOffsetFromWind(windSpeed):
   # some parameters for the custom mapping algo
   windCorrectionTerm = 2
   correctionTerm = -300
   correctionFactor = 2500

   splitCutoff = 350
   splitFactor = 4

   maxWindSpeed = 30

   # the algo
   mapped = (windSpeed + windCorrectionTerm) / maxWindSpeed * correctionFactor + correctionTerm

   # apply corrections because values above 350 climb too fast
   if(mapped > splitCutoff):
      factor = mapped / splitCutoff
      factor = factor - 1
      factor = factor / splitFactor
      factor = factor + 1
      factor = 1 / factor
      mapped = mapped * factor

   return mapped

def mapTemp(temp):   
   if temp <= minTemp:
      return 0
   if temp >= maxTemp:
      return len(colors)-1
   
   range = maxTemp - minTemp
   index = math.floor((temp - minTemp) / range * len(colors))

   return index

def getColors(colorIndex):
   return colors[colorIndex]

def getColor(index):
   return colors[index]


def getPairedColor(index):
   if index >= len(colors) -1:
      return (0,0,0)
   
   return colors[index +1]


def rotate(origin, point, angle):
   """
   Rotate a point counterclockwise by a given angle around a given origin.
   The angle should be given in radians.
   """
   ox, oy = origin
   px, py = point

   qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
   qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
   return round(qx), round(qy)


def uploadToGravatar(imageBase64):
   g = GravatarXMLRPC(email=EMAIL, password=PASSWORD)
   res = g._call("saveData", {'data':imageBase64})
   g._call("useUserimage",  {'userimage': res, 'addresses': MAILS_TO_ATTACH })


def fetch_weather():
    complete_url = base_url + "appid=" + OPEN_WEATHER_API_KEY + "&q=" + city_name 
    print(complete_url)
  
    # get method of requests module 
    # return response object 
    response = requests.get(complete_url) 
  
    # json method of response object  
    # convert json format data into 
    # python format data 
    x = response.json() 
    
    if x["cod"] != "404":
       return x
    else:
      return None

def createColorBlocks():
   # config
   size = 2000
   filename = "swaps.png"

   # init
   imgSwaps = Image.new(mode = "RGBA", size = (size, size), color = 'black')
   drawSwaps = ImageDraw.Draw(imgSwaps)

   # get dimensions
   rows = len(colors)
   cols = len(colors[0])

   colorCount = rows * cols
   grid = math.ceil(math.sqrt(colorCount))
   width = size / grid

   # colors loopen en telkens tekenen
   i = 0

   for row in range(0, grid):
      for col in range(0, grid):
         if i < colorCount:
            mainColorIndex = math.floor(i / cols)
            mainColor = colors[mainColorIndex]
            subColorIndex = i % cols
            color = mainColor[subColorIndex]

            x = math.floor(col * width)
            y = math.floor(row * width)
            x2 = x + width
            y2 = y + width
            drawSwaps.rectangle((x, y, x2, y2), fill=color, outline='black')
         i = i + 1

   imgSwaps.save(filename)
   exit(0)


def imgToBase64(filename):
   import base64

   with open(filename, "rb") as imageFile:
      return base64.b64encode(imageFile.read())
      

################################################################
#
#   MAIN
#
################################################################
def main():
   print ("create avatar image")
   res = fetch_weather()

   if res == None:
      print("error while fetching weather, try again of fix")
   else:
      weatherTuple = mapWeather(res)
      clouds = weatherTuple[0]
      windSpeed = weatherTuple[1]
      temp = weatherTuple[2]

      # test creation of image with hardcoded values
      temp = 273 + 20
      windSpeed = 0
      clouds = 23

      print("clouds     = ", clouds)
      print("windSpeed  = ", round(windSpeed))
      print("temp       = ", round(temp - 273))

      create_image_weather(clouds, temp, windSpeed)
      print("image created")
      encoded = imgToBase64(filename)
      print(filename)
      #uploadToGravatar(encoded)
      #print("image uploaded")

      # tonen welke colors er gedefinieerd zijn in de color array, om gemakkelijker te zien welke uit de toon vallen
      createColorBlocks()


if __name__ == "__main__":
    main()
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
crop = 400

# colorpalettes created with
# https://coolors.co/6ad2f5-118ab2-06d6a0-ffd166-f73562
#

colors = np.array(
   [
      ["#6AD2F5", "#5DC8EB", "#51BDE2", "#44B3D8", "#37A9CF", "#2A9FC5", "#1E94BC", "#118AB2"],
      ["#118AB2", "#0F95AF", "#0EA0AD", "#0CABAA", "#0BB5A8", "#09C0A5", "#08CBA3", "#06D6A0"],
      ["#06D6A0", "#2AD598", "#4DD58F", "#71D487", "#94D37F", "#B8D277", "#DBD26E", "#FFD166"],
      ["#FFD166", "#FEBB65", "#FDA465", "#FC8E64", "#FA7864", "#F96263", "#F84B63", "#F73562"],
      ["#F73562", "#F84C72", "#F96282", "#FA7992", "#FC8FA3", "#FDA6B3", "#FEBCC3", "#FFD3D3"]
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
   draw.polygon((p7, p8, pm), fill=colors[1], outline='black')
   draw.polygon((p8, p1, pm), fill=colors[3], outline='black')
   draw.polygon((p6, p5, pm), fill=colors[2], outline='black')
   draw.polygon((p1, p2, pm), fill=colors[4], outline='black')
   draw.polygon((p5, p4, pm), fill=colors[5], outline='black')
   draw.polygon((p2, p3, pm), fill=colors[6], outline='black')
   draw.polygon((p4, p3, pm), fill=colors[7], outline='black')

   # resizen om anti-alias mogelijk te maken, en saven; LANCZOS ~ anti-alias
   imageBg = imageBg.resize((dim_x2, dim_y2), resample=Image.LANCZOS)

   #dimensions to crop
   factor = 1 - ((windSpeed + 1) / 20)
   cropFactor = abs(math.ceil(crop * factor))

   print(cropFactor)

   dim1 = math.ceil(cropFactor)
   dim2 = math.ceil(dim_y/2 - cropFactor)
   box = (dim1, dim1, dim2, dim2)
   imageBg = imageBg.crop(box)

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
      print("image uploaded")

      # tonen welke colors er gedefinieerd zijn in de color array, om gemakkelijker te zien welke uit de toon vallen
      createColorBlocks()


if __name__ == "__main__":
    main()
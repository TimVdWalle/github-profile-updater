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

from datetime import date, datetime
# from libgravatar import Gravatar
from libgravatar import GravatarXMLRPC

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
MAILS_TO_ATTACH = os.environ.get('ATTACH_IMAGE_TO_MAILS_SIMPLE').split(',')

base_url = "http://api.openweathermap.org/data/2.5/weather?"
city_name = "Bruges"

# name of the file to save
filename = "img01_simple.png"
dim_x = 2000 * 2  # * 2 om te kunnen resizen ifv anti-alias
dim_y = 2000 * 2
crop = 300

# colorpalettes created with
# https://coolors.co/6ad2f5-118ab2-06d6a0-ffd166-f73562
# https://coolors.co/gradient-palette/f73562-ffd3d3?number=8

colors = np.array(
    [
        ["#6AD2F5", "#7BD7F6", "#8CDDF8", "#9DE2F9", "#ADE7FB", "#BEECFC", "#CFF2FE", "#E0F7FF"],
        ["#118AB2", "#2B99BD", "#46A8C8", "#60B7D3", "#7AC5DE", "#94D4E9", "#AFE3F4", "#C9F2FF"],
        ["#0F9DAE", "#27ABB9", "#3FB9C4", "#57C7CF", "#70D5DA", "#88E3E5", "#A0F1F0", "#B8FFFB"],
        ["#06D6A0", "#21DCAB", "#3DE2B7", "#58E8C2", "#74EDCE", "#8FF3D9", "#ABF9E5", "#C6FFF0"],
        ["#83D483", "#8DDA8D", "#96E096", "#A0E6A0", "#A9EDA9", "#B3F3B3", "#BCF9BC", "#C6FFC6"],
        ["#FFD166", "#FFD675", "#FFDA84", "#FFDF93", "#FFE3A3", "#FFE8B2", "#FFECC1", "#FFF1D0"],
        ["#FB8364", "#FC8F73", "#FC9B82", "#FDA791", "#FDB39F", "#FEBFAE", "#FECBBD", "#FFD7CC"],
        ["#F73562", "#F84C72", "#F96282", "#FA7992", "#FC8FA3", "#FDA6B3", "#FEBCC3", "#FFD3D3"]
    ]
)

minTemp = 273 - 1  # ~ -0 graden celcius
maxTemp = 273 + 35  # ~ 30 graden celcius



################################################################
#
#   INITZ
#
################################################################
dim_x2 = round(dim_x / 2)  # dimensies in 2 ifv gemakkelijker berekeningen
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
    # clouds = 100 - clouds
    colorIndex = mapTemp(temp)
    colors = getColors(colorIndex)

    # achtergrond kleur op grijs zetten
    imageBg = generate_gradient(colors[7], colors[0], dim_x, dim_y)

    # resizen om anti-alias mogelijk te maken, en saven; LANCZOS ~ anti-alias
    imageBg = imageBg.resize((dim_x2, dim_y2), resample=Image.LANCZOS)

    imageBg.save(filename)


def generate_gradient(
        colour1: str, colour2: str, width: int, height: int) -> Image:
    """Generate a vertical gradient."""
    base = Image.new('RGB', (width, height), colour1)
    top = Image.new('RGB', (width, height), colour2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def mapWeather(w):
    clouds = 0
    windSpeed = 0
    temp = 0

    # mss later gebruiken:
    # windDegree = 0
    # sunset = 0
    # sunrise = 0

    try:
        clouds = w["clouds"]["all"]
        windSpeed = w["wind"]["speed"]
        temp = w["main"]["feels_like"]
        # windDegree  = w["wind"]["deg"]
        # sunrise     = w["sys"]["sunrise"]
        # sunset      = w["sys"]["sunset"]
    except:
        print("error while parsing the weather")

    return (clouds, windSpeed, temp)


def mapTemp(temp):
    if temp <= minTemp:
        return 0
    if temp >= maxTemp:
        return len(colors) - 1

    range = maxTemp - minTemp
    index = math.floor((temp - minTemp) / range * len(colors))

    return index


def getColors(colorIndex):
    return colors[colorIndex]


def getColor(index):
    return colors[index]

def uploadToGravatar(imageBase64):
    g = GravatarXMLRPC(email=EMAIL, password=PASSWORD)
    res = g._call("saveData", {'data': imageBase64})
    g._call("useUserimage", {'userimage': res, 'addresses': MAILS_TO_ATTACH})


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
    imgSwaps = Image.new(mode="RGBA", size=(size, size), color='black')
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
    # add datetime to output for easier logging
    now = datetime.now()
    print("now =", now)

    print("create avatar image")
    res = fetch_weather()

    if res == None:
        print("error while fetching weather, try again of fix")
    else:
        weatherTuple = mapWeather(res)
        clouds = weatherTuple[0]
        windSpeed = weatherTuple[1]
        temp = weatherTuple[2]

        # test creation of image with hardcoded values
        # temp = 273 + 31
        # windSpeed = 7
        # clouds = 10

        print("clouds     = ", clouds)
        print("windSpeed  = ", round(windSpeed))
        print("temp       = ", round(temp - 273))

        create_image_weather(clouds, temp, windSpeed)
        print("image created")
        encoded = imgToBase64(filename)
        print(filename)
        uploadToGravatar(encoded)
        print("image uploaded")

        # tonen welke colors er gedefinieerd zijn in de color array, om gemakkelijker te zien welke uit de toon vallen
        createColorBlocks()


if __name__ == "__main__":
    main()

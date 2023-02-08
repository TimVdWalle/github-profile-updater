################################################################
#
#   INCLUDES / REQUIRES
#
################################################################
import os
from dotenv import load_dotenv
from datetime import date
import requests, json

from github import Github

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

base_url = "http://api.openweathermap.org/data/2.5/weather?"
city_name = "Bruges"

################################################################
#
#   INIT
#
################################################################
print ("github profile updater")
g = Github(GITHUB_ACCESS_TOKEN)


################################################################
#
#   FUNCTIONS
#
################################################################
def updateGitBio(bio):
    print("updating bio in github profile:")
    print(bio)
    g.get_user().edit(bio=bio)

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
    
    # Now x contains list of nested dictionaries 
    # Check the value of "cod" key is equal to 
    # "404", means city is found otherwise, 
    # city is not found 
    if x["cod"] != "404": 
        weather = x["weather"]
        weather_id = weather[0]["id"]
        weather_main = weather[0]["main"]
        windspeed = x["wind"]["speed"]
        #weather_description = weather[0]["description"] 
        
        #print(weather_id)
        #print(weather_main)
        #print(weather_description)

        print("windspeed = ", windspeed)

        return mapDescription(weather_id, weather_main, windspeed)
    
    else: 
        print(" City Not Found ") 
        return "not snowing"


def mapDescription(id, main, windspeed):
   if(main == "Mist"):
      return "misty"
   if(main == "Fog"):
      return "foggy"

   if (id == 202) or (id == 211) or (id == 212) or (id == 221) or (id == 232):
      return "storming a lot"
   if (id == 200) or (id == 201) or (id == 210) or (id == 230) or (id == 231):
      return "storming"
   if(main == "Drizzle"):
      return "drizzling"
   if (id == 500) or (id == 501) or (id == 520) :
      return "raining"
   if (id == 502) or (id == 503) or (id == 504) or (id == 511) or (id == 521) or (id == 522) or (id == 531):
      return "raining a lot"

   if (id == 602) or (id == 621) or (id == 622):
      return "snowing heavy"
   if (id == 600) or (id == 601) or (id == 613) or (id == 615) or (id == 620):
      return "snowing"

   if (windspeed > 14):
      return "storming"   

   if(main == "Clear"):
      "clear sky"
   if(main == "Clouds"):
      return "cloudy"

################################################################
#
#   MAIN
#
################################################################

# fetching data weekday
weekday = date.today().strftime('%A (%d %B)')
bio1 = "Today is " + weekday
print (bio1)

# fetching data weather
weather = fetch_weather()
print(weather)



# updating bio
bio = bio1 + " and it is _" + weather + "_ here in Belgium."
updateGitBio(bio)


 

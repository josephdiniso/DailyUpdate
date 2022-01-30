import requests
import json

api_key = "d7038e81777f7ba6e1cec0c2d1fbc473"
city = "Blacksburg"
state = "VA"
country = "USA"
units = "imperial"
# r = requests.get(
#     f"http://api.openweathermap.org/data/2.5/forecast?q={city},{state},{country}&appid={api_key}&units={units}")
#
with open("test.txt", "r") as f:
    text = f.read()

obj = json.dumps(json.loads(text), indent=4)
with open("test.json", "w") as f:
    f.write(obj)


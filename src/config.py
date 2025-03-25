import json


file = open("etc/config.json", mode="r", encoding="utf-8")
config = json.load(file)
file.close()

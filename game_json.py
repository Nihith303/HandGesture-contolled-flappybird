import json
import time
from datetime import datetime

data_file = "game_data.json"

def get_current_day():
    return datetime.now().strftime("%Y-%m-%d")


def cal_total_time_played(game_data, start_time):
    current_date = get_current_day()
    elapsed_time = time.time() - start_time
    return game_data[current_date]["time_played"] + elapsed_time


def save_game_data(game_data, score, elapsed_time):
    current_date = get_current_day()
    game_data[current_date]["time_played"] += elapsed_time
    if score > game_data['Over_all_highest']:
        game_data['Over_all_highest'] = score
    if score > game_data[current_date]["high_score"]:
        game_data[current_date]["high_score"] = score
    with open(data_file, "w") as file:
            json.dump(game_data, file, indent=4)


def read_json():
    try:
        with open(data_file, "r") as file:
            content = file.read()
            if content.strip(): 
                game_data = json.loads(content)
            else:
                game_data = {}
    except (FileNotFoundError, json.JSONDecodeError):
        game_data = {}
    return game_data

def check_date_exist(game_data):
    current_date = get_current_day()
    if current_date not in game_data:
        game_data[current_date] = {"time_played": 0, "high_score": 0}







# import json

# # Sample data
# data = {
#     "name": "Alice",
#     "age": 30,
#     "city": "New York"
# }

# # Writing data to a JSON file
# with open("data.json", "w") as file:
#     json.dump(data, file, indent=4)

# # Reading data from a JSON file
# with open("data.json", "r") as file:
#     loaded_data = json.load(file)

# print(loaded_data)

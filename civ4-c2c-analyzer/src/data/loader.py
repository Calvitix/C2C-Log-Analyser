import os
import json



def load_game_data(directory_path):
    """Load all game data from JSON files in the specified directory, without flattening."""
    try:
        players_file = os.path.join(directory_path, "game_data_summary.json")
        cities_file = os.path.join(directory_path, "cities.json")
        timings_file = os.path.join(directory_path, "player_turn_timings.json")
        
        missing_files = []
        if not os.path.exists(players_file):
            missing_files.append("game_data_summary.json")
        if not os.path.exists(cities_file):
            missing_files.append("cities.json")
        if not os.path.exists(timings_file):
            missing_files.append("player_turn_timings.json")
        
        if missing_files:
            return None, None, None, missing_files
        
        with open(players_file, 'r', encoding='utf-8-sig') as f:
            players_raw = json.load(f)
        with open(cities_file, 'r', encoding='utf-8-sig') as f:
            cities_raw = json.load(f)
        with open(timings_file, 'r', encoding='utf-8-sig') as f:
            timings_raw = json.load(f)
        
        # Retourne les objets bruts, non aplatis
        return players_raw, cities_raw, timings_raw, None
    except Exception as e:
        return None, None, None, str(e)
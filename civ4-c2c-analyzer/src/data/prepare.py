import pandas as pd

# Préparation des données
def prepare_player_stats_df(players_data):
    """Convert player stats history to DataFrame"""
    all_stats = []
    for player in players_data:
        if player['isHuman']:  # Focus sur les joueurs humains
            for stat in player['statsHistory']:
                stat['playerName'] = player['name']
                stat['player_id'] = player['id']  # <-- Ajout de l'ID
                all_stats.append(stat)
    return pd.DataFrame(all_stats)

def prepare_city_history_df(cities_data):
    """Convert city history to DataFrame"""
    all_history = []
    for city in cities_data:
        for hist in city['history']:
            hist['cityName'] = city['name']
            hist['x'] = city['x']
            hist['y'] = city['y']
            hist['foundedTurn'] = city['foundedTurn']
            all_history.append(hist)
    return pd.DataFrame(all_history)

def prepare_timings_df(timings_data):
    """Convert timings to DataFrame and calculate durations"""
    df = pd.DataFrame(timings_data)
    # Calculer la durée en secondes
    df['duration'] = df.apply(lambda x: x['endTimestamp'] - x['beginTimestamp'] 
                            if x['endTimestamp'] > 0 else 0, axis=1)
    return df
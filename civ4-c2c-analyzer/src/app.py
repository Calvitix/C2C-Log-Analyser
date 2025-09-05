import streamlit as st
import os
import pandas as pd

from config import DEFAULT_DATA_PATH
from data.loader import load_game_data
from data.prepare import prepare_player_stats_df, prepare_city_history_df, prepare_timings_df

from views.overview import display_overview
from views.players import display_players_current_stats, display_players_history
from views.cities import  display_city_analysis
from views.timings import display_turn_timings
from views.comparative import display_comparative_analysis
from views.rankings import display_rankings
from views.score import display_score_analysis
from views.military import display_military_analysis
from views.units import display_unit_evaluation
from graph_config import GRAPH_CONFIG

def main():
    st.set_page_config(
        page_title="Civ4 C2C Game Analyzer",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for improved appearance
    st.markdown("""
    <style>
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
            margin: 5px;
        }
        .plot-container {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🎮 Civilization IV C2C Game Analyzer")
    st.markdown("---")

    st.sidebar.title("⚙️ Configuration")
    data_directory = st.sidebar.text_input(
        "Data Directory Path",
        value=DEFAULT_DATA_PATH,
        help="Path to the directory containing the JSON files"
    )

    # Bouton pour recharger les données
    if st.sidebar.button("🔄 Reload Data"):
        st.cache_data.clear()
        st.rerun()

    if not os.path.exists(data_directory):
        st.sidebar.error(f"❌ Directory not found: {data_directory}")
        return

    players_raw, cities_raw, timings_raw, error = load_game_data(data_directory)

    if error:
        st.sidebar.error(f"Erreur lors du chargement des données : {error}")
        return

    if not players_raw or not cities_raw:
        st.error("Unable to load game data. Please check that the JSON files are present in the specified directory.")
        
        # Afficher les instructions
        st.markdown("""
        ### 📋 Required Files
        
        The following JSON files must be present in the data directory:
        
        1. **game_data_summary.json** - Player statistics and history
        2. **cities.json** - City information and history
        3. **player_turn_timings.json** - Turn timing data
        
        ### 📁 Directory Structure
        
        ```
        Data/
        └── Output/
            └── json/
                ├── game_data_summary.json
                ├── cities.json
                └── player_turn_timings.json
        ```
        
        ### 🔧 How to specify a different directory
        
        1. Enter the full path in the "Data Directory Path" field in the sidebar
        2. Click "Reload Data" to load files from the new location
        
        Examples:
        - Windows: `C:\\Games\\Civ4\\Logs\\json`
        - Linux/Mac: `/home/user/civ4/logs/json`
        """)
        
        st.stop()

    # Afficher le chemin actuel des données
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📂 Current Data Source")
    st.sidebar.code(data_directory, language=None)


    # Préparation des DataFrames
    df_player_stats = prepare_player_stats_df(players_raw)
    df_city_history = prepare_city_history_df(cities_raw)
    df_timings = prepare_timings_df(timings_raw)


    # Création de la liste des joueurs "ID - Nom", triée par ID croissant
    if 'playerId' in df_player_stats.columns and 'playerName' in df_player_stats.columns:
        player_options = (
            df_player_stats[['playerId', 'playerName']]
            .drop_duplicates()
            .sort_values('playerId')
            .apply(lambda row: f"{row['playerId']} - {row['playerName']}", axis=1)
            .tolist()
        )
    else:
        player_options = []

    selected_players = st.sidebar.multiselect(
        "Sélectionner les joueurs",
        player_options,
        default=player_options
    )

    # Récupérer les IDs sélectionnés
    selected_player_ids = [
        int(option.split(" - ")[0]) for option in selected_players
    ]

    # Filtrer le DataFrame selon les IDs sélectionnés
    filtered_df_player_stats = df_player_stats[df_player_stats['playerId'].isin(selected_player_ids)]

    min_turn = int(filtered_df_player_stats['turn'].min()) if 'turn' in filtered_df_player_stats.columns and not filtered_df_player_stats.empty else 0
    max_turn = int(filtered_df_player_stats['turn'].max()) if 'turn' in filtered_df_player_stats.columns and not filtered_df_player_stats.empty else 0

    if min_turn < max_turn:
        turn_range = st.sidebar.slider("Select turn range", min_value=min_turn, max_value=max_turn, value=(min_turn, max_turn))
    else:
        turn_range = (min_turn, max_turn)
        st.sidebar.info("Not enough data to select a turn range.")

    tabs = st.tabs([
        "📊 Overview", "👥 Players Analysis", "🏛️ Cities Analysis", 
        "⚔️&🛠️ Units", "🎯 Score Analysis",
        "🏆 Rankings", "⏱️ Turn Timings", "📈 Comparative Analysis" 
    ])

    with tabs[0]:
        display_overview(filtered_df_player_stats, df_city_history, players_raw, cities_raw, data_directory)
        # Add other graph calls here according to the checkboxes

    with tabs[1]:
        display_players_current_stats(players_raw, selected_player_ids)
        display_players_history(filtered_df_player_stats, selected_player_ids, turn_range)
    with tabs[2]:
        selected_playerId = st.selectbox(
            "Select a player for city analysis",
            options=selected_player_ids,
            format_func=lambda x: f"{x} - {df_player_stats[df_player_stats['playerId'] == x]['playerName'].values[0]}"
        )
        if selected_playerId is not None:
            display_city_analysis(cities_raw, turn_range, selected_playerId)        
    with tabs[3]:
        with st.expander("Show/Hide Graph Options", expanded=False):
            show_units_analysis = st.checkbox(
                "Show military units analysis",
                value=GRAPH_CONFIG["units"]["show_units_analysis"]
            )
            show_unit_evaluation = st.checkbox(
                "Show unit evaluation analysis",
                value=GRAPH_CONFIG["units"]["show_unit_evaluation"]
            )
        if show_units_analysis:
            display_military_analysis(filtered_df_player_stats, selected_player_ids, turn_range, players_raw)  # Remplacez par le bon DataFrame si besoin
        if show_unit_evaluation:
            display_unit_evaluation(players_raw, selected_player_ids, turn_range)
    with tabs[4]:
        display_score_analysis(filtered_df_player_stats, selected_player_ids, turn_range)
    with tabs[5]:
        display_rankings(filtered_df_player_stats)
    with tabs[6]:
        df_timings = pd.DataFrame(timings_raw)
        display_turn_timings(df_timings, selected_player_ids, turn_range)
    with tabs[7]:
        display_comparative_analysis(filtered_df_player_stats, selected_player_ids, turn_range)

if __name__ == "__main__":
    main()
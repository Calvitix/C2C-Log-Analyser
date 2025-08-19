from streamlit import title, selectbox, metric, subheader, plotly_chart
import pandas as pd
import streamlit as st
from utils.plot import create_metric_chart, create_player_history_chart, create_economic_analysis_chart

def display_players_analysis(df_player_stats, selected_players, turn_range):
    """
    Display analysis for selected players over the specified turn range.
    Args:
        df_player_stats (pd.DataFrame): Player statistics DataFrame.
        selected_players (list): List of selected player names.
        turn_range (tuple): (start_turn, end_turn)
    """
    title("👥 Players Analysis")
    
    if 'playerName' not in df_player_stats.columns:
        st.info("No player data available.")
        return

    for player_id in selected_players:
        # Filter DataFrame by ID and turn range
        player_info = df_player_stats[
            (df_player_stats['player_id'] == player_id) &
            (df_player_stats['turn'] >= turn_range[0]) &
            (df_player_stats['turn'] <= turn_range[1])
        ]
        player_name = player_info['playerName'].iloc[0] if not player_info.empty else str(player_id)
        if not player_info.empty:
            latest_score = player_info.sort_values('turn')['score'].iloc[-1] if 'score' in player_info.columns else None
            st.metric(f"{player_id} - {player_name} - Latest Score", latest_score)
        else:
            st.info(f"No data for player {player_id}.")

    # For the detailed selectbox, rebuild the "ID - Name" list
    player_options = [
        f"{row['player_id']} - {row['playerName']}"
        for _, row in df_player_stats[['player_id', 'playerName']].drop_duplicates().sort_values('player_id').iterrows()
        if row['player_id'] in selected_players
    ]
    
    if not player_options:
        st.info("No player selected for detailed analysis.")
        return

    selected_player_str = selectbox("Select a player for detailed analysis", options=player_options)
    if selected_player_str is None:
        st.info("Please select a player for detailed analysis.")
        return

    player_id = int(selected_player_str.split(" - ")[0])
    player_info = df_player_stats[df_player_stats['player_id'] == player_id]    
    
    if not player_info.empty:
        current_stats = player_info['currentStats']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            metric("Cities", current_stats['cities'])
            metric("Population", current_stats['population'])
        
        with col2:
            metric("Military Power", current_stats['power'])
            metric("Tech %", current_stats['techPercent'])
        
        with col3:
            metric("Treasury", current_stats['treasury'])
            metric("Science Output", current_stats['totalScienceOutput'])
        
        with col4:
            metric("Total Units", current_stats['numUnits'])
            metric("Anarchy Turns", current_stats['totalTurnsInAnarchy'])
        
        subheader("📈 Detailed Evolution")
        
        player_history = pd.DataFrame(player_info['statsHistory'])
        
        selected_metric = selectbox(
            "Select metric to display",
            options=['Population', 'Cities', 'Military Power', 'Technology %', 'Treasury', 'Science Output', 'Food Output', 'Production Output']
        )
        
        fig = create_player_history_chart(player_history, selected_metric)
        plotly_chart(fig, use_container_width=True)
        
        subheader("💰 Economic Analysis")
        
        economic_cols = ['treasury', 'goldRate', 'maintenanceCost', 'civicUpkeepCost', 'unitUpkeep']
        
        if all(col in player_history.columns for col in economic_cols):
            fig_eco = create_economic_analysis_chart(
                df_player_stats, [player_info['playerName'].iloc[0]], turn_range
            )
            plotly_chart(fig_eco, use_container_width=True)

def display_players_current_stats(players_raw, selected_player_ids):
    """
    Display current stats for selected players.
    """
    st.subheader("🔎 Current Stats")
    for player in players_raw:
        if player['id'] in selected_player_ids:
            player_name = player['name']
            player_id = player['id']
            current_stats = player.get('currentStats', {})
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric(f"{player_id} - {player_name} | Cities", current_stats.get('cities', 0))
                metric("Population", current_stats.get('population', 0))
            with col2:
                metric("Military Power", current_stats.get('power', 0))
                metric("Tech %", current_stats.get('techPercent', 0))
            with col3:
                metric("Treasury", current_stats.get('treasury', 0))
                metric("Science Output", current_stats.get('totalScienceOutput', 0))
            with col4:
                metric("Total Units", current_stats.get('numUnits', 0))
                metric("Anarchy Turns", current_stats.get('totalTurnsInAnarchy', 0))

def display_players_history(df_player_stats, selected_player_ids, turn_range):
    """
    Display historical evolution for selected players.
    """
    st.subheader("📈 Detailed Evolution")
    player_options = [
        f"{row['player_id']} - {row['playerName']}"
        for _, row in df_player_stats[['player_id', 'playerName']].drop_duplicates().sort_values('player_id').iterrows()
        if row['player_id'] in selected_player_ids
    ]
    
    if not player_options:
        st.info("No player selected for detailed analysis.")
        return

    selected_player_str = selectbox("Select a player for detailed analysis", options=player_options)
    if selected_player_str is None:
        st.info("Please select a player for detailed analysis.")
        return

    player_id = int(selected_player_str.split(" - ")[0])
    player_info = df_player_stats[
        (df_player_stats['player_id'] == player_id) &
        (df_player_stats['turn'] >= turn_range[0]) &
        (df_player_stats['turn'] <= turn_range[1])
    ]
    if not player_info.empty:
        player_history = player_info
        selected_metric = selectbox(
            "Select metric to display",
            options=['Population', 'Cities', 'Military Power', 'Technology %', 'Treasury', 'Science Output', 'Food Output', 'Production Output']
        )
        fig = create_player_history_chart(player_history, selected_metric)
        plotly_chart(fig, use_container_width=True)
        subheader("💰 Economic Analysis")
        economic_cols = ['treasury', 'goldRate', 'maintenanceCost', 'civicUpkeepCost', 'unitUpkeep']
        if all(col in player_history.columns for col in economic_cols):
            fig_eco = create_economic_analysis_chart(
                df_player_stats, [player_info['playerName'].iloc[0]], turn_range
            )
            plotly_chart(fig_eco, use_container_width=True)


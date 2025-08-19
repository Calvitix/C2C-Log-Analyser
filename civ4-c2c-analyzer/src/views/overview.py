import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def display_overview(df_player_stats, df_city_history, players_data, cities_data, data_directory):
    st.header("📊 Game Overview")
    
    # Display data source
    st.info(f"📁 Data loaded from: `{data_directory}`")
    
    # General metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_turns = df_player_stats['turn'].max() if not df_player_stats.empty else 0
        st.metric("Total Turns", total_turns)
    
    with col2:
        total_cities = len(cities_data)
        st.metric("Total Cities Founded", total_cities)
    
    with col3:
        human_count = len([p for p in players_data if p['isHuman']])
        st.metric("Human Players", human_count)
    
    with col4:
        npc_count = len([p for p in players_data if not p['isHuman']])
        st.metric("NPC Players", npc_count)
    
    # Player selection and turn range selection
    all_players = df_player_stats['playerName'].unique().tolist() if 'playerName' in df_player_stats.columns else []
    selected_players = st.multiselect("Select players to display", all_players, default=all_players)
    min_turn = int(df_player_stats['turn'].min()) if 'turn' in df_player_stats.columns and not df_player_stats.empty else 0
    max_turn = int(df_player_stats['turn'].max()) if 'turn' in df_player_stats.columns and not df_player_stats.empty else 0

    if min_turn < max_turn:
        turn_range = st.slider("Select turn range", min_value=min_turn, max_value=max_turn, value=(min_turn, max_turn))
    else:
        st.info("Not enough data to select a turn range.")
        turn_range = (min_turn, max_turn)

    # Global progression plots
    st.subheader("🌍 Global Progression")
    df_filtered = df_player_stats[
        (df_player_stats['playerName'].isin(selected_players)) &
        (df_player_stats['turn'] >= turn_range[0]) &
        (df_player_stats['turn'] <= turn_range[1])
    ]
    
    if not df_filtered.empty:
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Population Growth', 'Military Power', 
                            'Number of Cities', 'Technology Progress'),
            vertical_spacing=0.1
        )
        
        for player in selected_players:
            player_data = df_filtered[df_filtered['playerName'] == player]
            
            # Population
            fig.add_trace(
                go.Scatter(x=player_data['turn'], y=player_data['population'],
                           name=player, mode='lines+markers', showlegend=True),
                row=1, col=1
            )
            
            # Power
            fig.add_trace(
                go.Scatter(x=player_data['turn'], y=player_data['power'],
                           name=player, mode='lines+markers', showlegend=False),
                row=1, col=2
            )
            
            # Cities
            fig.add_trace(
                go.Scatter(x=player_data['turn'], y=player_data['cities'],
                           name=player, mode='lines+markers', showlegend=False),
                row=2, col=1
            )
            
            # Tech
            fig.add_trace(
                go.Scatter(x=player_data['turn'], y=player_data['techPercent'],
                           name=player, mode='lines+markers', showlegend=False),
                row=2, col=2
            )
        
        fig.update_layout(height=600, title_text="Civilization Progress Overview")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No player data available to display global progression.")
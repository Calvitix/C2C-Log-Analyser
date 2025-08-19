from utils.plot import create_ranking_chart
import streamlit as st

def display_rankings(df_player_stats):
    if 'turn' not in df_player_stats.columns:
        st.info("No turn data available for rankings.")
        return

    latest_turn = df_player_stats['turn'].max()
    latest_data = df_player_stats[df_player_stats['turn'] == latest_turn]

    st.subheader(f"Rankings for Turn {latest_turn}")
    st.dataframe(latest_data)
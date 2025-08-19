from utils.plot import create_radar_chart, create_comparison_table, create_heatmap
import streamlit as st
import pandas as pd

def display_comparative_analysis(df_player_stats, selected_players, turn_range):
    st.header("📈 Comparative Analysis")
    
    if 'turn' not in df_player_stats.columns:
        st.info("No turn data available for comparison.")
        return

    if 'name' not in df_player_stats.columns:
        st.info("No player name data available for comparison.")
        st.dataframe(df_player_stats)
        return

    min_turn = int(df_player_stats['turn'].min()) if not df_player_stats.empty else 0
    max_turn = int(df_player_stats['turn'].max()) if not df_player_stats.empty else 0

    if min_turn < max_turn:
        comparison_turn = st.slider(
            "Select turn for comparison",
            min_value=min_turn,
            max_value=max_turn,
            value=max_turn
        )
    else:
        st.info("Not enough data to select a comparison turn.")
        comparison_turn = max_turn
    
    player_col = 'playerName' if 'playerName' in df_player_stats.columns else 'name'

    filtered_df = df_player_stats[
        (df_player_stats[player_col].isin(selected_players)) &
        (df_player_stats['turn'] >= turn_range[0]) &
        (df_player_stats['turn'] <= turn_range[1])
    ]

    # Safe to filter now
    turn_data = df_player_stats[
        (df_player_stats['turn'] == comparison_turn) &
        (df_player_stats[player_col].isin(selected_players))
    ]
    
    if not turn_data.empty:
        st.subheader(f"🎯 Player Comparison - Turn {comparison_turn}")
        
        categories = ['population', 'cities', 'power', 'techPercent', 
                     'totalScienceOutput', 'totalProductionOutput']
        
        fig_radar = create_radar_chart(turn_data, categories, selected_players)
        st.plotly_chart(fig_radar, use_container_width=True)
        
        st.subheader("📊 Detailed Comparison Table")
        comparison_metrics = ['population', 'cities', 'power', 'techPercent',
                            'treasury', 'totalScienceOutput', 'totalProductionOutput',
                            'numUnits', 'totalTurnsInAnarchy']

        comparison_df = turn_data[[player_col] + comparison_metrics].set_index(player_col)
        st.dataframe(comparison_df, use_container_width=True)

        st.subheader("📊 Comparison Heatmap")
        normalized_df = comparison_df.copy()
        for col in comparison_metrics:
            normalized_df[col] = (normalized_df[col] / normalized_df[col].max()) * 100

        fig_heatmap = create_heatmap(normalized_df)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.warning("No data available for the selected turn.")
import streamlit as st
import pandas as pd
import plotly.express as px

def display_turn_timings(df_timings, selected_players, turn_range):
    """
    Display analysis for player turn timings.
    Args:
        df_timings (pd.DataFrame): Turn timings DataFrame.
        selected_players (list): List of selected player names.
        turn_range (tuple): (start_turn, end_turn)
    """
    if df_timings is None or df_timings.empty:
        st.info("No timing data available.")
        return

    if 'playerName' not in df_timings.columns:
        st.info("No player name data available in timings.")
        st.dataframe(df_timings)
        return

    # Filter by player and turn range
    filtered = df_timings[
        (df_timings['playerName'].isin(selected_players)) &
        (df_timings['turn'] >= turn_range[0]) &
        (df_timings['turn'] <= turn_range[1])
    ]

    # Calculate duration if possible
    if 'beginTimestamp' in filtered.columns and 'endTimestamp' in filtered.columns:
        filtered = filtered.copy()
        filtered['duration'] = filtered['endTimestamp'] - filtered['beginTimestamp']

    st.dataframe(filtered)

    st.header("⏱️ Turn Timings Analysis")
    
    # Filter the timing data
    df_timings_filtered = df_timings[
        (df_timings['playerName'].isin(selected_players)) &
        (df_timings['turn'] >= turn_range[0]) &
        (df_timings['turn'] <= turn_range[1])
    ]
    
    if not df_timings_filtered.empty:
        # Average duration by player
        st.subheader("⏳ Average Turn Duration by Player")
        
        avg_duration = df_timings_filtered.groupby('playerName')['duration'].mean().sort_values(ascending=False)
        
        fig_avg = px.bar(
            x=avg_duration.values,
            y=avg_duration.index,
            orientation='h',
            title="Average Turn Duration (seconds)",
            labels={'x': 'Duration (s)', 'y': 'Player'}
        )
        
        st.plotly_chart(fig_avg, use_container_width=True)
        
        # Evolution of turn durations
        st.subheader("📈 Turn Duration Evolution")
        
        fig_evolution = px.line(
            df_timings_filtered,
            x='turn',
            y='duration',
            color='playerName',
            title="Turn Duration Over Time",
            labels={'duration': 'Duration (s)', 'turn': 'Turn'}
        )
        
        st.plotly_chart(fig_evolution, use_container_width=True)
        
        # Heatmap of durations
        st.subheader("🔥 Turn Duration Heatmap")
        
        heatmap_data = df_timings_filtered.pivot_table(
            values='duration',
            index='playerName',
            columns='turn',
            aggfunc='mean'
        )
        
        fig_heatmap = px.imshow(
            heatmap_data,
            title="Turn Duration Heatmap",
            labels=dict(x="Turn", y="Player", color="Duration (s)"),
            aspect="auto"
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
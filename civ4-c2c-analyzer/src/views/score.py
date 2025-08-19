from streamlit import title, subheader, metric, plotly_chart
import streamlit as st
import pandas as pd
import plotly.express as px

def display_score_analysis(df_player_stats, selected_players, turn_range):
    required_columns = ['population', 'score', 'power']
    missing = [col for col in required_columns if col not in df_player_stats.columns]
    if missing:
        st.info(f"Missing columns for score analysis: {', '.join(missing)}")
        return

    title("🎯 Score Analysis")
    player_col = 'playerName' if 'playerName' in df_player_stats.columns else 'name'

    # Calculate composite score
    df_player_stats['composite_score'] = (
        df_player_stats['population'] * 10 +
        df_player_stats['cities'] * 50 +
        df_player_stats['power'] * 0.1 +
        df_player_stats['techPercent'] * 5
    )

    # Filter data based on selected players and turn range
    score_data = df_player_stats[
        (df_player_stats[player_col].isin(selected_players)) &
        (df_player_stats['turn'] >= turn_range[0]) &
        (df_player_stats['turn'] <= turn_range[1])
    ]

    if not score_data.empty:
        # Plot score evolution
        fig_score_evolution = px.line(
            score_data,
            x='turn',
            y='composite_score',
            color=player_col,
            title="Composite Score Evolution",
            labels={'composite_score': 'Composite Score', 'turn': 'Turn'}
        )
        
        plotly_chart(fig_score_evolution, use_container_width=True)

        # Display score data in a table
        score_summary = score_data[[player_col, 'turn', 'composite_score']]
        score_summary = score_summary.groupby(player_col).agg({'composite_score': 'max'}).reset_index()

        # Show the summary table
        st.subheader("📊 Score Summary")
        st.dataframe(score_summary, use_container_width=True)
    else:
        st.warning("No score data available for the selected players and turn range.")
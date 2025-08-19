from streamlit import title, subheader, selectbox, plotly_chart
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def display_units_analysis(units_data):
    title("⚔️ Military Units Analysis")
    
    if units_data is not None and not units_data.empty:
        subheader("📊 Units Overview")
        
        # Select a unit for detailed analysis
        unit_names = units_data['name'].unique()
        selected_unit = selectbox("Select a unit for detailed analysis", unit_names)
        
        unit_info = units_data[units_data['name'] == selected_unit]
        
        if not unit_info.empty:
            st.metric("Attack", unit_info['attack'].values[0])
            st.metric("Defense", unit_info['defense'].values[0])
            st.metric("Movement", unit_info['movement'].values[0])
            st.metric("Cost", unit_info['cost'].values[0])
            
            # Historical performance
            st.subheader("📈 Historical Performance")
            performance_data = unit_info['performanceHistory'].values[0]
            performance_df = pd.DataFrame(performance_data)
            
            fig = px.line(performance_df, x='turn', y='value', title=f"{selected_unit} Performance Over Time")
            plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No unit data available for analysis.")

def display_unit_evaluation(players_data, selected_players, turn_range):
    st.header("🧮 Unit Evaluation Analysis")

    # Collect evaluation data for selected players
    all_evaluations = []
    all_best_units = []
    for player in players_data:
        if player.get('isHuman') and 'unitEvaluation' in player:
            evals = player['unitEvaluation'].get('evaluations', [])
            for e in evals:
                e['playerName'] = player['name']
                e['playerId'] = player['unitEvaluation'].get('playerId', None)
                all_evaluations.append(e)
            best_units = player['unitEvaluation'].get('bestUnitsByAIType', {})
            for ai_type, units in best_units.items():
                for u in units:
                    u['playerName'] = player['name']
                    u['playerId'] = player['unitEvaluation'].get('playerId', None)
                    u['unitAIType'] = ai_type
                    all_best_units.append(u)

    if all_evaluations:
        df_eval = pd.DataFrame(all_evaluations)
        df_eval_filtered = df_eval[
            (df_eval['playerId'].isin(selected_players)) &
            (df_eval['turn'] >= turn_range[0]) &
            (df_eval['turn'] <= turn_range[1])
        ]

        st.subheader("📈 Unit Value Evolution")
        ai_types = sorted(df_eval_filtered['unitAIType'].unique())
        selected_ai_type = st.selectbox("Select AI Type", ai_types, key="unit_eval_ai_type")

        df_ai = df_eval_filtered[df_eval_filtered['unitAIType'] == selected_ai_type]

        if not df_ai.empty:

            # Add rolling mean and standard deviation analysis
            window_size = st.selectbox("Rolling window size", [10, 20, 50, 100], index=0)

            # Calculate rolling mean and standard deviation for each unitType
            df_ai_sorted = df_ai.sort_values(['unitType', 'turn'])
            df_ai_sorted['rolling_mean'] = df_ai_sorted.groupby('unitType')['calculatedValue'].transform(lambda x: x.rolling(window_size, min_periods=1).mean())
            df_ai_sorted['rolling_std'] = df_ai_sorted.groupby('unitType')['calculatedValue'].transform(lambda x: x.rolling(window_size, min_periods=1).std())

            # Display rolling mean (trié par tour)
            fig_mean = px.line(
                df_ai_sorted.sort_values('turn'),
                x='turn',
                y='rolling_mean',
                color='unitType',
                title=f"Rolling Mean ({window_size}) - Unit Value Evolution ({selected_ai_type})",
                labels={'rolling_mean': 'Rolling Mean', 'turn': 'Turn', 'unitType': 'Unit Type'}
            )
            st.plotly_chart(fig_mean, use_container_width=True)

            st.markdown("#### 🏅 Best Units per Turn")
            best_units_df = df_ai[df_ai.get('isBetterUnit', True)].sort_values('turn')
            if not best_units_df.empty:
                st.dataframe(
                    best_units_df[['turn', 'unitType', 'unitName', 'calculatedValue', 'baseValue', 'finalValue']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No best units for this AI type in the selected range.")
        else:
            st.warning("No evaluation data for this AI type in the selected range.")

    if all_best_units:
        df_best = pd.DataFrame(all_best_units)
        df_best_filtered = df_best[
            (df_best['playerId'].isin(selected_players)) &
            (df_best['unitAIType'] == selected_ai_type)
        ]

        st.subheader("🏆 Best Units by AI Type")
        if not df_best_filtered.empty:
            fig_best = px.scatter(
                df_best_filtered.sort_values('firstTurn'),
                x='firstTurn',
                y='finalValue',
                color='unitType',
                hover_data=['unitName', 'baseValue'],
                title=f"Best Units ({selected_ai_type}) Over Time",
                labels={'firstTurn': 'First Turn', 'finalValue': 'Final Value'}
            )
            st.plotly_chart(fig_best, use_container_width=True)

            st.dataframe(
                df_best_filtered.sort_values('firstTurn')[['firstTurn', 'unitType', 'unitName', 'finalValue', 'baseValue']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No best unit data available for this AI type.")
    else:
        st.warning("No best unit data available.")


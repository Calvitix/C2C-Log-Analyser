from streamlit import title, subheader, selectbox, plotly_chart
import streamlit as st
import pandas as pd
import plotly.express as px

def display_military_analysis(df_player_stats, selected_players, turn_range, players_data):
    title("⚔️ Units Analysis")

    # Prepare unit data
    all_units = []
    for player in players_data:
        if player['isHuman'] and 'unitInventories' in player:
            for inventory in player['unitInventories']:
                for unit_key, unit_data in inventory['unitsByType'].items():
                    unit_entry = {
                        'playerId': inventory['playerId'],
                        'playerName': player['name'],  # <-- add this line
                        'turn': inventory['turn'],
                        'unitType': unit_data['unitType'],
                        'unitAIType': unit_data['unitAIType'],
                        'count': unit_data['count'],
                        'combatValue': unit_data['combatValue'],
                        'movement': unit_data['movement']
                    }
                    all_units.append(unit_entry)

    # For the detailed selectbox, rebuild the "ID - Name" list
    player_options = [
        f"{row['player_id']} - {row['playerName']}"
        for _, row in df_player_stats[['player_id', 'playerName']].drop_duplicates().sort_values('player_id').iterrows()
        if row['player_id'] in selected_players
    ]

    if not player_options:
        st.info("No player selected for detailed analysis.")
        return



    df_units_compar = pd.DataFrame(all_units)

    # Apply filters
    df_units_compar_filtered = df_units_compar[
        (df_units_compar['playerId'].isin(selected_players)) &
        (df_units_compar['turn'] >= turn_range[0]) &
        (df_units_compar['turn'] <= turn_range[1])
    ]

    civil_ai_types = ['UNITAI_WORKER', 'UNITAI_SETTLE', 'UNITAI_PROPHET', 'UNITAI_SUBDUED_ANIMAL', 'UNITAI_MISSIONARY','UNITAI_SPY','UNITAI_CIVILIAN']
    military_ai_types = [
        'UNITAI_ATTACK', 'UNITAI_ATTACK_CITY', 'UNITAI_CITY_DEFENSE', 'UNITAI_COLLATERAL',
        'UNITAI_PILLAGE', 'UNITAI_RESERVE', 'UNITAI_COUNTER', 'UNITAI_PARADROP', 'UNITAI_HUNTER', 
        'UNITAI_ESCORT', 'UNITAI_ASSAULT_SEA', 'UNITAI_ASSAULT_AIR', 'UNITAI_CARRIER','UNITAI_AIRLIFT','UNITAI_AIR_STRIKE',
        'UNITAI_AIR_DEFENSE', 'UNITAI_AIR_PATROL', 'UNITAI_AIR_BOMBARD', 'UNITAI_AIR_RECON','UNITAI_AIR_ESCORT', 'UNITAI_AIR_CARRIER'
    ]


    # View 5: Military strength comparison
    st.subheader("⚔️ Military Strength Comparison")
    military_units = df_units_compar_filtered[df_units_compar_filtered['unitAIType'].isin(military_ai_types)]
    if not military_units.empty:
        military_strength = military_units.groupby(['turn', 'playerName'])['count'].sum().reset_index()
        military_strength.rename(columns={'count': 'military_units'}, inplace=True)
        fig_military = px.line(
            military_strength,
            x='turn',
            y='military_units',
            color='playerName',
            title="Military Units Comparison",
            markers=True
        )
        st.plotly_chart(fig_military, use_container_width=True)


    selected_player_str = selectbox(
        "Select a player for detailed analysis",
        options=player_options,
        key="military_player_selectbox"
    )
    
    if selected_player_str is None:
        st.info("Please select a player for detailed analysis.")
        return    

    player_id = int(selected_player_str.split(" - ")[0])
    player_info = df_player_stats[df_player_stats['player_id'] == player_id]    


    if all_units:
        df_units = pd.DataFrame(all_units)

        # Apply filters
        df_units_filtered = df_units[
            (df_units['playerId'] == player_id) &
            (df_units['turn'] >= turn_range[0]) &
            (df_units['turn'] <= turn_range[1])
        ]

        if not df_units_filtered.empty:
            # View 1: Total units over time
            st.subheader("📈 Total Units Evolution")
            total_units_by_turn = df_units_filtered.groupby(['turn', 'playerName'])['count'].sum().reset_index()
            fig_total_units = px.line(
                total_units_by_turn,
                x='turn',
                y='count',
                color='playerName',
                title=f"Total Units Over Time (Turns {turn_range[0]}-{turn_range[1]})",
                markers=True
            )
            st.plotly_chart(fig_total_units, use_container_width=True)


            # View 5: Military Unit Type Repartition History (selected player)
            st.subheader("⚔️ Military Unit Type Repartition History")

            # Filter only for the selected player
            player_turn_units = df_units_filtered[df_units_filtered['playerName'] == selected_player_str.split(" - ")[1]]

            if not player_turn_units.empty:
                # Group by turn and unitType, sum counts
                repartition_history = player_turn_units.groupby(['turn', 'unitType'])['count'].sum().reset_index()
                # Stacked area chart: evolution of unit types over time
                fig_repartition = px.area(
                    repartition_history,
                    x='turn',
                    y='count',
                    color='unitType',
                    title=f"{selected_player_str.split(' - ')[1]} - Unit Type Repartition History",
                    labels={'count': 'Number of Units', 'unitType': 'Unit Type'}
                )
                st.plotly_chart(fig_repartition, use_container_width=True)
            else:
                st.info("No unit data available for this player in the selected turn range.")


            # View: UnitAI Type Repartition History (selected player)
            st.subheader("🤖 UnitAI Type Repartition History")
            # Group by turn and unitAIType, sum counts
            repartition_ai_history = player_turn_units.groupby(['turn', 'unitAIType'])['count'].sum().reset_index()
            fig_ai_repartition = px.area(
                repartition_ai_history,
                x='turn',
                y='count',
                color='unitAIType',
                title=f"{selected_player_str.split(' - ')[1]} - UnitAI Type Repartition History",
                labels={'count': 'Number of Units', 'unitAIType': 'UnitAI Type'}
            )
            st.plotly_chart(fig_ai_repartition, use_container_width=True)


            # View 4: Specific unit types evolution
            st.subheader("📊 Specific Unit Types Evolution")
            all_unit_types = sorted(df_units_filtered['unitType'].unique())

            # Sélection par défaut : les 10 types les plus présents
            top_unit_types = (
                df_units_filtered.groupby('unitType')['count'].sum()
                .sort_values(ascending=False)
                .head(10)
                .index.tolist()
            )





            selected_unit_types = st.multiselect(
                "Select unit types to track",
                options=all_unit_types,
                default=top_unit_types
            )
            if not selected_unit_types:
                st.warning("Please select at least one unit type to display its evolution.")
                return
            # Filter for selected unit types and only for the selected player
            player_name = selected_player_str.split(" - ")[1]
            specific_units = df_units_filtered[
                (df_units_filtered['unitType'].isin(selected_unit_types)) &
                (df_units_filtered['playerName'] == player_name)
            ]
            if not specific_units.empty:
                # Sum counts for selected unit types per turn
                summed_units = specific_units.groupby('turn')['count'].sum().reset_index()
                fig_specific = px.line(
                    summed_units,
                    x='turn',
                    y='count',
                    title=f"{player_name} - Total Selected Unit Types Evolution",
                    markers=True,
                    labels={'count': 'Total Units'}
                )
                st.plotly_chart(fig_specific, use_container_width=True)

                # Show repartition of selected unit types over time (stacked area chart)
                repartition_selected_types = specific_units.groupby(['turn', 'unitType'])['count'].sum().reset_index()
                fig_repartition_selected = px.area(
                    repartition_selected_types,
                    x='turn',
                    y='count',
                    color='unitType',
                    title=f"{player_name} - Selected Unit Types Repartition Over Time",
                    labels={'count': 'Number of Units', 'unitType': 'Unit Type'}
                )
                st.plotly_chart(fig_repartition_selected, use_container_width=True)
            else:
                st.info("No data available for the selected unit types and player in the chosen turn range.")


            # View 3: Most popular unit types
            st.subheader("🏆 Most Popular Unit Types")
            available_turns = sorted(df_units_filtered['turn'].unique())
            analysis_turn = st.select_slider(
                "Select turn for unit analysis",
                options=available_turns,
                value=available_turns[-1] if available_turns else turn_range[1]
            )
            turn_units = df_units_filtered[df_units_filtered['turn'] == analysis_turn]
            turn_units = turn_units[~turn_units['unitAIType'].isin(civil_ai_types)]
            if not turn_units.empty:
                col1, col2 = st.columns(2)
                with col1:
                    for player in selected_players:
                        player_turn_units = turn_units[turn_units['playerName'] == player]
                        if not player_turn_units.empty:
                            top_units = player_turn_units.nlargest(5, 'count')[['unitType', 'unitAIType', 'count']]
                            st.markdown(f"**{player} - Top Units at Turn {analysis_turn}:**")
                            st.dataframe(
                                top_units,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    'unitType': 'Unit Type',
                                    'unitAIType': 'AI Type',
                                    'count': st.column_config.NumberColumn('Count', format='%d')
                                }
                            )
                with col2:
                    unit_distribution = turn_units.groupby('unitType')['count'].sum().sort_values(ascending=False).head(10)
                    fig_pie = px.pie(
                        values=unit_distribution.values,
                        names=unit_distribution.index,
                        title=f"Unit Distribution at Turn {analysis_turn}"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)


            # Military Repartition by Unit Type (sorted by count descending)
            st.subheader("⚔️ Military Repartition by Unit Type")
            unit_type_count = (
                turn_units.groupby('unitType')['count'].sum()
                .sort_values(ascending=False)
                .head(50)
            )
            unit_type_df = unit_type_count.reset_index()
            unit_type_df.columns = ["Unit Type", "Count"]
            fig_type = px.bar(
                unit_type_df,
                x="Unit Type",
                y="Count",
                title=f"Military Repartition by Unit Type at Turn {analysis_turn}",
                category_orders={"Unit Type": unit_type_df["Unit Type"].tolist()}
            )
            st.plotly_chart(fig_type, use_container_width=True)

            # Military Repartition by AI Type (colored by Unit Type)
            st.subheader("🤖 Military Repartition by AI Type (colored by Unit Type)")
            ai_type_unit_count = (
                turn_units.groupby(['unitAIType', 'unitType'])['count'].sum().reset_index()
            )
            # Trier les AI types par total décroissant
            ai_type_order = (
                ai_type_unit_count.groupby('unitAIType')['count'].sum()
                .sort_values(ascending=False)
                .index.tolist()
            )
            fig_ai_unit = px.bar(
                ai_type_unit_count,
                x="unitAIType",
                y="count",
                color="unitType",
                title=f"Military Repartition by AI Type at Turn {analysis_turn}",
                category_orders={"unitAIType": ai_type_order}
            )
            st.plotly_chart(fig_ai_unit, use_container_width=True)

            st.subheader("🛠️ Civil Units Repartition by AI Type (colored by Unit Type)")
            # Get civil units directly from all_units, reapplying filters for turn and player
            df_all_units = pd.DataFrame(all_units)
            civil_turn_units = df_all_units[
                (df_all_units['playerId'] == player_id) &
                (df_all_units['turn'] == analysis_turn) &
                (df_all_units['unitAIType'].isin(civil_ai_types))
            ]
            if not civil_turn_units.empty:
                civil_ai_type_unit_count = (
                    civil_turn_units.groupby(['unitAIType', 'unitType'])['count'].sum().reset_index()
                )
                # Sort AI types by total count (descending)
                civil_ai_type_order = (
                    civil_ai_type_unit_count.groupby('unitAIType')['count'].sum()
                    .sort_values(ascending=False)
                    .index.tolist()
                )
                fig_civil_ai_unit = px.bar(
                    civil_ai_type_unit_count,
                    x="unitAIType",
                    y="count",
                    color="unitType",
                    title=f"Civil Units Repartition by AI Type at Turn {analysis_turn}",
                    category_orders={"unitAIType": civil_ai_type_order}
                )
                st.plotly_chart(fig_civil_ai_unit, use_container_width=True)
            else:
                st.info("No civil unit data available for this turn.")

        else:
            st.warning(f"No unit data available for the selected players in turn range {turn_range[0]}-{turn_range[1]}")
    else:
        st.warning("No unit inventory data available.")

def display_military_units(df_player_stats, selected_players, turn_range):
    """
    Affiche l'évolution du nombre d'unités militaires pour les joueurs sélectionnés.
    Args:
        df_player_stats (pd.DataFrame): Statistiques des joueurs.
        selected_players (list): Joueurs à afficher.
        turn_range (tuple): (début, fin) du range de tours.
    """
    title("⚔️ Military Units Evolution")
    subheader("Units per Player Over Turns")

    if 'playerName' not in df_player_stats.columns:
        st.info("No player data available for military units analysis.")
        return

    df_filtered = df_player_stats[
        (df_player_stats['playerName'].isin(selected_players)) &
        (df_player_stats['turn'] >= turn_range[0]) &
        (df_player_stats['turn'] <= turn_range[1])
    ]

    if df_filtered.empty or "numUnits" not in df_filtered.columns:
        st.warning("No military units data available for the selected players and turns.")
        return

    fig = px.line(df_filtered, x="turn", y="numUnits", color="playerName",
                  title="Number of Military Units Over Turns", markers=True)
    plotly_chart(fig, use_container_width=True)



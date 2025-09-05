import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import plotly.graph_objects as go
from graph_config import GRAPH_CONFIG
from graph_config import UNITAI_COLORS


def display_city_analysis(cities_data, turn_range, selected_playerId=None):
    """
    Display analysis for cities belonging to the selected player.
    Args:
        cities_data (list or pd.DataFrame): List of city data dictionaries or DataFrame.
        turn_range (tuple): (start_turn, end_turn)
        selected_playerId (int, optional): ID of the selected player.
    """
    # DataFrame to list of dicts if needed
    if isinstance(cities_data, pd.DataFrame):
        if cities_data.empty:
            st.info("No city data available.")
            return
        cities_data = cities_data.to_dict(orient="records")
    elif not cities_data:
        st.info("No city data available.")
        return

    # Filter by player if needed
    if selected_playerId is not None:
        cities_data = [city for city in cities_data if city.get("ownerId") == selected_playerId]

    filtered_cities = [
        city for city in cities_data
        if isinstance(city, dict)
    ]

    if not filtered_cities:
        st.info("No cities found for the selected player.")
        return

    # --- Expander for checkboxes ---
    with st.expander("Show/Hide Graph Options", expanded=False):
        show_city_overview = st.checkbox(
            "Show cities overview",
            value=GRAPH_CONFIG["cities"]["show_city_overview"]
        )
        show_city_history = st.checkbox(
            "Show city history",
            value=GRAPH_CONFIG["cities"]["show_city_history"]
        )
        show_city_production = st.checkbox(
            "Show city production",
            value=GRAPH_CONFIG["cities"]["show_city_production"]
        )
        show_city_orders = st.checkbox(
            "Show AI orders",
            value=GRAPH_CONFIG["cities"]["show_city_orders"]
        )

    # City selection
    city_names = [city["name"] for city in filtered_cities]
    city_names_with_all = ["All"] + city_names
    selected_city = st.selectbox("Select a city", city_names_with_all)

    # Conditional display
    if show_city_overview:
        display_city_overview(filtered_cities, None if selected_city == "All" else selected_city)
    if show_city_history:
        display_city_history(filtered_cities, turn_range, None if selected_city == "All" else selected_city)
    if show_city_production:
        display_city_production(filtered_cities, turn_range, selected_city)
    if show_city_orders and selected_city != "All":
        display_city_orders(filtered_cities, turn_range, selected_city)


def display_city_overview(cities_data, selected_city):
    if selected_city is None:
        # Display overview for all cities
        overview_df = pd.DataFrame([{
            "City": city["name"],
            "Owner": city["ownerName"],
            "Population": city["population"],
            "Threat Level": city["threatLevel"],
            "Workers Have": city["workersHave"],
            "Workers Needed": city["workersNeeded"],
            "X": city["x"],
            "Y": city["y"],
            "Founded Turn": city["foundedTurn"]
        } for city in cities_data])
        st.subheader("Cities Overview")
        st.dataframe(overview_df)
    else:
        city_info = next((c for c in cities_data if c["name"] == selected_city), None)
        if city_info:
            overview_df = pd.DataFrame([{
                "City": city_info["name"],
                "Owner": city_info["ownerName"],
                "Population": city_info["population"],
                "Threat Level": city_info["threatLevel"],
                "Workers Have": city_info["workersHave"],
                "Workers Needed": city_info["workersNeeded"],
                "X": city_info["x"],
                "Y": city_info["y"],
                "Founded Turn": city_info["foundedTurn"]
            }])
            st.subheader("City Overview")
            st.dataframe(overview_df)


def display_city_history(cities_data, turn_range, selected_city):
    if selected_city is None:
        # Concaténer tous les historiques
        all_histories = []
        for city in cities_data:
            if city.get("history"):
                df = pd.DataFrame(city["history"])
                df = df[(df["turn"] >= turn_range[0]) & (df["turn"] <= turn_range[1])]
                all_histories.append(df)
        if not all_histories:
            st.info("Aucune donnée d'historique disponible.")
            return
        history_df = pd.concat(all_histories)
        numeric_cols = history_df.select_dtypes(include=np.number).columns
        grouped = history_df.groupby("turn")[numeric_cols].agg(['mean', 'std'])
        st.subheader("Toutes les villes - Moyenne et Écart-type des métriques")

        # --- Food, Happiness, Health ---
        metrics_food_colors = {
            "foodSurplus": "green",
            "foodTradeYield": "olive",
            "netHappiness": "magenta",
            "netHealth": "teal"
        }
        fig_food = go.Figure()
        for metric, color in metrics_food_colors.items():
            if metric in grouped.columns.get_level_values(0):
                # Moyenne (axe gauche)
                fig_food.add_trace(go.Scatter(
                    x=grouped.index,
                    y=grouped[(metric, 'mean')],
                    name=f"{metric} (moyenne)",
                    line=dict(color=color)
                ))
                # Écart-type (axe droite)
                fig_food.add_trace(go.Scatter(
                    x=grouped.index,
                    y=grouped[(metric, 'std')],
                    name=f"{metric} (écart-type)",
                    line=dict(color=color, dash='dot'),
                    yaxis="y2"
                ))
        fig_food.update_layout(
            title="Food, Happiness & Health Metrics (Moyenne & Écart-type)",
            xaxis_title="Turn",
            yaxis=dict(
                title="Moyenne",
                side="left"
            ),
            yaxis2=dict(
                title="Écart-type",
                overlaying="y",
                side="right"
            ),
            legend=dict(x=0, y=1)
        )
        st.plotly_chart(fig_food, use_container_width=True)

        # --- Production, Science, Culture, Income, Education ---
        metrics_colors = {
            "production": "blue",
            "science": "cyan",
            "culture": "purple",
            "income": "orange",
            "education": "purple"
        }
        fig_metrics = go.Figure()
        for metric, color in metrics_colors.items():
            if metric in grouped.columns.get_level_values(0):
                fig_metrics.add_trace(go.Scatter(
                    x=grouped.index,
                    y=grouped[(metric, 'mean')],
                    name=f"{metric} (moyenne)",
                    line=dict(color=color)
                ))
                fig_metrics.add_trace(go.Scatter(
                    x=grouped.index,
                    y=grouped[(metric, 'std')],
                    name=f"{metric} (écart-type)",
                    line=dict(color=color, dash='dot'),
                    yaxis="y2"
                ))
        fig_metrics.update_layout(
            title="Production, Science, Culture, Income, Education (Moyenne & Écart-type)",
            xaxis_title="Turn",
            yaxis=dict(
                title="Moyenne",
                side="left"
            ),
            yaxis2=dict(
                title="Écart-type",
                overlaying="y",
                side="right"
            ),
            legend=dict(x=0, y=1)
        )
        st.plotly_chart(fig_metrics, use_container_width=True)

        # --- Social & Environmental Metrics ---
        metrics2_colors = {
            "criminalite": "black",
            "maladie": "darkgreen",
            "pollutionEau": "blue",
            "pollutionAir": "cyan",
            "risqueIncendie": "red",
            "tourisme": "orange"
        }
        fig2 = go.Figure()
        for metric, color in metrics2_colors.items():
            if metric in grouped.columns.get_level_values(0):
                fig2.add_trace(go.Scatter(
                    x=grouped.index,
                    y=grouped[(metric, 'mean')],
                    name=f"{metric} (moyenne)",
                    line=dict(color=color)
                ))
                fig2.add_trace(go.Scatter(
                    x=grouped.index,
                    y=grouped[(metric, 'std')],
                    name=f"{metric} (écart-type)",
                    line=dict(color=color, dash='dot'),
                    yaxis="y2"
                ))
        fig2.update_layout(
            title="City Social & Environmental Metrics (Moyenne & Écart-type)",
            xaxis_title="Turn",
            yaxis=dict(
                title="Moyenne",
                side="left"
            ),
            yaxis2=dict(
                title="Écart-type",
                overlaying="y",
                side="right"
            ),
            legend=dict(x=0, y=1)
        )
        st.plotly_chart(fig2, use_container_width=True)

        # --- S&E Metrics Change ---
        metrics_change_colors = {
            "criminaliteChange": "black",
            "maladieChange": "darkgreen",
            "pollutionEauChange": "blue",
            "pollutionAirChange": "cyan",
            "educationChange": "purple",
            "risqueIncendieChange": "red",
            "tourismeChange": "orange"
        }
        fig_change = go.Figure()
        for metric, color in metrics_change_colors.items():
            if metric in grouped.columns.get_level_values(0):
                fig_change.add_trace(go.Scatter(
                    x=grouped.index,
                    y=grouped[(metric, 'mean')],
                    name=f"{metric} (moyenne)",
                    line=dict(color=color)
                ))
                fig_change.add_trace(go.Scatter(
                    x=grouped.index,
                    y=grouped[(metric, 'std')],
                    name=f"{metric} (écart-type)",
                    line=dict(color=color, dash='dot'),
                    yaxis="y2"
                ))
        fig_change.update_layout(
            title="S&E Metrics Change (Moyenne & Écart-type)",
            xaxis_title="Turn",
            yaxis=dict(
                title="Moyenne",
                side="left"
            ),
            yaxis2=dict(
                title="Écart-type",
                overlaying="y",
                side="right"
            ),
            legend=dict(x=0, y=1)
        )
        st.plotly_chart(fig_change, use_container_width=True)
        return

    city_info = next((c for c in cities_data if c["name"] == selected_city), None)
    if city_info and city_info.get("history"):
        history_df = pd.DataFrame(city_info["history"])
        history_df = history_df[
            (history_df["turn"] >= turn_range[0]) &
            (history_df["turn"] <= turn_range[1])
        ]
        history_df = history_df.sort_values("turn")  # <-- Ajout du tri par tour
        st.subheader(f"{selected_city} - History Metrics")

        fig = go.Figure()

        # Population (secondary axis)
        fig.add_trace(go.Scatter(
            x=history_df["turn"],
            y=history_df["population"],
            name="Population",
            yaxis="y2",
            line=dict(color="red")
        ))

        # Other metrics (primary axis) - FoodSurplus retiré, Education ajouté
        metrics_colors = {
            "production": "blue",
            "science": "cyan",
            "culture": "purple",
            "income": "orange",
            "education": "purple"  # Ajouté ici
        }
        for metric, color in metrics_colors.items():
            if metric in history_df.columns:
                fig.add_trace(go.Scatter(
                    x=history_df["turn"],
                    y=history_df[metric],
                    name=metric.capitalize(),
                    line=dict(color=color)
                ))

        fig.update_layout(
            title="City History Metrics",
            xaxis_title="Turn",
            yaxis=dict(
                title="Production / Science / Culture / Income / Education",
                side="left"
            ),
            yaxis2=dict(
                title="Population",
                overlaying="y",
                side="right"
            ),
            legend=dict(x=0, y=1)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Nouveau graphique : FoodSurplus, foodTradeYield, netHappiness, netHealth
        metrics_food_colors = {
            "foodSurplus": "green",
            "foodTradeYield": "olive",
            "netHappiness": "magenta",
            "netHealth": "teal"
        }
        fig_food = go.Figure()
        for metric, color in metrics_food_colors.items():
            if metric in history_df.columns:
                fig_food.add_trace(go.Scatter(
                    x=history_df["turn"],
                    y=history_df[metric],
                    name=metric,
                    line=dict(color=color)
                ))
        fig_food.update_layout(
            title="Food, Happiness & Health Metrics",
            xaxis_title="Turn",
            yaxis_title="Value",
            legend=dict(x=0, y=1)
        )
        st.plotly_chart(fig_food, use_container_width=True)

        # Second graph: city negative/positive metrics (sans education)
        metrics2_colors = {
            "criminalite": "black",
            "maladie": "darkgreen",
            "pollutionEau": "blue",
            "pollutionAir": "cyan",
            "risqueIncendie": "red",
            "tourisme": "orange"
        }
        fig2 = go.Figure()
        for metric, color in metrics2_colors.items():
            if metric in history_df.columns:
                fig2.add_trace(go.Scatter(
                    x=history_df["turn"],
                    y=history_df[metric],
                    name=metric.capitalize(),
                    line=dict(color=color)
                ))
        fig2.update_layout(
            title="City Social & Environmental Metrics",
            xaxis_title="Turn",
            yaxis_title="Value",
            legend=dict(x=0, y=1)
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Nouveau graphique : changements S&E
        metrics_change_colors = {
            "criminaliteChange": "black",
            "maladieChange": "darkgreen",
            "pollutionEauChange": "blue",
            "pollutionAirChange": "cyan",
            "educationChange": "purple",
            "risqueIncendieChange": "red",
            "tourismeChange": "orange"
        }
        fig_change = go.Figure()
        for metric, color in metrics_change_colors.items():
            if metric in history_df.columns:
                fig_change.add_trace(go.Scatter(
                    x=history_df["turn"],
                    y=history_df[metric],
                    name=metric,
                    line=dict(color=color)
                ))
        fig_change.update_layout(
            title="S&E Metrics Change",
            xaxis_title="Turn",
            yaxis_title="Change Value",
            legend=dict(x=0, y=1)
        )
        st.plotly_chart(fig_change, use_container_width=True)


def display_city_production(cities_data, turn_range, selected_city):

    if selected_city == "All":
        # Agréger la production de toutes les villes
        all_prod = []
        for city in cities_data:
            if city.get("produced"):
                all_prod.extend(city["produced"])
        prod_df = pd.DataFrame(all_prod)
        prod_df = prod_df[
            (prod_df["turn"] >= turn_range[0]) &
            (prod_df["turn"] <= turn_range[1])
        ]
        st.subheader("All Cities - Production History")
    else:
        city_info = next((c for c in cities_data if c["name"] == selected_city), None)
        if city_info and city_info.get("produced"):
            prod_df = pd.DataFrame(city_info["produced"])
            prod_df = prod_df[
                (prod_df["turn"] >= turn_range[0]) &
                (prod_df["turn"] <= turn_range[1])
            ]
            st.subheader(f"{selected_city} - Production History")
        else:
            st.info("No production data for this city.")
            return
    # UNITAI type count
    if not prod_df.empty:
        # Extract UNITAI type from productName
        def extract_unitai(text):
            if isinstance(text, str) and "UNITAI" in text and "for type " in text:
                after = text.split("for type ", 1)[-1]
                # Optionally, remove trailing info (e.g. parentheses, commas)
                return after.split()[0]
            return None

        prod_df["UNITAI_Type"] = prod_df["productName"].apply(extract_unitai)
        unitai_count = prod_df["UNITAI_Type"].value_counts()
        unitai_count_df = unitai_count.reset_index()
        unitai_count_df.columns = ["UNITAI Type", "Count"]
        unitai_count_df = unitai_count_df[unitai_count_df["UNITAI Type"].notnull()]

        if not unitai_count_df.empty:
            fig_unitai = px.bar(
                unitai_count_df,
                x="UNITAI Type",
                y="Count",
                title="Production Count by UNITAI Type",
                category_orders={"UNITAI Type": unitai_count_df["UNITAI Type"].tolist()},
                color="UNITAI Type",
                color_discrete_map=UNITAI_COLORS
            )
            st.plotly_chart(fig_unitai, use_container_width=True)
        else:
            st.info("No UNITAI type found in production data.")

    if not prod_df.empty:
        # Map each product to its UNITAI type
        prod_df["UNITAI_Type"] = prod_df["productName"].apply(extract_unitai)
        prod_count = prod_df["productName"].value_counts().head(50)
        prod_count_df = prod_count.reset_index()
        prod_count_df.columns = ["Product", "Count"]
        prod_count_df = prod_count_df.sort_values("Count", ascending=False)
        # Merge UNITAI type for each product
        prod_unitai_map = prod_df.drop_duplicates(subset=["productName"])[["productName", "UNITAI_Type"]]
        prod_count_df = prod_count_df.merge(prod_unitai_map, left_on="Product", right_on="productName", how="left")
        # Replace missing UNITAI types by "UNKNOWN"
        prod_count_df["UNITAI_Type"] = prod_count_df["UNITAI_Type"].fillna("UNKNOWN")
        fig = px.bar(
            prod_count_df,
            x="Product",
            y="Count",
            color="UNITAI_Type",
            title="Production Count (Top 50)",
            category_orders={"Product": prod_count_df["Product"].tolist()},
            color_discrete_map=UNITAI_COLORS
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No production data available for the selected city/cities.")






def display_city_orders(cities_data, turn_range, selected_city):
    city_info = next((c for c in cities_data if c["name"] == selected_city), None)
    if city_info and city_info.get("ordersToCentral"):
        orders_df = pd.DataFrame(city_info["ordersToCentral"])
        orders_df = orders_df[
            (orders_df["turn"] >= turn_range[0]) &
            (orders_df["turn"] <= turn_range[1])
        ]
        st.subheader(f"{selected_city} - AI Orders to Central")
        st.dataframe(orders_df)
        st.bar_chart(orders_df["aiType"].value_counts())

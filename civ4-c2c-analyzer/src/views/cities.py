import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import plotly.graph_objects as go


def display_city_analysis(cities_data, turn_range, selected_player_id=None):
    """
    Display analysis for cities belonging to the selected player.
    Args:
        cities_data (list or pd.DataFrame): List of city data dictionaries or DataFrame.
        turn_range (tuple): (start_turn, end_turn)
        selected_player_id (int, optional): ID of the selected player.
    """
    # Conversion DataFrame -> liste de dicts si besoin
    if isinstance(cities_data, pd.DataFrame):
        if cities_data.empty:
            st.info("No city data available.")
            return
        cities_data = cities_data.to_dict(orient="records")
    elif not cities_data:
        st.info("No city data available.")
        return

    # Filtrer par joueur si demandé
    if selected_player_id is not None:
        cities_data = [city for city in cities_data if city.get("ownerId") == selected_player_id]

    # Ne pas filtrer par foundedTurn, garder toutes les villes du joueur
    filtered_cities = [
        city for city in cities_data
        if isinstance(city, dict)
    ]

    if not filtered_cities:
        st.info("No cities found for the selected player.")
        return

    # Passe la ville sélectionnée à chaque vue
    display_city_overview(filtered_cities, None)

    # Sélection unique de la ville, avec option "All"
    city_names = [city["name"] for city in filtered_cities]
    city_names_with_all = ["All"] + city_names
    selected_city = st.selectbox("Select a city", city_names_with_all)

    if selected_city == "All":
        # Vue production pour toutes les villes (somme)
        display_city_history(filtered_cities, turn_range, None)
        display_city_production(filtered_cities, turn_range, "All")
        display_city_orders(filtered_cities, turn_range, None)
    else:
    display_city_history(filtered_cities, turn_range, selected_city)
    display_city_production(filtered_cities, turn_range, selected_city)
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

        # Other metrics (primary axis)
        metrics_colors = {
            "production": "blue",
            "science": "cyan",
            "culture": "purple",
            "income": "orange",
            "foodSurplus": "green"
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
                title="Production / Science / Culture / Income / Food Surplus",
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

        # Second graph: city negative/positive metrics
        metrics2_colors = {
            "criminalite": "black",
            "maladie": "darkgreen",
            "pollutionEau": "blue",
            "pollutionAir": "cyan",
            "education": "purple",
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

    if not prod_df.empty:
        prod_count = prod_df["productName"].value_counts().head(50)
        prod_count_df = prod_count.reset_index()
        prod_count_df.columns = ["Product", "Count"]
        prod_count_df = prod_count_df.sort_values("Count", ascending=False)
        fig = px.bar(prod_count_df, x="Product", y="Count", title="Production Count (Top 50)", 
                     category_orders={"Product": prod_count_df["Product"].tolist()})
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

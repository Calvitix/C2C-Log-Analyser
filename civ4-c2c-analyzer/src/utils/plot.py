import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

def create_overview_plots(df_player_stats, selected_players, turn_range):
    df_filtered = df_player_stats[
        (df_player_stats['playerName'].isin(selected_players)) &
        (df_player_stats['turn'] >= turn_range[0]) &
        (df_player_stats['turn'] <= turn_range[1])
    ]
    
    if df_filtered.empty:
        return None

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Population Growth', 'Military Power', 
                        'Number of Cities', 'Technology Progress'),
        vertical_spacing=0.1
    )

    for player in selected_players:
        player_data = df_filtered[df_filtered['playerName'] == player]

        fig.add_trace(
            go.Scatter(x=player_data['turn'], y=player_data['population'],
                       name=player, mode='lines+markers', showlegend=True),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(x=player_data['turn'], y=player_data['power'],
                       name=player, mode='lines+markers', showlegend=False),
            row=1, col=2
        )

        fig.add_trace(
            go.Scatter(x=player_data['turn'], y=player_data['cities'],
                       name=player, mode='lines+markers', showlegend=False),
            row=2, col=1
        )

        fig.add_trace(
            go.Scatter(x=player_data['turn'], y=player_data['techPercent'],
                       name=player, mode='lines+markers', showlegend=False),
            row=2, col=2
        )

    fig.update_layout(height=600, title_text="Civilization Progress Overview")
    return fig

def create_player_comparison_radar(turn_data, selected_players):
    categories = ['population', 'cities', 'power', 'techPercent', 
                  'totalScienceOutput', 'totalProductionOutput']

    fig_radar = go.Figure()

    for player in selected_players:
        player_data = turn_data[turn_data['playerName'] == player]
        if not player_data.empty:
            values = player_data[categories].values.flatten().tolist()
            values += values[:1]  # Repeat the first value to close the circle
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=player
            ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Civilization Comparison"
    )
    return fig_radar

def create_heatmap(data):
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=data.values,
        x=data.columns,
        y=data.index,
        colorscale='Viridis'
    ))
    fig_heatmap.update_layout(title="Heatmap of Player Metrics")
    return fig_heatmap

def create_metric_chart(df, metric, selected_players, turn_range, chart_type="line"):
    """
    Génère un graphique pour une métrique donnée sur la période sélectionnée.
    Args:
        df (pd.DataFrame): DataFrame des statistiques joueurs.
        metric (str): Nom de la colonne à afficher.
        selected_players (list): Liste des joueurs à afficher.
        turn_range (tuple): (début, fin) du range de tours.
        chart_type (str): "line" ou "bar".
    Returns:
        fig (plotly.graph_objs.Figure): Figure Plotly.
    """
    df_filtered = df[
        (df['playerName'].isin(selected_players)) &
        (df['turn'] >= turn_range[0]) &
        (df['turn'] <= turn_range[1])
    ]
    if df_filtered.empty:
        return None

    if chart_type == "line":
        fig = px.line(df_filtered, x="turn", y=metric, color="playerName", markers=True,
                      title=f"{metric} over Turns")
    elif chart_type == "bar":
        fig = px.bar(df_filtered, x="turn", y=metric, color="playerName",
                     title=f"{metric} over Turns")
    else:
        raise ValueError("chart_type must be 'line' or 'bar'")

    fig.update_layout(height=400)
    return fig


def create_player_history_chart(df_player_stats, player_name, metrics=None):
    """
    Affiche l'évolution des métriques d'un joueur au fil des tours.
    Args:
        df_player_stats (pd.DataFrame): DataFrame des statistiques joueurs.
        player_name (str): Nom du joueur à afficher.
        metrics (list): Liste des métriques à afficher (ex: ['score', 'population', ...]).
    Returns:
        fig (plotly.graph_objs.Figure): Figure Plotly.
    """
    if metrics is None:
        metrics = ['score', 'population', 'power', 'cities', 'techPercent']

    player_data = df_player_stats[df_player_stats['playerName'] == player_name]
    if player_data.empty:
        return None

    fig = go.Figure()
    for metric in metrics:
        if metric in player_data.columns:
            fig.add_trace(go.Scatter(
                x=player_data['turn'],
                y=player_data[metric],
                mode='lines+markers',
                name=metric
            ))

    fig.update_layout(
        title=f"History for {player_name}",
        xaxis_title="Turn",
        yaxis_title="Metric Value",
        height=400
    )
    return fig

def create_economic_analysis_chart(df_player_stats, selected_players, turn_range):
    """
    Affiche l'évolution de la science et de la production pour les joueurs sélectionnés.
    Args:
        df_player_stats (pd.DataFrame): DataFrame des statistiques joueurs.
        selected_players (list): Liste des joueurs à afficher.
        turn_range (tuple): (début, fin) du range de tours.
    Returns:
        fig (plotly.graph_objs.Figure): Figure Plotly.
    """
    df_filtered = df_player_stats[
        (df_player_stats['playerName'].isin(selected_players)) &
        (df_player_stats['turn'] >= turn_range[0]) &
        (df_player_stats['turn'] <= turn_range[1])
    ]
    if df_filtered.empty:
        return None

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Science Output', 'Production Output'),
        horizontal_spacing=0.15
    )

    for player in selected_players:
        player_data = df_filtered[df_filtered['playerName'] == player]
        fig.add_trace(
            go.Scatter(x=player_data['turn'], y=player_data['totalScienceOutput'],
                       name=player, mode='lines+markers', showlegend=True),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=player_data['turn'], y=player_data['totalProductionOutput'],
                       name=player, mode='lines+markers', showlegend=False),
            row=1, col=2
        )

    fig.update_layout(height=400, title_text="Economic Analysis")
    return fig

def create_radar_chart(df, selected_players, metrics=None, turn=None):
    """
    Crée un radar chart pour comparer les joueurs sur plusieurs métriques à un tour donné.
    Args:
        df (pd.DataFrame): DataFrame des statistiques joueurs.
        selected_players (list): Liste des joueurs à afficher.
        metrics (list): Liste des métriques à comparer.
        turn (int): Tour à afficher (dernier tour si None).
    Returns:
        fig (plotly.graph_objs.Figure): Figure Plotly.
    """
    if metrics is None:
        metrics = ['score', 'population', 'power', 'cities', 'techPercent',
                   'totalScienceOutput', 'totalProductionOutput']

    if turn is None:
        turn = df['turn'].max()

    fig = go.Figure()
    for player in selected_players:
        player_col = 'playerName' if 'playerName' in df.columns else 'name'
        player_data = df[(df[player_col] == player) & (df['turn'] == turn)]
        if not player_data.empty:
            values = [player_data[metric].values[0] if metric in player_data.columns else 0 for metric in metrics]
            values += values[:1]  # Boucle pour fermer le radar
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metrics + [metrics[0]],
                fill='toself',
                name=player
            ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True,
        title=f"Radar Chart - Turn {turn}",
        height=400
    )
    return fig


def create_comparison_table(df, selected_players, metrics=None, turn=None):
    """
    Crée un tableau de comparaison des joueurs pour les métriques spécifiées à un tour donné.
    Args:
        df (pd.DataFrame): DataFrame des statistiques joueurs.
        selected_players (list): Liste des joueurs à afficher.
        metrics (list): Liste des métriques à comparer.
        turn (int): Tour à afficher (dernier tour si None).
    Returns:
        pd.DataFrame: Tableau de comparaison.
    """
    if metrics is None:
        metrics = ['score', 'population', 'power', 'cities', 'techPercent',
                   'totalScienceOutput', 'totalProductionOutput']

    if turn is None:
        turn = df['turn'].max()

    table_data = []
    for player in selected_players:
        player_data = df[(df['playerName'] == player) & (df['turn'] == turn)]
        if not player_data.empty:
            row = {'playerName': player}
            for metric in metrics:
                row[metric] = player_data[metric].values[0] if metric in player_data.columns else None
            table_data.append(row)

    return pd.DataFrame(table_data)


def create_ranking_chart(df, metric="score", turn=None, top_n=10):
    """
    Crée un graphique de classement des joueurs selon une métrique à un tour donné.
    Args:
        df (pd.DataFrame): DataFrame des statistiques joueurs.
        metric (str): Nom de la métrique à classer.
        turn (int): Tour à afficher (dernier tour si None).
        top_n (int): Nombre de joueurs à afficher.
    Returns:
        fig (plotly.graph_objs.Figure): Figure Plotly.
    """
    if turn is None:
        turn = df['turn'].max()

    df_turn = df[df['turn'] == turn]
    if df_turn.empty or metric not in df_turn.columns:
        return None

    df_sorted = df_turn.sort_values(by=metric, ascending=False).head(top_n)
    fig = px.bar(df_sorted, x="playerName", y=metric, color="playerName",
                 title=f"Top {top_n} Players by {metric} (Turn {turn})")
    fig.update_layout(height=400, xaxis_title="Player", yaxis_title=metric)
    return fig


def create_player_history_chart(player_history, selected_metric):
    # Exemple simple pour une courbe
    if selected_metric == 'Population':
        y = player_history['population'] if 'population' in player_history.columns else []
        fig = go.Figure(data=go.Scatter(x=player_history['turn'], y=y, mode='lines+markers'))
        fig.update_layout(title="Population Over Time", xaxis_title="Turn", yaxis_title="Population")
        return fig
    # Ajoute d'autres métriques ici...
    # Si aucune métrique valide, retourne une figure vide
    return go.Figure()
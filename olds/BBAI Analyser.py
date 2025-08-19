"""
Civ4 C2C Dashboard - Enhanced Version with Directory Selection
Visualizes parsed game data from JSON files
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import os

# Configuration de la page
st.set_page_config(
    page_title="Civ4 C2C Game Analyzer",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS pour améliorer l'apparence
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
    }
    .plot-container {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.title("🎮 Civilization IV C2C Game Analyzer")
st.markdown("---")

# Configuration du répertoire des données
DEFAULT_DATA_PATH = os.path.join("Data", "Output", "json")

# Sidebar pour la configuration
st.sidebar.title("⚙️ Configuration")

# Sélection du répertoire
data_directory = st.sidebar.text_input(
    "Data Directory Path",
    value=DEFAULT_DATA_PATH,
    help="Path to the directory containing the JSON files"
)

# Vérifier si le répertoire existe
if not os.path.exists(data_directory):
    st.sidebar.error(f"❌ Directory not found: {data_directory}")
    st.sidebar.info("Please ensure the directory exists and contains the JSON files")
    
    # Créer le répertoire si demandé
    if st.sidebar.button("Create Directory"):
        try:
            os.makedirs(data_directory, exist_ok=True)
            st.sidebar.success(f"✅ Directory created: {data_directory}")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error creating directory: {e}")
else:
    st.sidebar.success(f"✅ Directory found: {data_directory}")
    
    # Lister les fichiers JSON disponibles
    json_files = [f for f in os.listdir(data_directory) if f.endswith('.json')]
    if json_files:
        st.sidebar.info(f"Found {len(json_files)} JSON files")
        with st.sidebar.expander("📁 Available Files"):
            for file in json_files:
                st.write(f"• {file}")
    else:
        st.sidebar.warning("No JSON files found in the directory")

# Fonction de chargement des données
@st.cache_data
def load_game_data(directory_path):
    """Load all game data from JSON files in the specified directory"""
    try:
        # Chemins des fichiers
        players_file = os.path.join(directory_path, "game_data_summary.json")
        cities_file = os.path.join(directory_path, "cities.json")
        timings_file = os.path.join(directory_path, "player_turn_timings.json")
        
        # Vérifier l'existence des fichiers
        missing_files = []
        if not os.path.exists(players_file):
            missing_files.append("game_data_summary.json")
        if not os.path.exists(cities_file):
            missing_files.append("cities.json")
        if not os.path.exists(timings_file):
            missing_files.append("player_turn_timings.json")
        
        if missing_files:
            st.error(f"Missing required files in {directory_path}:")
            for file in missing_files:
                st.error(f"  • {file}")
            return None, None, None
        
        # Chargement des données avec utf-8-sig pour gérer le BOM
        with open(players_file, 'r', encoding='utf-8-sig') as f:
            players_data = json.load(f)
        
        with open(cities_file, 'r', encoding='utf-8-sig') as f:
            cities_data = json.load(f)
            
        with open(timings_file, 'r', encoding='utf-8-sig') as f:
            timings_data = json.load(f)
            
        return players_data, cities_data, timings_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

# Bouton pour recharger les données
if st.sidebar.button("🔄 Reload Data"):
    st.cache_data.clear()
    st.rerun()

# Chargement des données seulement si le répertoire existe
if os.path.exists(data_directory):
    players_data, cities_data, timings_data = load_game_data(data_directory)
else:
    players_data, cities_data, timings_data = None, None, None

if not players_data or not cities_data:
    st.error("Unable to load game data. Please check that the JSON files are present in the specified directory.")
    
    # Afficher les instructions
    st.markdown("""
    ### 📋 Required Files
    
    The following JSON files must be present in the data directory:
    
    1. **game_data_summary.json** - Player statistics and history
    2. **cities.json** - City information and history
    3. **player_turn_timings.json** - Turn timing data
    
    ### 📁 Directory Structure
    
    ```
    Data/
    └── Output/
        └── json/
            ├── game_data_summary.json
            ├── cities.json
            └── player_turn_timings.json
    ```
    
    ### 🔧 How to specify a different directory
    
    1. Enter the full path in the "Data Directory Path" field in the sidebar
    2. Click "Reload Data" to load files from the new location
    
    Examples:
    - Windows: `C:\\Games\\Civ4\\Logs\\json`
    - Linux/Mac: `/home/user/civ4/logs/json`
    """)
    
    st.stop()

# Afficher le chemin actuel des données
st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Current Data Source")
st.sidebar.code(data_directory, language=None)

# Préparation des données
def prepare_player_stats_df(players_data):
    """Convert player stats history to DataFrame"""
    all_stats = []
    for player in players_data:
        if player['isHuman']:  # Focus sur les joueurs humains
            for stat in player['statsHistory']:
                stat['playerName'] = player['name']
                all_stats.append(stat)
    return pd.DataFrame(all_stats)

def prepare_city_history_df(cities_data):
    """Convert city history to DataFrame"""
    all_history = []
    for city in cities_data:
        for hist in city['history']:
            hist['cityName'] = city['name']
            hist['x'] = city['x']
            hist['y'] = city['y']
            hist['foundedTurn'] = city['foundedTurn']
            all_history.append(hist)
    return pd.DataFrame(all_history)

def prepare_timings_df(timings_data):
    """Convert timings to DataFrame and calculate durations"""
    df = pd.DataFrame(timings_data)
    # Calculer la durée en secondes
    df['duration'] = df.apply(lambda x: x['endTimestamp'] - x['beginTimestamp'] 
                              if x['endTimestamp'] > 0 else 0, axis=1)
    return df

# Préparation des DataFrames
df_player_stats = prepare_player_stats_df(players_data)
df_city_history = prepare_city_history_df(cities_data)
df_timings = prepare_timings_df(timings_data)

# Sidebar pour la navigation et les filtres
st.sidebar.markdown("---")
st.sidebar.title("🎯 Navigation")

# Ajouter ces nouvelles options dans le menu de navigation
view_mode = st.sidebar.radio(
    "Select View",
    ["📊 Overview", "👥 Players Analysis", "🏛️ Cities Analysis", 
     "⏱️ Turn Timings", "📈 Comparative Analysis", "🏆 Rankings",
     "🎯 Score Analysis", "⚔️ Military Units", "🧮 Unit Evaluation"]  # Nouvelles options
)

# Filtres globaux
st.sidebar.markdown("### 🔍 Filters")

# Filtre par joueur
human_players = [p for p in players_data if p['isHuman']]
selected_players = st.sidebar.multiselect(
    "Select Players",
    options=[p['name'] for p in human_players],
    default=[p['name'] for p in human_players]
)

# Filtre par tour
if not df_player_stats.empty:
    turn_range = st.sidebar.slider(
        "Turn Range",
        min_value=int(df_player_stats['turn'].min()),
        max_value=int(df_player_stats['turn'].max()),
        value=(int(df_player_stats['turn'].min()), int(df_player_stats['turn'].max()))
    )
else:
    turn_range = (0, 100)

# Informations sur les données chargées
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Info")
if not df_player_stats.empty:
    st.sidebar.info(f"""
    **Loaded Data:**
    - Players: {len(human_players)}
    - Cities: {len(cities_data)}
    - Turns: {df_player_stats['turn'].max() + 1}
    - Data points: {len(df_player_stats)}
    """)

# Vue d'ensemble
if view_mode == "📊 Overview":
    st.header("📊 Game Overview")
    
    # Afficher le chemin des données
    st.info(f"📁 Data loaded from: `{data_directory}`")
    
    # Métriques générales
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
    
    # Graphique de progression globale
    st.subheader("🌍 Global Progression")
    
    # Filtrer les données
    df_filtered = df_player_stats[
        (df_player_stats['playerName'].isin(selected_players)) &
        (df_player_stats['turn'] >= turn_range[0]) &
        (df_player_stats['turn'] <= turn_range[1])
    ]
    
    if not df_filtered.empty:
        # Créer des sous-graphiques
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

# [Le reste du code reste identique...]

# Analyse des joueurs
elif view_mode == "👥 Players Analysis":
    st.header("👥 Players Analysis")
    
    # Sélection d'un joueur spécifique
    selected_player = st.selectbox(
        "Select a player for detailed analysis",
        options=selected_players
    )
    
    # Obtenir les données du joueur
    player_info = next((p for p in players_data if p['name'] == selected_player), None)
    
    if player_info:
        # Informations actuelles
        st.subheader(f"Current Status - {selected_player}")
        
        current_stats = player_info['currentStats']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Cities", current_stats['cities'])
            st.metric("Population", current_stats['population'])
        
        with col2:
            st.metric("Military Power", current_stats['power'])
            st.metric("Tech %", current_stats['techPercent'])
        
        with col3:
            st.metric("Treasury", current_stats['treasury'])
            st.metric("Science Output", current_stats['totalScienceOutput'])
        
        with col4:
            st.metric("Total Units", current_stats['numUnits'])
            st.metric("Anarchy Turns", current_stats['totalTurnsInAnarchy'])
        
        # Graphiques détaillés
        st.subheader("📈 Detailed Evolution")
        
        player_history = pd.DataFrame(player_info['statsHistory'])
        
        # Sélection de la métrique à afficher
        metric_options = {
            'Population': 'population',
            'Cities': 'cities',
            'Military Power': 'power',
            'Technology %': 'techPercent',
            'Treasury': 'treasury',
            'Science Output': 'totalScienceOutput',
            'Food Output': 'totalFoodOutput',
            'Production Output': 'totalProductionOutput'
        }
        
        selected_metric = st.selectbox(
            "Select metric to display",
            options=list(metric_options.keys())
        )
        
        # Graphique de la métrique sélectionnée
        fig = px.line(
            player_history,
            x='turn',
            y=metric_options[selected_metric],
            title=f"{selected_metric} Evolution - {selected_player}",
            markers=True
        )
        
        fig.update_layout(
            xaxis_title="Turn",
            yaxis_title=selected_metric,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse économique
        st.subheader("💰 Economic Analysis")
        
        economic_cols = ['treasury', 'goldRate', 'maintenanceCost', 
                        'civicUpkeepCost', 'unitUpkeep']
        
        if all(col in player_history.columns for col in economic_cols):
            fig_eco = go.Figure()
            
            for col in economic_cols:
                fig_eco.add_trace(go.Scatter(
                    x=player_history['turn'],
                    y=player_history[col],
                    name=col.replace('Cost', ' Cost').title(),
                    mode='lines+markers'
                ))
            
            fig_eco.update_layout(
                title=f"Economic Overview - {selected_player}",
                xaxis_title="Turn",
                yaxis_title="Gold",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_eco, use_container_width=True)

# Analyse des villes
elif view_mode == "🏛️ Cities Analysis":
    st.header("🏛️ Cities Analysis")
    
    # Vue d'ensemble des villes
    st.subheader("🗺️ Cities Overview")
    
    # Carte des villes
    city_locations = pd.DataFrame([
        {
            'name': city['name'],
            'x': city['x'],
            'y': city['y'],
            'foundedTurn': city['foundedTurn'],
            'population': city['population']
        }
        for city in cities_data
    ])

    if not city_locations.empty:
        # Calculer les limites pour avoir une carte carrée
        x_min, x_max = city_locations['x'].min() - 5, city_locations['x'].max() + 5
        y_min, y_max = city_locations['y'].min() - 5, city_locations['y'].max() + 5
        
        # Calculer la taille maximale pour avoir un carré
        x_range = x_max - x_min
        y_range = y_max - y_min
        max_range = max(x_range, y_range)
        
        # Ajuster les limites pour avoir un carré centré
        if x_range < max_range:
            x_center = (x_min + x_max) / 2
            x_min = x_center - max_range / 2
            x_max = x_center + max_range / 2
        if y_range < max_range:
            y_center = (y_min + y_max) / 2
            y_min = y_center - max_range / 2
            y_max = y_center + max_range / 2
        
        fig_map = px.scatter(
            city_locations,
            x='x',
            y='y',
            size='population',
            hover_name='name',
            hover_data=['foundedTurn', 'population'],
            title="City Locations Map",
            size_max=20
        )
        
        # Configurer la carte pour être carrée avec une grille
        fig_map.update_layout(
            xaxis=dict(
                title="X Coordinate",
                range=[x_min, x_max],
                constrain='domain',
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                dtick=10,  # Grille tous les 10 unités
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='gray'
            ),
            yaxis=dict(
                title="Y Coordinate",
                range=[y_min, y_max],
                scaleanchor="x",  # Force le ratio 1:1 avec l'axe X
                scaleratio=1,
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                dtick=10,  # Grille tous les 10 unités
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='gray'
            ),
            height=600,
            width=600,  # Largeur fixe pour avoir un carré
            plot_bgcolor='rgba(240, 240, 240, 0.5)',  # Fond légèrement gris
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        # Ajouter les noms des villes
        for _, city in city_locations.iterrows():
            fig_map.add_annotation(
                x=city['x'],
                y=city['y'],
                text=city['name'],
                showarrow=False,
                yshift=10,
                font=dict(size=10, color='black'),
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='black',
                borderwidth=1
            )
        
        # Ajouter des lignes de grille principales tous les 50 unités
        for x in range(int(x_min // 50) * 50, int(x_max) + 50, 50):
            if x_min <= x <= x_max:
                fig_map.add_vline(x=x, line_width=2, line_dash="solid", line_color="darkgray")
        
        for y in range(int(y_min // 50) * 50, int(y_max) + 50, 50):
            if y_min <= y <= y_max:
                fig_map.add_hline(y=y, line_width=2, line_dash="solid", line_color="darkgray")
        
        # Centrer la carte dans Streamlit
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.plotly_chart(fig_map, use_container_width=False)    
            
        
    # Sélection d'une ville pour analyse détaillée
    city_names = [city['name'] for city in cities_data]
    selected_city = st.selectbox("Select a city for detailed analysis", city_names)
    
    # Obtenir les données de la ville
    city_info = next((c for c in cities_data if c['name'] == selected_city), None)
    
    if city_info:
        st.subheader(f"📊 {selected_city} - Detailed Analysis")
        
        # Informations de base
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Founded Turn", city_info['foundedTurn'])
            st.metric("Current Population", city_info['population'])
        
        with col2:
            st.metric("Location", f"({city_info['x']}, {city_info['y']})")
            st.metric("Threat Level", city_info['threatLevel'])
        
        with col3:
            st.metric("Workers Have", city_info['workersHave'])
            st.metric("Workers Needed", city_info['workersNeeded'])
        
        with col4:
            total_produced = len(city_info.get('produced', []))
            st.metric("Total Productions", total_produced)
        
        # Historique de la ville
        if city_info.get('history'):
            city_history_df = pd.DataFrame(city_info['history'])
            
            # Appliquer le filtre de tours
            city_history_filtered = city_history_df[
                (city_history_df['turn'] >= turn_range[0]) &
                (city_history_df['turn'] <= turn_range[1])
            ]
            
            if not city_history_filtered.empty:
                # Graphique de croissance
                fig_growth = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Population & Production', 'Science & Culture',
                                  'Health & Happiness', 'City Problems')
                )
                
                # Population et Production
                fig_growth.add_trace(
                    go.Scatter(x=city_history_filtered['turn'], y=city_history_filtered['population'],
                              name='Population', mode='lines+markers'),
                    row=1, col=1
                )
                fig_growth.add_trace(
                    go.Scatter(x=city_history_filtered['turn'], y=city_history_filtered['production'],
                              name='Production', mode='lines+markers', yaxis='y2'),
                    row=1, col=1
                )
                
                # Science et Culture
                fig_growth.add_trace(
                    go.Scatter(x=city_history_filtered['turn'], y=city_history_filtered['science'],
                              name='Science', mode='lines+markers'),
                    row=1, col=2
                )
                fig_growth.add_trace(
                    go.Scatter(x=city_history_filtered['turn'], y=city_history_filtered['culture'],
                              name='Culture', mode='lines+markers'),
                    row=1, col=2
                )
                
                # Santé et Bonheur
                fig_growth.add_trace(
                    go.Scatter(x=city_history_filtered['turn'], y=city_history_filtered['netHealth'],
                              name='Health', mode='lines+markers'),
                    row=2, col=1
                )
                fig_growth.add_trace(
                    go.Scatter(x=city_history_filtered['turn'], y=city_history_filtered['netHappiness'],
                              name='Happiness', mode='lines+markers'),
                    row=2, col=1
                )
                
                # Problèmes de la ville
                fig_growth.add_trace(
                    go.Scatter(x=city_history_filtered['turn'], y=city_history_filtered['criminalite'],
                              name='Crime', mode='lines+markers'),
                    row=2, col=2
                )
                fig_growth.add_trace(
                    go.Scatter(x=city_history_filtered['turn'], y=city_history_filtered['maladie'],
                              name='Disease', mode='lines+markers'),
                    row=2, col=2
                )
                
                fig_growth.update_layout(
                    height=700,
                    title_text=f"{selected_city} - Historical Evolution (Turns {turn_range[0]}-{turn_range[1]})",
                    showlegend=True
                )
                
                st.plotly_chart(fig_growth, use_container_width=True)
            else:
                st.warning(f"No data available for {selected_city} in the selected turn range ({turn_range[0]}-{turn_range[1]})")

        # Productions de la ville
        if city_info.get('produced'):
            st.subheader("🏗️ Production History")
            
            productions_df = pd.DataFrame(city_info['produced'])
            
            # Appliquer le filtre de tours
            productions_filtered = productions_df[
                (productions_df['turn'] >= turn_range[0]) &
                (productions_df['turn'] <= turn_range[1])
            ]
            
            if not productions_filtered.empty:
                # Vue 1: Timeline de production
                st.markdown("#### 📅 Production Timeline")
                
                # Créer un diagramme de Gantt-like pour visualiser quand chaque type a été produit
                production_timeline = productions_filtered.copy()
                production_timeline['count'] = 1
                
                # Grouper par tranches de tours (convertir en string pour éviter l'erreur JSON)
                min_turn = production_timeline['turn'].min()
                max_turn = production_timeline['turn'].max()
                
                # Adapter la taille des bins selon la plage de tours
                turn_span = max_turn - min_turn
                if turn_span <= 100:
                    bin_size = 10
                elif turn_span <= 500:
                    bin_size = 50
                else:
                    bin_size = 100
                    
                turn_bins = list(range(min_turn, max_turn + bin_size, bin_size))
                production_timeline['turn_range'] = pd.cut(production_timeline['turn'], bins=turn_bins)
                
                # Convertir les intervalles en strings
                production_timeline['turn_range_str'] = production_timeline['turn_range'].astype(str)
                
                # Compter les productions par type et par période
                timeline_summary = production_timeline.groupby(['turn_range_str', 'productName']).size().reset_index(name='count')
                
                fig_timeline = px.bar(
                    timeline_summary,
                    x='turn_range_str',
                    y='count',
                    color='productName',
                    title=f"Production Timeline - {selected_city} (Turns {turn_range[0]}-{turn_range[1]})",
                    labels={'turn_range_str': 'Turn Range', 'count': 'Units Produced'}
                )
                
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Vue 2: Analyse par catégorie
                st.markdown("#### 🎯 Production by Category")
                
                # Catégoriser les productions
                def categorize_production(prod_name):
                    prod_lower = prod_name.lower()
                    if 'unit' in prod_lower or 'warrior' in prod_lower or 'archer' in prod_lower or 'lanceur' in prod_lower:
                        return 'Military Units'
                    elif 'habitation' in prod_lower or 'building' in prod_lower:
                        return 'Buildings'
                    elif 'doctrine' in prod_lower:
                        return 'Doctrines'
                    elif 'alpha' in prod_lower:
                        return 'Leaders'
                    elif 'worker' in prod_lower or 'settler' in prod_lower:
                        return 'Civilian Units'
                    else:
                        return 'Other'
                
                productions_filtered['category'] = productions_filtered['productName'].apply(categorize_production)
                
                category_counts = productions_filtered['category'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_pie = px.pie(
                        values=category_counts.values,
                        names=category_counts.index,
                        title=f"Production Distribution by Category (Turns {turn_range[0]}-{turn_range[1]})"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    # Tableau des catégories
                    st.dataframe(
                        category_counts.to_frame('Count').reset_index().rename(columns={'index': 'Category'}),
                        use_container_width=True,
                        hide_index=True
                    )
                
                # Vue 3: Évolution de la spécialisation (adaptée au filtre)
                st.markdown("#### 📈 Production Specialization Over Time")
                
                # Analyser comment la production évolue dans le temps
                min_turn = productions_filtered['turn'].min()
                max_turn = productions_filtered['turn'].max()
                turn_span = max_turn - min_turn
                
                # Créer des ères dynamiques basées sur la plage filtrée
                num_eras = min(6, max(2, turn_span // 50))  # Entre 2 et 6 ères
                era_size = turn_span // num_eras
                
                era_bins = [min_turn + i * era_size for i in range(num_eras + 1)]
                era_bins[-1] = max_turn + 1  # S'assurer que la dernière bin inclut tout
                
                era_labels = [f"Period {i+1}" for i in range(num_eras)]
                
                productions_filtered['era'] = pd.cut(
                    productions_filtered['turn'], 
                    bins=era_bins,
                    labels=era_labels,
                    include_lowest=True
                )
                
                era_category = productions_filtered.groupby(['era', 'category']).size().unstack(fill_value=0)
                
                if not era_category.empty:
                    fig_specialization = px.bar(
                        era_category.T,
                        title=f"Production Focus by Period (Turns {turn_range[0]}-{turn_range[1]})",
                        labels={'value': 'Number of Productions', 'index': 'Category'},
                        barmode='group'
                    )
                    
                    st.plotly_chart(fig_specialization, use_container_width=True)
                
                # Vue 4: Efficacité de production
                st.markdown("#### ⚡ Production Efficiency")
                
                # Calculer le temps entre productions
                productions_sorted = productions_filtered.sort_values('turn')
                productions_sorted['turns_since_last'] = productions_sorted['turn'].diff()
                
                # Moyenne de tours entre productions par période
                efficiency_data = []
                window_size = max(5, len(productions_sorted) // 10)  # Adapter la fenêtre à la quantité de données
                
                for i in range(0, len(productions_sorted), window_size):
                    slice_df = productions_sorted.iloc[i:i+window_size]
                    if len(slice_df) > 1 and slice_df['turns_since_last'].notna().any():
                        avg_turns = slice_df['turns_since_last'].mean()
                        avg_turn = slice_df['turn'].mean()
                        if not pd.isna(avg_turns):
                            efficiency_data.append({
                                'turn': avg_turn,
                                'avg_turns_between_production': avg_turns
                            })
                
                if efficiency_data:
                    efficiency_df = pd.DataFrame(efficiency_data)
                    
                    fig_efficiency = px.line(
                        efficiency_df,
                        x='turn',
                        y='avg_turns_between_production',
                        title=f"Production Efficiency Over Time (Turns {turn_range[0]}-{turn_range[1]})",
                        labels={'avg_turns_between_production': 'Average Turns Between Productions'},
                        markers=True
                    )
                    
                    fig_efficiency.add_hline(
                        y=efficiency_df['avg_turns_between_production'].mean(),
                        line_dash="dash",
                        annotation_text="Average"
                    )
                    
                    st.plotly_chart(fig_efficiency, use_container_width=True)
                
                # Vue 5: Productions dans la période sélectionnée
                st.markdown("#### 🎯 Productions in Selected Period")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Premières et dernières productions de la période
                    st.markdown("**First 5 Productions in Period:**")
                    first_productions = productions_sorted.head(5)[['turn', 'productName']]
                    st.dataframe(
                        first_productions,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            'turn': st.column_config.NumberColumn('Turn', format='%d'),
                            'productName': 'Production'
                        }
                    )
                    
                    st.markdown("**Last 5 Productions in Period:**")
                    last_productions = productions_sorted.tail(5)[['turn', 'productName']]
                    st.dataframe(
                        last_productions,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            'turn': st.column_config.NumberColumn('Turn', format='%d'),
                            'productName': 'Production'
                        }
                    )
                
                with col2:
                    # Distribution des catégories dans la période
                    category_dist = productions_filtered['category'].value_counts()
                    
                    fig_period_dist = px.bar(
                        x=category_dist.index,
                        y=category_dist.values,
                        title=f"Production Focus (Turns {turn_range[0]}-{turn_range[1]})",
                        labels={'x': 'Category', 'y': 'Count'}
                    )
                    
                    st.plotly_chart(fig_period_dist, use_container_width=True)
                
                # Vue 6: Analyse des patterns de production
                st.markdown("#### 🔄 Production Patterns")
                
                # Identifier les productions répétitives dans la période
                production_counts = productions_filtered['productName'].value_counts()
                repeated_productions = production_counts[production_counts > 1]
                
                if len(repeated_productions) > 0:
                    # Pour chaque production répétée, montrer quand elle a été produite
                    st.markdown("**Repeated Productions Timeline:**")
                    
                    # Sélectionner les 5 productions les plus répétées
                    top_repeated = repeated_productions.head(5)
                    
                    pattern_data = []
                    for prod_name, count in top_repeated.items():
                        turns = productions_filtered[productions_filtered['productName'] == prod_name]['turn'].tolist()
                        for turn in turns:
                            pattern_data.append({
                                'productName': prod_name,
                                'turn': turn,
                                'count': count
                            })
                    
                    pattern_df = pd.DataFrame(pattern_data)
                    
                    fig_patterns = px.scatter(
                        pattern_df,
                        x='turn',
                        y='productName',
                        size='count',
                        title=f"When Repeated Productions Were Built (Turns {turn_range[0]}-{turn_range[1]})",
                        labels={'turn': 'Turn', 'productName': 'Production Type'},
                        size_max=20
                    )
                    
                    # Ajouter les limites du filtre
                    fig_patterns.add_vline(x=turn_range[0], line_dash="dash", line_color="gray", opacity=0.5)
                    fig_patterns.add_vline(x=turn_range[1], line_dash="dash", line_color="gray", opacity=0.5)
                    
                    st.plotly_chart(fig_patterns, use_container_width=True)
            else:
                st.warning(f"No productions found for {selected_city} in the selected turn range ({turn_range[0]}-{turn_range[1]})")
        
# Analyse des timings
elif view_mode == "⏱️ Turn Timings":
    st.header("⏱️ Turn Timings Analysis")
    
    # Filtrer les données de timing
    df_timings_filtered = df_timings[
        (df_timings['playerName'].isin(selected_players)) &
        (df_timings['turn'] >= turn_range[0]) &
        (df_timings['turn'] <= turn_range[1])
    ]
    
    if not df_timings_filtered.empty:
        # Durée moyenne par joueur
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
        
        # Evolution de la durée des tours
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
        
        # Heatmap des durées
        st.subheader("🔥 Turn Duration Heatmap")
        
        # Créer une matrice pour la heatmap
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

# Analyse comparative
elif view_mode == "📈 Comparative Analysis":
    st.header("📈 Comparative Analysis")
    
    # Sélection du tour pour la comparaison
    comparison_turn = st.slider(
        "Select turn for comparison",
        min_value=turn_range[0],
        max_value=turn_range[1],
        value=turn_range[1]
    )
    
    # Obtenir les données pour le tour sélectionné
    turn_data = df_player_stats[
        (df_player_stats['turn'] == comparison_turn) &
        (df_player_stats['playerName'].isin(selected_players))
    ]
    
    if not turn_data.empty:
        # Graphique radar
        st.subheader(f"🎯 Player Comparison - Turn {comparison_turn}")
        
        categories = ['population', 'cities', 'power', 'techPercent', 
                     'totalScienceOutput', 'totalProductionOutput']
        
        fig_radar = go.Figure()
        
        for player in selected_players:
            player_data = turn_data[turn_data['playerName'] == player]
            if not player_data.empty:
                values = []
                for cat in categories:
                    max_val = turn_data[cat].max()
                    if max_val > 0:
                        values.append(player_data[cat].values[0] / max_val * 100)
                    else:
                        values.append(0)
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=['Population', 'Cities', 'Military', 'Technology', 
                          'Science', 'Production'],
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
            title=f"Civilization Comparison - Turn {comparison_turn}"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Tableau comparatif
        st.subheader("📊 Detailed Comparison Table")

        comparison_metrics = ['population', 'cities', 'power', 'techPercent',
                            'treasury', 'totalScienceOutput', 'totalProductionOutput',
                            'numUnits', 'totalTurnsInAnarchy']

        comparison_df = turn_data[['playerName'] + comparison_metrics].set_index('playerName')

        # Utiliser st.dataframe avec des paramètres de formatage
        st.dataframe(
            comparison_df,
            use_container_width=True,
            column_config={
                'population': st.column_config.NumberColumn('Population', format='%d'),
                'cities': st.column_config.NumberColumn('Cities', format='%d'),
                'power': st.column_config.NumberColumn('Power', format='%d'),
                'techPercent': st.column_config.NumberColumn('Tech %', format='%d%%'),
                'treasury': st.column_config.NumberColumn('Treasury', format='%d'),
                'totalScienceOutput': st.column_config.NumberColumn('Science', format='%d'),
                'totalProductionOutput': st.column_config.NumberColumn('Production', format='%d'),
                'numUnits': st.column_config.NumberColumn('Units', format='%d'),
                'totalTurnsInAnarchy': st.column_config.NumberColumn('Anarchy Turns', format='%d')
            }
        )

        # Alternative : créer une heatmap avec plotly
        st.subheader("📊 Comparison Heatmap")

        # Normaliser les données pour la heatmap
        normalized_df = comparison_df.copy()
        for col in comparison_metrics:
            max_val = normalized_df[col].max()
            if max_val > 0:
                normalized_df[col] = (normalized_df[col] / max_val * 100).round(0)

        fig_heatmap = px.imshow(
            normalized_df.T,
            labels=dict(x="Player", y="Metric", color="Relative Value (%)"),
            aspect="auto",
            color_continuous_scale="RdYlGn",
            title="Player Comparison Heatmap (Normalized to 100%)"
        )

        # Utiliser update_layout au lieu de update_xaxis
        fig_heatmap.update_layout(
            xaxis=dict(side="top")
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)

# Rankings
elif view_mode == "🏆 Rankings":
    st.header("🏆 Rankings & Achievements")
    
    # Obtenir les dernières données
    latest_turn = df_player_stats['turn'].max()
    latest_data = df_player_stats[
        (df_player_stats['turn'] == latest_turn) &
        (df_player_stats['playerName'].isin(selected_players))
    ]
    
    if not latest_data.empty:
        # Créer différents classements
        rankings = {
            '👑 Population': latest_data.nlargest(10, 'population')[['playerName', 'population']],
            '⚔️ Military Power': latest_data.nlargest(10, 'power')[['playerName', 'power']],
            '🏛️ Number of Cities': latest_data.nlargest(10, 'cities')[['playerName', 'cities']],
            '🔬 Technology': latest_data.nlargest(10, 'techPercent')[['playerName', 'techPercent']],
            '💰 Treasury': latest_data.nlargest(10, 'treasury')[['playerName', 'treasury']],
            '📚 Science Output': latest_data.nlargest(10, 'totalScienceOutput')[['playerName', 'totalScienceOutput']]
        }
        
        # Afficher les classements en colonnes
        cols = st.columns(3)
        
        for i, (title, ranking) in enumerate(rankings.items()):
            with cols[i % 3]:
                st.subheader(title)
                
                # Ajouter des médailles pour le top 3
                for idx, row in ranking.iterrows():
                    position = ranking.index.get_loc(idx) + 1
                    medal = ""
                    if position == 1:
                        medal = "🥇 "
                    elif position == 2:
                        medal = "🥈 "
                    elif position == 3:
                        medal = "🥉 "
                    
                    value_col = ranking.columns[1]
                    st.write(f"{medal}{position}. **{row['playerName']}**: {row[value_col]:,}")
        
    # Graphique de progression du score
    st.subheader("📈 Score Evolution")

    # Calculer un score composite
    df_player_stats['composite_score'] = (
        df_player_stats['population'] * 10 +
        df_player_stats['cities'] * 50 +
        df_player_stats['power'] * 0.1 +
        df_player_stats['techPercent'] * 5
    )

    # Appliquer le filtre de tours et de joueurs
    score_data = df_player_stats[
        (df_player_stats['playerName'].isin(selected_players)) &
        (df_player_stats['turn'] >= turn_range[0]) &
        (df_player_stats['turn'] <= turn_range[1])
    ]

    if not score_data.empty:
        fig_score = px.line(
            score_data,
            x='turn',
            y='composite_score',
            color='playerName',
            title=f"Composite Score Evolution (Turns {turn_range[0]}-{turn_range[1]})",
            labels={'composite_score': 'Score', 'turn': 'Turn'},
            markers=True
        )
        
        # Ajouter des annotations pour les valeurs finales
        for player in selected_players:
            player_data = score_data[score_data['playerName'] == player]
            if not player_data.empty:
                last_point = player_data.iloc[-1]
                fig_score.add_annotation(
                    x=last_point['turn'],
                    y=last_point['composite_score'],
                    text=f"{int(last_point['composite_score'])}",
                    showarrow=False,
                    xshift=10,
                    font=dict(size=10)
                )
        
        st.plotly_chart(fig_score, use_container_width=True)
        
        # Afficher les détails du calcul du score
        with st.expander("📊 Score Calculation Details"):
            st.markdown("""
            **Composite Score Formula:**
            - Population × 10
            - Cities × 50
            - Military Power × 0.1
            - Technology % × 5
            """)
            
            # Tableau des scores actuels
            latest_turn_in_range = score_data['turn'].max()
            latest_scores = score_data[score_data['turn'] == latest_turn_in_range][
                ['playerName', 'population', 'cities', 'power', 'techPercent', 'composite_score']
            ].copy()
            
            if not latest_scores.empty:
                latest_scores['score_breakdown'] = latest_scores.apply(
                    lambda row: f"Pop({row['population']}×10) + Cities({row['cities']}×50) + Power({row['power']}×0.1) + Tech({row['techPercent']}×5)",
                    axis=1
                )
                
                st.markdown(f"**Score Breakdown at Turn {latest_turn_in_range}:**")
                st.dataframe(
                    latest_scores[['playerName', 'composite_score', 'score_breakdown']].rename(columns={
                        'playerName': 'Player',
                        'composite_score': 'Total Score',
                        'score_breakdown': 'Calculation'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.warning(f"No score data available for the selected players in turn range {turn_range[0]}-{turn_range[1]}")
  

# Nouvelle vue : Score Analysis
elif view_mode == "🎯 Score Analysis":
    st.header("🎯 Score Analysis")
    
    # Préparer les données de score
    all_scores = []
    for player in players_data:
        if player['isHuman'] and 'scoreHistory' in player:
            for score in player['scoreHistory']:
                score_entry = score.copy()
                score_entry['playerName'] = player['name']
                all_scores.append(score_entry)
    
    if all_scores:
        df_scores = pd.DataFrame(all_scores)
        
        # Appliquer les filtres
        df_scores_filtered = df_scores[
            (df_scores['playerName'].isin(selected_players)) &
            (df_scores['turn'] >= turn_range[0]) &
            (df_scores['turn'] <= turn_range[1])
        ]
        
        if not df_scores_filtered.empty:
            # Vue 1: Score total au fil du temps
            st.subheader("📊 Total Score Evolution")
            
            fig_total_score = px.line(
                df_scores_filtered,
                x='turn',
                y='total',
                color='playerName',
                title=f"Total Score Evolution (Turns {turn_range[0]}-{turn_range[1]})",
                markers=True
            )
            
            st.plotly_chart(fig_total_score, use_container_width=True)
            
            # Vue 2: Composantes du score
            st.subheader("🧩 Score Components")
            
            score_components = ['population', 'territory', 'technologies', 'wonders']
            
            # Créer des sous-graphiques pour chaque composante
            fig_components = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Population Score', 'Territory Score', 
                              'Technology Score', 'Wonders Score']
            )
            
            for player in selected_players:
                player_data = df_scores_filtered[df_scores_filtered['playerName'] == player]
                if not player_data.empty:
                    # Population
                    fig_components.add_trace(
                        go.Scatter(x=player_data['turn'], y=player_data['population'],
                                  name=player, mode='lines+markers', showlegend=True),
                        row=1, col=1
                    )
                    # Territory
                    fig_components.add_trace(
                        go.Scatter(x=player_data['turn'], y=player_data['territory'],
                                  name=player, mode='lines+markers', showlegend=False),
                        row=1, col=2
                    )
                    # Technologies
                    fig_components.add_trace(
                        go.Scatter(x=player_data['turn'], y=player_data['technologies'],
                                  name=player, mode='lines+markers', showlegend=False),
                        row=2, col=1
                    )
                    # Wonders
                    fig_components.add_trace(
                        go.Scatter(x=player_data['turn'], y=player_data['wonders'],
                                  name=player, mode='lines+markers', showlegend=False),
                        row=2, col=2
                    )
            
            fig_components.update_layout(height=600, title_text="Score Components Breakdown")
            st.plotly_chart(fig_components, use_container_width=True)
            
            # Vue 3: Victory Score et moyennes économiques
            st.subheader("🏆 Victory Score & Economic Averages")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_victory = px.line(
                    df_scores_filtered,
                    x='turn',
                    y='victoryScore',
                    color='playerName',
                    title="Victory Score Evolution",
                    markers=True
                )
                st.plotly_chart(fig_victory, use_container_width=True)
            
            with col2:
                # Moyennes économiques
                fig_eco_avg = go.Figure()
                
                for player in selected_players:
                    player_data = df_scores_filtered[df_scores_filtered['playerName'] == player]
                    if not player_data.empty:
                        fig_eco_avg.add_trace(go.Scatter(
                            x=player_data['turn'],
                            y=player_data['economyAvg'],
                            name=f"{player} - Economy",
                            mode='lines+markers'
                        ))
                        fig_eco_avg.add_trace(go.Scatter(
                            x=player_data['turn'],
                            y=player_data['industryAvg'],
                            name=f"{player} - Industry",
                            mode='lines+markers',
                            line=dict(dash='dash')
                        ))
                        fig_eco_avg.add_trace(go.Scatter(
                            x=player_data['turn'],
                            y=player_data['agricultureAvg'],
                            name=f"{player} - Agriculture",
                            mode='lines+markers',
                            line=dict(dash='dot')
                        ))
                
                fig_eco_avg.update_layout(
                    title="Economic Averages",
                    xaxis_title="Turn",
                    yaxis_title="Average Value"
                )
                st.plotly_chart(fig_eco_avg, use_container_width=True)
            
            # Vue 4: Analyse comparative à un tour donné
            st.subheader("📊 Score Comparison at Specific Turn")
            
            available_turns = sorted(df_scores_filtered['turn'].unique())
            selected_turn = st.select_slider(
                "Select turn for comparison",
                options=available_turns,
                value=available_turns[-1] if available_turns else turn_range[1]
            )
            
            turn_data = df_scores_filtered[df_scores_filtered['turn'] == selected_turn]
            
            if not turn_data.empty:
                # Graphique en barres empilées
                fig_stacked = go.Figure()
                
                for component in ['population', 'territory', 'technologies', 'wonders']:
                    fig_stacked.add_trace(go.Bar(
                        name=component.capitalize(),
                        x=turn_data['playerName'],
                        y=turn_data[component]
                    ))
                
                fig_stacked.update_layout(
                    barmode='stack',
                    title=f"Score Composition at Turn {selected_turn}",
                    xaxis_title="Player",
                    yaxis_title="Score"
                )
                
                st.plotly_chart(fig_stacked, use_container_width=True)
                
                # Tableau détaillé
                st.markdown(f"**Detailed Scores at Turn {selected_turn}:**")
                display_cols = ['playerName', 'population', 'territory', 'technologies', 
                               'wonders', 'total', 'victoryScore', 'economyAvg', 
                               'industryAvg', 'agricultureAvg']
                
                st.dataframe(
                    turn_data[display_cols].rename(columns={
                        'playerName': 'Player',
                        'population': 'Pop',
                        'territory': 'Terr',
                        'technologies': 'Tech',
                        'wonders': 'Wond',
                        'total': 'Total',
                        'victoryScore': 'Victory',
                        'economyAvg': 'Eco',
                        'industryAvg': 'Ind',
                        'agricultureAvg': 'Agr'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.warning(f"No score data available for the selected players in turn range {turn_range[0]}-{turn_range[1]}")
    else:
        st.warning("No score history data available")

# Nouvelle vue : Military Units
elif view_mode == "⚔️ Military Units":
    st.header("⚔️ Military Units Analysis")
    
    # Préparer les données d'unités
    all_units = []
    for player in players_data:
        if player['isHuman'] and 'unitInventories' in player:
            for inventory in player['unitInventories']:
                # Créer une entrée pour chaque type d'unité
                for unit_key, unit_data in inventory['unitsByType'].items():
                    unit_entry = {
                        'playerName': player['name'],
                        'turn': inventory['turn'],
                        'unitType': unit_data['unitType'],
                        'unitAIType': unit_data['unitAIType'],
                        'count': unit_data['count'],
                        'combatValue': unit_data['combatValue'],
                        'movement': unit_data['movement']
                    }
                    all_units.append(unit_entry)
    
    if all_units:
        df_units = pd.DataFrame(all_units)
        
        # Appliquer les filtres
        df_units_filtered = df_units[
            (df_units['playerName'].isin(selected_players)) &
            (df_units['turn'] >= turn_range[0]) &
            (df_units['turn'] <= turn_range[1])
        ]
        
        if not df_units_filtered.empty:
            # Vue 1: Total des unités au fil du temps
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
            
            # Vue 2: Composition des unités par type d'IA
            st.subheader("🎯 Unit Composition by AI Type")
            
            # Obtenir les types d'IA uniques
            ai_types = df_units_filtered['unitAIType'].unique()
            
            # Créer un graphique pour chaque joueur
            for player in selected_players:
                player_units = df_units_filtered[df_units_filtered['playerName'] == player]
                
                if not player_units.empty:
                    # Agréger par type d'IA et tour
                    ai_composition = player_units.groupby(['turn', 'unitAIType'])['count'].sum().reset_index()
                    
                    fig_ai_comp = px.area(
                        ai_composition,
                        x='turn',
                        y='count',
                        color='unitAIType',
                        title=f"{player} - Unit Composition by AI Type",
                        labels={'count': 'Number of Units', 'unitAIType': 'AI Type'}
                    )
                    
                    st.plotly_chart(fig_ai_comp, use_container_width=True)
            
            # Vue 3: Types d'unités les plus populaires
            st.subheader("🏆 Most Popular Unit Types")
            
            # Sélectionner un tour spécifique pour l'analyse
            available_turns = sorted(df_units_filtered['turn'].unique())
            analysis_turn = st.select_slider(
                "Select turn for unit analysis",
                options=available_turns,
                value=available_turns[-1] if available_turns else turn_range[1]
            )
            
            turn_units = df_units_filtered[df_units_filtered['turn'] == analysis_turn]
            
            if not turn_units.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Top unités par joueur
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
                    # Graphique circulaire de la répartition
                    unit_distribution = turn_units.groupby('unitType')['count'].sum().sort_values(ascending=False).head(10)
                    
                    fig_pie = px.pie(
                        values=unit_distribution.values,
                        names=unit_distribution.index,
                        title=f"Unit Distribution at Turn {analysis_turn}"
                    )
                    
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            # Vue 4: Evolution des types d'unités spécifiques
            st.subheader("📊 Specific Unit Types Evolution")
            
            # Sélectionner les types d'unités à suivre
            all_unit_types = sorted(df_units_filtered['unitType'].unique())
            selected_unit_types = st.multiselect(
                "Select unit types to track",
                options=all_unit_types,
                default=all_unit_types[:5] if len(all_unit_types) > 5 else all_unit_types
            )
            
            if selected_unit_types:
                # Filtrer pour les types sélectionnés
                specific_units = df_units_filtered[df_units_filtered['unitType'].isin(selected_unit_types)]
                
                # Créer un graphique pour chaque joueur
                for player in selected_players:
                    player_specific = specific_units[specific_units['playerName'] == player]
                    
                    if not player_specific.empty:
                        fig_specific = px.line(
                            player_specific,
                            x='turn',
                            y='count',
                            color='unitType',
                            title=f"{player} - Selected Unit Types Evolution",
                            markers=True
                        )
                        
                        st.plotly_chart(fig_specific, use_container_width=True)
            
            # Vue 5: Analyse comparative des forces militaires
            st.subheader("⚔️ Military Strength Comparison")
            
            # Créer une métrique de force militaire basée sur les types d'unités
            military_ai_types = ['UNITAI_ATTACK', 'UNITAI_CITY_DEFENSE', 'UNITAI_COLLATERAL', 
                                'UNITAI_PILLAGE', 'UNITAI_RESERVE', 'UNITAI_COUNTER', 'UNITAI_PARADROP']
            
            military_units = df_units_filtered[df_units_filtered['unitAIType'].isin(military_ai_types)]
            
            if not military_units.empty:
                military_strength = military_units.groupby(['turn', 'playerName'])['count'].sum().reset_index()
                military_strength.rename(columns={'count': 'military_units'}, inplace=True)
                
                fig_military = px.bar(
                    military_strength,
                    x='turn',
                    y='military_units',
                    color='playerName',
                    title="Military Units Comparison",
                    barmode='group'
                )
                
                st.plotly_chart(fig_military, use_container_width=True)
        else:
            st.warning(f"No unit data available for the selected players in turn range {turn_range[0]}-{turn_range[1]}")
    else:
        st.warning("No unit inventory data available.")  

elif view_mode == "🧮 Unit Evaluation":
    st.header("🧮 Unit Evaluation Analysis")

    # Récupérer les données d'évaluation des unités pour les joueurs sélectionnés
    all_evaluations = []
    all_best_units = []
    for player in players_data:
        if player['isHuman'] and 'unitEvaluation' in player:
            evals = player['unitEvaluation'].get('evaluations', [])
            for e in evals:
                e['playerName'] = player['name']
                all_evaluations.append(e)
            best_units = player['unitEvaluation'].get('bestUnitsByAIType', {})
            for ai_type, units in best_units.items():
                for u in units:
                    u['playerName'] = player['name']
                    u['unitAIType'] = ai_type
                    all_best_units.append(u)

    if all_evaluations:
        df_eval = pd.DataFrame(all_evaluations)
        df_eval_filtered = df_eval[
            (df_eval['playerName'].isin(selected_players)) &
            (df_eval['turn'] >= turn_range[0]) &
            (df_eval['turn'] <= turn_range[1])
        ]

        st.subheader("📈 Unit Value Evolution")
        # Sélectionner le type d'IA à analyser
        ai_types = sorted(df_eval_filtered['unitAIType'].unique())
        selected_ai_type = st.selectbox("Select AI Type", ai_types)

        df_ai = df_eval_filtered[df_eval_filtered['unitAIType'] == selected_ai_type]

        if not df_ai.empty:
            fig_unit_value = px.line(
                df_ai,
                x='turn',
                y='calculatedValue',
                color='unitType',
                line_dash='cityName',
                title=f"Unit Value Evolution ({selected_ai_type})",
                labels={'calculatedValue': 'Calculated Value', 'turn': 'Turn', 'unitType': 'Unit Type'}
            )
            st.plotly_chart(fig_unit_value, use_container_width=True)

            # Tableau des unités "isBetterUnit"
            st.markdown("#### 🏅 Best Units per Turn")
            best_units_df = df_ai[df_ai.get('isBetterUnit', False)]
            st.dataframe(
                best_units_df[['turn', 'cityName', 'unitType', 'unitName', 'calculatedValue', 'baseValue', 'finalValue']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No evaluation data for this AI type in the selected range.")

    if all_best_units:
        df_best = pd.DataFrame(all_best_units)
        df_best_filtered = df_best[
            (df_best['playerName'].isin(selected_players)) &
            (df_best['unitAIType'] == selected_ai_type)
        ]

        st.subheader("🏆 Best Units by AI Type")
        fig_best = px.scatter(
            df_best_filtered,
            x='firstTurn',
            y='finalValue',
            color='unitType',
            hover_data=['unitName', 'baseValue'],
            title=f"Best Units ({selected_ai_type}) Over Time",
            labels={'firstTurn': 'First Turn', 'finalValue': 'Final Value'}
        )
        st.plotly_chart(fig_best, use_container_width=True)

        st.dataframe(
            df_best_filtered[['firstTurn', 'unitType', 'unitName', 'finalValue', 'baseValue']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No best unit data available.")

# Footer avec statistiques
st.markdown("---")
st.markdown("### 📊 Session Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"📁 Data loaded from {len(players_data)} players")

with col2:
    st.info(f"🏛️ Tracking {len(cities_data)} cities")

with col3:
    total_turns = df_player_stats['turn'].max() if not df_player_stats.empty else 0
    st.info(f"🎮 Game progress: Turn {total_turns}")

# Export des données
with st.expander("💾 Export Data"):
    st.markdown("### Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Player Stats to CSV"):
            csv = df_player_stats.to_csv(index=False)
            st.download_button(
                label="Download Player Stats CSV",
                data=csv,
                file_name=f"player_stats_turn_{total_turns}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Export City History to CSV"):
            csv = df_city_history.to_csv(index=False)
            st.download_button(
                label="Download City History CSV",
                data=csv,
                file_name=f"city_history_turn_{total_turns}.csv",
                mime="text/csv"
            )
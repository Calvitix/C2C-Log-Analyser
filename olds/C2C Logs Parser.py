"""
Civ4 C2C Log Parser - Object-Oriented Design
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
import re
import pandas as pd
from abc import ABC, abstractmethod


# Enums for type safety
class CivicCategory(Enum):
    GOVERNMENT = "government"
    LEGAL = "legal"
    LABOR = "labor"
    ECONOMY = "economy"
    RELIGION = "religion"
    MILITARY = "military"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    CULTURE = "culture"
    INFRASTRUCTURE = "infrastructure"


class UnitType(Enum):
    MILITARY = "military"
    WORKER = "worker"
    SETTLER = "settler"
    SCOUT = "scout"
    NAVAL = "naval"
    AIR = "air"
    GREAT_PERSON = "great_person"


class EventType(Enum):
    TURN_START = "turn_start"
    CITY_FOUNDED = "city_founded"
    BUILDING_COMPLETED = "building_completed"
    UNIT_BUILT = "unit_built"
    TECH_DISCOVERED = "tech_discovered"
    CIVIC_CHANGED = "civic_changed"
    WAR_DECLARED = "war_declared"
    PEACE_SIGNED = "peace_signed"


# Data classes for structured data
@dataclass
class TurnInfo:
    """Represents a turn in the game"""
    turn_number: int
    timestamp: float
    active_player_id: int
    active_player_name: str


@dataclass
class EconomicStats:
    """Economic statistics for a player"""
    treasury: int = 0
    gold_rate: int = 0
    total_gold_income: int = 0
    gold_income_from_self: int = 0
    gold_from_trade_agreements: int = 0
    research_rate: int = 0
    culture_rate: int = 0
    espionage_rate: int = 0
    upgrade_budget: int = 0


@dataclass
class MilitaryStats:
    """Military statistics for a player"""
    total_units: int = 0
    military_units: int = 0
    worker_units: int = 0
    unit_breakdown: Dict[UnitType, int] = field(default_factory=dict)


@dataclass
class CivicConfiguration:
    """Current civic configuration for a player"""
    civics: Dict[CivicCategory, str] = field(default_factory=dict)
    
    def get_civic(self, category: CivicCategory) -> Optional[str]:
        return self.civics.get(category)
    
    def set_civic(self, category: CivicCategory, civic_name: str):
        self.civics[category] = civic_name


@dataclass
class PlayerStats:
    """Complete stats for a player at a specific turn"""
    turn: int
    player_id: int
    player_name: str
    cities: int = 0
    population: int = 0
    power: int = 0
    tech_percent: int = 0
    
    # Composed objects
    economics: EconomicStats = field(default_factory=EconomicStats)
    military: MilitaryStats = field(default_factory=MilitaryStats)
    civics: CivicConfiguration = field(default_factory=CivicConfiguration)
    
    # Anarchy
    current_anarchy_turns: int = 0
    total_turns_in_anarchy: int = 0
    
    # Metadata
    timestamp: float = 0.0


@dataclass
class City:
    """Represents a city with its properties"""
    name: str
    owner_id: int
    owner_name: str
    x: int
    y: int
    founded_turn: int
    
    # Current stats
    population: int = 1
    threat_level: int = 0
    current_production: Optional[str] = None
    production_value: int = 0
    
    # History tracking
    production_history: List[tuple[int, str]] = field(default_factory=list)
    population_history: List[tuple[int, int]] = field(default_factory=list)
    
    def update_population(self, turn: int, new_pop: int):
        self.population = new_pop
        self.population_history.append((turn, new_pop))
    
    def start_production(self, turn: int, building: str):
        self.current_production = building
        self.production_history.append((turn, building))


class Player:
    """Represents a player/civilization in the game"""
    
    def __init__(self, player_id: int, name: str):
        self.id = player_id
        self.name = name
        self.is_human = player_id < 40  # NPCs have ID >= 40
        
        # Cities owned
        self.cities: Dict[str, City] = {}
        
        # Stats history
        self.stats_history: List[PlayerStats] = []
        
        # Current state
        self.current_stats: Optional[PlayerStats] = None
        
    def add_city(self, city: City):
        self.cities[city.name] = city
    
    def update_stats(self, turn: int, stats: PlayerStats):
        self.current_stats = stats
        self.stats_history.append(stats)
    
    def get_stats_at_turn(self, turn: int) -> Optional[PlayerStats]:
        for stats in self.stats_history:
            if stats.turn == turn:
                return stats
        return None


class Game:
    """Represents the entire game state"""
    
    def __init__(self):
        self.players: Dict[int, Player] = {}
        self.turns: List[TurnInfo] = []
        self.current_turn = 0
        self.all_cities: Dict[str, City] = {}
        
    def add_player(self, player_id: int, name: str) -> Player:
        if player_id not in self.players:
            self.players[player_id] = Player(player_id, name)
        return self.players[player_id]
    
    def add_turn(self, turn_info: TurnInfo):
        self.turns.append(turn_info)
        self.current_turn = turn_info.turn_number
    
    def add_city(self, city: City):
        self.all_cities[city.name] = city
        if city.owner_id in self.players:
            self.players[city.owner_id].add_city(city)


# Parser components
class LogPattern(ABC):
    """Abstract base class for log patterns"""
    
    @abstractmethod
    def match(self, line: str) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def process(self, match_data: Dict, game: Game, context: Dict):
        pass


class TurnActivePattern(LogPattern):
    """Pattern for turn activation"""
    
    def __init__(self):
        self.pattern = re.compile(r'Player\s+(\d+)\s*\(([^)]+)\)\s*setTurnActive for turn\s+(\d+)')
    
    def match(self, line: str) -> Optional[Dict]:
        match = self.pattern.search(line)
        if match:
            return {
                'player_id': int(match.group(1)),
                'player_name': match.group(2),
                'turn': int(match.group(3))
            }
        return None
    
    def process(self, match_data: Dict, game: Game, context: Dict):
        turn_info = TurnInfo(
            turn_number=match_data['turn'],
            timestamp=context.get('timestamp', 0.0),
            active_player_id=match_data['player_id'],
            active_player_name=match_data['player_name']
        )
        game.add_turn(turn_info)
        game.add_player(match_data['player_id'], match_data['player_name'])
        context['active_player'] = match_data['player_id']
        context['current_turn'] = match_data['turn']


class PlayerStatsPattern(LogPattern):
    """Pattern for player statistics"""
    
    def __init__(self):
        self.pattern = re.compile(
            r'Player\s+(\d+)\s*\(([^)]+)\)\s*has\s+(\d+)\s+cities,\s+(\d+)\s+pop,\s+(\d+)\s+power,\s+(\d+)\s+tech percent'
        )
    
    def match(self, line: str) -> Optional[Dict]:
        match = self.pattern.search(line)
        if match:
            return {
                'player_id': int(match.group(1)),
                'player_name': match.group(2),
                'cities': int(match.group(3)),
                'population': int(match.group(4)),
                'power': int(match.group(5)),
                'tech_percent': int(match.group(6))
            }
        return None
    
    def process(self, match_data: Dict, game: Game, context: Dict):
        player = game.add_player(match_data['player_id'], match_data['player_name'])
        
        stats = PlayerStats(
            turn=context.get('current_turn', 0),
            player_id=match_data['player_id'],
            player_name=match_data['player_name'],
            cities=match_data['cities'],
            population=match_data['population'],
            power=match_data['power'],
            tech_percent=match_data['tech_percent'],
            timestamp=context.get('timestamp', 0.0)
        )
        
        player.update_stats(stats.turn, stats)


class CityFoundingPattern(LogPattern):
    """Pattern for city founding"""
    
    def __init__(self):
        self.pattern = re.compile(
            r'Player\s+(\d+)\s*\(([^)]+)\)\s*founds new city\s+([^)]+)\s+at\s+(\d+),\s+(\d+)'
        )
    
    def match(self, line: str) -> Optional[Dict]:
        match = self.pattern.search(line)
        if match:
            return {
                'player_id': int(match.group(1)),
                'player_name': match.group(2),
                'city_name': match.group(3),
                'x': int(match.group(4)),
                'y': int(match.group(5))
            }
        return None
    
    def process(self, match_data: Dict, game: Game, context: Dict):
        city = City(
            name=match_data['city_name'],
            owner_id=match_data['player_id'],
            owner_name=match_data['player_name'],
            x=match_data['x'],
            y=match_data['y'],
            founded_turn=context.get('current_turn', 0)
        )
        game.add_city(city)


class Civ4LogParser:
    """Main parser class using OOP design"""
    
    def __init__(self):
        self.game = Game()
        self.patterns: List[LogPattern] = [
            TurnActivePattern(),
            PlayerStatsPattern(),
            CityFoundingPattern(),
            # Add more patterns here
        ]
        self.context = {
            'timestamp': 0.0,
            'current_turn': 0,
            'active_player': None
        }
    
    def parse_file(self, file_content: str) -> Game:
        """Parse the entire log file"""
        lines = file_content.split('\n')
        
        for line in lines:
            if line.strip():
                self._parse_line(line)
        
        return self.game
    
    def _parse_line(self, line: str):
        """Parse a single line"""
        # Extract timestamp
        timestamp_match = re.match(r'^\[(\d+\.\d+)\]', line)
        if timestamp_match:
            self.context['timestamp'] = float(timestamp_match.group(1))
        
        # Try all patterns
        for pattern in self.patterns:
            match_data = pattern.match(line)
            if match_data:
                pattern.process(match_data, self.game, self.context)
    
    def export_to_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Convert game data to pandas DataFrames"""
        # Table 1: Turn Timeline
        turn_data = []
        for turn in self.game.turns:
            turn_data.append({
                'timestamp': turn.timestamp,
                'turn': turn.turn_number,
                'active_player_id': turn.active_player_id,
                'active_player_name': turn.active_player_name
            })
        df_timeline = pd.DataFrame(turn_data)
        
        # Table 2: Player Stats
        stats_data = []
        for player in self.game.players.values():
            for stats in player.stats_history:
                row = {
                    'turn': stats.turn,
                    'player_id': stats.player_id,
                    'player_name': stats.player_name,
                    'cities': stats.cities,
                    'population': stats.population,
                    'power': stats.power,
                    'tech_percent': stats.tech_percent,
                    'treasury': stats.economics.treasury,
                    'gold_rate': stats.economics.gold_rate,
                    'total_gold_income': stats.economics.total_gold_income,
                    'gold_income_from_self': stats.economics.gold_income_from_self,
                    'gold_from_trade_agreements': stats.economics.gold_from_trade_agreements,
                    'num_units': stats.military.total_units,
                    'total_turns_in_anarchy': stats.total_turns_in_anarchy,
                    'upgrade_budget': stats.economics.upgrade_budget
                }
                
                # Add civic columns
                for category in CivicCategory:
                    civic_name = stats.civics.get_civic(category)
                    row[f'civic_{category.value}'] = civic_name
                
                stats_data.append(row)
        
        df_player_stats = pd.DataFrame(stats_data)
        
        # Table 3: City Data
        city_data = []
        for city in self.game.all_cities.values():
            city_data.append({
                'city_name': city.name,
                'owner_id': city.owner_id,
                'owner_name': city.owner_name,
                'x': city.x,
                'y': city.y,
                'founded_turn': city.founded_turn,
                'current_population': city.population,
                'current_production': city.current_production,
                'threat_level': city.threat_level
            })
        
        df_cities = pd.DataFrame(city_data)
        
        return {
            'turn_timeline': df_timeline,
            'player_stats': df_player_stats,
            'city_data': df_cities
        }


# Usage
def parse_civ4_log(file_path: str) -> tuple[Game, Dict[str, pd.DataFrame]]:
    """Parse a Civ4 log file using OOP approach"""
    parser = Civ4LogParser()
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse
    game = parser.parse_file(content)
    dataframes = parser.export_to_dataframes()
    
    return game, dataframes


game = parse_civ4_log(".\Logs_test_Japon_NormalDLL\BBAI.log")
# This function can be called with the path to the log file to get the game state and dataframes.
# The returned `game` object contains the entire game state, while `dataframes` contains the structured data in pandas DataFrames.

#export dataframes = game.export_to_dataframes()
# This can be used to save or manipulate the data further.
# For example, you can save the dataframes to CSV files or use them for analysis.
# df_timeline.to_csv('turn_timeline.csv', index=False)
# df_player_stats.to_csv('player_stats.csv', index=False)
# df_cities.to_csv('city_data.csv', index=False)
# This allows for easy export and further analysis of the parsed game data.
# The above code provides a structured and object-oriented approach to parsing Civ4 logs, making it
# easier to maintain and extend in the future. Each component is responsible for a specific part of
# the parsing process, and the use of data classes allows for clear and concise representation of game
# entities and statistics. The parser can be easily extended with new patterns or features as needed.   
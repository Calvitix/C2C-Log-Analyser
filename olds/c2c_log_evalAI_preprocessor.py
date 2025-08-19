"""
Civ4 C2C Secondary Log Preprocessor
Processes evaluation logs using timestamp-to-turn mapping from main log
Categories: EvalTech, EvalUnit, EvalCityPlot
"""

import re
from enum import Enum
from typing import Dict, Optional, Tuple, List
import codecs
import bisect


class EvalLogCategory(Enum):
    EVAL_TECH = "EvalTech"
    EVAL_UNIT = "EvalUnit"
    EVAL_CITY_PLOT = "EvalCityPlot"
    UNKNOWN = "Unknown"


class TimestampTurnMapper:
    """Maps timestamps to turns using data from the main log"""
    
    def __init__(self):
        # List of (timestamp, turn, player_id) tuples, sorted by timestamp
        self.timestamp_mappings: List[Tuple[float, int, int]] = []
    
    def load_from_processed_file(self, processed_file_path: str, encoding: str = 'utf-8'):
        """Load timestamp mappings from a processed main log file"""
        timestamp_pattern = re.compile(r'^\[(\d+)\|(-?\d+)\|[^\]]+\]')
        
        with codecs.open(processed_file_path, 'r', encoding=encoding) as f:
            for line in f:
                # Extract turn and player from processed line
                match = timestamp_pattern.match(line)
                if match:
                    turn = int(match.group(1))
                    player_id = int(match.group(2))
                    
                    # Try to find original timestamp in the line
                    # Look for patterns like "Player X setTurnActive for turn Y"
                    if "setTurnActive for turn" in line:
                        # Extract timestamp from original content if preserved
                        # This assumes the preprocessor kept some reference to timestamps
                        # If not, we'll need to read the original file
                        pass
        
        # Sort mappings by timestamp
        self.timestamp_mappings.sort(key=lambda x: x[0])
    
    def load_from_original_file(self, original_file_path: str, encoding: str = 'windows-1252'):
        """Load timestamp mappings directly from the original log file"""
        timestamp_pattern = re.compile(r'^\[(\d+\.\d+)\]')
        turn_pattern = re.compile(r'Player\s+(\d+)\s*\([^)]+\)\s*setTurnActive for turn\s+(\d+)')
        
        current_turn = 0
        current_player = -1
        
        with codecs.open(original_file_path, 'r', encoding=encoding) as f:
            for line in f:
                # Extract timestamp
                timestamp_match = timestamp_pattern.match(line)
                if timestamp_match:
                    timestamp = float(timestamp_match.group(1))
                    
                    # Check for turn change
                    turn_match = turn_pattern.search(line)
                    if turn_match:
                        current_player = int(turn_match.group(1))
                        current_turn = int(turn_match.group(2))
                        
                        # Add mapping
                        self.timestamp_mappings.append((timestamp, current_turn, current_player))
        
        # Sort by timestamp
        self.timestamp_mappings.sort(key=lambda x: x[0])
        
        print(f"Loaded {len(self.timestamp_mappings)} timestamp-turn mappings")
    
    def get_turn_for_timestamp(self, timestamp: float) -> Tuple[int, int]:
        """Get turn and player_id for a given timestamp"""
        if not self.timestamp_mappings:
            return 0, -1
        
        # Use binary search to find the appropriate turn
        timestamps = [t[0] for t in self.timestamp_mappings]
        idx = bisect.bisect_right(timestamps, timestamp) - 1
        
        if idx < 0:
            # Timestamp is before first turn change
            return 0, -1
        
        return self.timestamp_mappings[idx][1], self.timestamp_mappings[idx][2]


class EvalLogPreprocessor:
    """Preprocesses evaluation log files"""
    
    def __init__(self, timestamp_mapper: TimestampTurnMapper):
        self.timestamp_mapper = timestamp_mapper
        
        # Patterns for categorization
        self.patterns = {
            # EvalCityPlot patterns
            'city_plot_patterns': [
                re.compile(r'begin Update City Sites'),
                re.compile(r'end Update City Sites'),
                re.compile(r'Potential best city site'),
                re.compile(r'Found City Site at'),
                re.compile(r'found value is \d+'),
                re.compile(r'player modified value to \d+'),
            ],
            
            # EvalUnit patterns
            'unit_patterns': [
                re.compile(r'AI_bestUnitAI'),
                re.compile(r'evaluate Value for unit'),
                re.compile(r'Better AI Unit found'),
                re.compile(r'AI Unit not chosen'),
                re.compile(r'Taking Better AI Unit'),
                re.compile(r'combat value'),
                re.compile(r'Calculated value'),
                re.compile(r'base value.*final value'),
                re.compile(r'UNITAI_'),
                re.compile(r'as type UNITAI_'),
            ],
            
            # EvalTech patterns
            'tech_patterns': [
                re.compile(r'evaluate TechBuilding'),
                re.compile(r'new mechanism value:'),
                re.compile(r'TechBuilding.*value:'),
            ],
        }
        
        # Extract player ID patterns
        self.player_patterns = {
            'player_id': re.compile(r'(?:Player|AI Player)\s+(\d+)'),
            'city_owner': re.compile(r'City\s+([^,]+)'),  # We'll need to map cities to players
        }
        
        # City to player mapping (will be populated as we process)
        self.city_to_player: Dict[str, int] = {}
    
    def categorize_line(self, line: str) -> EvalLogCategory:
        """Determine the category of a log line"""
        
        # Check EvalCityPlot patterns
        for pattern in self.patterns['city_plot_patterns']:
            if pattern.search(line):
                return EvalLogCategory.EVAL_CITY_PLOT
        
        # Check EvalUnit patterns
        for pattern in self.patterns['unit_patterns']:
            if pattern.search(line):
                return EvalLogCategory.EVAL_UNIT
        
        # Check EvalTech patterns
        for pattern in self.patterns['tech_patterns']:
            if pattern.search(line):
                return EvalLogCategory.EVAL_TECH
        
        return EvalLogCategory.UNKNOWN
    
    def extract_player_id(self, line: str) -> int:
        """Extract player ID from line"""
        # Direct player mention
        player_match = self.player_patterns['player_id'].search(line)
        if player_match:
            return int(player_match.group(1))
        
        # City mention - need to look up owner
        city_match = self.player_patterns['city_owner'].search(line)
        if city_match:
            city_name = city_match.group(1).strip()
            return self.city_to_player.get(city_name, -1)
        
        return -1
    
    def update_city_mapping(self, line: str):
        """Update city to player mapping if we find city ownership info"""
        # Pattern for city founding or ownership
        founding_pattern = re.compile(r'Player\s+(\d+).*?City\s+([^,\s]+)')
        match = founding_pattern.search(line)
        if match:
            player_id = int(match.group(1))
            city_name = match.group(2).strip()
            self.city_to_player[city_name] = player_id
    
    def extract_timestamp(self, line: str) -> Tuple[Optional[float], str]:
        """Extract timestamp and return cleaned line"""
        match = re.match(r'^\[(\d+\.\d+)\]\s*(.*)', line)
        if match:
            timestamp = float(match.group(1))
            cleaned_line = match.group(2)
            return timestamp, cleaned_line
        return None, line
    
    def process_line(self, line: str) -> Optional[str]:
        """Process a single line and return formatted output"""
        if not line.strip():
            return None
        
        # Extract timestamp and clean line
        timestamp, cleaned_line = self.extract_timestamp(line)
        
        if timestamp is None:
            return None
        
        # Get turn and player from timestamp
        turn, active_player = self.timestamp_mapper.get_turn_for_timestamp(timestamp)
        
        # Update city mapping if applicable
        self.update_city_mapping(cleaned_line)
        
        # Try to extract player ID from the line itself
        line_player_id = self.extract_player_id(cleaned_line)
        
        # Use line player ID if found, otherwise use active player
        player_id = line_player_id if line_player_id != -1 else active_player
        
        # Categorize the line
        category = self.categorize_line(cleaned_line)
        
        # Format output: [turn|player_id|category] content
        formatted_line = f"[{turn}|{player_id}|{category.value}] {cleaned_line}"
        
        return formatted_line
    
    def process_file(self, input_file: str, output_file: str, encoding: str = 'windows-1252'):
        """Process entire evaluation log file"""
        processed_lines = []
        line_count = 0
        category_counts = {cat: 0 for cat in EvalLogCategory}
        
        try:
            with codecs.open(input_file, 'r', encoding=encoding) as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        processed = self.process_line(line)
                        if processed:
                            processed_lines.append(processed)
                            line_count += 1
                            
                            # Count categories
                            for cat in EvalLogCategory:
                                if f"|{cat.value}]" in processed:
                                    category_counts[cat] += 1
                                    break
                    except Exception as e:
                        print(f"Error processing line {line_num}: {e}")
                        continue
        
        except UnicodeDecodeError as e:
            print(f"Encoding error: {e}")
            raise
        
        # Write processed file
        with codecs.open(output_file, 'w', encoding='utf-8') as f:
            for line in processed_lines:
                f.write(line + '\n')
        
        return {
            'total_lines': line_count,
            'category_counts': category_counts,
            'city_mappings': len(self.city_to_player)
        }


def process_eval_log(main_log_file: str, eval_log_file: str, output_file: str, 
                     main_encoding: str = 'windows-1252', eval_encoding: str = 'windows-1252'):
    """Process evaluation log using timestamp mappings from main log"""
    
    print("Step 1: Loading timestamp mappings from main log...")
    mapper = TimestampTurnMapper()
    mapper.load_from_original_file(main_log_file, main_encoding)
    
    print("\nStep 2: Processing evaluation log...")
    preprocessor = EvalLogPreprocessor(mapper)
    stats = preprocessor.process_file(eval_log_file, output_file, eval_encoding)
    
    print(f"\nProcessing complete!")
    print(f"Output written to: {output_file}")
    print(f"\nStatistics:")
    print(f"- Total lines processed: {stats['total_lines']}")
    print(f"- City mappings found: {stats['city_mappings']}")
    print(f"\nCategory breakdown:")
    for category, count in stats['category_counts'].items():
        percentage = (count / stats['total_lines'] * 100) if stats['total_lines'] > 0 else 0
        print(f"  - {category.value}: {count} lines ({percentage:.1f}%)")


def preview_processed_eval_log(eval_log_file: str, main_log_file: str, 
                              num_lines: int = 50, encoding: str = 'windows-1252'):
    """Preview processed evaluation log"""
    # Load mappings
    mapper = TimestampTurnMapper()
    mapper.load_from_original_file(main_log_file, encoding)
    
    # Create preprocessor
    preprocessor = EvalLogPreprocessor(mapper)
    
    print(f"Preview of first {num_lines} processed lines:\n")
    count = 0
    
    try:
        with codecs.open(eval_log_file, 'r', encoding=encoding) as f:
            for line in f:
                processed = preprocessor.process_line(line)
                if processed and count < num_lines:
                    print(processed)
                    count += 1
                elif count >= num_lines:
                    break
    except Exception as e:
        print(f"Error reading file: {e}")


# Combined processing function
def process_both_logs(main_log: str, eval_log: str, 
                     main_output: str = "main_processed.log",
                     eval_output: str = "eval_processed.log",
                     encoding: str = 'windows-1252'):
    """Process both main and evaluation logs"""
    
    print("=== Processing Main Log ===")
    from c2c_log_preprocessor import preprocess_civ4_log  # Import the first script
    preprocess_civ4_log(main_log, main_output, encoding)
    
    print("\n=== Processing Evaluation Log ===")
    process_eval_log(main_log, eval_log, eval_output, encoding, encoding)
    
    print("\n=== Processing Complete ===")
    print(f"Main log processed: {main_output}")
    print(f"Eval log processed: {eval_output}")


if __name__ == "__main__":
    # Example usage
    main_log_file = ".\\Logs_test_Japon_NormalDLL\\BBAI.log"
    eval_log_file = ".\\Logs_test_Japon_NormalDLL\\AiEvaluation.log"
    output_file = "civ4_eval_processed.log"
    
    # Process evaluation log
    process_eval_log(main_log_file, eval_log_file, output_file)
    
    # Preview results
    preview_processed_eval_log(eval_log_file, main_log_file, 30)
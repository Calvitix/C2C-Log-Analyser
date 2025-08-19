"""
Civ4 C2C Log Preprocessor - Enhanced Version
Transforms raw log lines into structured format:
[turn_number|player_id|category] original_line_without_timestamp
"""

import re
from enum import Enum
from typing import Optional, Tuple
import codecs


class LogCategory(Enum):
    EMPIRE = "Empire"
    TEAM = "Team"
    CITY = "City"
    UNIT = "Unit"
    TECH = "Tech"
    UNKNOWN = "Unknown"


class LogPreprocessor:
    """Preprocesses Civ4 log files to add structure"""
    
    def __init__(self):
        # State tracking - persistent across lines
        self.current_turn = 0  # Start at 0, not -1
        self.active_player_id = -1  # -1 means no player active yet
        self.active_player_name = ""
        
        # Patterns for line categorization
        self.patterns = {
            # Turn change pattern
            'turn_change': re.compile(r'Player\s+(\d+)\s*\(([^)]+)\)\s*setTurnActive for turn\s+(\d+)'),

            'player_change': re.compile(r'Player\s+\d+\s*'), #\(([^)]+)\)\s*get message : Player\s+(\d+)\s*\(([^)]+)\)\s*has changed'),

            # Empire/Team patterns
            'empire_patterns': [
                re.compile(r'Player\s+\d+.*has\s+\d+\s+cities'),
                re.compile(r'setTurnActive'),
                re.compile(r'gold rate'),
                re.compile(r'treasury'),
                re.compile(r'tech percent'),
                re.compile(r'needs\s+\d+\s+Workers'),
                re.compile(r'have\s+\d+\s+City Sites'),
                re.compile(r'get message'),
                re.compile(r'Team\s+\d+'),
                re.compile(r'estimating warplan'),
                re.compile(r'at war with'),
                re.compile(r'has met:'),
                re.compile(r'Begin best tech evaluation'),
                re.compile(r'Enemy power perc'),
                # New patterns from the example
                re.compile(r'stats for turn'),
                re.compile(r'Gold rate:'),
                re.compile(r'Science rate:'),
                re.compile(r'Culture rate:'),
                re.compile(r'Espionage rate:'),
                re.compile(r'Treasury:'),
                re.compile(r'Total gold income'),
                re.compile(r'Num units:'),
                re.compile(r'Num selection groups:'),
                re.compile(r'Unit Upkeep'),
                re.compile(r'Unit supply cost'),
                re.compile(r'Maintenance cost'),
                re.compile(r'Civic upkeep cost'),
                re.compile(r'Corporate maintenance'),
                re.compile(r'Inflation effect:'),
                re.compile(r'Is in financial difficulties:'),
                re.compile(r'Total science output:'),
                re.compile(r'Total espionage output:'),
                re.compile(r'Total cultural output:'),
                re.compile(r'Total population:'),
                re.compile(r'Total food output:'),
                re.compile(r'Total production output:'),
                re.compile(r'Num cities:'),
                re.compile(r'National rev index:'),
                re.compile(r'Number of barbarian units killed:'),
                re.compile(r'Number of animals subdued:'),
                re.compile(r'Civic switches:'),
                re.compile(r'Total num civics switched:'),
                re.compile(r'Total turns in anarchy:'),
                re.compile(r'Current civics:'),
                re.compile(r'Gouvernement:'),
                re.compile(r'Règles:'),
                re.compile(r'Pouvoir:'),
                re.compile(r'Militaire:'),
                re.compile(r'Religion:'),
                re.compile(r'Société:'),
                re.compile(r'Economie:'),
                re.compile(r'Bien-être:'),
                re.compile(r'Monnaie:'),
                re.compile(r'Travail:'),
                re.compile(r'Education:'),
                re.compile(r'Langue:'),
                re.compile(r'Immigration:'),
                re.compile(r'Agriculture:'),
                re.compile(r'Traitement des déchets:'),
                re.compile(r'Civic switch history:'),
                re.compile(r'No switches made'),
                re.compile(r'trade calc'),
                re.compile(r'calculates upgrade budget'),
            ],
            
            # City patterns
            'city_patterns': [
                re.compile(r'City\s+[^,]+'),
                re.compile(r'city:\s+[^,]+'),
                re.compile(r'founds new city'),
                re.compile(r'Fondation de'),
                re.compile(r'pushes production'),
                re.compile(r'has threat level'),
                re.compile(r'requests\s+\d+\s+floating defender'),
                re.compile(r'Considering new production'),
                re.compile(r'CalculateAllBuildingValues'),
                re.compile(r'base value for'),
                re.compile(r'final value'),
                re.compile(r'evaluating recent hunter deaths'),
                re.compile(r'puts out tenders'),
                re.compile(r'Calc value for'),
                # New patterns from the example
                re.compile(r'Player\s+\d+.*-\s+[^(]+\(pop\s+\d+\)'),
                re.compile(r'Area workers'),
                re.compile(r'workers assigned to city'),
                re.compile(r'iNumSettlers'),
                re.compile(r'iMaxSettlers'),
                re.compile(r'Population:'),
                re.compile(r'Production:'),
                re.compile(r'Food surplus:'),
                re.compile(r'Local rev index:'),
                re.compile(r'Maintenance:'),
                re.compile(r'Income:'),
                re.compile(r'Science:'),
                re.compile(r'Espionage:'),
                re.compile(r'Culture:'),
                re.compile(r'Net happyness:'),
                re.compile(r'Net health:'),
                re.compile(r'Food trade yield:'),
                re.compile(r'Production trade yield:'),
                re.compile(r'Commerce trade yield:'),
                re.compile(r'Properties:'),
                re.compile(r'Criminalité: value'),
                re.compile(r'Maladie: value'),
                re.compile(r'Education: value'),
                re.compile(r'Pollution de L\'eau: value'),
                re.compile(r'Pollution de L\'air: value'),
                re.compile(r'PropertyBuildings:'),
            ],
            
            # Unit patterns
            'unit_patterns': [
                re.compile(r'AI_bestUnitAI'),
                re.compile(r'evaluate Value for unit'),
                re.compile(r'Better AI Unit found'),
                re.compile(r'AI Unit not chosen'),
                re.compile(r'Taking Better AI Unit'),
                re.compile(r'UNITAI_'),
                re.compile(r'combat value'),
                re.compile(r'unit strength'),
                re.compile(r'num units'),
                re.compile(r'military units'),
                re.compile(r'worker units'),
                # New patterns from the example
                re.compile(r'Units:'),
                re.compile(r'Lanceur de Pierres'),
                re.compile(r'Gardien Tribal'),
                re.compile(r'\(UNITAI_[^)]+\):\s*\d+'),
            ],
            
            # Tech patterns
            'tech_patterns': [
                re.compile(r'calculate value for tech'),
                re.compile(r'raw value for tech'),
                re.compile(r'evaluating buildings for tech'),
                re.compile(r'Building.*new mechanism value'),
                re.compile(r'tech.*cost.*value'),
                re.compile(r'Evaluated tech path'),
                re.compile(r'Civic.*base value'),
                re.compile(r'enabled civic'),
                re.compile(r'Misc value:'),
                re.compile(r'Corporation value:'),
                re.compile(r'Promotion value:'),
                re.compile(r'Tile improvement value:'),
                re.compile(r'Build value:'),
                re.compile(r'Bonus reveal value:'),
                re.compile(r'Unit value:'),
                re.compile(r'Building value:'),
                re.compile(r'additional tech value'),
                re.compile(r'Beelining'),
                re.compile(r'Non-beeline tech choice'),
                re.compile(r'Free on first discovery'),
                # New patterns from the example
                re.compile(r'Evaluate tech path value:'),
                re.compile(r'selects tech'),
                re.compile(r'Best tech for player'),
                re.compile(r'Best tech for team'),
                re.compile(r'Best tech for empire'),
                re.compile(r'Best tech for city'),
                re.compile(r'Best tech for unit'),
                re.compile(r'Best tech for building'),                
                re.compile(r'Civic.*modifier'),
                re.compile(r'Civic.*enables building'),
                re.compile(r'Civic.*disables building'),
                re.compile(r'Civic.*commerce value'),
                re.compile(r'Civic.*health value'),
                re.compile(r'Civic.*yield value'),
                re.compile(r'Civic.*food production value'),
                re.compile(r'Civic.*share value'),
                
                
                re.compile(r'Civic.*upkeep modifier'),
            ],
        }
    
    def categorize_line(self, line: str) -> LogCategory:
        """Determine the category of a log line"""
        
        # Check Empire/Team patterns first
        for pattern in self.patterns['empire_patterns']:
            if pattern.search(line):
                # Distinguish between Empire and Team
                if 'Team' in line:
                    return LogCategory.TEAM
                return LogCategory.EMPIRE
        
        # Check City patterns
        for pattern in self.patterns['city_patterns']:
            if pattern.search(line):
                return LogCategory.CITY
        
        # Check Unit patterns
        for pattern in self.patterns['unit_patterns']:
            if pattern.search(line):
                return LogCategory.UNIT
        
        # Check Tech patterns
        for pattern in self.patterns['tech_patterns']:
            if pattern.search(line):
                return LogCategory.TECH
        
        # Default to Unknown
        return LogCategory.UNKNOWN
    
    def extract_timestamp(self, line: str) -> Tuple[Optional[float], str]:
        """Extract timestamp and return cleaned line"""
        match = re.match(r'^\[(\d+\.\d+)\]\s*(.*)', line)
        if match:
            timestamp = float(match.group(1))
            cleaned_line = match.group(2)
            return timestamp, cleaned_line
        return None, line
    
    def check_turn_change(self, line: str) -> bool:
        """Check if line indicates a turn change and update state"""
        match = self.patterns['turn_change'].search(line)
        if match:
            self.active_player_id = int(match.group(1))
            self.active_player_name = match.group(2)
            self.current_turn = int(match.group(3))
            return True
        return False
    
    def check_player_change(self, line: str) -> bool:
        """Check if line indicates a change of player and update state"""
        match = self.patterns['player_change'].search(line)
        if match:
            self.active_player_id = int(match.group(1))
            self.active_player_name = match.group(2)
            //self.current_turn = int(match.group(3))
            return True
        return False    
    
    def process_line(self, line: str) -> Optional[str]:
        """Process a single line and return formatted output"""
        if not line.strip():
            return None
        
        # Extract timestamp and clean line
        timestamp, cleaned_line = self.extract_timestamp(line)
        
        # Check for turn change - this updates state if found
        self.check_turn_change(cleaned_line)

        self.check_player_change(cleaned_line)
        
        # Categorize the line
        category = self.categorize_line(cleaned_line)
        
        # Format output: [turn|player_id|category] content
        # Using current state (which persists from previous lines if not updated)
        formatted_line = f"[{self.current_turn}|{self.active_player_id}|{category.value}] {cleaned_line}"
        
        return formatted_line
    
    def process_file(self, input_file: str, output_file: str, encoding: str = 'windows-1252'):
        """
        Process entire log file
        Default encoding is windows-1252 (ANSI)
        """
        processed_lines = []
        line_count = 0
        category_counts = {cat: 0 for cat in LogCategory}
        
        # Read and process file with ANSI encoding
        try:
            with codecs.open(input_file, 'r', encoding=encoding) as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        processed = self.process_line(line)
                        if processed:
                            processed_lines.append(processed)
                            line_count += 1
                            
                            # Count categories for statistics
                            for cat in LogCategory:
                                if f"|{cat.value}]" in processed:
                                    category_counts[cat] += 1
                                    break
                    except Exception as e:
                        print(f"Error processing line {line_num}: {e}")
                        continue
        
        except UnicodeDecodeError as e:
            print(f"Encoding error: {e}")
            print("Try using a different encoding (e.g., 'cp1252', 'iso-8859-1', 'utf-8')")
            raise
        
        # Write processed file in UTF-8 for better compatibility
        with codecs.open(output_file, 'w', encoding='utf-8') as f:
            for line in processed_lines:
                f.write(line + '\n')
        
        # Return statistics
        return {
            'total_lines': line_count,
            'category_counts': category_counts,
            'turns_found': self.current_turn + 1,
            'last_active_player': f"{self.active_player_name} (ID: {self.active_player_id})" if self.active_player_id != -1 else "None"
        }
    
    def process_file_to_dataframe(self, input_file: str, encoding: str = 'windows-1252') -> 'pd.DataFrame':
        """Process file and return a DataFrame for easy analysis"""
        import pandas as pd
        
        data = []
        
        with codecs.open(input_file, 'r', encoding=encoding) as f:
            for line_num, line in enumerate(f, 1):
                try:
                    processed = self.process_line(line)
                    if processed:
                        # Parse the formatted line
                        match = re.match(r'\[(\d+)\|(-?\d+)\|(\w+)\]\s*(.*)', processed)
                        if match:
                            data.append({
                                'line_number': line_num,
                                'turn': int(match.group(1)),
                                'player_id': int(match.group(2)),
                                'category': match.group(3),
                                'content': match.group(4)
                            })
                except Exception as e:
                    print(f"Error processing line {line_num}: {e}")
                    continue
        
        return pd.DataFrame(data)


# Usage functions remain the same
def preprocess_civ4_log(input_file: str, output_file: str, encoding: str = 'windows-1252'):
    """Main function to preprocess a Civ4 log file"""
    preprocessor = LogPreprocessor()
    
    print(f"Processing {input_file} with {encoding} encoding...")
    
    try:
        stats = preprocessor.process_file(input_file, output_file, encoding)
        
        print(f"\nProcessing complete!")
        print(f"Output written to: {output_file}")
        print(f"\nStatistics:")
        print(f"- Total lines processed: {stats['total_lines']}")
        print(f"- Turns found: {stats['turns_found']}")
        print(f"- Last active player: {stats['last_active_player']}")
        print(f"\nCategory breakdown:")
        for category, count in stats['category_counts'].items():
            percentage = (count / stats['total_lines'] * 100) if stats['total_lines'] > 0 else 0
            print(f"  - {category.value}: {count} lines ({percentage:.1f}%)")
            
    except Exception as e:
        print(f"Error during processing: {e}")
        raise


def preview_processed_log(input_file: str, num_lines: int = 50, encoding: str = 'windows-1252'):
    """Preview the first N lines of processed output"""
    preprocessor = LogPreprocessor()
    
    print(f"Preview of first {num_lines} processed lines:\n")
    count = 0
    
    try:
        with codecs.open(input_file, 'r', encoding=encoding) as f:
            for line in f:
                processed = preprocessor.process_line(line)
                if processed and count < num_lines:
                    print(processed)
                    count += 1
                elif count >= num_lines:
                    break
    except Exception as e:
        print(f"Error reading file: {e}")


if __name__ == "__main__":
    # Example usage
    input_log = ".\\Logs_test_Japon_NormalDLL\\BBAI.log"
    output_log = ".\\output\\BBAI_processed.log"

      
    # Ensure output directory exists
    import os
    os.makedirs(os.path.dirname(output_log), exist_ok=True)
    # Check if input file exists
    if not os.path.isfile(input_log):
        print(f"Input file {input_log} does not exist.")
        exit(1)
    # Ensure the input file is readable
    if not os.access(input_log, os.R_OK):
        print(f"Input file {input_log} is not readable.")
        exit(1)
    # Ensure the output file is writable
    if not os.access(os.path.dirname(output_log), os.W_OK):
        print(f"Output directory {os.path.dirname(output_log)} is not writable.")
        exit(1)
    
    # Print initial message
    print(f"Starting preprocessing of {input_log}...")
    print(f"Output will be saved to {output_log}\n")

    # Option 1: Process with specific encoding
    preprocess_civ4_log(input_log, output_log, encoding='windows-1252')
    
    # Option 2: Process with auto-detected encoding
    # process_with_auto_encoding(input_log, output_log)
    
    # Preview results
    preview_processed_log(input_log, 30)


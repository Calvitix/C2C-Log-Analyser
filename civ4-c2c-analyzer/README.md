# Civ4 C2C Analyzer

## Overview
The Civ4 C2C Analyzer is a Streamlit application designed to visualize and analyze game data from Civilization IV: Caveman 2 Cosmos (C2C) mod. It provides insights into player statistics, city management, turn timings, and more through interactive visualizations.

## Features
- **Overview Dashboard**: Displays general game metrics and statistics.
- **Player Analysis**: Detailed statistics and visualizations for individual players.
- **City Analysis**: Insights into city locations, populations, and historical data.
- **Turn Timings**: Analysis of turn durations and efficiency.
- **Comparative Analysis**: Compare players based on various metrics.
- **Rankings**: Display rankings and achievements of players.
- **Score Analysis**: Evaluate player scores and performance metrics.
- **Military Units**: Analyze military units and their effectiveness.
- **Unit Evaluation**: Assess units based on various criteria.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/civ4-c2c-analyzer.git
   ```
2. Navigate to the project directory:
   ```
   cd civ4-c2c-analyzer
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
streamlit run src/app.py
```
This will start the Streamlit server and open the application in your default web browser.

## Directory Structure
```
civ4-c2c-analyzer
├── src
│   ├── app.py                # Main entry point of the application
│   ├── config.py             # Configuration settings
│   ├── data                   # Data loading and preparation
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── prepare.py
│   ├── views                  # Different views for analysis
│   │   ├── __init__.py
│   │   ├── overview.py
│   │   ├── players.py
│   │   ├── cities.py
│   │   ├── timings.py
│   │   ├── comparative.py
│   │   ├── rankings.py
│   │   ├── score.py
│   │   ├── military.py
│   │   └── units.py
│   └── utils                  # Utility functions
│       ├── __init__.py
│       └── plot.py
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
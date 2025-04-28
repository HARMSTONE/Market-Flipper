# Albion Market Analyzer

A PyQt5 application for Albion Online that helps players analyze market prices and track gold trends.

## Features
- Market flipping analysis between cities
- Gold price tracking with historical charts
- Multi-region support (Europe, America, Asia)
- Automatic data refreshing every 5 minutes
- Customizable alert sounds

## Requirements
- Python 3.7+
- PyQt5
- matplotlib
- requests
- python-dateutil
- numpy

## Installation
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Run: `python albion_market_analyzer.py`

## Usage
1. Select your server region on startup
2. Use the Market Flipping tab to compare prices between cities
3. Check the Gold Tracker tab for price trends and recommendations

Note: Requires logo.png, Market_Flipper.png, and gold_sound.mp3 in the same directory
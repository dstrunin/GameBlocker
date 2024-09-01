# Game Blocker

A Python script to track and limit daily game playtime.

## Features

- Tracks hours and minutes played per day
- Shuts down the game when daily limit is reached
- Provides sound notifications:
  - 20 minutes before shutdown
  - 5 minutes before shutdown

## Usage

1. Set your daily time limit in the script
2. Run the script before starting your game
3. The script will monitor playtime and enforce the limit

## Requirements

- Python 3.x
- [Additional dependencies, if any]

## Setup

1. Clone the repository
2. Install required dependencies: `pip install -r requirements.txt`
3. Configure game executable path and time limit in `config.py`

## Running the Script

1. Run the script: `python game_blocker.py`
2. The script will start monitoring playtime
3. If the daily limit is reached, the game will be automatically shut down

## Configuration

- `game_path`: Path to the game executable
- `daily_limit`: Daily playtime limit (hours)

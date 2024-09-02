# Game Blocker

Game Blocker is a Python application that helps users manage their gaming time by setting daily time limits for specified games.

## Features

- Set daily time limits for gaming
- Track multiple games
- Visual progress bar showing time used
- Sound notifications when approaching the time limit
- Automatically closes games when the time limit is reached
- Persists time limits and usage across application restarts

## Requirements

- Windows 10 (for .exe version)
- Python 3.x (for running from source)
- tkinter (usually comes pre-installed with Python)
- psutil

## Installation

### Option 1: Executable Version (Windows only)

1. Download the 'game_blocker_windows_exe.zip' file and extract anywhere. Double click on the 'game_blocker.exe' file to run the application.
2. No installation required - the .exe file can be run directly.

### Option 2: Running from Source

1. Clone this repository or download the source code.
2. Install the required dependencies:

   ```bash
   pip install psutil
   ```

## Usage

### Option 1: Running the Executable (Windows only)

1. Double-click the `game_blocker.exe` file to run the application.
2. When first launched, you'll be prompted to set a daily time limit.
3. Use the "Add Game" button to select executable files of games you want to track.
4. The application will monitor the specified games and track your playing time.
5. When your daily limit is reached, the application will automatically close the game.

### Option 2: Running from Source

1. Run the application:

   ```bash
   python game_blocker.py
   ```

2. Follow steps 2-5 from Option 1.

## How it works

- The application monitors running processes to detect when tracked games are running.
- It accumulates the time spent playing these games.
- Sound notifications are played when approaching the time limit (in the last 15 seconds).
- The progress bar and time display update in real-time to show remaining time.
- Game processes are forcefully terminated when the time limit is reached.

## Notes

- The application saves your time limit and game list, so you don't need to re-enter this information every time you start the program.
- The time limit resets at midnight each day.
- You can modify the time limit by closing and reopening the application (it will prompt for a new limit if it's a new day).
- This application has been tested on Windows 10 only. Compatibility with other operating systems is not guaranteed.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the issues page if you want to contribute.

## License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).
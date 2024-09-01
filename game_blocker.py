import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import json
import time
import psutil
import winsound
from datetime import datetime, timedelta
import os
import threading
import logging
import sys

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Sound notifications for the last 15 seconds
NOTIFICATION_SOUNDS = {
    15: 500,  # frequency in Hz
    10: 1000,
    5: 1500,
    1: 2000
}

class GameBlockerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Game Blocker")
        master.geometry("400x500")  # Set initial window size

        # Set up the close window protocol
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize total_time_used
        self.total_time_used = 0

        # Load or ask for time limit before creating the main window
        self.load_or_ask_time_limit()

        # Add padding around the main frame
        main_frame = ttk.Frame(master, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.exe_listbox = tk.Listbox(main_frame, width=50, height=10)
        self.exe_listbox.pack(pady=10)

        ttk.Button(main_frame, text="Add Game", command=self.add_game).pack(pady=5)
        ttk.Button(main_frame, text="Remove Game", command=self.remove_game).pack(pady=5)

        ttk.Label(main_frame, text=f"Daily Time Limit: {self.hours:02d}:{self.minutes:02d}").pack(pady=5)

        self.status_text = tk.StringVar()
        self.status_text.set("Monitoring started")
        ttk.Label(main_frame, textvariable=self.status_text).pack(pady=5)

        self.time_left_text = tk.StringVar()
        self.time_left_text.set(f"Time left: {self.hours:02d}:{self.minutes:02d}")
        ttk.Label(main_frame, textvariable=self.time_left_text, font=("Arial", 16, "bold")).pack(pady=10)

        self.progress = ttk.Progressbar(main_frame, length=300, mode='determinate')
        self.progress.pack(pady=10)

        self.monitoring = False
        self.monitor_thread = None
        self.last_reset = datetime.now().date()

        self.load_games()
        self.start_monitoring()

    def load_or_ask_time_limit(self):
        try:
            with open("time_limit.json", "r") as f:
                data = json.load(f)
                saved_date = datetime.strptime(data['date'], "%Y-%m-%d").date()
                if saved_date == datetime.now().date():
                    self.hours = data['hours']
                    self.minutes = data['minutes']
                    self.total_time_used = data.get('total_time_used', 0)  # Use get() with default value
                else:
                    self.ask_time_limit()
                    self.total_time_used = 0
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            self.ask_time_limit()
            self.total_time_used = 0

    def ask_time_limit(self):
        class TimeDialog(simpledialog.Dialog):
            def body(self, master):
                tk.Label(master, text="Hours:").grid(row=0)
                tk.Label(master, text="Minutes:").grid(row=1)
                self.hours_entry = tk.Entry(master)
                self.minutes_entry = tk.Entry(master)
                self.hours_entry.grid(row=0, column=1)
                self.minutes_entry.grid(row=1, column=1)
                self.hours_entry.insert(0, "2")  # Default value
                self.minutes_entry.insert(0, "0")  # Default value
                return self.hours_entry  # Initial focus

            def validate(self):
                try:
                    self.hours = int(self.hours_entry.get())
                    self.minutes = int(self.minutes_entry.get())
                    if 0 <= self.hours <= 23 and 0 <= self.minutes <= 59:
                        return True
                    else:
                        messagebox.showerror("Invalid Input", "Hours must be 0-23 and minutes 0-59.")
                        return False
                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter valid numbers.")
                    return False

            def apply(self):
                self.result = (self.hours, self.minutes)

        dialog = TimeDialog(self.master, "Set Daily Time Limit")
        if dialog.result:
            self.hours, self.minutes = dialog.result
        else:
            self.hours, self.minutes = 2, 0  # Default values if dialog is cancelled

        self.total_time_used = 0  # Reset total_time_used when asking for a new limit
        self.save_time_limit()

    def save_time_limit(self):
        data = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'hours': self.hours,
            'minutes': self.minutes,
            'total_time_used': self.total_time_used
        }
        with open("time_limit.json", "w") as f:
            json.dump(data, f)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.save_time_limit()
            self.stop_monitoring()
            self.master.destroy()
            sys.exit()

    def add_game(self):
        file_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
        if file_path and file_path not in self.exe_listbox.get(0, tk.END):
            self.exe_listbox.insert(tk.END, file_path)
            self.save_games()

    def remove_game(self):
        selected = self.exe_listbox.curselection()
        if selected:
            self.exe_listbox.delete(selected)
            self.save_games()

    def save_games(self):
        games = list(self.exe_listbox.get(0, tk.END))
        with open("games.json", "w") as f:
            json.dump(games, f)

    def load_games(self):
        try:
            with open("games.json", "r") as f:
                games = json.load(f)
                for game in games:
                    self.exe_listbox.insert(tk.END, game)
        except FileNotFoundError:
            pass

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_games)
            self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)  # Wait for the thread to finish
        self.status_text.set("Monitoring stopped")
        self.progress['value'] = 0

    def monitor_games(self):
        daily_limit = (self.hours * 3600) + (self.minutes * 60)  # Convert to seconds
        executables = list(self.exe_listbox.get(0, tk.END))
        last_check = datetime.now()

        logging.info(f"Starting monitoring with executables: {executables}")

        while self.monitoring:
            try:
                current_time = datetime.now()

                # Reset timer if it's a new day
                if current_time.date() != self.last_reset:
                    self.total_time_used = 0
                    self.last_reset = current_time.date()
                    logging.info("Daily timer reset")
                    self.load_or_ask_time_limit()  # Ask for new time limit on a new day
                    daily_limit = (self.hours * 3600) + (self.minutes * 60)  # Update daily limit

                game_process = self.get_game_process(executables)
                
                if game_process:
                    logging.info(f"Game detected: {game_process.name()}")
                    elapsed = (current_time - last_check).total_seconds()
                    self.total_time_used += elapsed
                    remaining_time = max(0, daily_limit - self.total_time_used)

                    if remaining_time <= 0:
                        self.status_text.set("Time limit reached. Shutting down the game.")
                        game_process.terminate()
                        break

                    self.status_text.set(f"Game running: {game_process.name()}")

                    # Play notifications only in the last 15 seconds
                    if remaining_time <= 15:
                        self.play_notification(int(remaining_time))
                else:
                    remaining_time = daily_limit - self.total_time_used
                    self.status_text.set("No tracked game running")

                minutes_left = int(remaining_time / 60)
                seconds_left = int(remaining_time % 60)
                self.time_left_text.set(f"Time left: {minutes_left:02d}:{seconds_left:02d}")
                self.progress['value'] = (self.total_time_used / daily_limit) * 100

                last_check = current_time
                time.sleep(1)  # Check every second
            except Exception as e:
                logging.error(f"Error in monitor_games: {str(e)}")
                time.sleep(5)  # Wait a bit longer if there's an error

    def get_game_process(self, executables):
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                proc_exe = proc.info['exe']
                if proc_exe:
                    if proc_exe in executables:
                        return proc
                    # Check if the executable name (without path) matches
                    proc_name = os.path.basename(proc_exe).lower()
                    if proc_name in [os.path.basename(exe).lower() for exe in executables]:
                        return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, TypeError) as e:
                logging.debug(f"Error checking process {proc.pid}: {str(e)}")
        return None

    def play_notification(self, seconds_left):
        for time, frequency in NOTIFICATION_SOUNDS.items():
            if seconds_left == time:
                winsound.Beep(frequency, 200)  # 200ms duration for each beep
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = GameBlockerGUI(root)
    root.mainloop()

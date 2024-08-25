import tkinter as tk
from tkinter import messagebox


def get_user_input():
    global league_url, match_format, sleep_time
    league_url = entry_league_url.get()
    match_format = entry_match_format.get()
    sleep_time = entry_sleep_time.get()

    if not league_url or not match_format or not sleep_time:
        messagebox.showerror("error", "empty values")
        return

    root.destroy()


def show_input_window():
    global root, entry_league_url, entry_match_format, entry_sleep_time
    global league_url, match_format, sleep_time

    league_url = None
    match_format = None
    sleep_time = None

    root = tk.Tk()
    root.title("entering")

    tk.Label(root, text="league URL:").grid(row=0, column=0, padx=10, pady=10)
    entry_league_url = tk.Entry(root, width=50)
    entry_league_url.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="match format:").grid(row=1, column=0, padx=10, pady=10)
    entry_match_format = tk.Entry(root, width=50)
    entry_match_format.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="time to sleep (sec):").grid(row=2, column=0, padx=10, pady=10)
    entry_sleep_time = tk.Entry(root, width=50)
    entry_sleep_time.grid(row=2, column=1, padx=10, pady=10)

    submit_button = tk.Button(root, text="start", command=get_user_input)
    submit_button.grid(row=3, column=0, columnspan=2, pady=10)

    root.mainloop()

    return league_url, match_format, sleep_time


if __name__ == "__main__":
    league_url, match_format, sleep_time = show_input_window()
    if league_url and match_format and sleep_time:
        print(f"League URL: {league_url}")
        print(f"Match format (1, 2 ,3) {match_format}")
        print(f"Time to sleep (sec): {sleep_time}")
    else:
        print("empty values")

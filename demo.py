import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import pygame


AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}


class MusicPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Music Player")
        self.root.geometry("720x460")
        self.root.minsize(600, 380)

        self.current_folder = None
        self.songs = []
        self.is_paused = False

        pygame.init()
        pygame.mixer.init()

        self.folder_text = tk.StringVar(value="No folder selected")
        self.song_text = tk.StringVar(value="Choose a music folder to begin")
        self.status_text = tk.StringVar(value="Ready")

        self.configure_styles()
        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def configure_styles(self):
        self.root.configure(bg="#101418")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#101418")
        style.configure("Header.TFrame", background="#151b22")
        style.configure("TLabel", background="#101418", foreground="#e8edf2")
        style.configure("Muted.TLabel", foreground="#9aa7b2")
        style.configure("Title.TLabel", font=("Helvetica", 22, "bold"))
        style.configure("Now.TLabel", font=("Helvetica", 13, "bold"))
        style.configure("TButton", font=("Helvetica", 11), padding=(12, 8))
        style.map("TButton", background=[("active", "#26313c")])

    def build_ui(self):
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(22, 18))
        header.pack(fill="x")

        title = ttk.Label(
            header,
            text="My Music Player",
            style="Title.TLabel",
            background="#151b22",
        )
        title.pack(anchor="w")

        folder_label = ttk.Label(
            header,
            textvariable=self.folder_text,
            style="Muted.TLabel",
            background="#151b22",
        )
        folder_label.pack(anchor="w", pady=(6, 0))

        body = ttk.Frame(self.root, padding=22)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(body)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        ttk.Button(toolbar, text="Choose Folder", command=self.choose_folder).pack(
            side="left"
        )
        ttk.Button(toolbar, text="Play", command=self.play_selected).pack(
            side="left", padx=(10, 0)
        )
        ttk.Button(toolbar, text="Pause", command=self.pause).pack(
            side="left", padx=(10, 0)
        )
        ttk.Button(toolbar, text="Resume", command=self.resume).pack(
            side="left", padx=(10, 0)
        )
        ttk.Button(toolbar, text="Stop", command=self.stop).pack(side="left", padx=(10, 0))

        list_frame = ttk.Frame(body)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.playlist = tk.Listbox(
            list_frame,
            bg="#151b22",
            fg="#e8edf2",
            selectbackground="#2f7dd1",
            selectforeground="#ffffff",
            activestyle="none",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#2a333d",
            highlightcolor="#2f7dd1",
            font=("Helvetica", 12),
        )
        self.playlist.grid(row=0, column=0, sticky="nsew")
        self.playlist.bind("<Double-Button-1>", lambda event: self.play_selected())

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.playlist.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.playlist.configure(yscrollcommand=scrollbar.set)

        footer = ttk.Frame(body)
        footer.grid(row=2, column=0, sticky="ew", pady=(16, 0))

        ttk.Label(footer, textvariable=self.song_text, style="Now.TLabel").pack(anchor="w")
        ttk.Label(footer, textvariable=self.status_text, style="Muted.TLabel").pack(
            anchor="w", pady=(4, 0)
        )

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Choose your music folder")
        if not folder:
            return

        self.current_folder = Path(folder)
        self.folder_text.set(str(self.current_folder))
        self.load_songs()

    def load_songs(self):
        self.stop()
        self.playlist.delete(0, tk.END)

        self.songs = sorted(
            [
                path
                for path in self.current_folder.iterdir()
                if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
            ],
            key=lambda path: path.name.lower(),
        )

        for song in self.songs:
            self.playlist.insert(tk.END, song.name)

        if self.songs:
            self.playlist.selection_set(0)
            self.song_text.set("Select a song and press Play")
            self.status_text.set(f"{len(self.songs)} songs loaded")
        else:
            self.song_text.set("No supported audio files found")
            self.status_text.set("Use MP3, WAV, OGG, FLAC, or M4A files")

    def selected_song(self):
        selection = self.playlist.curselection()
        if not selection:
            return None
        return self.songs[selection[0]]

    def play_selected(self):
        song = self.selected_song()
        if song is None:
            messagebox.showinfo("No song selected", "Choose a folder and select a song.")
            return

        try:
            pygame.mixer.music.load(str(song))
            pygame.mixer.music.play()
        except pygame.error as error:
            messagebox.showerror("Playback error", str(error))
            self.status_text.set("Could not play this file")
            return

        self.is_paused = False
        self.song_text.set(song.name)
        self.status_text.set("Playing")

    def pause(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True
            self.status_text.set("Paused")

    def resume(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.status_text.set("Playing")

    def stop(self):
        pygame.mixer.music.stop()
        self.is_paused = False
        self.status_text.set("Stopped")

    def close(self):
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.quit()
        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    app = MusicPlayerApp(window)
    window.mainloop()

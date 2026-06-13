import os
import time
import math
import random
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
# pyrefly: ignore [missing-import]
import customtkinter as ctk
# pyrefly: ignore [missing-import]
import mutagen

AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}

class MusicPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aura Beats - Premium Music Player")
        self.root.geometry("850x550")
        self.root.minsize(780, 480)

        # Style themes
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # State variables
        self.current_folder = None
        self.songs = []
        self.song_rows = []
        self.is_paused = False
        self.is_playing = False
        self.current_song_index = -1
        self.song_duration = 0
        self.current_play_time = 0
        self.seek_offset = 0
        self.is_seeking = False
        self.is_muted = False
        self.pre_mute_volume = 0.7

        pygame.mixer.init()

        self.folder_text = tk.StringVar(value="No folder selected")

        self.build_ui()

        # Visualizer data
        self.visualizer_heights = [2] * 18
        self.update_visualizer()
        self.update_disc_pulse()

        # Setup periodic update calls
        self.root.after(200, self.update_playback_state)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def build_ui(self):
        # Configure window base layout grid
        self.root.columnconfigure(0, weight=3) # Sidebar (Playlist)
        self.root.columnconfigure(1, weight=5) # Main Area (Controls & Visuals)
        self.root.rowconfigure(0, weight=1)

        # ------------------ SIDEBAR PANEL ------------------
        sidebar = ctk.CTkFrame(self.root, fg_color="#0f131a", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")

        # Header Title
        logo_lbl = ctk.CTkLabel(
            sidebar, 
            text="🎵 Aura Beats", 
            font=("Helvetica", 20, "bold"), 
            text_color="#a78bfa"
        )
        logo_lbl.pack(anchor="w", padx=20, pady=(25, 2))

        tagline_lbl = ctk.CTkLabel(
            sidebar, 
            text="Your Personal Sound Space", 
            font=("Helvetica", 11), 
            text_color="#55637d"
        )
        tagline_lbl.pack(anchor="w", padx=20, pady=(0, 20))

        # Folder action buttons
        folder_btn = ctk.CTkButton(
            sidebar,
            text="📂 Open Music Folder",
            font=("Helvetica", 13, "bold"),
            fg_color="#6366f1",
            hover_color="#4f46e5",
            corner_radius=8,
            height=38,
            command=self.choose_folder
        )
        folder_btn.pack(fill="x", padx=20, pady=(0, 10))

        self.folder_path_lbl = ctk.CTkLabel(
            sidebar,
            textvariable=self.folder_text,
            font=("Helvetica", 11),
            text_color="#55637d",
            anchor="w",
            wraplength=260
        )
        self.folder_path_lbl.pack(fill="x", anchor="w", padx=20, pady=(0, 15))

        # Playlist Header
        playlist_title = ctk.CTkLabel(
            sidebar, 
            text="PLAYLIST / TRACKS", 
            font=("Helvetica", 11, "bold"), 
            text_color="#8f9bb3"
        )
        playlist_title.pack(anchor="w", padx=20, pady=(10, 5))

        # Playlist frame
        self.playlist_scroll_frame = ctk.CTkScrollableFrame(
            sidebar,
            fg_color="transparent",
            scrollbar_button_color="#1e293b",
            scrollbar_button_hover_color="#334155"
        )
        self.playlist_scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 20))

        # ------------------ MAIN PANEL ------------------
        main_panel = ctk.CTkFrame(self.root, fg_color="#070a0e", corner_radius=0)
        main_panel.grid(row=0, column=1, sticky="nsew")

        # Now Playing Card
        now_playing_card = ctk.CTkFrame(main_panel, fg_color="#0f131a", corner_radius=16)
        now_playing_card.pack(fill="both", expand=True, padx=25, pady=(25, 15))

        # Large vinyl disc/music symbol
        self.disc_label = ctk.CTkLabel(
            now_playing_card,
            text="💿",
            font=("Helvetica", 96),
            text_color="#8b5cf6"
        )
        self.disc_label.pack(pady=(40, 10))

        # Canvas Bouncing Visualizer
        self.visualizer_canvas = ctk.CTkCanvas(
            now_playing_card,
            bg="#0f131a",
            highlightthickness=0,
            height=70
        )
        self.visualizer_canvas.pack(fill="x", padx=40, pady=(15, 10))
        
        # Setup visualizer bars in canvas
        self.visualizer_bars = []
        bar_width = 8
        spacing = 5
        start_x = 75
        canvas_height = 70
        for i in range(18):
            x0 = start_x + i * (bar_width + spacing)
            y0 = canvas_height - 2
            x1 = x0 + bar_width
            y1 = canvas_height
            bar = self.visualizer_canvas.create_rectangle(
                x0, y0, x1, y1,
                fill="#6366f1",
                outline=""
            )
            self.visualizer_bars.append(bar)

        # Track Metadata Details
        self.song_title_lbl = ctk.CTkLabel(
            now_playing_card,
            text="No Track Selected",
            font=("Helvetica", 18, "bold"),
            text_color="#f3f4f6",
            wraplength=400,
            justify="center"
        )
        self.song_title_lbl.pack(padx=20, pady=(15, 2))

        self.song_artist_lbl = ctk.CTkLabel(
            now_playing_card,
            text="Select a song to start listening",
            font=("Helvetica", 13),
            text_color="#8f9bb3",
            wraplength=400,
            justify="center"
        )
        self.song_artist_lbl.pack(padx=20, pady=(0, 30))

        # Playback Controls Panel
        controls_panel = ctk.CTkFrame(main_panel, fg_color="#0f131a", corner_radius=16)
        controls_panel.pack(fill="x", padx=25, pady=(0, 25))

        # Track Seekbar Frame
        seekbar_frame = ctk.CTkFrame(controls_panel, fg_color="transparent")
        seekbar_frame.pack(fill="x", padx=20, pady=(15, 8))

        self.time_lbl_left = ctk.CTkLabel(
            seekbar_frame, 
            text="00:00", 
            font=("Helvetica", 11), 
            text_color="#55637d"
        )
        self.time_lbl_left.pack(side="left", padx=(5, 10))

        self.progress_slider = ctk.CTkSlider(
            seekbar_frame,
            from_=0,
            to=1.0,
            number_of_steps=1000,
            fg_color="#20293a",
            progress_color="#6366f1",
            button_color="#8b5cf6",
            button_hover_color="#a78bfa",
            height=14,
            command=self.on_slider_change
        )
        self.progress_slider.pack(side="left", fill="x", expand=True)
        self.progress_slider.set(0)
        self.progress_slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        self.time_lbl_right = ctk.CTkLabel(
            seekbar_frame, 
            text="00:00", 
            font=("Helvetica", 11), 
            text_color="#55637d"
        )
        self.time_lbl_right.pack(side="right", padx=(10, 5))

        # Media controls & Volume layout
        bottom_bar = ctk.CTkFrame(controls_panel, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=20, pady=(0, 15))

        # Left spacer to align buttons center
        spacer_left = ctk.CTkFrame(bottom_bar, fg_color="transparent", width=140, height=1)
        spacer_left.pack(side="left")

        # Center playback controls
        btn_frame = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        btn_frame.pack(side="left", fill="x", expand=True)

        self.prev_btn = ctk.CTkButton(
            btn_frame,
            text="⏮",
            font=("Helvetica", 18),
            width=40,
            height=40,
            fg_color="transparent",
            text_color="#d0d7de",
            hover_color="#1f293d",
            command=self.play_prev_song
        )
        self.prev_btn.pack(side="left", expand=True)

        self.play_btn = ctk.CTkButton(
            btn_frame,
            text="▶",
            font=("Helvetica", 22),
            width=50,
            height=50,
            fg_color="#6366f1",
            text_color="#ffffff",
            hover_color="#4f46e5",
            corner_radius=25,
            command=self.toggle_play_pause
        )
        self.play_btn.pack(side="left", expand=True)

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹",
            font=("Helvetica", 18),
            width=40,
            height=40,
            fg_color="transparent",
            text_color="#d0d7de",
            hover_color="#1f293d",
            command=self.stop
        )
        self.stop_btn.pack(side="left", expand=True)

        self.next_btn = ctk.CTkButton(
            btn_frame,
            text="⏭",
            font=("Helvetica", 18),
            width=40,
            height=40,
            fg_color="transparent",
            text_color="#d0d7de",
            hover_color="#1f293d",
            command=self.play_next_song
        )
        self.next_btn.pack(side="left", expand=True)

        # Right volume control panel
        vol_frame = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        vol_frame.pack(side="right")

        self.volume_btn = ctk.CTkButton(
            vol_frame,
            text="🔊",
            font=("Helvetica", 14),
            width=30,
            fg_color="transparent",
            text_color="#d0d7de",
            hover_color="#1f293d",
            command=self.toggle_mute
        )
        self.volume_btn.pack(side="left")

        self.volume_slider = ctk.CTkSlider(
            vol_frame,
            from_=0.0,
            to=1.0,
            width=90,
            fg_color="#20293a",
            progress_color="#6366f1",
            button_color="#8b5cf6",
            button_hover_color="#a78bfa",
            command=self.on_volume_change
        )
        self.volume_slider.pack(side="left", padx=5)
        self.volume_slider.set(self.pre_mute_volume)

        self.volume_label = ctk.CTkLabel(
            vol_frame, 
            text=f"{int(self.pre_mute_volume * 100)}%", 
            font=("Helvetica", 11), 
            text_color="#55637d", 
            width=30
        )
        self.volume_label.pack(side="left")

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Choose your music folder")
        if not folder:
            return

        self.current_folder = Path(folder)
        # Update display path in shortened layout if too long
        self.folder_text.set(str(self.current_folder))
        self.load_songs()

    def load_songs(self):
        self.stop()
        
        # Clear playlist display frames
        for row in self.song_rows:
            row.destroy()
        self.song_rows.clear()

        # Load file list
        self.songs = sorted(
            [
                path
                for path in self.current_folder.iterdir()
                if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
            ],
            key=lambda path: path.name.lower(),
        )

        # Build custom UI rows for playlist
        for idx, song in enumerate(self.songs):
            self.add_song_row(idx, song)

        if self.songs:
            self.current_song_index = 0
            self.update_song_details(0, autoplay=False)
            self.highlight_active_song()
        else:
            self.song_title_lbl.configure(text="No Audio Files Found")
            self.song_artist_lbl.configure(text="Please load another directory")

    def add_song_row(self, index, song_path):
        row_frame = ctk.CTkFrame(
            self.playlist_scroll_frame, 
            fg_color="transparent", 
            corner_radius=6, 
            height=40
        )
        row_frame.pack(fill="x", pady=2, padx=4)
        row_frame.pack_propagate(False)

        self.song_rows.append(row_frame)

        # Index text
        idx_lbl = ctk.CTkLabel(
            row_frame, 
            text=f"{index+1:02d}", 
            font=("Helvetica", 11, "bold"), 
            text_color="#55637d", 
            width=30
        )
        idx_lbl.pack(side="left", padx=(10, 5))

        # Song Title text
        name_lbl = ctk.CTkLabel(
            row_frame, 
            text=song_path.stem, 
            font=("Helvetica", 12), 
            text_color="#d0d7de", 
            anchor="w"
        )
        name_lbl.pack(side="left", fill="x", expand=True, padx=5)

        # Event binds for hover and click states
        def on_enter(e):
            if self.current_song_index != index:
                row_frame.configure(fg_color="#181e29")

        def on_leave(e):
            if self.current_song_index != index:
                row_frame.configure(fg_color="transparent")

        def on_click(e):
            self.play_song_at_index(index)

        for widget in (row_frame, idx_lbl, name_lbl):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

    def highlight_active_song(self):
        for idx, row in enumerate(self.song_rows):
            if idx == self.current_song_index:
                row.configure(fg_color="#232a3b")
                for child in row.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        child.configure(text_color="#a78bfa")
            else:
                row.configure(fg_color="transparent")
                # Reset to defaults
                for i, child in enumerate(row.winfo_children()):
                    if isinstance(child, ctk.CTkLabel):
                        if i == 0: # Index label
                            child.configure(text_color="#55637d")
                        else: # Song Name label
                            child.configure(text_color="#d0d7de")

    def get_audio_metadata(self, filepath):
        try:
            audio = mutagen.File(filepath)
            if audio is None:
                return filepath.stem, "Unknown Artist", 0
            
            # Duration
            duration = int(audio.info.length) if hasattr(audio, "info") and hasattr(audio.info, "length") else 0
            
            # Title & Artist
            title = filepath.stem
            artist = "Unknown Artist"
            
            if audio.tags:
                for key in ["title", "TIT2"]:
                    if key in audio:
                        title = str(audio[key][0])
                        break
                for key in ["artist", "TPE1"]:
                    if key in audio:
                        artist = str(audio[key][0])
                        break
            
            return title, artist, duration
        except Exception:
            return filepath.stem, "Unknown Artist", 0

    def update_song_details(self, index, autoplay=True):
        if index < 0 or index >= len(self.songs):
            return

        song_path = self.songs[index]
        title, artist, duration = self.get_audio_metadata(song_path)

        self.song_title_lbl.configure(text=title)
        self.song_artist_lbl.configure(text=artist)
        self.song_duration = duration
        self.seek_offset = 0
        self.current_play_time = 0

        self.time_lbl_left.configure(text="00:00")
        self.time_lbl_right.configure(text=self.format_time(duration))
        self.progress_slider.set(0)

        if autoplay:
            try:
                pygame.mixer.music.load(str(song_path))
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
                self.play_btn.configure(text="⏸")
            except pygame.error as error:
                messagebox.showerror("Playback error", f"Could not play this track:\n{error}")
                self.stop()

    def play_song_at_index(self, index):
        self.current_song_index = index
        self.update_song_details(index, autoplay=True)
        self.highlight_active_song()

    def toggle_play_pause(self):
        if not self.songs:
            messagebox.showinfo("No songs loaded", "Please choose a folder with supported audio files first.")
            return

        if self.current_song_index == -1:
            self.play_song_at_index(0)
            return

        if self.is_playing:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.play_btn.configure(text="⏸")
            else:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.play_btn.configure(text="▶")
        else:
            self.play_song_at_index(self.current_song_index)

    def play_next_song(self):
        if not self.songs:
            return
        self.current_song_index = (self.current_song_index + 1) % len(self.songs)
        self.play_song_at_index(self.current_song_index)

    def play_prev_song(self):
        if not self.songs:
            return
        # If song has been playing for more than 3 seconds, restart it
        if self.current_play_time > 3:
            self.seek_to(0)
        else:
            self.current_song_index = (self.current_song_index - 1) % len(self.songs)
            self.play_song_at_index(self.current_song_index)

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.seek_offset = 0
        self.current_play_time = 0
        self.play_btn.configure(text="▶")
        self.progress_slider.set(0)
        self.time_lbl_left.configure(text="00:00")

    def seek_to(self, value):
        if not self.songs or self.current_song_index == -1:
            return

        song_path = self.songs[self.current_song_index]
        self.seek_offset = float(value)
        self.current_play_time = self.seek_offset

        try:
            # Re-initialize play from position
            pygame.mixer.music.play(start=self.seek_offset)
            if self.is_paused:
                pygame.mixer.music.pause()
        except pygame.error:
            # Some formats do not support seek via start parameter
            pass

    def on_slider_change(self, value):
        if self.is_seeking and self.song_duration > 0:
            target_time = value * self.song_duration
            self.time_lbl_left.configure(text=self.format_time(target_time))

    def on_slider_press(self, event):
        self.is_seeking = True

    def on_slider_release(self, event):
        self.is_seeking = False
        if self.song_duration > 0:
            val = self.progress_slider.get()
            self.seek_to(val * self.song_duration)

    def on_volume_change(self, value):
        pygame.mixer.music.set_volume(value)
        if value == 0:
            self.volume_btn.configure(text="🔇")
        elif value < 0.3:
            self.volume_btn.configure(text="🔈")
        elif value < 0.7:
            self.volume_btn.configure(text="🔉")
        else:
            self.volume_btn.configure(text="🔊")
        self.volume_label.configure(text=f"{int(value * 100)}%")

    def toggle_mute(self):
        if self.is_muted:
            self.is_muted = False
            self.volume_slider.set(self.pre_mute_volume)
            self.on_volume_change(self.pre_mute_volume)
        else:
            self.is_muted = True
            self.pre_mute_volume = self.volume_slider.get()
            self.volume_slider.set(0.0)
            self.on_volume_change(0.0)

    def update_playback_state(self):
        if self.is_playing and not self.is_paused:
            if not pygame.mixer.music.get_busy():
                # Autoplay next song when finished
                self.play_next_song()
            else:
                elapsed = pygame.mixer.music.get_pos() / 1000.0
                self.current_play_time = self.seek_offset + elapsed
                
                # Update seekbar time and slider position
                if not self.is_seeking and self.song_duration > 0:
                    curr_str = self.format_time(self.current_play_time)
                    dur_str = self.format_time(self.song_duration)
                    self.time_lbl_left.configure(text=curr_str)
                    self.time_lbl_right.configure(text=dur_str)

                    progress = self.current_play_time / self.song_duration
                    # Cap progress to 1.0 to avoid overflow slider visual issues
                    self.progress_slider.set(min(1.0, progress))

        self.root.after(200, self.update_playback_state)

    def update_visualizer(self):
        if not hasattr(self, "visualizer_canvas"):
            return

        canvas_height = 70
        
        # Calculate heights for visualizer bars
        if self.is_playing and not self.is_paused:
            t = time.time() * 8
            for i in range(18):
                h = 5 + 40 * abs(math.sin(t + i * 0.45)) + random.randint(0, 15)
                h = min(h, canvas_height - 5)
                self.visualizer_heights[i] = h
        else:
            # Decay to baseline
            for i in range(18):
                if self.visualizer_heights[i] > 2:
                    self.visualizer_heights[i] -= 3
                    if self.visualizer_heights[i] < 2:
                        self.visualizer_heights[i] = 2

        # Draw the coordinates in canvas
        bar_width = 8
        spacing = 5
        start_x = 75
        for i, bar in enumerate(self.visualizer_bars):
            h = self.visualizer_heights[i]
            x0 = start_x + i * (bar_width + spacing)
            y0 = canvas_height - h
            x1 = x0 + bar_width
            y1 = canvas_height
            self.visualizer_canvas.coords(bar, x0, y0, x1, y1)

            # Apply gradient color based on height
            if h > 45:
                color = "#d8b4fe" # light purple
            elif h > 25:
                color = "#a78bfa" # mid purple
            else:
                color = "#6366f1" # indigo
            self.visualizer_canvas.itemconfig(bar, fill=color)

        self.root.after(60, self.update_visualizer)

    def update_disc_pulse(self):
        if hasattr(self, "disc_label"):
            if self.is_playing and not self.is_paused:
                # Modulate color hue slowly
                t = time.time() * 2
                val = abs(math.sin(t))
                # Interpolate color components between indigo (#6366f1) and light purple (#d8b4fe)
                r = int(99 + val * (216 - 99))
                g = int(102 + val * (180 - 102))
                b = int(241 + val * (254 - 241))
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.disc_label.configure(text_color=color)
            else:
                # Muted gray color when stopped/paused
                self.disc_label.configure(text_color="#334155")
        
        self.root.after(100, self.update_disc_pulse)

    def format_time(self, seconds):
        if seconds is None or seconds < 0:
            return "00:00"
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"

    def close(self):
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    window = ctk.CTk()
    app = MusicPlayerApp(window)
    window.mainloop()

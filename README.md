# CodeAlpha Music Player 🎵

A sleek, dark-themed, desktop music player application built with Python using **Tkinter** for the user interface and **Pygame** for high-quality audio playback.

This project is part of the CodeAlpha Internship program.

## 🚀 Features

- **Format Variety**: Play audio files across multiple popular formats, including `.mp3`, `.wav`, `.ogg`, `.flac`, and `.m4a`.
- **Easy Directory Navigation**: Load entire folders of music with a single click.
- **Classic Playback Controls**: Easily `Play`, `Pause`, `Resume`, and `Stop` music tracks.
- **Interactive Playlist**: View loaded tracks in a list, select with a click, or double-click any track to play it instantly.
- **Sleek Modern Design**: Features a customized slate-dark UI theme built on Tkinter's `ttk` styling engine.
- **Robust Error Handling**: Displays helpful alerts if files are unsupported or corrupted.
- **Graceful Termination**: Ensures pygame resources are cleanly released when exiting the app.

---

## 🛠️ Tech Stack & Dependencies

- **Language**: Python 3.x
- **GUI Library**: `tkinter` (Standard Python Library)
- **Audio Engine**: `pygame`
- **Path Operations**: `pathlib`

---

## 📥 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/CodeAlpha_MusicPlayer.git
cd CodeAlpha_MusicPlayer
```

### 2. Install Dependencies
You will need `pygame` installed. You can install it using `pip`:
```bash
pip install pygame
```

---

## 🖥️ How to Run

Run the application using Python:
```bash
python demo.py
```

### How to Use:
1. Click the **Choose Folder** button to load a directory containing your audio files.
2. Select a song from the playlist.
3. Use the control buttons (**Play**, **Pause**, **Resume**, **Stop**) to manage playback, or simply **double-click** a song in the list to play it immediately.

---

## 📂 Project Structure

- `demo.py`: Main application code containing UI setup, playback functions, and styling configuration.
- `README.md`: Project documentation.

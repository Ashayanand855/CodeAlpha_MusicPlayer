# CodeAlpha Music Player 🎵

A sleek, dark-themed, desktop music player application built with Python using **Tkinter** for the user interface and **Pygame** for high-quality audio playback.

This project is part of the CodeAlpha Internship program.

## 🚀 Features

- **Premium Modern Design**: Features a highly polished slate-dark UI theme built with CustomTkinter, rounded corners, responsive layout, and smooth interactions.
- **Audio Visualizer**: Interactive canvas-based sound-wave spectrum animation that pulses dynamically to the playback.
- **Format Variety**: Play audio files across multiple popular formats, including `.mp3`, `.wav`, `.ogg`, `.flac`, and `.m4a`.
- **Metadata Support**: Automatically extracts song titles, artist names, and exact durations using `mutagen`.
- **Seekable Progress Bar**: Scrub or click anywhere on the progress bar to seek to different parts of the track.
- **Volume & Mute Controls**: Seamlessly adjust volume with a custom slider and toggle mute.
- **Classic Playback Controls**: Easily `Play`, `Pause`, `Resume`, `Stop`, `Next`, and `Previous` tracks.
- **Interactive Playlist**: View loaded tracks in a custom list with interactive hover-state rows; select a track or double-click to play immediately.
- **Auto-Play Queue**: Automatically plays the next track when the current song completes.

---

## 🛠️ Tech Stack & Dependencies

- **Language**: Python 3.x
- **GUI Library**: `customtkinter` (Modern Tkinter wrapper)
- **Audio Engine**: `pygame`
- **Metadata Reader**: `mutagen`
- **Path Operations**: `pathlib`

---

## 📥 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/CodeAlpha_MusicPlayer.git
cd CodeAlpha_MusicPlayer
```

### 2. Set Up Virtual Environment & Install Dependencies
Create a virtual environment and install the required libraries:
```bash
python3 -m venv .venv
.venv/bin/pip install customtkinter pygame mutagen
```

---

## 🖥️ How to Run

Run the application using the virtual environment python interpreter:
```bash
.venv/bin/python demo.py
```

### How to Use:
1. Click the **Open Music Folder** button to load a directory containing your audio files.
2. Click any track in the playlist sidebar on the left.
3. Use the control buttons (**Play**, **Stop**, **Prev**, **Next**) to manage playback.
4. Drag or click the **Seekbar** to fast-forward/rewind.
5. Control the volume with the slider or click the speaker icon to mute/unmute.


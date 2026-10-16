import json
import os
import random
import sys
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import pygame

# app theme setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# determine persistent directory (works for both raw python and pyinstaller onefile)
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(APP_DIR, "player_config.json")


class MusicPlayer(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Neon Beats — Music Player Pro")
        self.geometry("940x660")
        self.resizable(False, False)

        # audio engine init (mixer only, no display subsystem)
        pygame.mixer.init()

        # playback state
        self.playlist = []
        self.filtered_indices = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.is_seeking = False
        self.shuffle_mode = False
        self.repeat_mode = False
        self.is_muted = False
        self.pre_mute_volume = 0.7

        # track timing state
        self.track_length = 0.0
        self.seek_offset = 0.0

        # neon visualizer color palettes
        self.vis_themes = [
            ["#00F5D4", "#00BBF9", "#9B5DE5", "#F15BB5"],  # cyberpunk
            ["#00FF66", "#00DD44", "#00AA22", "#66FF99"],  # matrix
            ["#FF0055", "#FF5500", "#FFAA00", "#FFD700"],  # sunset
            ["#00D4FF", "#0088FF", "#3A0CA3", "#4CC9F0"],  # electric ice
        ]
        self.current_theme_idx = 0

        self._build_ui()
        self._init_visualizer()
        self._bind_hotkeys()

        # load persistent playlist & settings
        self._load_config()

        # save on window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # start polling loop for track end & progress
        self._poll_music_events()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # left pane: playlist, search, controls
        left_frame = ctk.CTkFrame(self, corner_radius=15)
        left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.lbl_playlist_title = ctk.CTkLabel(
            left_frame, text="My Playlist (0)", font=("Segoe UI", 17, "bold")
        )
        self.lbl_playlist_title.pack(pady=(12, 6))

        # search input
        self.search_entry = ctk.CTkEntry(
            left_frame,
            placeholder_text="🔍 Search tracks...",
            height=30,
            font=("Segoe UI", 11),
        )
        self.search_entry.pack(fill="x", padx=12, pady=(0, 8))
        self.search_entry.bind("<KeyRelease>", self._filter_playlist)

        # playlist listbox
        self.track_listbox = tk.Listbox(
            left_frame,
            bg="#18181F",
            fg="#E0E0E0",
            selectbackground="#3B8ED0",
            selectforeground="#FFFFFF",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 10),
            activestyle="none",
        )
        self.track_listbox.pack(
            fill="both", expand=True, padx=12, pady=(0, 8)
        )
        self.track_listbox.bind("<Double-Button-1>", self.on_track_double_click)
        self.track_listbox.bind("<Delete>", lambda e: self.remove_track())

        # playlist buttons: row 1 (+ files, + folder)
        pl_btn_row1 = ctk.CTkFrame(left_frame, fg_color="transparent")
        pl_btn_row1.pack(fill="x", padx=12, pady=(0, 4))

        btn_add_files = ctk.CTkButton(
            pl_btn_row1,
            text="+ Files",
            height=30,
            font=("Segoe UI", 11, "bold"),
            command=self.load_tracks,
        )
        btn_add_files.pack(side="left", expand=True, fill="x", padx=(0, 3))

        btn_add_folder = ctk.CTkButton(
            pl_btn_row1,
            text="+ Folder",
            height=30,
            font=("Segoe UI", 11, "bold"),
            command=self.load_folder,
        )
        btn_add_folder.pack(side="left", expand=True, fill="x", padx=(3, 0))

        # playlist buttons: row 2 (remove, clear)
        pl_btn_row2 = ctk.CTkFrame(left_frame, fg_color="transparent")
        pl_btn_row2.pack(fill="x", padx=12, pady=(0, 12))

        btn_del = ctk.CTkButton(
            pl_btn_row2,
            text="✕ Remove",
            height=28,
            font=("Segoe UI", 11),
            fg_color="#33333E",
            hover_color="#D9534F",
            command=self.remove_track,
        )
        btn_del.pack(side="left", expand=True, fill="x", padx=(0, 3))

        btn_clear = ctk.CTkButton(
            pl_btn_row2,
            text="Clear",
            height=28,
            font=("Segoe UI", 11),
            fg_color="#33333E",
            hover_color="#555555",
            command=self.clear_playlist,
        )
        btn_clear.pack(side="left", expand=True, fill="x", padx=(3, 0))

        # right pane: player, visualizer, timeline
        right_frame = ctk.CTkFrame(self, corner_radius=15)
        right_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")

        # top row: theme switch
        top_bar = ctk.CTkFrame(right_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(15, 0))

        self.btn_theme = ctk.CTkButton(
            top_bar,
            text="🎨 Theme",
            width=70,
            height=26,
            font=("Segoe UI", 10, "bold"),
            fg_color="#2B2B36",
            command=self._cycle_vis_theme,
        )
        self.btn_theme.pack(side="right")

        # now playing title
        self.lbl_current_track = ctk.CTkLabel(
            right_frame,
            text="No track selected",
            font=("Segoe UI", 16, "bold"),
            text_color="#8AB4F8",
            wraplength=480,
        )
        self.lbl_current_track.pack(pady=(15, 5))

        # visualizer canvas
        self.canvas_vis = tk.Canvas(
            right_frame,
            width=520,
            height=160,
            bg="#131318",
            bd=0,
            highlightthickness=0,
        )
        self.canvas_vis.pack(pady=10)

        # timeline seek bar & counters
        timeline_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        timeline_frame.pack(fill="x", padx=35, pady=(5, 5))

        self.lbl_current_time = ctk.CTkLabel(
            timeline_frame,
            text="00:00",
            font=("Segoe UI", 11),
            text_color="#A0A0A0",
        )
        self.lbl_current_time.pack(side="left", padx=(0, 8))

        self.slider_progress = ctk.CTkSlider(
            timeline_frame, from_=0, to=100, command=self.on_seeking
        )
        self.slider_progress.set(0)
        self.slider_progress.pack(side="left", fill="x", expand=True)
        self.slider_progress.bind("<ButtonPress-1>", self.on_seek_start)
        self.slider_progress.bind("<ButtonRelease-1>", self.on_seek_end)

        self.lbl_total_time = ctk.CTkLabel(
            timeline_frame,
            text="00:00",
            font=("Segoe UI", 11),
            text_color="#A0A0A0",
        )
        self.lbl_total_time.pack(side="left", padx=(8, 0))

        # volume & mute bar
        vol_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        vol_frame.pack(fill="x", padx=90, pady=(5, 12))

        self.btn_mute = ctk.CTkButton(
            vol_frame,
            text="🔊",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color="#2B2B36",
            font=("Segoe UI Emoji", 14),
            command=self.toggle_mute,
        )
        self.btn_mute.pack(side="left", padx=(0, 6))

        self.slider_vol = ctk.CTkSlider(
            vol_frame, from_=0, to=1, command=self.set_volume
        )
        self.slider_vol.set(0.7)
        pygame.mixer.music.set_volume(0.7)
        self.slider_vol.pack(side="left", fill="x", expand=True)

        self.lbl_vol_pct = ctk.CTkLabel(
            vol_frame, text="70%", font=("Segoe UI", 11), text_color="#A0A0A0"
        )
        self.lbl_vol_pct.pack(side="left", padx=(8, 0))

        # transport buttons
        controls_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        controls_frame.pack(pady=(0, 10))

        self.btn_shuffle = ctk.CTkButton(
            controls_frame,
            text="🔀",
            width=42,
            height=42,
            font=("Segoe UI Emoji", 14),
            corner_radius=21,
            fg_color="#2B2B36",
            hover_color="#3A3D40",
            command=self.toggle_shuffle,
        )
        self.btn_shuffle.pack(side="left", padx=10)

        btn_prev = ctk.CTkButton(
            controls_frame,
            text="⏮",
            width=48,
            height=48,
            font=("Segoe UI", 16),
            corner_radius=24,
            command=self.prev_track,
        )
        btn_prev.pack(side="left", padx=8)

        self.btn_play = ctk.CTkButton(
            controls_frame,
            text="▶",
            width=64,
            height=64,
            font=("Segoe UI", 22, "bold"),
            corner_radius=32,
            fg_color="#3B8ED0",
            command=self.toggle_play,
        )
        self.btn_play.pack(side="left", padx=12)

        btn_next = ctk.CTkButton(
            controls_frame,
            text="⏭",
            width=48,
            height=48,
            font=("Segoe UI", 16),
            corner_radius=24,
            command=self.next_track,
        )
        btn_next.pack(side="left", padx=8)

        self.btn_repeat = ctk.CTkButton(
            controls_frame,
            text="🔁",
            width=42,
            height=42,
            font=("Segoe UI Emoji", 14),
            corner_radius=21,
            fg_color="#2B2B36",
            hover_color="#3A3D40",
            command=self.toggle_repeat,
        )
        self.btn_repeat.pack(side="left", padx=10)

    # global keybinds
    def _bind_hotkeys(self):
        self.bind("<space>", lambda e: self.toggle_play())
        self.bind("<Left>", lambda e: self.seek_relative(-5))
        self.bind("<Right>", lambda e: self.seek_relative(5))
        self.bind("<Up>", lambda e: self._adjust_volume(0.05))
        self.bind("<Down>", lambda e: self._adjust_volume(-0.05))
        self.bind("<m>", lambda e: self.toggle_mute())

    # visualizer animation loop
    def _init_visualizer(self):
        self.num_bars = 34
        self.bar_width = 11
        self.spacing = 4
        self.canvas_height = 160
        self.bar_heights = [6] * self.num_bars
        self.target_heights = [6] * self.num_bars
        self._animate_visualizer()

    def _animate_visualizer(self):
        self.canvas_vis.delete("all")
        palette = self.vis_themes[self.current_theme_idx]

        for i in range(self.num_bars):
            if self.is_playing and not self.is_paused:
                if random.random() < 0.3:
                    self.target_heights[i] = random.randint(
                        15, self.canvas_height - 18
                    )
                self.bar_heights[i] += (
                    self.target_heights[i] - self.bar_heights[i]
                ) * 0.25
            else:
                self.bar_heights[i] += (4 - self.bar_heights[i]) * 0.15

            h = max(3, self.bar_heights[i])
            x0 = 8 + i * (self.bar_width + self.spacing)
            y0 = self.canvas_height - h
            x1 = x0 + self.bar_width
            y1 = self.canvas_height

            color = palette[int((i / self.num_bars) * len(palette))]

            self.canvas_vis.create_rectangle(
                x0, y0, x1, y1, fill=color, outline=""
            )
            self.canvas_vis.create_rectangle(
                x0, y0 - 3, x1, y0, fill="#FFFFFF", outline=""
            )

        self.after(30, self._animate_visualizer)

    def _cycle_vis_theme(self):
        self.current_theme_idx = (self.current_theme_idx + 1) % len(
            self.vis_themes
        )
        self._save_config()

    # timer loop (replaces event-based queue)
    def _poll_music_events(self):
        # detect track completion without pygame video subsystem
        if (
            self.is_playing
            and not self.is_paused
            and not self.is_seeking
            and not pygame.mixer.music.get_busy()
        ):
            self.on_track_finished()

        # sync timeline slider
        if self.is_playing and not self.is_paused and not self.is_seeking:
            raw_pos = pygame.mixer.music.get_pos()
            if raw_pos != -1:
                current_sec = self.seek_offset + (raw_pos / 1000.0)
                self.lbl_current_time.configure(
                    text=self._format_time(current_sec)
                )

                if self.track_length > 0:
                    pct = min(100.0, (current_sec / self.track_length) * 100)
                    self.slider_progress.set(pct)

        self.after(250, self._poll_music_events)

    # playback logic
    def play_track(self, index, start_time=0.0):
        if not self.playlist or index < 0 or index >= len(self.playlist):
            return

        self.current_index = index
        track_path = self.playlist[self.current_index]

        try:
            try:
                snd = pygame.mixer.Sound(track_path)
                self.track_length = snd.get_length()
            except Exception:
                self.track_length = 0.0

            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(start=start_time)
            self.seek_offset = start_time
            self.is_playing = True
            self.is_paused = False
            self.btn_play.configure(text="⏸")

            track_name = os.path.basename(track_path)
            self.lbl_current_track.configure(text=track_name)
            self.lbl_total_time.configure(
                text=self._format_time(self.track_length)
            )

            self._sync_listbox_selection()
            self._save_config()
        except Exception as e:
            self.lbl_current_track.configure(text=f"Error: {e}")

    def toggle_play(self):
        if not self.playlist:
            return

        if not self.is_playing:
            self.play_track(self.current_index)
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.btn_play.configure(text="⏸")
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.btn_play.configure(text="▶")

    def stop_playback(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.btn_play.configure(text="▶")
        self.lbl_current_time.configure(text="00:00")
        self.slider_progress.set(0)

    # track switching & navigation
    def next_track(self):
        if not self.playlist:
            return
        if self.shuffle_mode:
            next_idx = random.randint(0, len(self.playlist) - 1)
        else:
            next_idx = (self.current_index + 1) % len(self.playlist)
        self.play_track(next_idx)

    def prev_track(self):
        if not self.playlist:
            return
        prev_idx = (self.current_index - 1) % len(self.playlist)
        self.play_track(prev_idx)

    def on_track_finished(self):
        if not self.playlist or not self.is_playing:
            return

        if self.repeat_mode:
            self.play_track(self.current_index)
        elif self.shuffle_mode:
            next_idx = random.randint(0, len(self.playlist) - 1)
            self.play_track(next_idx)
        else:
            self.next_track()

    # seeking handlers
    def on_seek_start(self, event):
        self.is_seeking = True

    def on_seeking(self, val):
        if self.track_length > 0:
            target_sec = (val / 100.0) * self.track_length
            self.lbl_current_time.configure(text=self._format_time(target_sec))

    def on_seek_end(self, event):
        if not self.is_playing or self.track_length <= 0:
            self.is_seeking = False
            return

        pct = self.slider_progress.get()
        target_sec = (pct / 100.0) * self.track_length
        self.play_track(self.current_index, start_time=target_sec)
        self.is_seeking = False

    def seek_relative(self, delta_sec):
        if not self.is_playing or self.track_length <= 0:
            return
        raw_pos = pygame.mixer.music.get_pos()
        current_sec = self.seek_offset + max(0, raw_pos / 1000.0)
        target_sec = max(0, min(self.track_length - 1, current_sec + delta_sec))
        self.play_track(self.current_index, start_time=target_sec)

    # volume and mute controls
    def set_volume(self, val):
        vol = float(val)
        pygame.mixer.music.set_volume(vol)
        self.lbl_vol_pct.configure(text=f"{int(vol * 100)}%")
        if vol == 0:
            self.btn_mute.configure(text="🔇")
            self.is_muted = True
        else:
            self.btn_mute.configure(text="🔊")
            self.is_muted = False
            self.pre_mute_volume = vol

    def toggle_mute(self):
        if self.is_muted:
            self.slider_vol.set(self.pre_mute_volume)
            self.set_volume(self.pre_mute_volume)
        else:
            self.pre_mute_volume = self.slider_vol.get()
            self.slider_vol.set(0)
            self.set_volume(0)

    def _adjust_volume(self, delta):
        cur = self.slider_vol.get()
        new_vol = max(0.0, min(1.0, cur + delta))
        self.slider_vol.set(new_vol)
        self.set_volume(new_vol)
        self._save_config()

    # shuffle and repeat toggles
    def toggle_shuffle(self):
        self.shuffle_mode = not self.shuffle_mode
        self.btn_shuffle.configure(
            fg_color="#3B8ED0" if self.shuffle_mode else "#2B2B36"
        )
        self._save_config()

    def toggle_repeat(self):
        self.repeat_mode = not self.repeat_mode
        self.btn_repeat.configure(
            fg_color="#3B8ED0" if self.repeat_mode else "#2B2B36"
        )
        self._save_config()

    # playlist management & search
    def load_tracks(self):
        files = filedialog.askopenfilenames(
            title="Select audio files",
            filetypes=[("Audio files", "*.mp3 *.wav *.ogg *.flac")],
        )
        if files:
            self._add_files_to_playlist(files)

    def load_folder(self):
        folder = filedialog.askdirectory(title="Select folder with audio")
        if folder:
            valid_exts = (".mp3", ".wav", ".ogg", ".flac")
            found = []
            for root, _, files in os.walk(folder):
                for f in sorted(files):
                    if f.lower().endswith(valid_exts):
                        found.append(os.path.join(root, f))
            if found:
                self._add_files_to_playlist(found)

    def _add_files_to_playlist(self, file_paths):
        for f in file_paths:
            if f not in self.playlist:
                self.playlist.append(f)
        self._refresh_listbox()
        self._update_playlist_title()
        self._save_config()

        if not self.is_playing:
            self.play_track(0)

    def remove_track(self):
        sel = self.track_listbox.curselection()
        if not sel:
            return
        disp_idx = sel[0]
        real_idx = (
            self.filtered_indices[disp_idx]
            if self.filtered_indices
            else disp_idx
        )

        del self.playlist[real_idx]
        self._refresh_listbox()
        self._update_playlist_title()
        self._save_config()

        if real_idx == self.current_index:
            if self.playlist:
                new_idx = real_idx % len(self.playlist)
                self.play_track(new_idx)
            else:
                self.stop_playback()
                self.lbl_current_track.configure(text="No track selected")
                self.lbl_total_time.configure(text="00:00")
        elif real_idx < self.current_index:
            self.current_index -= 1

    def clear_playlist(self):
        self.stop_playback()
        self.playlist.clear()
        self._refresh_listbox()
        self._update_playlist_title()
        self._save_config()
        self.lbl_current_track.configure(text="No track selected")
        self.lbl_total_time.configure(text="00:00")

    def _filter_playlist(self, event=None):
        query = self.search_entry.get().strip().lower()
        self.track_listbox.delete(0, tk.END)
        self.filtered_indices = []

        for idx, path in enumerate(self.playlist):
            name = os.path.basename(path)
            if query in name.lower():
                self.track_listbox.insert(tk.END, f"  🎵 {name}")
                self.filtered_indices.append(idx)

        self._sync_listbox_selection()

    def _refresh_listbox(self):
        self._filter_playlist()

    def _sync_listbox_selection(self):
        self.track_listbox.selection_clear(0, tk.END)
        if not self.playlist:
            return

        if self.filtered_indices:
            if self.current_index in self.filtered_indices:
                disp_idx = self.filtered_indices.index(self.current_index)
                self.track_listbox.selection_set(disp_idx)
                self.track_listbox.see(disp_idx)
        else:
            if 0 <= self.current_index < self.track_listbox.size():
                self.track_listbox.selection_set(self.current_index)
                self.track_listbox.see(self.current_index)

    def on_track_double_click(self, event):
        sel = self.track_listbox.curselection()
        if not sel:
            return
        disp_idx = sel[0]
        real_idx = (
            self.filtered_indices[disp_idx]
            if self.filtered_indices
            else disp_idx
        )
        self.play_track(real_idx)

    def _update_playlist_title(self):
        self.lbl_playlist_title.configure(
            text=f"My Playlist ({len(self.playlist)})"
        )

    # state persistence
    def _save_config(self):
        data = {
            "playlist": [f for f in self.playlist if os.path.exists(f)],
            "volume": self.slider_vol.get(),
            "shuffle": self.shuffle_mode,
            "repeat": self.repeat_mode,
            "theme_idx": self.current_theme_idx,
            "last_index": self.current_index,
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            raw_pl = data.get("playlist", [])
            self.playlist = [f for f in raw_pl if os.path.exists(f)]
            self._refresh_listbox()
            self._update_playlist_title()

            vol = data.get("volume", 0.7)
            self.slider_vol.set(vol)
            self.set_volume(vol)

            if data.get("shuffle", False):
                self.toggle_shuffle()
            if data.get("repeat", False):
                self.toggle_repeat()

            self.current_theme_idx = data.get("theme_idx", 0)

            last_idx = data.get("last_index", 0)
            if self.playlist and 0 <= last_idx < len(self.playlist):
                self.current_index = last_idx
                track_name = os.path.basename(self.playlist[last_idx])
                self.lbl_current_track.configure(text=track_name)
                self._sync_listbox_selection()
        except Exception:
            pass

    def _on_closing(self):
        self._save_config()
        self.destroy()

    @staticmethod
    def _format_time(sec):
        m, s = divmod(int(max(0, sec)), 60)
        return f"{m:02d}:{s:02d}"


if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()
import os
import random
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import pygame

# app theme setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MusicPlayer(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Neon Beats — Music Player")
        self.geometry("820x540")
        self.resizable(False, False)

        # audio engine init
        pygame.mixer.init()

        # player state
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False

        self._build_ui()
        self._init_visualizer()

    def _build_ui(self):
        # 2-column layout: playlist on the left, player on the right
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # left pane: playlist
        left_frame = ctk.CTkFrame(self, corner_radius=15)
        left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        playlist_title = ctk.CTkLabel(
            left_frame, text="My Playlist", font=("Segoe UI", 18, "bold")
        )
        playlist_title.pack(pady=(15, 10))

        self.track_listbox = tk.Listbox(
            left_frame,
            bg="#1E1E24",
            fg="#E0E0E0",
            selectbackground="#3B8ED0",
            selectforeground="#FFFFFF",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 10),
            activestyle="none",
        )
        self.track_listbox.pack(
            fill="both", expand=True, padx=12, pady=(0, 10)
        )
        self.track_listbox.bind("<Double-Button-1>", self.on_track_double_click)

        btn_add = ctk.CTkButton(
            left_frame,
            text="+ Add Tracks",
            font=("Segoe UI", 13, "bold"),
            command=self.load_tracks,
        )
        btn_add.pack(fill="x", padx=12, pady=(0, 15))

        # right pane: player & visualizer
        right_frame = ctk.CTkFrame(self, corner_radius=15)
        right_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")

        # track title label
        self.lbl_current_track = ctk.CTkLabel(
            right_frame,
            text="No track selected",
            font=("Segoe UI", 16, "bold"),
            text_color="#8AB4F8",
            wraplength=450,
        )
        self.lbl_current_track.pack(pady=(25, 10))

        # neon visualizer canvas
        self.canvas_vis = tk.Canvas(
            right_frame,
            width=460,
            height=180,
            bg="#18181F",
            bd=0,
            highlightthickness=0,
        )
        self.canvas_vis.pack(pady=15)

        # volume slider
        vol_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        vol_frame.pack(fill="x", padx=40, pady=(5, 15))

        lbl_vol = ctk.CTkLabel(
            vol_frame, text="🔊", font=("Segoe UI Emoji", 14)
        )
        lbl_vol.pack(side="left", padx=(0, 10))

        self.slider_vol = ctk.CTkSlider(
            vol_frame, from_=0, to=1, command=self.set_volume
        )
        self.slider_vol.set(0.7)
        pygame.mixer.music.set_volume(0.7)
        self.slider_vol.pack(side="left", fill="x", expand=True)

        # playback controls
        controls_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        controls_frame.pack(pady=15)

        btn_prev = ctk.CTkButton(
            controls_frame,
            text="⏮",
            width=50,
            height=50,
            font=("Segoe UI", 18),
            corner_radius=25,
            command=self.prev_track,
        )
        btn_prev.pack(side="left", padx=10)

        self.btn_play = ctk.CTkButton(
            controls_frame,
            text="▶",
            width=65,
            height=65,
            font=("Segoe UI", 22, "bold"),
            corner_radius=33,
            fg_color="#3B8ED0",
            command=self.toggle_play,
        )
        self.btn_play.pack(side="left", padx=15)

        btn_next = ctk.CTkButton(
            controls_frame,
            text="⏭",
            width=50,
            height=50,
            font=("Segoe UI", 18),
            corner_radius=25,
            command=self.next_track,
        )
        btn_next.pack(side="left", padx=10)

    # visualizer setup & animation loop
    def _init_visualizer(self):
        self.num_bars = 28
        self.bar_width = 12
        self.spacing = 4
        self.canvas_height = 180
        self.bar_heights = [10] * self.num_bars
        self.target_heights = [10] * self.num_bars
        self._animate_visualizer()

    def _animate_visualizer(self):
        self.canvas_vis.delete("all")

        # neon gradient palette
        colors = ["#00F5D4", "#00BBF9", "#9B5DE5", "#F15BB5"]

        for i in range(self.num_bars):
            if self.is_playing and not self.is_paused:
                # bounce bars randomly when playing
                if random.random() < 0.25:
                    self.target_heights[i] = random.randint(
                        20, self.canvas_height - 25
                    )
                # smooth lerp to target height
                self.bar_heights[i] += (
                    self.target_heights[i] - self.bar_heights[i]
                ) * 0.25
            else:
                # idle decay when stopped or paused
                self.bar_heights[i] += (5 - self.bar_heights[i]) * 0.15

            h = max(4, self.bar_heights[i])
            x0 = 15 + i * (self.bar_width + self.spacing)
            y0 = self.canvas_height - h
            x1 = x0 + self.bar_width
            y1 = self.canvas_height

            color = colors[int((i / self.num_bars) * len(colors))]

            # draw bar body & top peak cap
            self.canvas_vis.create_rectangle(
                x0, y0, x1, y1, fill=color, outline=""
            )
            self.canvas_vis.create_rectangle(
                x0, y0 - 3, x1, y0, fill="#FFFFFF", outline=""
            )

        # ~30fps frame tick
        self.after(30, self._animate_visualizer)

    # file picking & listbox update
    def load_tracks(self):
        files = filedialog.askopenfilenames(
            title="Select audio files",
            filetypes=[("Audio files", "*.mp3 *.wav *.ogg")],
        )
        if files:
            for file in files:
                if file not in self.playlist:
                    self.playlist.append(file)
                    filename = os.path.basename(file)
                    self.track_listbox.insert(tk.END, f" 🎵 {filename}")

            # auto play first track if idle
            if not self.is_playing:
                self.play_track(0)

    # playback logic
    def play_track(self, index):
        if not self.playlist or index >= len(self.playlist):
            return

        self.current_index = index
        track_path = self.playlist[self.current_index]

        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.btn_play.configure(text="⏸")

            # update title & listbox highlight
            track_name = os.path.basename(track_path)
            self.lbl_current_track.configure(text=track_name)

            self.track_listbox.selection_clear(0, tk.END)
            self.track_listbox.selection_set(self.current_index)
            self.track_listbox.activate(self.current_index)
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

    # track switching
    def next_track(self):
        if self.playlist:
            next_idx = (self.current_index + 1) % len(self.playlist)
            self.play_track(next_idx)

    def prev_track(self):
        if self.playlist:
            prev_idx = (self.current_index - 1) % len(self.playlist)
            self.play_track(prev_idx)

    def on_track_double_click(self, event):
        selection = self.track_listbox.curselection()
        if selection:
            self.play_track(selection[0])

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))


if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()
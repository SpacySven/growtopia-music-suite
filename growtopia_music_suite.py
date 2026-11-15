# -----------------------------------------------------------------------------
# =============================================================================
#   GROWTOPIA MUSIC SUITE
# =============================================================================
#
#   AUTHOR: SpacySven
#   VERSION: 5.0
#
# =============================================================================
# -----------------------------------------------------------------------------

# ---------------------------
# 1. IMPORTS & SETUP
# ---------------------------

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import time
import threading
import random
import os
from pathlib import Path
import math
import platform

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.005
except ImportError:
    pyautogui = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

try:
    import keyboard
except ImportError:
    keyboard = None

try:
    from pynput import mouse as pynput_mouse
except ImportError:
    pynput_mouse = None

# ---------------------------
# 2. VISUAL THEME
# ---------------------------

THEME = {
    "BG": "#07060a",
    "CARD": "#0f0d13",
    "PANEL": "#15121a",
    "ACCENT": "#9b30ff",
    "ACCENT_SOFT": "#7a1ad1",
    "TEXT": "#f3eaff",
    "MUTED": "#9c90a8",
    "PANEL_DARK": "#0b0a0f",
    "ERROR": "#ff6b6b",
    "SUCCESS": "#39d98a",
    "WARNING": "#ffc107",
    "TITLEBAR": "#1F1B24",
    "CLOSE_BTN": "#e81123",
    "VIS_BG": "#000000",
    "VIS_GRID": "#1a1a1a",
    "VIS_NATURAL": "#00e5ff",
    "VIS_SHARP": "#ff4081",
    "VIS_FLAT": "#7c4dff",
    "VIS_RECEPTOR": "#ffffff",
    "VIS_GLOW": "#ffcc00",
    # Dual instance accent colors
    "INST1": "#9b30ff",   # Purple for instance 1
    "INST2": "#ff6b00",   # Orange for instance 2
}

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 11, "bold")
FONT_LARGE = ("Segoe UI", 14, "bold")
FONT_SMALL = ("Segoe UI", 8)

# ---------------------------
# 3. MUSIC CONSTANTS
# ---------------------------

CALIBRATOR_NOTE_ORDER = [
    "c1", "d1", "e1", "f1", "g1", "a", "b", "c", "d", "e", "f", "g", "a2", "b2",
    "c1b", "d1b", "e1b", "f1b", "g1b", "ab", "bb", "cb", "db", "eb", "fb", "gb",
    "a2b", "b2b", "c1#", "d1#", "e1#", "f1#", "g1#", "a#", "b#", "c#", "d#", "e#", "f#", "g#", "a2#", "b2#"
]

DEFAULT_TEMPO = 1.0
MIN_TEMPO = 0.1
MAX_TEMPO = 2.5
TEMPO_STEP = 0.05  # Each step is 0.05x, so 5 steps = 0.25x

COLOR_PALETTE = {
    "BG": "#1E1E1E",
    "BG_LIGHT": "#2D2D2D",
    "FG": "#FFFFFF",
    "NOTE_NATURAL": "#007ACC",
    "NOTE_SHARP": "#DC3545",
    "NOTE_FLAT": "#6f42c1",
    "SUCCESS": "#28A745",
    "ERROR": "#DC3545",
    "PIANO_WHITE_KEY": "#F0F0F0",
    "PIANO_TEXT": "#1E1E1E",
    "PLAYHEAD": "#FFC107",
    "SELECTION": "#007ACC"
}

FONT_FAMILY = "Segoe UI"

PIANO_ROLL_DISPLAY_ORDER = [
    'b2', 'a2', 'g', 'f', 'e', 'd', 'c', 'b', 'a', 'g1', 'f1', 'e1', 'd1', 'c1'
]

MINI_ROLL_COLUMN_MAP = {
    'c1': 0, 'd1': 1, 'e1': 2, 'f1': 3, 'g1': 4, 'a': 5, 'b': 6,
    'c': 7, 'd': 8, 'e': 9, 'f': 10, 'g': 11, 'a2': 12, 'b2': 13
}

NOTE_FREQUENCIES = {
    'c1': 131, 'c1#': 139, 'c1b': 123, 'd1': 147, 'd1#': 156, 'd1b': 139, 'e1': 165, 'e1b': 156,
    'f1': 175, 'f1#': 185, 'f1b': 165, 'g1': 196, 'g1#': 208, 'g1b': 185, 'a': 220, 'a#': 233,
    'ab': 208, 'b': 247, 'bb': 233, 'c': 262, 'c#': 277, 'cb': 247, 'd': 294, 'd#': 311, 'db': 277,
    'e': 330, 'eb': 311, 'f': 349, 'f#': 370, 'fb': 330, 'g': 392, 'g#': 415, 'gb': 370,
    'a2': 440, 'a2#': 466, 'a2b': 415, 'b2': 494, 'b2b': 466, 'b#': 262, 'e#': 349
}

# ---------------------------
# 4. UTILITY FUNCTIONS
# ---------------------------

def safe_json_load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load JSON: {e}")

def perform_click_or_press(mapping):
    if not pyautogui: return
    try:
        if isinstance(mapping, (list, tuple)) and len(mapping) >= 2:
            pyautogui.click(int(mapping[0]), int(mapping[1]))
        elif isinstance(mapping, str):
            pyautogui.press(mapping)
    except Exception:
        pass

def clamp(v, a, b):
    return max(a, min(b, v))

def play_sound_in_thread(freq, duration):
    threading.Thread(target=play_sound, args=(freq, duration), daemon=True).start()

def play_sound(freq, duration):
    if platform.system() == "Windows":
        try:
            import winsound
            winsound.Beep(int(freq), int(duration))
        except Exception:
            pass

# ---------------------------
# 5. CUSTOM UI WIDGETS
# ---------------------------

class ModernTitleBar(tk.Frame):
    def __init__(self, parent, title_text, on_close, on_minimize):
        super().__init__(parent, bg=THEME["TITLEBAR"], height=30)
        self.parent = parent
        self.pack(side="top", fill="x")
        self.pack_propagate(False)
        self._x_axis = 0
        self._y_axis = 0

        self.title_lbl = tk.Label(self, text=title_text, bg=THEME["TITLEBAR"], fg=THEME["TEXT"], font=("Segoe UI", 9, "bold"))
        self.title_lbl.pack(side="left", padx=10)

        self.btn_close = tk.Button(self, text="✕", bg=THEME["TITLEBAR"], fg=THEME["TEXT"], bd=0, font=("Segoe UI", 9), command=on_close, width=4, activebackground="#c42b1c", activeforeground="white")
        self.btn_close.pack(side="right", fill="y")
        self.btn_close.bind("<Enter>", lambda e: self.btn_close.config(bg=THEME["CLOSE_BTN"], fg="white"))
        self.btn_close.bind("<Leave>", lambda e: self.btn_close.config(bg=THEME["TITLEBAR"], fg=THEME["TEXT"]))

        self.btn_min = tk.Button(self, text="—", bg=THEME["TITLEBAR"], fg=THEME["TEXT"], bd=0, font=("Segoe UI", 9), command=on_minimize, width=4, activebackground="#3a3a3a", activeforeground="white")
        self.btn_min.pack(side="right", fill="y")
        self.btn_min.bind("<Enter>", lambda e: self.btn_min.config(bg="#3a3a3a"))
        self.btn_min.bind("<Leave>", lambda e: self.btn_min.config(bg=THEME["TITLEBAR"]))

        self.bind("<Button-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)
        self.title_lbl.bind("<Button-1>", self.start_move)
        self.title_lbl.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self._x_axis = event.x
        self._y_axis = event.y

    def do_move(self, event):
        x = self.parent.winfo_x() + (event.x - self._x_axis)
        y = self.parent.winfo_y() + (event.y - self._y_axis)
        self.parent.geometry(f"+{x}+{y}")


class HamburgerMenu(tk.Menubutton):
    def __init__(self, parent, app_instance):
        super().__init__(parent, text="☰", font=("Segoe UI", 12, "bold"), bg=THEME["CARD"], fg=THEME["TEXT"], activebackground=THEME["PANEL"], activeforeground=THEME["ACCENT"], bd=0, relief="flat", direction="right", width=3)
        self.app = app_instance
        self.menu = tk.Menu(self, tearoff=0, bg=THEME["PANEL"], fg=THEME["TEXT"], activebackground=THEME["ACCENT"], activeforeground="white", font=FONT, relief="flat", bd=1)
        self["menu"] = self.menu
        self.menu.add_checkbutton(label="Loop Song", variable=self.app.looping)
        self.menu.add_separator()
        self.menu.add_checkbutton(label="Always on Top", variable=self.app.always_on_top, command=self.app.toggle_topmost)


class MiniScrollingPianoRoll(tk.Canvas):
    def __init__(self, parent, width=200, height=80, bg=THEME["VIS_BG"]):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=1, highlightbackground=THEME["PANEL"])
        self.width = width
        self.height = height
        self.columns = 14
        self.col_width = width / self.columns
        for i in range(self.columns):
            x = i * self.col_width
            self.create_line(x, 0, x, height, fill=THEME["VIS_GRID"], width=1)
        self.receptor_y = height - 15
        self.receptor_id = self.create_line(0, self.receptor_y, width, self.receptor_y, fill=THEME["VIS_RECEPTOR"], width=2)
        self.song_notes = []
        self.pixels_per_second = 60
        self.visual_latency_offset = 0.25

    def set_song_data(self, song_data):
        self.delete("note_block")
        self.song_notes = []
        if not song_data or not isinstance(song_data, list): return
        for event in song_data:
            note_name = event.get("note", "")
            if not note_name: continue
            base_note = note_name.replace("#", "").replace("b", "")
            accidental = "natural"
            if "#" in note_name: accidental = "sharp"
            elif "b" in note_name: accidental = "flat"
            if base_note in MINI_ROLL_COLUMN_MAP:
                col_idx = MINI_ROLL_COLUMN_MAP[base_note]
                color = THEME["VIS_NATURAL"]
                if accidental == "sharp": color = THEME["VIS_SHARP"]
                elif accidental == "flat": color = THEME["VIS_FLAT"]
                self.song_notes.append({'time': event.get("time", 0), 'col': col_idx, 'color': color, 'drawn': False, 'id': None})
        self.song_notes.sort(key=lambda x: x['time'])

    def update_visuals(self, current_time):
        synced_time = current_time + self.visual_latency_offset
        window_start = synced_time - 0.5
        window_end = synced_time + (self.height / self.pixels_per_second) + 0.5
        hit_detected = False
        for note in self.song_notes:
            t = note['time']
            if t < window_start:
                if note['drawn'] and note['id']:
                    self.delete(note['id']); note['drawn'] = False; note['id'] = None
                continue
            if t > window_end: break
            dt = t - synced_time
            y_center = self.receptor_y - (dt * self.pixels_per_second)
            x1 = note['col'] * self.col_width + 1
            x2 = x1 + self.col_width - 1
            y1, y2 = y_center - 4, y_center + 4
            if not note['drawn']:
                note['id'] = self.create_rectangle(x1, y1, x2, y2, fill=note['color'], outline="", tags="note_block")
                note['drawn'] = True
            else:
                self.coords(note['id'], x1, y1, x2, y2)
            if abs(dt) < 0.04:
                self.itemconfig(note['id'], fill="white"); hit_detected = True
            else:
                self.itemconfig(note['id'], fill=note['color'])
        if hit_detected:
            self.itemconfig(self.receptor_id, fill=THEME["VIS_GLOW"], width=3)
        else:
            self.itemconfig(self.receptor_id, fill=THEME["VIS_RECEPTOR"], width=2)


class SpinningDisc(tk.Canvas):
    def __init__(self, parent, size=28, bg=THEME["CARD"]):
        super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0)
        self.size = size; self.angle = 0; self.is_spinning = False
        self.disc = self.create_oval(3, 3, size-3, size-3, outline=THEME["MUTED"], width=2)
        self.shine = self.create_arc(5, 5, size-5, size-5, start=45, extent=90, style=tk.ARC, outline=THEME["TEXT"], width=1)
        self.spindle = self.create_oval(size/2-2, size/2-2, size/2+2, size/2+2, fill=THEME["PANEL_DARK"], outline="")
    def _rotate(self):
        if not self.is_spinning: return
        self.angle = (self.angle + 10) % 360
        self.itemconfig(self.shine, start=self.angle)
        self.after(50, self._rotate)
    def start(self):
        if not self.is_spinning: self.is_spinning = True; self._rotate()
    def stop(self): self.is_spinning = False


class Marquee(ttk.Frame):
    def __init__(self, parent, width=350, height=36, font=None, fg=None, bg=None, speed_ms=30, step=1):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, width=width, height=height, bg=bg or THEME["CARD"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.font, self.fg, self.bg = font or FONT_BOLD, fg or THEME["TEXT"], bg or THEME["CARD"]
        self.speed_ms, self.step = speed_ms, step
        self.text_id, self.text, self._pos, self._running = None, "", 0, False

    def set_text(self, text):
        self.stop(); self.canvas.delete("all"); self.text = text
        self.text_id = self.canvas.create_text(10, self.canvas.winfo_reqheight()/2, text=self.text, anchor="w", fill=self.fg, font=self.font)
        self._start()

    def _start(self): self._running = True; self.canvas.after(100, self._tick)

    def _tick(self):
        if not self._running: return
        bbox = self.canvas.bbox(self.text_id)
        if not bbox: self.canvas.after(100, self._tick); return
        text_width = bbox[2] - bbox[0]
        canvas_width = self.canvas.winfo_width()
        if text_width < canvas_width:
            self.canvas.coords(self.text_id, (canvas_width - text_width)//2, self.canvas.winfo_height()/2); return
        self.canvas.move(self.text_id, -self.step, 0)
        if bbox[2] < 0: self.canvas.coords(self.text_id, canvas_width + 20, self.canvas.winfo_height()/2)
        self.canvas.after(self.speed_ms, self._tick)

    def stop(self): self._running = False


class ToolTip:
    def __init__(self, widget, text):
        self.widget, self.text, self.tw = widget, text, None
        widget.bind("<Enter>", self._show); widget.bind("<Leave>", self._hide)
    def _show(self, _ev=None):
        if self.tw: return
        x, y = self.widget.winfo_rootx() + 20, self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tw = tw = tk.Toplevel(self.widget); tw.wm_overrideredirect(True); tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, bg="#121018", fg=THEME["MUTED"], font=("Segoe UI", 9), bd=0, padx=6, pady=4).pack()
    def _hide(self, _ev=None):
        if self.tw: self.tw.destroy(); self.tw = None


class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, color, hover_color, text_color, text, command):
        super().__init__(parent, borderwidth=0, relief="flat", highlightthickness=0, bg=parent.cget("bg"))
        self.command = command
        self.config(width=width, height=height, cursor="hand2")
        self.color, self.hover_color = color, hover_color
        self.rect = self._create_rounded_rect(0, 0, width, height, cornerradius, fill=color, outline="")
        self.create_text(width/2, height/2, text=text, fill=text_color, font=FONT_BOLD)
        self.bind("<Enter>", self._on_enter); self.bind("<Leave>", self._on_leave); self.bind("<Button-1>", self._on_click)
    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)
    def _on_enter(self, _e): self.itemconfig(self.rect, fill=self.hover_color)
    def _on_leave(self, _e): self.itemconfig(self.rect, fill=self.color)
    def _on_click(self, _e):
        if self.command: self.command()

# ---------------------------
# 6. PIANO ROLL EDITOR
# ---------------------------

class PianoRollEditor:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Piano Roll Editor")
        self.window.geometry("1200x700")
        self.window.configure(bg=COLOR_PALETTE["BG"])
        self.window.transient(parent)
        self.window.grab_set()
        self.cell_width, self.cell_height = 40, 25
        self.notes_data = {}
        self.rows = len(PIANO_ROLL_DISPLAY_ORDER)
        self.cols = 640
        self.is_animating = False
        self.playback_line = None
        self.playback_map = {}
        self.accidental_mode = tk.StringVar(value="natural")
        self.selection_rect = None
        self.selection_start_cell = None
        self.selection_end_cell = None
        self.clipboard_data = []
        self.last_mouse_grid_pos = (0, 0)
        self._create_widgets()
        self._bind_events()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.after(100, self.draw_piano_grid)

    def _create_widgets(self):
        control_frame = tk.Frame(self.window, bg=COLOR_PALETTE["BG"])
        control_frame.pack(fill="x", padx=10, pady=5)
        style = ttk.Style(self.window)
        style.configure('Tool.TRadiobutton', background=COLOR_PALETTE["BG_LIGHT"], foreground=COLOR_PALETTE["FG"], font=(FONT_FAMILY, 9, "bold"), padding=8)
        style.map('Tool.TRadiobutton', background=[('active', COLOR_PALETTE["BG"]), ('selected', COLOR_PALETTE["NOTE_NATURAL"])])
        ttk.Radiobutton(control_frame, text="Natural", variable=self.accidental_mode, value="natural", style='Tool.TRadiobutton').pack(side="left", padx=2)
        style.map('Sharp.Tool.TRadiobutton', background=[('selected', COLOR_PALETTE["NOTE_SHARP"])])
        ttk.Radiobutton(control_frame, text="Sharp (#)", variable=self.accidental_mode, value="sharp", style='Sharp.Tool.TRadiobutton').pack(side="left", padx=2)
        style.map('Flat.Tool.TRadiobutton', background=[('selected', COLOR_PALETTE["NOTE_FLAT"])])
        ttk.Radiobutton(control_frame, text="Flat (b)", variable=self.accidental_mode, value="flat", style='Flat.Tool.TRadiobutton').pack(side="left", padx=2)
        tk.Button(control_frame, text="↑ Pitch", command=lambda: self.transpose(1), bg=THEME["PANEL"], fg=THEME["ACCENT"], font=(FONT_FAMILY, 8, "bold")).pack(side="left", padx=10)
        tk.Button(control_frame, text="↓ Pitch", command=lambda: self.transpose(-1), bg=THEME["PANEL"], fg=THEME["ACCENT"], font=(FONT_FAMILY, 8, "bold")).pack(side="left", padx=2)
        tk.Button(control_frame, text="Load Song", command=self.load_song, bg="#5A6268", fg="white", font=(FONT_FAMILY, 9, "bold")).pack(side="right", padx=(10, 5))
        tk.Button(control_frame, text="Save Song", command=self.save_song, bg=COLOR_PALETTE["SUCCESS"], fg="white", font=(FONT_FAMILY, 9, "bold")).pack(side="right", padx=5)
        tk.Button(control_frame, text="Clear All", command=self.clear_all, bg=COLOR_PALETTE["ERROR"], fg="white", font=(FONT_FAMILY, 9, "bold")).pack(side="right", padx=5)
        self.play_btn = tk.Button(control_frame, text="▶ Play", command=self.start_animation, bg=COLOR_PALETTE["NOTE_NATURAL"], fg="white", font=(FONT_FAMILY, 9, "bold"))
        self.play_btn.pack(side="right", padx=(10, 2))
        self.stop_btn = tk.Button(control_frame, text="■ Stop", command=self.stop_animation, bg=COLOR_PALETTE["ERROR"], fg="white", font=(FONT_FAMILY, 9, "bold"), state=tk.DISABLED)
        self.stop_btn.pack(side="right", padx=2)
        tk.Label(control_frame, text="BPM:", bg=COLOR_PALETTE["BG"], fg="white").pack(side="right", padx=(10, 0))
        self.bpm_var = tk.IntVar(value=50)
        tk.Entry(control_frame, textvariable=self.bpm_var, width=5, bg=COLOR_PALETTE["BG_LIGHT"], fg="white", insertbackground="white").pack(side="right")
        ruler_frame = tk.Frame(self.window, bg=COLOR_PALETTE["BG"]); ruler_frame.pack(fill="x", padx=10, pady=(0, 2))
        tk.Label(ruler_frame, width=14, bg=COLOR_PALETTE["PIANO_WHITE_KEY"]).pack(side="left")
        self.ruler_canvas = tk.Canvas(ruler_frame, bg=COLOR_PALETTE["BG_LIGHT"], height=20, highlightthickness=0)
        self.ruler_canvas.pack(side="left", fill="x", expand=True)
        canvas_frame = tk.Frame(self.window, bg=COLOR_PALETTE["BG"]); canvas_frame.pack(fill="both", expand=True, padx=10)
        self.label_canvas = tk.Canvas(canvas_frame, width=100, bg=COLOR_PALETTE["PIANO_WHITE_KEY"], highlightthickness=0)
        self.label_canvas.pack(side="left", fill="y")
        self.grid_canvas = tk.Canvas(canvas_frame, bg=COLOR_PALETTE["BG_LIGHT"], highlightthickness=0)
        self.grid_canvas.pack(side="left", fill="both", expand=True)
        self.y_scroll = tk.Scrollbar(canvas_frame, orient="vertical", command=self._on_vertical_scroll)
        self.y_scroll.pack(side="right", fill="y")
        self.x_scroll = tk.Scrollbar(self.window, orient="horizontal", command=self._on_horizontal_scroll)
        self.x_scroll.pack(side="bottom", fill="x", padx=10, pady=(0, 5))
        self.grid_canvas.config(xscrollcommand=self.x_scroll.set, yscrollcommand=self.y_scroll.set)
        self.ruler_canvas.config(xscrollcommand=self.x_scroll.set)
        self.label_canvas.config(yscrollcommand=self.y_scroll.set)
        self.status_var = tk.StringVar(value="Ready. Shift+Drag to select. Ctrl+C to copy, Ctrl+V to paste.")
        tk.Label(self.window, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg=COLOR_PALETTE["BG_LIGHT"], fg=COLOR_PALETTE["FG"]).pack(side=tk.BOTTOM, fill=tk.X)

    def _on_vertical_scroll(self, *args): self.label_canvas.yview(*args); self.grid_canvas.yview(*args)
    def _on_horizontal_scroll(self, *args): self.grid_canvas.xview(*args); self.ruler_canvas.xview(*args)

    def draw_piano_grid(self):
        self.label_canvas.delete("all"); self.grid_canvas.delete("grid_line", "note_rect"); self.ruler_canvas.delete("all")
        total_grid_width = self.cols * self.cell_width
        total_grid_height = self.rows * self.cell_height
        self.label_canvas.configure(scrollregion=(0, 0, 100, total_grid_height))
        self.grid_canvas.configure(scrollregion=(0, 0, total_grid_width, total_grid_height))
        self.ruler_canvas.configure(scrollregion=(0, 0, total_grid_width, 20))
        for row, note in enumerate(PIANO_ROLL_DISPLAY_ORDER):
            y = row * self.cell_height
            self.label_canvas.create_rectangle(0, y, 100, y + self.cell_height, fill=COLOR_PALETTE["PIANO_WHITE_KEY"], outline="#999")
            self.label_canvas.create_text(50, y + self.cell_height / 2, text=note.upper(), font=(FONT_FAMILY, 10, "bold"), fill=COLOR_PALETTE["PIANO_TEXT"])
        for col in range(self.cols + 1):
            x, is_beat = col * self.cell_width, col % 4 == 0
            self.grid_canvas.create_line(x, 0, x, total_grid_height, fill="#888" if is_beat else "#444", tags="grid_line")
            if is_beat:
                self.ruler_canvas.create_line(x, 10, x, 20, fill="#AAA")
                self.ruler_canvas.create_text(x + 2, 9, text=str((col // 4) + 1), anchor='nw', font=(FONT_FAMILY, 8), fill="#AAA")
        for row in range(self.rows): self.grid_canvas.create_line(0, row * self.cell_height, total_grid_width, row * self.cell_height, fill="#555", tags="grid_line")
        for (col, row_note), accidental in self.notes_data.items():
            try:
                row_index = PIANO_ROLL_DISPLAY_ORDER.index(row_note)
                y, x = row_index * self.cell_height, col * self.cell_width
                color, note_text = {"natural": (COLOR_PALETTE["NOTE_NATURAL"], ""), "sharp": (COLOR_PALETTE["NOTE_SHARP"], "#"), "flat": (COLOR_PALETTE["NOTE_FLAT"], "b")}.get(accidental)
                self.grid_canvas.create_rectangle(x+1, y+1, x + self.cell_width-1, y + self.cell_height-1, fill=color, outline="white", width=1.5, tags="note_rect")
                self.grid_canvas.create_text(x + self.cell_width/2, y + self.cell_height/2, text=f"{row_note[0].upper()}{note_text}", font=(FONT_FAMILY, 9, "bold"), fill="white", tags="note_rect")
            except ValueError: continue

    def _bind_events(self):
        self.grid_canvas.bind("<ButtonPress-1>", self.on_press)
        self.grid_canvas.bind("<Button-3>", self.on_right_click)
        self.grid_canvas.bind("<Shift-ButtonPress-1>", self.on_selection_start)
        self.grid_canvas.bind("<Shift-B1-Motion>", self.on_selection_drag)
        self.grid_canvas.bind("<Motion>", self.on_mouse_move)
        self.window.bind("<Control-c>", self.copy_selection)
        self.window.bind("<Control-v>", self.paste_selection)
        for widget in [self.grid_canvas, self.label_canvas]:
            widget.bind("<MouseWheel>", self._on_mousewheel)
            widget.bind("<Button-4>", self._on_mousewheel)
            widget.bind("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        delta = -1 if event.num == 5 or event.delta < 0 else 1
        self.grid_canvas.yview_scroll(delta, "units"); self.label_canvas.yview_scroll(delta, "units"); return "break"

    def get_cell_from_event(self, event):
        x, y = self.grid_canvas.canvasx(event.x), self.grid_canvas.canvasy(event.y)
        col, row_idx = int(x // self.cell_width), int(y // self.cell_height)
        return (col, row_idx) if 0 <= col < self.cols and 0 <= row_idx < self.rows else (None, None)

    def on_press(self, event): self.clear_selection(); self.toggle_note(*self.get_cell_from_event(event))
    def on_right_click(self, event): self.clear_selection(); self.toggle_note(*self.get_cell_from_event(event), force_remove=True)

    def toggle_note(self, col, row_idx, force_remove=False):
        if col is None or row_idx is None: return
        row_note = PIANO_ROLL_DISPLAY_ORDER[row_idx]; key = (col, row_note)
        if force_remove or key in self.notes_data:
            if key in self.notes_data: del self.notes_data[key]; play_sound_in_thread(220, 75)
        else:
            accidental = self.accidental_mode.get(); self.notes_data[key] = accidental
            final_note = row_note + ("#" if accidental == "sharp" else "b" if accidental == "flat" else "")
            play_sound_in_thread(NOTE_FREQUENCIES.get(final_note, 440), 75)
        self.draw_piano_grid()

    def on_mouse_move(self, event): self.last_mouse_grid_pos = self.get_cell_from_event(event)
    def on_selection_start(self, event):
        self.clear_selection(); self.selection_start_cell = self.get_cell_from_event(event)
        if self.selection_start_cell[0] is not None:
            x0, y0 = self.selection_start_cell[0] * self.cell_width, self.selection_start_cell[1] * self.cell_height
            self.selection_rect = self.grid_canvas.create_rectangle(x0, y0, x0+1, y0+1, fill=COLOR_PALETTE["SELECTION"], stipple="gray25", outline=COLOR_PALETTE["SELECTION"])

    def on_selection_drag(self, event):
        if not self.selection_rect: return
        self.selection_end_cell = self.get_cell_from_event(event)
        if self.selection_end_cell[0] is not None:
            start_col, start_row = self.selection_start_cell; end_col, end_row = self.selection_end_cell
            x0, y0 = min(start_col, end_col) * self.cell_width, min(start_row, end_row) * self.cell_height
            x1, y1 = (max(start_col, end_col)+1) * self.cell_width, (max(start_row, end_row)+1) * self.cell_height
            self.grid_canvas.coords(self.selection_rect, x0, y0, x1, y1)

    def clear_selection(self):
        if self.selection_rect: self.grid_canvas.delete(self.selection_rect); self.selection_rect = None
        self.selection_start_cell, self.selection_end_cell = None, None

    def copy_selection(self, event=None):
        if not self.selection_start_cell or not self.selection_end_cell: return self.status_var.set("Copy failed: No selection.")
        self.clipboard_data.clear()
        start_col = min(self.selection_start_cell[0], self.selection_end_cell[0]); end_col = max(self.selection_start_cell[0], self.selection_end_cell[0])
        start_row = min(self.selection_start_cell[1], self.selection_end_cell[1]); end_row = max(self.selection_start_cell[1], self.selection_end_cell[1])
        for (col, note_name), accidental in self.notes_data.items():
            try:
                row_idx = PIANO_ROLL_DISPLAY_ORDER.index(note_name)
                if start_col <= col <= end_col and start_row <= row_idx <= end_row: self.clipboard_data.append((col - start_col, row_idx - start_row, accidental))
            except ValueError: continue
        self.status_var.set(f"Copied {len(self.clipboard_data)} notes to clipboard.")

    def paste_selection(self, event=None):
        if not self.clipboard_data: return self.status_var.set("Paste failed: Clipboard is empty.")
        paste_col, paste_row_idx = self.last_mouse_grid_pos
        if paste_col is None: return self.status_var.set("Paste failed: Mouse is outside the grid.")
        for rel_col, rel_row_idx, accidental in self.clipboard_data:
            new_col, new_row_idx = paste_col + rel_col, paste_row_idx + rel_row_idx
            if 0 <= new_col < self.cols and 0 <= new_row_idx < self.rows: self.notes_data[(new_col, PIANO_ROLL_DISPLAY_ORDER[new_row_idx])] = accidental
        self.draw_piano_grid(); self.status_var.set(f"Pasted {len(self.clipboard_data)} notes.")

    def transpose(self, direction):
        if not self.notes_data: return
        new_data = {}; count = 0
        for (col, row_note), accidental in self.notes_data.items():
            try:
                current_idx = PIANO_ROLL_DISPLAY_ORDER.index(row_note)
                new_idx = current_idx - direction
                if 0 <= new_idx < len(PIANO_ROLL_DISPLAY_ORDER): new_data[(col, PIANO_ROLL_DISPLAY_ORDER[new_idx])] = accidental; count += 1
            except ValueError: continue
        self.notes_data = new_data; self.draw_piano_grid(); self.status_var.set(f"Transposed {count} notes.")

    def start_animation(self):
        if self.is_animating: return
        self.is_animating = True; self.play_btn.config(state=tk.DISABLED); self.stop_btn.config(state=tk.NORMAL)
        self.playback_map = {col: [] for col in range(self.cols)}
        for (col, row_note), accidental in self.notes_data.items(): self.playback_map[col].append(row_note + ("#" if accidental == "sharp" else "b" if accidental == "flat" else ""))
        if self.playback_line: self.grid_canvas.delete(self.playback_line)
        self.playback_line = self.grid_canvas.create_line(0, 0, 0, self.rows * self.cell_height, fill=COLOR_PALETTE["PLAYHEAD"], width=3, stipple="gray50")
        threading.Thread(target=self._animate, daemon=True).start()

    def _animate(self):
        try: bpm = self.bpm_var.get(); assert bpm > 0
        except: bpm = 50
        seconds_per_col, start_time, last_played_col = (60.0 / bpm) / 4, time.time(), -1
        while self.is_animating:
            elapsed = time.time() - start_time
            if elapsed > self.cols * seconds_per_col: break
            current_col_float = elapsed / seconds_per_col
            self.grid_canvas.coords(self.playback_line, current_col_float * self.cell_width, 0, current_col_float * self.cell_width, self.rows * self.cell_height)
            if (current_col_int := int(current_col_float)) > last_played_col:
                for note in self.playback_map.get(current_col_int, []): play_sound_in_thread(NOTE_FREQUENCIES.get(note, 440), 100)
                last_played_col = current_col_int
            time.sleep(0.01)
        self.stop_animation()

    def stop_animation(self):
        self.is_animating = False
        try:
            self.play_btn.config(state=tk.NORMAL); self.stop_btn.config(state=tk.DISABLED)
            self.grid_canvas.delete(self.playback_line); self.playback_line = None
        except tk.TclError: pass

    def load_song(self):
        if self.notes_data and not messagebox.askyesno("Load Song", "This will clear the current song. Continue?", parent=self.window): return
        if not (path := filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], parent=self.window)): return
        try:
            with open(path) as f: song_data = json.load(f)
            seconds_per_col = (60.0 / self.bpm_var.get()) / 4; self.clear_all(confirm=False)
            for event in song_data:
                col = int((event["time"] / seconds_per_col) + 0.5); note = event["note"]; row_note, accidental = note, "natural"
                if note.endswith('#'): row_note, accidental = note[:-1], "sharp"
                elif note.endswith('b'): row_note, accidental = note[:-1], "flat"
                if row_note in PIANO_ROLL_DISPLAY_ORDER: self.notes_data[(col, row_note)] = accidental
            self.draw_piano_grid(); messagebox.showinfo("Success", f"Loaded {len(song_data)} notes.", parent=self.window)
        except Exception as e: messagebox.showerror("Error", f"Failed to load song:\n{e}", parent=self.window)

    def save_song(self):
        seconds_per_col = (60.0 / self.bpm_var.get()) / 4
        song_data = [{"time": round(col * seconds_per_col, 4), "note": row_note + ("#" if acc == "sharp" else "b" if acc == "flat" else "")} for (col, row_note), acc in self.notes_data.items()]
        if not song_data: return messagebox.showinfo("Empty", "No notes to save.", parent=self.window)
        song_data.sort(key=lambda e: e['time'])
        if path := filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], parent=self.window):
            with open(path, "w") as f: json.dump(song_data, f, indent=2); messagebox.showinfo("Saved", f"Saved {len(song_data)} notes.", parent=self.window)

    def on_close(self): self.stop_animation(); self.window.destroy()
    def clear_all(self, confirm=True):
        if confirm and not messagebox.askyesno("Confirm", "Clear all notes?", parent=self.window): return
        self.notes_data.clear(); self.clear_selection(); self.draw_piano_grid()


# ---------------------------
# 7. INSTANCE PANEL (for dual-instance mode)
# ---------------------------

class InstancePanel(tk.LabelFrame):
    """
    A self-contained playback panel for one Growtopia instance.
    Used when Dual Mode is active.
    """
    def __init__(self, parent, instance_num, shared_tempo_var, shared_tempo_ref, song_dir_var, map_dir_var, accent_color):
        label_text = f"  Instance {instance_num}  "
        super().__init__(parent, text=label_text, bg=THEME["CARD"], fg=accent_color,
                         font=("Segoe UI", 9, "bold"), bd=1, relief="groove",
                         highlightbackground=accent_color, highlightthickness=1)
        self.instance_num = instance_num
        self.accent = accent_color
        self.shared_tempo_var = shared_tempo_var
        self.shared_tempo_ref = shared_tempo_ref
        self.song_dir_var = song_dir_var
        self.map_dir_var = map_dir_var

        self.note_map = {}
        self.song = []
        self.song_type = None
        self.is_playing = False
        self.is_paused = False
        self.song_duration = 0
        self.playback_start_offset = 0
        self.is_seeking = False
        self.play_thread = None

        # ── Conductor-sync support ──
        # When True, this panel's Start/Pause/Stop buttons are being driven
        # by the main app's synchronized dual-instance conductor thread
        # instead of this panel's own standalone playback thread.
        self.conductor_mode_active = False
        # Callback the main app wires up to route pause presses to the
        # conductor when conductor_mode_active is True.
        self.app_conductor_pause_cb = None

        self._build()

    def _build(self):
        # Song row
        row1 = tk.Frame(self, bg=THEME["CARD"]); row1.pack(fill="x", padx=6, pady=(4, 2))
        tk.Button(row1, text="Load Song", bg=self.accent, fg=THEME["BG"], font=FONT_BOLD, bd=0, relief="flat",
                  cursor="hand2", command=self.load_song, width=10).pack(side="left", padx=(0, 4))
        self.song_label = tk.Label(row1, text="No song loaded", bg=THEME["CARD"], fg=THEME["MUTED"],
                                   font=FONT_SMALL, anchor="w")
        self.song_label.pack(side="left", fill="x", expand=True)

        # Map row
        row2 = tk.Frame(self, bg=THEME["CARD"]); row2.pack(fill="x", padx=6, pady=2)
        tk.Button(row2, text="Load Map", bg=THEME["PANEL"], fg=self.accent, font=FONT_BOLD, bd=0, relief="flat",
                  cursor="hand2", command=self.load_note_map, width=10).pack(side="left", padx=(0, 4))
        self.map_label = tk.Label(row2, text="No map loaded", bg=THEME["CARD"], fg=THEME["MUTED"],
                                  font=FONT_SMALL, anchor="w")
        self.map_label.pack(side="left", fill="x", expand=True)

        # Controls row
        ctrl = tk.Frame(self, bg=THEME["CARD"]); ctrl.pack(fill="x", padx=6, pady=(4, 2))
        self.btn_start = tk.Button(ctrl, text="▶ START", bg=self.accent, fg=THEME["BG"], font=FONT_BOLD, bd=0,
                                   relief="flat", cursor="hand2", command=self.start_playing, width=9)
        self.btn_start.pack(side="left", padx=(0, 3))
        self.btn_pause = tk.Button(ctrl, text="⏸ PAUSE", bg=THEME["WARNING"], fg="#000", font=FONT_BOLD, bd=0,
                                   relief="flat", cursor="hand2", command=self.toggle_pause, state=tk.DISABLED, width=9)
        self.btn_pause.pack(side="left", padx=3)
        self.btn_stop = tk.Button(ctrl, text="■ STOP", bg=THEME["PANEL"], fg=THEME["TEXT"], font=FONT_BOLD, bd=0,
                                  relief="flat", cursor="hand2", command=self.stop_playing, state=tk.DISABLED, width=9)
        self.btn_stop.pack(side="left", padx=3)

        # Status
        self.status_label = tk.Label(self, text="Status: Ready", bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT_SMALL)
        self.status_label.pack(fill="x", padx=8, pady=(2, 4))
        self.counter_label = tk.Label(self, text="Played: 0 / 0", bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT_SMALL)
        self.counter_label.pack(fill="x", padx=8, pady=(0, 6))

    def load_song(self):
        init_dir = self.song_dir_var.get() or "/"
        path = filedialog.askopenfilename(title=f"Load Song — Instance {self.instance_num}",
                                          initialdir=init_dir,
                                          filetypes=[("JSON files", "*.json")])
        if not path: return
        try:
            data = safe_json_load(path)
            if not isinstance(data, list) or not data: raise RuntimeError("Song must be a non-empty list.")
            first = data[0]
            if isinstance(first, str): self.song_type = "notes"
            elif "position" in first: self.song_type = "recorded"
            elif "note" in first: self.song_type = "timed-notes"
            else: raise RuntimeError("Unknown song format.")
            self.song = data if self.song_type != "timed-notes" else sorted(data, key=lambda x: x.get("time", 0))
            self.song_label.config(text=os.path.basename(path), fg=THEME["SUCCESS"])
            self.song_duration = self._calculate_song_duration()
            self.counter_label.config(text=f"Played: 0 / {len(self.song)}")
            self.status_label.config(text="Status: Song loaded", fg=THEME["SUCCESS"])
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def load_note_map(self):
        init_dir = self.map_dir_var.get() or "/"
        path = filedialog.askopenfilename(title=f"Load Note Map — Instance {self.instance_num}",
                                          initialdir=init_dir,
                                          filetypes=[("JSON files", "*.json")])
        if not path: return
        try:
            self.note_map = dict(safe_json_load(path))
            self.map_label.config(text=os.path.basename(path), fg=THEME["SUCCESS"])
            self.status_label.config(text=f"Map loaded: {len(self.note_map)} entries", fg=THEME["SUCCESS"])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _calculate_song_duration(self):
        if not self.song: return 0
        if self.song_type in ("timed-notes", "recorded"): return self.song[-1].get("time", 0)
        elif self.song_type == "notes": return len(self.song) * 0.15 / DEFAULT_TEMPO
        return 0

    def get_merged_events(self):
        """
        Returns this instance's song as a flat, time-ordered list of dicts:
        {'time': float, 'type': 'note'|'position', 'value': ...}
        'time' is expressed in nominal (tempo=1.0) song-time units, exactly
        like the timing already used by the standalone playback thread —
        this keeps behavior identical, it's just exposed so the main app's
        synchronized dual-instance conductor can merge both instances'
        events onto one shared clock instead of running two separate
        threads that can drift apart.
        """
        events = []
        if not self.song:
            return events
        if self.song_type == "notes":
            for idx, note in enumerate(self.song):
                events.append({'time': idx * 0.15, 'type': 'note', 'value': note})
        elif self.song_type == "timed-notes":
            for ev in self.song:
                events.append({'time': ev.get('time', 0), 'type': 'note', 'value': ev.get('note')})
        elif self.song_type == "recorded":
            for ev in self.song:
                events.append({'time': ev.get('time', 0), 'type': 'position', 'value': ev.get('position')})
        events.sort(key=lambda e: e['time'])
        return events

    def _set_conductor_ui(self, status_text, color, playing):
        """Update this panel's buttons/status without touching its own
        standalone playback thread — used by the conductor."""
        try:
            self.status_label.config(text=status_text, fg=color)
            if playing:
                self.btn_start.config(state="disabled")
                self.btn_stop.config(state="normal")
                self.btn_pause.config(state="normal", text="⏸ PAUSE", bg=THEME["WARNING"])
            else:
                self.btn_start.config(state="normal")
                self.btn_stop.config(state="disabled")
                self.btn_pause.config(state="disabled", text="⏸ PAUSE", bg=THEME["WARNING"])
        except tk.TclError:
            pass

    def toggle_pause(self):
        # If the main app's synchronized conductor is currently driving both
        # instances together, route the pause press there instead of pausing
        # only this panel's (inactive) standalone thread.
        if self.conductor_mode_active and self.app_conductor_pause_cb:
            self.app_conductor_pause_cb()
            return
        if not self.is_playing: return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.config(text="▶ RESUME", bg=THEME["SUCCESS"])
            self.status_label.config(text="Status: Paused", fg=THEME["WARNING"])
        else:
            self.btn_pause.config(text="⏸ PAUSE", bg=THEME["WARNING"])
            self.status_label.config(text="Status: Playing...", fg=THEME["SUCCESS"])

    def start_playing(self, start_offset=None):
        if self.is_playing: return
        if not self.song:
            messagebox.showwarning("No Song", f"Instance {self.instance_num}: Load a song first."); return
        if self.song_type in ("notes", "timed-notes") and not self.note_map:
            messagebox.showwarning("No Note Map", f"Instance {self.instance_num}: This song requires a Note Map."); return
        self.is_playing = True; self.is_paused = False
        if start_offset is None: start_offset = self.playback_start_offset
        self.playback_start_offset = start_offset
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_pause.config(state="normal", text="⏸ PAUSE", bg=THEME["WARNING"])
        self.status_label.config(text="Status: Playing...", fg=THEME["SUCCESS"])
        self.play_thread = threading.Thread(target=self._play_thread, args=(start_offset,), daemon=True)
        self.play_thread.start()

    def stop_playing(self, is_seeking=False):
        if not self.is_playing: return
        self.is_playing = False; self.is_paused = False
        if not is_seeking:
            self.playback_start_offset = 0
            self.status_label.config(text="Status: Stopped", fg=THEME["MUTED"])
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.btn_pause.config(state="disabled", text="⏸ PAUSE", bg=THEME["WARNING"])

    def _play_thread(self, start_offset=0):
        tempo = self.shared_tempo_ref[0]
        start_time = time.perf_counter() - (start_offset / tempo)
        start_index = 0
        if self.song_type in ("timed-notes", "recorded"):
            for i, ev in enumerate(self.song):
                if ev.get("time", 0) >= start_offset: start_index = i; break
        elif self.song_type == "notes":
            dur = self._calculate_song_duration()
            start_index = int((start_offset / dur) * len(self.song)) if dur > 0 else 0
            start_index = max(0, min(start_index, len(self.song) - 1))
        i = start_index; total_notes = len(self.song)
        while i < total_notes and self.is_playing:
            tempo = self.shared_tempo_ref[0]
            if self.is_paused:
                pause_start = time.perf_counter()
                while self.is_paused and self.is_playing: time.sleep(0.05)
                start_time += (time.perf_counter() - pause_start)
                if not self.is_playing: break
            ev = self.song[i]
            current_audio_time = (time.perf_counter() - start_time) * tempo
            self.counter_label.config(text=f"Played: {i+1} / {total_notes}")
            if self.song_type == "notes":
                if mapping := self.note_map.get(ev): perform_click_or_press(mapping)
                time.sleep(0.15 / tempo); i += 1
            else:
                target_time = ev.get("time", 0)
                if current_audio_time >= target_time:
                    key_field = "position" if self.song_type == "recorded" else "note"
                    if key_field == "position":
                        if pos := ev.get("position"): perform_click_or_press(pos)
                    else:
                        if (note := ev.get("note")) and (mapping := self.note_map.get(note)): perform_click_or_press(mapping)
                    i += 1
                else:
                    time.sleep(0.001)
        if self.is_playing:
            self.is_playing = False
            self.status_label.config(text="Status: Finished", fg=THEME["MUTED"])
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.btn_pause.config(state="disabled")


# ---------------------------
# 8. MAIN APP CONTROLLER
# ---------------------------

class GrowtopiaMusicSuite:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry("700x680")
        self.root.configure(bg=THEME["BG"])
        self.root.resizable(False, False)

        # ── Shared state ──
        self.note_map, self.song, self.song_type = {}, [], None
        self.is_playing, self.is_paused = False, False
        self.tempo = DEFAULT_TEMPO
        # shared_tempo_ref is a mutable list so both instance panels read live value
        self.shared_tempo_ref = [DEFAULT_TEMPO]

        self.looping = tk.BooleanVar(value=False)
        self.always_on_top = tk.BooleanVar(value=False)

        self.song_duration = 0
        self.is_seeking = False
        self.playback_start_offset = 0

        # ── Dual-instance synchronized conductor state ──
        # A single thread drives BOTH instances off one shared clock so that
        # clicks for instance 1 and instance 2 can never drift apart the way
        # two independent threads could (Python's GIL forces threads to take
        # turns, and there's only ever one real OS mouse cursor to move, so
        # "two parallel threads" was never really parallel to begin with).
        self._conductor_running = False
        self._conductor_paused = False
        self.conductor_thread = None

        # ── Default directory paths (configurable) ──
        # Song dir defaults to Documents/ETC (user fills in their own username)
        docs = Path.home() / "Documents" / "ETC"
        self.song_dir = tk.StringVar(value=str(docs) if docs.exists() else str(Path.home()))
        self.map_dir = tk.StringVar(value=str(docs) if docs.exists() else str(Path.home()))

        # ── Dual mode flag ──
        self.dual_mode = tk.BooleanVar(value=False)

        self._setup_style()
        self._build_ui()
        self._setup_hotkeys()

    def _setup_style(self):
        style = ttk.Style(self.root)
        try: style.theme_use("clam")
        except Exception: pass
        style.configure("Card.TFrame", background=THEME["CARD"])
        style.configure("Panel.TFrame", background=THEME["PANEL"])
        style.configure("Accent.TButton", background=THEME["ACCENT"], foreground=THEME["BG"], font=FONT_BOLD)
        style.configure("Horizontal.TScale", troughcolor=THEME["PANEL_DARK"], background=THEME["ACCENT"])

    def _build_ui(self):
        # Title bar
        self.title_bar = ModernTitleBar(self.root, "Growtopia Music Suite — Neon EXE v5.0", self.close_app, self.minimize_app)

        # Header
        header = tk.Frame(self.root, bg=THEME["BG"]); header.pack(pady=(10, 5))
        tk.Label(header, text="Growtopia Music Suite", font=FONT_LARGE, foreground=THEME["TEXT"], bg=THEME["BG"]).pack()

        # Main card
        card = tk.Frame(self.root, bg=THEME["CARD"]); card.pack(padx=20, pady=6, fill="both", expand=True)

        # ── Path config row ──
        path_frame = tk.Frame(card, bg=THEME["CARD"]); path_frame.pack(fill="x", padx=12, pady=(10, 4))

        # Song dir
        tk.Label(path_frame, text="Song Dir:", bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT_SMALL).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.song_dir_entry = tk.Entry(path_frame, textvariable=self.song_dir, bg=THEME["PANEL"], fg=THEME["TEXT"],
                                        insertbackground=THEME["TEXT"], font=FONT_SMALL, relief="flat", width=34)
        self.song_dir_entry.grid(row=0, column=1, sticky="ew", padx=(0, 4))
        tk.Button(path_frame, text="Browse", bg=THEME["PANEL"], fg=THEME["ACCENT"], font=FONT_SMALL, bd=0, relief="flat",
                  cursor="hand2", command=lambda: self._browse_dir(self.song_dir)).grid(row=0, column=2, padx=(0, 10))

        # Map dir
        tk.Label(path_frame, text="Map Dir:", bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT_SMALL).grid(row=1, column=0, sticky="w", padx=(0, 4), pady=(4, 0))
        self.map_dir_entry = tk.Entry(path_frame, textvariable=self.map_dir, bg=THEME["PANEL"], fg=THEME["TEXT"],
                                       insertbackground=THEME["TEXT"], font=FONT_SMALL, relief="flat", width=34)
        self.map_dir_entry.grid(row=1, column=1, sticky="ew", padx=(0, 4), pady=(4, 0))
        tk.Button(path_frame, text="Browse", bg=THEME["PANEL"], fg=THEME["ACCENT"], font=FONT_SMALL, bd=0, relief="flat",
                  cursor="hand2", command=lambda: self._browse_dir(self.map_dir)).grid(row=1, column=2, padx=(0, 10), pady=(4, 0))
        path_frame.columnconfigure(1, weight=1)

        # ── Dual mode toggle ──
        mode_row = tk.Frame(card, bg=THEME["CARD"]); mode_row.pack(fill="x", padx=12, pady=(4, 0))
        self.dual_toggle_btn = tk.Button(mode_row, text="☐  Dual Instance Mode", bg=THEME["PANEL"], fg=THEME["MUTED"],
                                          font=FONT_BOLD, bd=0, relief="flat", cursor="hand2",
                                          command=self._toggle_dual_mode)
        self.dual_toggle_btn.pack(side="left")
        ToolTip(self.dual_toggle_btn, "Run two songs at once — one per account.\nMouse switches rapidly between click positions.")

        # ── SINGLE mode frame ──
        self.single_frame = tk.Frame(card, bg=THEME["CARD"]); self.single_frame.pack(fill="both", expand=True)
        self._build_single_ui(self.single_frame)

        # ── DUAL mode frame (hidden initially) ──
        self.dual_frame = tk.Frame(card, bg=THEME["CARD"]); # not packed yet
        self._build_dual_ui(self.dual_frame)

        # Footer
        bottom_frame = tk.Frame(self.root, bg=THEME["BG"]); bottom_frame.pack(side="bottom", fill="x", pady=8, padx=20)
        RoundedButton(bottom_frame, 120, 30, 15, THEME["PANEL"], THEME["ACCENT"], THEME["TEXT"], "Calibrator", self.open_calibrator_small).pack(side="left")
        RoundedButton(bottom_frame, 120, 30, 15, THEME["PANEL"], THEME["ACCENT"], THEME["TEXT"], "Piano Roll", self.open_piano_roll_editor).pack(side="left", padx=10)

        gen_btn = tk.Button(bottom_frame, text="Gen Random", bg=THEME["PANEL"], fg=THEME["ACCENT"], bd=0,
                            relief="flat", cursor="hand2", command=lambda: self.generate_random_song_small(20), width=10)
        gen_btn.pack(side="right"); self._apply_hover(gen_btn)

        tk.Label(bottom_frame, text="- / = keys = speed ±0.05x", bg=THEME["BG"], fg=THEME["MUTED"], font=FONT_SMALL).pack(side="right", padx=10)

    def _build_single_ui(self, parent):
        # Top buttons
        top_buttons_frame = tk.Frame(parent, bg=THEME["CARD"], height=50); top_buttons_frame.pack(fill="x", padx=12, pady=(10, 10))
        self.btn_load_song = RoundedButton(top_buttons_frame, 180, 36, 18, THEME["ACCENT"], THEME["ACCENT_SOFT"], THEME["BG"], "Load Song", self.load_song)
        self.btn_load_song.place(relx=0.25, rely=0.5, anchor="center")
        self.btn_load_map = RoundedButton(top_buttons_frame, 180, 36, 18, THEME["PANEL"], THEME["ACCENT_SOFT"], THEME["TEXT"], "Load Note Map", self.load_note_map)
        self.btn_load_map.place(relx=0.75, rely=0.5, anchor="center")

        # Info & Visualizer
        info_row = tk.Frame(parent, bg=THEME["CARD"]); info_row.pack(fill="x", padx=12, pady=(0, 6))
        left_info_frame = tk.Frame(info_row, bg=THEME["CARD"]); left_info_frame.pack(side="left", fill="both", expand=True)
        meta_row = tk.Frame(left_info_frame, bg=THEME["CARD"]); meta_row.pack(fill="x", anchor="w")
        self.spinning_disc = SpinningDisc(meta_row, bg=THEME["CARD"])
        self.marquee = Marquee(meta_row, width=180); self.marquee.pack(side="left", padx=(0, 10))
        self.meta = tk.Frame(meta_row, bg=THEME["CARD"]); self.meta.pack(side="left", anchor="n")
        self.lbl_song_type = tk.Label(self.meta, text="Type: N/A", bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT_SMALL); self.lbl_song_type.pack(anchor="w")
        self.lbl_song_count = tk.Label(self.meta, text="Notes: 0", bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT_SMALL); self.lbl_song_count.pack(anchor="w", pady=(2, 0))
        vis_container = tk.Frame(info_row, bg=THEME["PANEL_DARK"], bd=1, relief="solid"); vis_container.pack(side="right", padx=(10, 0))
        self.mini_piano = MiniScrollingPianoRoll(vis_container, width=240, height=100); self.mini_piano.pack()

        # Tempo
        tempo_frame = tk.Frame(parent, bg=THEME["CARD"]); tempo_frame.pack(fill="x", padx=12, pady=(8, 6))
        tempo_top = tk.Frame(tempo_frame, bg=THEME["CARD"]); tempo_top.pack(fill="x")
        tk.Label(tempo_top, text="Tempo", bg=THEME["CARD"], fg=THEME["TEXT"], font=FONT_BOLD).pack(side="left")
        self.menu_btn = HamburgerMenu(tempo_top, self); self.menu_btn.pack(side="right")
        tempo_row = tk.Frame(tempo_frame, bg=THEME["CARD"]); tempo_row.pack(fill="x", pady=(6, 0))
        self.tempo_var = tk.DoubleVar(value=DEFAULT_TEMPO)
        self.tempo_scale = ttk.Scale(tempo_row, from_=MIN_TEMPO, to=MAX_TEMPO, orient="horizontal",
                                      variable=self.tempo_var, length=380, command=self._on_tempo_drag)
        self.tempo_scale.pack(side="left", padx=(0, 10))
        self.tempo_scale.bind("<ButtonRelease-1>", self._on_tempo_release)
        self.tempo_label_val = tk.Label(tempo_row, text=f"{DEFAULT_TEMPO:.2f}x", bg=THEME["CARD"],
                                         fg=THEME["ACCENT"], font=FONT_BOLD, width=6)
        self.tempo_label_val.pack(side="left")
        preset_frame = tk.Frame(tempo_frame, bg=THEME["CARD"]); preset_frame.pack(pady=(8, 0), anchor="w")
        for v in (0.5, 1.0, 1.4, 2.0):
            b = tk.Button(preset_frame, text=f"{v}x", command=lambda vv=v: self._set_tempo(vv),
                          bg=THEME["PANEL"], fg=THEME["ACCENT"], bd=0, relief="flat", width=6)
            b.pack(side="left", padx=6); self._apply_hover(b)

        # Progress
        progress_frame = tk.Frame(parent, bg=THEME["CARD"]); progress_frame.pack(fill="x", padx=12, pady=(12, 5))
        self.current_time_label = tk.Label(progress_frame, text="00:00", bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT); self.current_time_label.pack(side="left")
        self.progress_var = tk.DoubleVar()
        self.progress_scale = ttk.Scale(progress_frame, from_=0, to=100, orient="horizontal", variable=self.progress_var, state="disabled")
        self.progress_scale.pack(side="left", fill="x", expand=True, padx=10)
        self.progress_scale.bind("<ButtonPress-1>", self._on_seek_press)
        self.progress_scale.bind("<ButtonRelease-1>", self._on_seek_release)
        self.duration_label = tk.Label(progress_frame, text="00:00", bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT); self.duration_label.pack(side="right")

        # Play controls
        play_frame = tk.Frame(parent, bg=THEME["CARD"]); play_frame.pack(fill="x", pady=(5, 6), anchor="center", padx=12)
        self.btn_start = tk.Button(play_frame, text="START (9)", command=self.start_playing, bg=THEME["ACCENT"], fg=THEME["BG"], font=FONT_BOLD, width=14, bd=0, relief="flat", cursor="hand2")
        self.btn_start.pack(side="left", padx=4)
        self.btn_pause = tk.Button(play_frame, text="PAUSE (8)", command=self.toggle_pause, bg=THEME["WARNING"], fg="#000000", font=FONT_BOLD, width=14, bd=0, relief="flat", cursor="hand2", state=tk.DISABLED)
        self.btn_pause.pack(side="left", padx=4)
        self.btn_stop = tk.Button(play_frame, text="STOP (0)", command=self.stop_playing, bg=THEME["PANEL"], fg=THEME["TEXT"], font=FONT_BOLD, width=14, bd=0, relief="flat", cursor="hand2", state=tk.DISABLED)
        self.btn_stop.pack(side="left", padx=4)
        self._apply_hover(self.btn_start, enter_bg=THEME["ACCENT_SOFT"], enter_fg=THEME["BG"])
        self._apply_hover(self.btn_pause, enter_bg="#e0a800", enter_fg="#000000")
        self._apply_hover(self.btn_stop, enter_bg="#2b2b2b", enter_fg=THEME["TEXT"])

        self.status_label = tk.Label(parent, text="Status: Ready", bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT); self.status_label.pack(fill="x", padx=12, pady=(2, 0))
        self.counter_label = tk.Label(parent, text="Played: 0 / 0", bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT); self.counter_label.pack(fill="x", padx=12, pady=(2, 6))

        self._on_tempo_drag(self.tempo_var.get())

    def _build_dual_ui(self, parent):
        """Build the two-instance side-by-side layout."""
        tk.Label(parent, text="Dual Instance Mode — Both songs share the same Tempo setting",
                 bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT_SMALL).pack(pady=(8, 4))

        panels_row = tk.Frame(parent, bg=THEME["CARD"]); panels_row.pack(fill="both", expand=True, padx=8, pady=4)

        self.inst1 = InstancePanel(panels_row, 1, self.tempo_var, self.shared_tempo_ref,
                                    self.song_dir, self.map_dir, THEME["INST1"])
        self.inst1.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.inst2 = InstancePanel(panels_row, 2, self.tempo_var, self.shared_tempo_ref,
                                    self.song_dir, self.map_dir, THEME["INST2"])
        self.inst2.pack(side="left", fill="both", expand=True)

        # Wire up the conductor pause callback so each panel's PAUSE button
        # controls the synchronized conductor whenever "START BOTH" is used.
        self.inst1.app_conductor_pause_cb = self._toggle_conductor_pause
        self.inst2.app_conductor_pause_cb = self._toggle_conductor_pause

        # Shared tempo for dual mode
        dual_tempo_frame = tk.Frame(parent, bg=THEME["CARD"]); dual_tempo_frame.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(dual_tempo_frame, text="Shared Tempo", bg=THEME["CARD"], fg=THEME["TEXT"], font=FONT_BOLD).pack(side="left")
        dual_tempo_row = tk.Frame(parent, bg=THEME["CARD"]); dual_tempo_row.pack(fill="x", padx=12)
        if not hasattr(self, 'tempo_var'):
            self.tempo_var = tk.DoubleVar(value=DEFAULT_TEMPO)
        self.dual_tempo_scale = ttk.Scale(dual_tempo_row, from_=MIN_TEMPO, to=MAX_TEMPO, orient="horizontal",
                                           variable=self.tempo_var, length=430, command=self._on_tempo_drag_dual)
        self.dual_tempo_scale.pack(side="left", padx=(0, 10))
        self.dual_tempo_scale.bind("<ButtonRelease-1>", self._on_tempo_release)
        self.dual_tempo_label = tk.Label(dual_tempo_row, text=f"{DEFAULT_TEMPO:.2f}x",
                                          bg=THEME["CARD"], fg=THEME["ACCENT"], font=FONT_BOLD, width=6)
        self.dual_tempo_label.pack(side="left")
        preset_row = tk.Frame(parent, bg=THEME["CARD"]); preset_row.pack(pady=(6, 4), anchor="w", padx=12)
        for v in (0.5, 1.0, 1.4, 2.0):
            b = tk.Button(preset_row, text=f"{v}x", command=lambda vv=v: self._set_tempo(vv),
                          bg=THEME["PANEL"], fg=THEME["ACCENT"], bd=0, relief="flat", width=6)
            b.pack(side="left", padx=6); self._apply_hover(b)

        # Dual start/stop all
        ctrl_row = tk.Frame(parent, bg=THEME["CARD"]); ctrl_row.pack(pady=(4, 8))
        tk.Button(ctrl_row, text="▶ START BOTH", bg=THEME["ACCENT"], fg=THEME["BG"], font=FONT_BOLD, bd=0,
                  relief="flat", cursor="hand2", command=self._dual_start_all, width=16).pack(side="left", padx=6)
        tk.Button(ctrl_row, text="■ STOP BOTH", bg=THEME["PANEL"], fg=THEME["TEXT"], font=FONT_BOLD, bd=0,
                  relief="flat", cursor="hand2", command=self._dual_stop_all, width=16).pack(side="left", padx=6)
        tk.Label(parent, text="START BOTH now runs both songs off one shared clock so\n"
                              "they can't drift out of sync with each other.",
                 bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT_SMALL, justify="left").pack(pady=(0, 6))

    def _toggle_dual_mode(self):
        self.dual_mode.set(not self.dual_mode.get())
        if self.dual_mode.get():
            self.single_frame.pack_forget()
            self.dual_frame.pack(fill="both", expand=True)
            self.dual_toggle_btn.config(text="☑  Dual Instance Mode", fg=THEME["INST2"])
            self.root.geometry("780x760")
        else:
            self.dual_frame.pack_forget()
            self.single_frame.pack(fill="both", expand=True)
            self.dual_toggle_btn.config(text="☐  Dual Instance Mode", fg=THEME["MUTED"])
            self.root.geometry("700x680")

    # --- Synchronized dual-instance conductor ---
    # A single thread merges both instances' note events into one sorted
    # timeline and dispatches clicks off ONE shared clock (time.perf_counter).
    # This is what actually fixes the "one instance is faster" problem:
    # previously each instance ran its own thread with its own start_time,
    # and Python's GIL + a single real mouse cursor meant those two threads
    # were never truly simultaneous — they'd fight for CPU turns and slowly
    # drift apart. With one thread and one clock, drift between instances is
    # no longer possible; both instances' notes fire at their correct time
    # relative to the SAME start point.

    def _dual_start_all(self):
        if self._conductor_running:
            return
        if not self.inst1.song or not self.inst2.song:
            messagebox.showwarning("Missing Song", "Both instances need a song loaded before starting together.")
            return
        if (self.inst1.song_type in ("notes", "timed-notes") and not self.inst1.note_map) or \
           (self.inst2.song_type in ("notes", "timed-notes") and not self.inst2.note_map):
            messagebox.showwarning("Missing Note Map", "Both instances need a note map loaded before starting together.")
            return
        self._on_tempo_release()
        self._conductor_running = True
        self._conductor_paused = False
        self.inst1.conductor_mode_active = True
        self.inst2.conductor_mode_active = True
        self.inst1._set_conductor_ui("Status: Playing (synced)...", THEME["SUCCESS"], True)
        self.inst2._set_conductor_ui("Status: Playing (synced)...", THEME["SUCCESS"], True)
        self.conductor_thread = threading.Thread(target=self._dual_conductor_run, daemon=True)
        self.conductor_thread.start()

    def _dual_conductor_run(self):
        ev1 = [dict(e, inst=1) for e in self.inst1.get_merged_events()]
        ev2 = [dict(e, inst=2) for e in self.inst2.get_merged_events()]
        merged = sorted(ev1 + ev2, key=lambda e: e['time'])
        total1, total2 = len(ev1), len(ev2)
        played1, played2 = 0, 0
        n = len(merged)
        idx = 0
        start_time = time.perf_counter()
        while idx < n and self._conductor_running:
            if self._conductor_paused:
                pause_start = time.perf_counter()
                while self._conductor_paused and self._conductor_running:
                    time.sleep(0.02)
                start_time += (time.perf_counter() - pause_start)
                continue
            tempo = self.shared_tempo_ref[0]
            elapsed = (time.perf_counter() - start_time) * tempo
            ev = merged[idx]
            if elapsed >= ev['time']:
                panel = self.inst1 if ev['inst'] == 1 else self.inst2
                if ev['type'] == 'position':
                    if ev['value']:
                        perform_click_or_press(ev['value'])
                else:
                    mapping = panel.note_map.get(ev['value'])
                    if mapping:
                        perform_click_or_press(mapping)
                if ev['inst'] == 1:
                    played1 += 1
                else:
                    played2 += 1
                p1, p2 = played1, played2
                self.root.after(0, lambda p=p1, t=total1: self.inst1.counter_label.config(text=f"Played: {p} / {t}"))
                self.root.after(0, lambda p=p2, t=total2: self.inst2.counter_label.config(text=f"Played: {p} / {t}"))
                idx += 1
            else:
                time.sleep(0.001)
        if self._conductor_running:
            self._conductor_running = False
            self.root.after(0, self._dual_conductor_finished)

    def _dual_conductor_finished(self):
        self.inst1.conductor_mode_active = False
        self.inst2.conductor_mode_active = False
        self.inst1._set_conductor_ui("Status: Finished", THEME["MUTED"], False)
        self.inst2._set_conductor_ui("Status: Finished", THEME["MUTED"], False)

    def _toggle_conductor_pause(self):
        if not self._conductor_running:
            return
        self._conductor_paused = not self._conductor_paused
        if self._conductor_paused:
            self.inst1.status_label.config(text="Status: Paused", fg=THEME["WARNING"])
            self.inst2.status_label.config(text="Status: Paused", fg=THEME["WARNING"])
            self.inst1.btn_pause.config(text="▶ RESUME", bg=THEME["SUCCESS"])
            self.inst2.btn_pause.config(text="▶ RESUME", bg=THEME["SUCCESS"])
        else:
            self.inst1.status_label.config(text="Status: Playing (synced)...", fg=THEME["SUCCESS"])
            self.inst2.status_label.config(text="Status: Playing (synced)...", fg=THEME["SUCCESS"])
            self.inst1.btn_pause.config(text="⏸ PAUSE", bg=THEME["WARNING"])
            self.inst2.btn_pause.config(text="⏸ PAUSE", bg=THEME["WARNING"])

    def _dual_stop_all(self):
        self._conductor_running = False
        self._conductor_paused = False
        self.inst1.conductor_mode_active = False
        self.inst2.conductor_mode_active = False
        self.inst1.is_playing = False
        self.inst2.is_playing = False
        self.inst1._set_conductor_ui("Status: Stopped", THEME["MUTED"], False)
        self.inst2._set_conductor_ui("Status: Stopped", THEME["MUTED"], False)

    # --- Path helpers ---
    def _browse_dir(self, string_var):
        d = filedialog.askdirectory(initialdir=string_var.get() or str(Path.home()),
                                     title="Choose default directory")
        if d: string_var.set(d)

    # --- Window Management ---
    def close_app(self): self.root.destroy()
    def minimize_app(self):
        self.root.overrideredirect(False); self.root.iconify()
        self.root.after(100, lambda: self.root.overrideredirect(True))

    def toggle_topmost(self):
        self.root.attributes('-topmost', self.always_on_top.get()); self.root.lift()

    # --- Helpers ---
    def open_piano_roll_editor(self): PianoRollEditor(self.root)
    def _apply_hover(self, btn, enter_bg=THEME["ACCENT_SOFT"], enter_fg="#ffffff"):
        original_bg, original_fg = btn.cget("background"), btn.cget("foreground")
        btn.bind("<Enter>", lambda e: e.widget.config(bg=enter_bg, fg=enter_fg))
        btn.bind("<Leave>", lambda e: e.widget.config(bg=original_bg, fg=original_fg))

    def _setup_hotkeys(self):
        if keyboard:
            try:
                # 9 = start (single) or start both (dual)
                keyboard.add_hotkey('9', lambda: self.root.after(0, self._hotkey_start))
                # 0 = stop (single) or stop both (dual)
                keyboard.add_hotkey('0', lambda: self.root.after(0, self._hotkey_stop))
                keyboard.add_hotkey('8', lambda: self.root.after(0, self.toggle_pause))
                # Speed shortcuts: - = slower (-1 step = -0.05x), = = faster (+1 step = +0.05x)
                keyboard.add_hotkey('-', lambda: self.root.after(0, self._speed_step, -1))
                keyboard.add_hotkey('=', lambda: self.root.after(0, self._speed_step, +1))
            except Exception:
                try:
                    self.status_label.config(text="Hotkey setup failed. Run as admin.", fg=THEME["ERROR"])
                except Exception:
                    pass
        else:
            try:
                self.status_label.config(text="Hotkeys disabled: 'keyboard' lib not found.", fg=THEME["ERROR"])
            except Exception:
                pass

    def _hotkey_start(self):
        """9 key: start both instances in dual mode, single instance otherwise."""
        if self.dual_mode.get():
            self._dual_start_all()
        else:
            self.start_playing()

    def _hotkey_stop(self):
        """0 key: stop both instances in dual mode, single instance otherwise."""
        if self.dual_mode.get():
            self._dual_stop_all()
        else:
            self.stop_playing()

    def _speed_step(self, steps):
        """
        Adjusts tempo by `steps` increments of TEMPO_STEP (0.05).
        = = +1 step = +0.05x faster
        - = -1 step = -0.05x slower
        """
        current = self.tempo_var.get()
        new_val = clamp(round((current + steps * TEMPO_STEP) / TEMPO_STEP) * TEMPO_STEP, MIN_TEMPO, MAX_TEMPO)
        self._set_tempo(new_val)
        # Brief flash on the label to give feedback
        if hasattr(self, 'tempo_label_val'):
            self.tempo_label_val.config(fg=THEME["SUCCESS"])
            self.root.after(300, lambda: self.tempo_label_val.config(fg=THEME["ACCENT"]))
        if hasattr(self, 'dual_tempo_label'):
            self.dual_tempo_label.config(fg=THEME["SUCCESS"])
            self.root.after(300, lambda: self.dual_tempo_label.config(fg=THEME["ACCENT"]))

    def _format_time(self, seconds):
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _update_progress_ui(self, current_time):
        if not self.is_seeking and self.is_playing and not self.is_paused:
            self.progress_var.set(current_time)
            self.current_time_label.config(text=self._format_time(current_time))

    def _on_seek_press(self, event): self.is_seeking = True
    def _on_seek_release(self, event):
        self.is_seeking = False
        self.seek_song(self.progress_var.get())

    def seek_song(self, seek_time):
        was_playing = self.is_playing
        self.stop_playing(is_seeking=True)
        if was_playing: self.root.after(100, lambda: self.start_playing(start_offset=seek_time))
        else:
            self.playback_start_offset = seek_time
            self.current_time_label.config(text=self._format_time(seek_time))
            self.progress_var.set(seek_time)

    def load_note_map(self):
        path = filedialog.askopenfilename(title="Load Note Map",
                                           initialdir=self.map_dir.get(),
                                           filetypes=[("JSON files", "*.json")])
        if not path: return
        try:
            self.note_map = dict(safe_json_load(path))
            messagebox.showinfo("Note Map", f"Loaded {len(self.note_map)} entries.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _calculate_song_duration(self):
        if not self.song: return 0
        if self.song_type in ("timed-notes", "recorded"): return self.song[-1].get("time", 0)
        elif self.song_type == "notes": return len(self.song) * 0.15 / DEFAULT_TEMPO
        return 0

    def load_song(self):
        path = filedialog.askopenfilename(title="Load Song",
                                           initialdir=self.song_dir.get(),
                                           filetypes=[("JSON files", "*.json")])
        if not path: return
        try:
            data = safe_json_load(path)
            if not isinstance(data, list) or not data: raise RuntimeError("Song must be a non-empty list.")
            first = data[0]
            if isinstance(first, str): self.song_type = "notes"
            elif "position" in first: self.song_type = "recorded"
            elif "note" in first: self.song_type = "timed-notes"
            else: raise RuntimeError("Unknown song format.")
            self.song = data if self.song_type != "timed-notes" else sorted(data, key=lambda x: x.get("time", 0))
            self.spinning_disc.pack(side="left", padx=(0, 8), anchor="w", before=self.marquee)
            self.spinning_disc.start()
            self.marquee.set_text(os.path.basename(path))
            self.lbl_song_type.config(text=f"Type: {self.song_type}")
            self.lbl_song_count.config(text=f"Notes: {len(self.song)}")
            self.counter_label.config(text=f"Played: 0 / {len(self.song)}")
            self.status_label.config(text="Status: Loaded", fg=THEME["SUCCESS"])
            self.mini_piano.set_song_data(self.song)
            self.song_duration = self._calculate_song_duration()
            self.progress_scale.config(to=self.song_duration, state="normal")
            self.duration_label.config(text=self._format_time(self.song_duration))
            self.current_time_label.config(text="00:00")
            self.progress_var.set(0)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def generate_random_song_small(self, length=20):
        if not self.note_map: return messagebox.showwarning("No Note Map", "Load a note map first.")
        if not (keys := list(self.note_map.keys())): return messagebox.showwarning("No keys", "Note map empty.")
        self.song = [{"time": round(sum(random.choice([0.15, 0.2, 0.25]) for _ in range(i+1)), 3), "note": random.choice(keys)} for i in range(length)]
        self.song_type = "timed-notes"
        self.spinning_disc.pack(side="left", padx=(0, 8), anchor="w", before=self.marquee)
        self.spinning_disc.start()
        self.marquee.set_text("Random Generated Song")
        self.lbl_song_count.config(text=f"Notes: {len(self.song)}")
        self.lbl_song_type.config(text="Type: timed-notes")
        self.counter_label.config(text=f"Played: 0 / {len(self.song)}")
        self.status_label.config(text="Status: Random song ready", fg=THEME["MUTED"])
        self.mini_piano.set_song_data(self.song)
        self.song_duration = self._calculate_song_duration()
        self.progress_scale.config(to=self.song_duration, state="normal")
        self.duration_label.config(text=self._format_time(self.song_duration))
        self.current_time_label.config(text="00:00")
        self.progress_var.set(0)

    def _on_tempo_drag(self, value_str):
        try:
            v = clamp(round(float(value_str) / TEMPO_STEP) * TEMPO_STEP, MIN_TEMPO, MAX_TEMPO)
            self.tempo_label_val.config(text=f"{v:.2f}x")
        except Exception:
            pass

    def _on_tempo_drag_dual(self, value_str):
        try:
            v = clamp(round(float(value_str) / TEMPO_STEP) * TEMPO_STEP, MIN_TEMPO, MAX_TEMPO)
            self.dual_tempo_label.config(text=f"{v:.2f}x")
        except Exception:
            pass

    def _on_tempo_release(self, _ev=None):
        try:
            snapped = clamp(round(self.tempo_var.get() / TEMPO_STEP) * TEMPO_STEP, MIN_TEMPO, MAX_TEMPO)
            self.tempo_var.set(snapped); self.tempo = snapped
            self.shared_tempo_ref[0] = snapped
            try: self.tempo_label_val.config(text=f"{snapped:.2f}x")
            except Exception: pass
            try: self.dual_tempo_label.config(text=f"{snapped:.2f}x")
            except Exception: pass
        except Exception:
            pass

    def _set_tempo(self, v):
        self.tempo_var.set(v); self.tempo = v
        self.shared_tempo_ref[0] = v
        try: self.tempo_label_val.config(text=f"{v:.2f}x")
        except Exception: pass
        try: self.dual_tempo_label.config(text=f"{v:.2f}x")
        except Exception: pass

    def focus_growtopia(self):
        if not gw: return True
        try:
            wins = gw.getWindowsWithTitle("Growtopia")
            if not wins: raise RuntimeError("Growtopia window not found.")
            win = wins[0]
            if not win.isActive: win.activate()
            if win.isMinimized: win.restore()
            time.sleep(0.35)
            return True
        except Exception:
            return messagebox.askyesno("Focus Error",
                "Growtopia window not detected!\n\nDo you want to start playing anyway?\n(You must click the game window immediately)")

    def toggle_pause(self):
        if not self.is_playing: return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.config(text="RESUME (8)", bg=THEME["SUCCESS"])
            self.status_label.config(text="Status: Paused", fg=THEME["WARNING"])
        else:
            self.btn_pause.config(text="PAUSE (8)", bg=THEME["WARNING"])
            self.status_label.config(text="Status: Playing...", fg=THEME["SUCCESS"])

    def start_playing(self, start_offset=None):
        if self.is_playing: return
        if not self.song: return messagebox.showwarning("No Song", "Load a song first.")
        if self.song_type in ("notes", "timed-notes") and not self.note_map: return messagebox.showwarning("No Note Map", "This song requires a Note Map.")
        self._on_tempo_release(); self.is_playing = True; self.is_paused = False
        if start_offset is None: start_offset = self.playback_start_offset
        self.playback_start_offset = start_offset
        self.btn_start.config(state="disabled"); self.btn_stop.config(state="normal")
        self.btn_pause.config(state="normal", text="PAUSE (8)", bg=THEME["WARNING"])
        self.status_label.config(text="Status: Playing...", fg=THEME["SUCCESS"])
        self.play_thread = threading.Thread(target=self.play_song_thread, args=(start_offset,), daemon=True)
        self.play_thread.start()

    def stop_playing(self, is_seeking=False):
        if not self.is_playing: return
        self.is_playing = False; self.is_paused = False
        if not is_seeking:
            self.playback_start_offset = 0
            self.root.after(100, lambda: self._update_progress_ui(0))
            self.status_label.config(text="Status: Stopped", fg=THEME["MUTED"])
            self.btn_start.config(state="normal"); self.btn_stop.config(state="disabled")
            self.btn_pause.config(state="disabled", text="PAUSE (8)", bg=THEME["WARNING"])
        else:
            self.status_label.config(text="Status: Seeking...", fg=THEME["MUTED"])

    def _playback_finished(self):
        if self.looping.get() and self.is_playing:
            self.status_label.config(text="Status: Looping...", fg=THEME["ACCENT"])
            self.is_playing = False
            self.root.after(500, lambda: self.start_playing(0))
        else:
            self.stop_playing()
            self.status_label.config(text="Status: Finished", fg=THEME["MUTED"])

    def play_song_thread(self, start_offset=0):
        if not self.focus_growtopia():
            self.root.after(0, self.stop_playing); return
        start_time = time.perf_counter() - (start_offset / self.tempo)
        start_index = 0
        if self.song_type in ("timed-notes", "recorded"):
            for i, ev in enumerate(self.song):
                if ev.get("time", 0) >= start_offset: start_index = i; break
        elif self.song_type == "notes":
            start_index = int((start_offset / self.song_duration) * len(self.song)) if self.song_duration > 0 else 0
            start_index = max(0, min(start_index, len(self.song) - 1))
        i = start_index; total_notes = len(self.song)
        while i < total_notes and self.is_playing:
            if self.is_paused:
                pause_start = time.perf_counter()
                while self.is_paused and self.is_playing: time.sleep(0.05)
                start_time += (time.perf_counter() - pause_start)
                if not self.is_playing: break
            ev = self.song[i]
            current_audio_time = (time.perf_counter() - start_time) * self.tempo
            self.root.after(0, self._update_progress_ui, current_audio_time)
            self.root.after(0, self.mini_piano.update_visuals, current_audio_time)
            self.root.after(0, lambda p=i+1, t=total_notes: self.counter_label.config(text=f"Played: {p} / {t}"))
            if self.song_type == "notes":
                if mapping := self.note_map.get(ev): perform_click_or_press(mapping)
                time.sleep(0.15 / self.tempo); i += 1
            else:
                target_time = ev.get("time", 0)
                if current_audio_time >= target_time:
                    key_field = "position" if self.song_type == "recorded" else "note"
                    if key_field == "position":
                        if pos := ev.get("position"): perform_click_or_press(pos)
                    else:
                        if (note := ev.get("note")) and (mapping := self.note_map.get(note)): perform_click_or_press(mapping)
                    i += 1
                else:
                    time.sleep(0.001)
        if self.is_playing: self.root.after(0, self._playback_finished)

    def open_calibrator_small(self):
        win = tk.Toplevel(self.root); win.title("Calibrator — Sequential"); win.geometry("460x320")
        win.configure(bg=THEME["CARD"]); win.transient(self.root); win.grab_set()
        tk.Label(win, text="Calibrator: Click notes in order shown", bg=THEME["CARD"], fg=THEME["TEXT"], font=FONT_BOLD).pack(pady=8)
        self.cal_status = tk.Label(win, text="Ready. Press Start.", bg=THEME["CARD"], fg=THEME["MUTED"], font=FONT); self.cal_status.pack(pady=(6, 10))
        btn_frame = tk.Frame(win, bg=THEME["CARD"]); btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Start Calibration", bg=THEME["PANEL"], fg=THEME["ACCENT"], command=lambda: self._start_calibration(win), bd=0, relief="flat", padx=10, pady=5).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Save Map", bg=THEME["PANEL"], fg=THEME["ACCENT"], command=self._save_note_map_dialog, bd=0, relief="flat", padx=10, pady=5).pack(side="left", padx=8)
        self.cal_next_label = tk.Label(win, text="", bg=THEME["CARD"], fg=THEME["TEXT"], font=FONT_BOLD); self.cal_next_label.pack(pady=(18, 4))

    def _start_calibration(self, parent_win):
        if not CALIBRATOR_NOTE_ORDER: return messagebox.showwarning("No order", "No calibration order defined.")
        self._cal_index, self._captured_map = 0, {}
        time.sleep(0.25); self._prompt_next_calibration(parent_win)

    def _prompt_next_calibration(self, parent_win):
        if self._cal_index >= len(CALIBRATOR_NOTE_ORDER):
            self.cal_status.config(text="All notes calibrated! Don't forget to save.", fg=THEME["SUCCESS"])
            return messagebox.showinfo("Done", "Calibration finished. You can now save the note map.", parent=parent_win)
        note = CALIBRATOR_NOTE_ORDER[self._cal_index]
        self.cal_next_label.config(text=f"CLICK the position for note '{note}'")
        self.cal_status.config(text=f"Waiting for click for note '{note}'", fg=THEME["MUTED"])
        if pynput_mouse:
            listener = pynput_mouse.Listener(on_click=lambda x, y, btn, press: (self.root.after(0, self._after_click_recorded, note, x, y, parent_win), False)[1])
            listener.start()
        else:
            messagebox.showinfo("Fallback", "Pynput not found. Move cursor to note position and press OK.", parent=parent_win)
            self._after_click_recorded(note, *self.root.winfo_pointerxy(), parent_win)

    def _after_click_recorded(self, note, x, y, parent_win):
        self._captured_map[note] = [int(x), int(y)]
        self.cal_status.config(text=f"Recorded '{note}' at ({int(x)}, {int(y)})", fg=THEME["TEXT"])
        self._cal_index += 1; self.note_map.update(self._captured_map)
        self.root.after(250, lambda: self._prompt_next_calibration(parent_win))

    def _save_note_map_dialog(self):
        combined_map = {**self.note_map, **getattr(self, '_captured_map', {})}
        if not combined_map: return messagebox.showwarning("No data", "No calibration data to save.")
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Save Note Map",
                                             initialdir=self.map_dir.get())
        if not path: return
        try:
            with open(path, "w") as f: json.dump(combined_map, f, indent=2); messagebox.showinfo("Saved", f"Saved note map to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ---------------------------
# 9. ENTRY POINT
# ---------------------------

def main():
    root = tk.Tk()
    app = GrowtopiaMusicSuite(root)
    root.mainloop()

if __name__ == "__main__":
    main()

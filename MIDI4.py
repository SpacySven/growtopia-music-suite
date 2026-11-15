import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import os

try:
    import mido
except ImportError:
    print("Error: Library 'mido' not found.")
    print("Run: pip install mido")
    input("Press Enter...")
    sys.exit()

# =========================================================
#  SETTINGS
# =========================================================

# 1.0 = Normal Speed, 2.0 = Half Speed
SLOW_FACTOR = 1.0

# Minimum gap between notes (seconds) to prevent skipping
MIN_GAP = 0.12

# =========================================================

GT_NOTES = {
    48: "c1",  49: "c1#", 50: "d1",  51: "d1#", 52: "e1",  53: "f1",
    54: "f1#", 55: "g1",  56: "g1#", 57: "a",   58: "a#",  59: "b",
    60: "c",   61: "c#",  62: "d",   63: "d#",  64: "e",   65: "f",
    66: "f#",  67: "g",   68: "g#",  69: "a2",  70: "a2#", 71: "b2"
}

def get_best_octave_shift(midi_notes):
    """
    Analyzes the song to find the best octave shift (-24, -12, 0, +12, etc)
    that keeps the most notes inside Growtopia's range (48-71) without 
    breaking the melody.
    """
    if not midi_notes:
        return 0

    best_shift = 0
    max_notes_in_range = -1

    # Test shifting the song up/down by up to 4 octaves
    possible_shifts = range(-48, 49, 12) 

    for shift in possible_shifts:
        in_range_count = 0
        for note in midi_notes:
            shifted_note = note + shift
            if 48 <= shifted_note <= 71:
                in_range_count += 1
        
        # We prefer the shift that fits the most notes naturally
        if in_range_count > max_notes_in_range:
            max_notes_in_range = in_range_count
            best_shift = shift
            
    return best_shift

def main():
    root = tk.Tk()
    root.withdraw()

    print("--- MIDI to Growtopia Smart Converter v4 ---")
    
    # 1. Select File
    midi_path = filedialog.askopenfilename(
        title="Select MIDI File",
        filetypes=[("MIDI files", "*.mid *.midi")]
    )
    if not midi_path: return

    try:
        mid = mido.MidiFile(midi_path)
    except Exception as e:
        messagebox.showerror("Error", f"Bad MIDI:\n{e}")
        return

    # 2. Pre-Scan to find Best Fit
    all_pitches = []
    for msg in mid:
        if msg.type == 'note_on' and msg.velocity > 0:
            all_pitches.append(msg.note)
            
    if not all_pitches:
        messagebox.showwarning("Empty", "No notes found.")
        return

    # Calculate the global shift needed
    global_shift = get_best_octave_shift(all_pitches)
    print(f"Applying Global Shift: {global_shift} semitones")

    # 3. Process Notes
    raw_notes = []
    current_time = 0.0
    
    for msg in mid:
        current_time += (msg.time * SLOW_FACTOR)
        
        if msg.type == 'note_on' and msg.velocity > 0:
            # Apply the Global Best Fit shift
            note = msg.note + global_shift
            
            # ONLY wrap if the note is STILL outside the range 
            # after the global shift. This preserves the melody for 90% of notes.
            while note < 48: note += 12
            while note > 71: note -= 12
            
            if note in GT_NOTES:
                raw_notes.append({
                    "time": current_time,
                    "note": GT_NOTES[note]
                })

    # 4. Fix Overlapping / Timing
    raw_notes.sort(key=lambda x: x["time"])

    fixed_notes = []
    last_click_time = -1.0

    for note_data in raw_notes:
        desired_time = note_data["time"]
        
        if desired_time < (last_click_time + MIN_GAP):
            actual_time = last_click_time + MIN_GAP
        else:
            actual_time = desired_time
            
        note_data["time"] = round(actual_time, 3)
        fixed_notes.append(note_data)
        last_click_time = actual_time

    # 5. Save
    save_path = filedialog.asksaveasfilename(
        title="Save JSON",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialfile="converted_song.json"
    )

    if save_path:
        with open(save_path, "w") as f:
            json.dump(fixed_notes, f, indent=2)
        messagebox.showinfo("Success", f"Done!\n\nSmart Shift: {global_shift}\nSpeed: {SLOW_FACTOR}x")

if __name__ == "__main__":
    main()
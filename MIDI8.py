import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

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

# Overall song speed. 1.0 = original speed.
# Lower than 1.0 = FASTER (e.g. 0.8 = ~20% faster, notes closer together).
# Higher than 1.0 = slower.
SLOW_FACTOR = 0.8

# Minimum gap (seconds) between two notes played by the SAME player.
# Lower = faster clicking required, but risk of missed clicks if too low.
MIN_GAP = 0.09

# Max notes allowed to play at the exact same instant (before splitting).
MAX_POLYPHONY = 2

# =========================================================

GT_NOTES = {
    48: "c1",  49: "c1#", 50: "d1",  51: "d1#", 52: "e1",  53: "f1",
    54: "f1#", 55: "g1",  56: "g1#", 57: "a",   58: "a#",  59: "b",
    60: "c",   61: "c#",  62: "d",   63: "d#",  64: "e",   65: "f",
    66: "f#",  67: "g",   68: "g#",  69: "a2",  70: "a2#", 71: "b2"
}

RANGE_CENTER = 59.5  # midpoint of 48-71, used to keep the melody centered


def get_best_octave_shift(midi_notes):
    """Pick the octave shift that fits the most notes in range (48-71).
    Ties are broken by whichever shift keeps the melody closest to the
    center of the range, so the song doesn't cluster toward the very top
    or bottom of the available notes."""
    if not midi_notes:
        return 0
    best_shift = 0
    best_score = None
    for shift in range(-48, 49, 12):
        shifted = [n + shift for n in midi_notes]
        in_range = sum(1 for n in shifted if 48 <= n <= 71)
        avg = sum(shifted) / len(shifted)
        score = (in_range, -abs(avg - RANGE_CENTER))
        if best_score is None or score > best_score:
            best_score = score
            best_shift = shift
    return best_shift


def thin_chord(pitches, max_notes):
    """Keep only the highest and lowest pitch (melody + bass) if a chord
    has more notes than allowed."""
    if len(pitches) <= max_notes:
        return pitches
    pitches = sorted(pitches)
    if max_notes == 1:
        return [pitches[-1]]
    if max_notes == 2:
        return [pitches[0], pitches[-1]]
    step = (len(pitches) - 1) / (max_notes - 1)
    return [pitches[round(i * step)] for i in range(max_notes)]


def apply_min_gap(events):
    """Enforce MIN_GAP between consecutive notes WITHIN one player's own
    list only (each player only ever needs to worry about their own
    clicks, not the other player's)."""
    events = sorted(events, key=lambda e: e["time"])
    fixed = []
    last_time = -1.0
    for ev in events:
        t = ev["time"]
        if t < last_time + MIN_GAP:
            t = last_time + MIN_GAP
        ev = {"time": round(t, 3), "note": ev["note"]}
        fixed.append(ev)
        last_time = t
    return fixed


def convert_and_split(midi_path):
    """MIDI -> two polyphony-limited, timing-synced note lists (Player 1 =
    melody / higher note of each chord, Player 2 = bass / lower note)."""
    mid = mido.MidiFile(midi_path)

    all_pitches = [msg.note for msg in mid if msg.type == 'note_on' and msg.velocity > 0]
    if not all_pitches:
        raise ValueError("No notes found in this MIDI file.")

    global_shift = get_best_octave_shift(all_pitches)

    # Group note_on events by their true elapsed time (before any spacing
    # is applied) -- this is the only point where "same instant" is real.
    current_time = 0.0
    chord_groups = []
    time_to_group = {}

    for msg in mid:
        current_time += (msg.time * SLOW_FACTOR)
        if msg.type == 'note_on' and msg.velocity > 0:
            note = msg.note + global_shift
            while note < 48: note += 12
            while note > 71: note -= 12
            if note not in GT_NOTES:
                continue
            key = round(current_time, 6)
            if key not in time_to_group:
                group = [key, []]
                time_to_group[key] = group
                chord_groups.append(group)
            time_to_group[key][1].append(note)

    chord_groups.sort(key=lambda g: g[0])

    p1_events = []  # melody: solo notes + higher note of any chord
    p2_events = []  # harmony/bass: lower note, only when a real chord exists
    dropped = 0

    for time, pitches in chord_groups:
        # De-dupe first -- two source notes can wrap into the SAME
        # Growtopia note (e.g. an octave apart), which used to make
        # Player 1 and Player 2 click the identical note at once.
        unique_pitches = sorted(set(pitches))
        dropped += len(pitches) - len(unique_pitches)

        kept = thin_chord(unique_pitches, MAX_POLYPHONY)
        dropped += len(unique_pitches) - len(kept)

        if len(kept) == 1:
            p1_events.append({"time": time, "note": GT_NOTES[kept[0]]})
        else:
            low, high = min(kept), max(kept)
            # Push Player 2's note down an octave when possible, so it
            # sits clearly lower / separate instead of crowding the same
            # register as Player 1's melody note.
            bass_note = low - 12 if (low - 12) >= 48 else low
            p1_events.append({"time": time, "note": GT_NOTES[high]})
            p2_events.append({"time": time, "note": GT_NOTES[bass_note]})

    p1_fixed = apply_min_gap(p1_events)
    p2_fixed = apply_min_gap(p2_events)

    return p1_fixed, p2_fixed, global_shift, dropped


def main():
    root = tk.Tk()
    root.withdraw()

    print("--- MIDI to Growtopia Converter v7 (limit + synced split, no dupes) ---")

    midi_path = filedialog.askopenfilename(
        title="Select MIDI File",
        filetypes=[("MIDI files", "*.mid *.midi")]
    )
    if not midi_path:
        return

    try:
        p1_notes, p2_notes, shift, dropped = convert_and_split(midi_path)
    except Exception as e:
        messagebox.showerror("Error", f"Conversion failed:\n{e}")
        return

    if not p1_notes and not p2_notes:
        messagebox.showwarning("Empty", "No usable notes found.")
        return

    save_path = filedialog.asksaveasfilename(
        title="Save as (base name — _player1 / _player2 will be added)",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialfile=Path(midi_path).stem + ".json"
    )
    if not save_path:
        return

    base = Path(save_path)
    p1_path = base.with_name(base.stem + "_player1.json")
    p2_path = base.with_name(base.stem + "_player2.json")

    with open(p1_path, "w") as f:
        json.dump(p1_notes, f, indent=2)
    with open(p2_path, "w") as f:
        json.dump(p2_notes, f, indent=2)

    messagebox.showinfo(
        "Success",
        f"Done!\n\nShift: {shift}\nMax notes at once: {MAX_POLYPHONY}\n"
        f"Speed: {SLOW_FACTOR}x   Min gap: {MIN_GAP}s\n"
        f"Dropped: {dropped} extra notes\n\n"
        f"Player 1 (melody) → {p1_path.name} ({len(p1_notes)} notes)\n"
        f"Player 2 (bass)   → {p2_path.name} ({len(p2_notes)} notes)"
    )


if __name__ == "__main__":
    main()

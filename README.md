# Growtopia Music Suite

Plays songs in Growtopia by clicking the notes on your keytar for you. You load a song and a note map, press start, and it plays.

Windows only.

Be aware its made with claude, there will be bugs

## Installation

1. Install Python from https://www.python.org/downloads/ and **tick "Add python.exe to PATH"** during install.
2. Download this project (green **Code** button, then **Download ZIP**) and extract it.
3. Double-click `install.bat`.

To start the program, double-click `growtopia_music_suite.py`.

<details>
<summary>Manual install</summary>

```
python -m pip install pyautogui pygetwindow keyboard pynput mido
python growtopia\_music\_suite.py
```

</details>

\---

## Making your note map

The program needs to know where the notes are on your screen. That's the note map. You make it once, but you have to use the game window in the exact same spot every time, otherwise the clicks land in the wrong place.

1. Open Growtopia in **windowed mode** and equip your keytar.
2. Move the Growtopia window to the **top left or top right corner** of your screen, exactly in the corner. Do this every time you play so the map still lines up. Yes, it's tedious.
3. Stand on the middle note (usually B, or wherever you can see all of the notes), then **zoom out all the way**.
4. In the Music Suite click **Calibrator**, then **Start Calibration**.
5. It will say `CLICK the position for note 'c1'`. Click that note in the game and it moves on to the next one (`d1`, `e1`, ...). The order is natural notes first, then flats (`b`), then sharps (`#`). Just follow what it tells you.
6. Click **Save Map** and save it somewhere you'll remember.

<img width="800" height="489" alt="gif1" src="https://github.com/user-attachments/assets/2b09443c-7319-4581-b4fe-f300476eeb0d" />


## Playing a song

1. Click **Load Note Map** and pick your map.
2. Click **Load Song** and pick a song `.json` (there's one in `examples/` to test with).
3. Put the Growtopia window in the same corner spot you calibrated in.
4. Press **START** or the hotkey `9`.

<img width="800" height="364" alt="gif2" src="https://github.com/user-attachments/assets/87ccac1b-b0cb-4d65-80f9-b121a84a1001" />



|Key|Action|
|-|-|
|`9`|Start|
|`8`|Pause / Resume|
|`0`|Stop|
|`-`|Slower|
|`=`|Faster|

If the mouse starts doing something it shouldn't, move it into the top left corner of the screen to emergency stop.

\---

## Making a song

1. Find a song on https://onlinesequencer.net and download it as a **MIDI** file.
2. Run `MIDI4.py` (double-click it, or `python MIDI4.py`). It asks for the MIDI file, converts it to the Growtopia notes, and asks where to save the `.json`.
3. Load that `.json` in the Music Suite like in "Playing a song".

`MIDI4.py` shifts the song up or down by octaves so it fits the keytar's range. You can open it in a text editor and change two settings at the top:

* `SLOW\_FACTOR`: `1.0` is normal speed, `2.0` is half speed.
* `MIN\_GAP`: the minimum time in seconds between notes. If it's too low, notes get skipped.
<img width="1056" height="772" alt="image" src="https://github.com/user-attachments/assets/1e9e89fa-d5c3-44da-be56-982225c3a932" />


## Two players (dual instance)

For songs with two parts you can run two Growtopia instances at once. **Easier using two monitors.**

How to open two instances: https://www.youtube.com/watch?v=BBbG8HEWICY

1. Convert the MIDI with `MIDI8.py` instead of `MIDI4.py`. It splits the song into two files: `\_player1.json` (the top / higher notes) and `\_player2.json` (the bottom / lower notes).
2. Make a note map for each game window (one per monitor), the same way as above.
3. In the Music Suite tick **Dual Instance Mode**, load a song and a note map for each instance, and press **START BOTH**.

`MIDI8.py` also has settings at the top: `SLOW\_FACTOR` (here lower means faster), `MIN\_GAP`, and `MAX\_POLYPHONY` (how many notes can play at the same time).

\---

## Known bugs

* The falling notes display is bugged.
* Slowing the song down while it's playing makes the script pause for a moment.

\---

MIT license. Made by SpacySven.


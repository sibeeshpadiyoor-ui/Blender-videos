# Induction kit, Video 1: The bulb with no battery

- **Topic:** mutual induction and the jumping ring (class 8-10)
- **Length:** 76 seconds, horizontal (16:9), because the kit is wide
- **One idea:** a *changing* magnetic field pushes a current around any closed
  loop it passes through, whether that loop is a coil or a plain metal ring.
- **Model:** `animations/induction_kit.py` (the animation itself is not built yet)

| Time | Narration (spoken) | On screen |
|---|---|---|
| 0–6 s | "This bulb has no battery. No wire joins it to the supply. So why is it glowing?" | Close on the bulb coil glowing on the core. Camera circles it to show there are no leads. Large **?** |
| 6–20 s | "The lower coil carries alternating current, which goes back and forth fifty times a second. So its magnetic field keeps growing, shrinking and reversing. The iron core carries that changing field upward." | Pull back to the whole kit. Press the switch. Field lines pulse out of the primary and up the core, reversing direction. Labels: **primary coil**, **iron core** |
| 20–31 s | "A changing magnetic field through a coil pushes a current around it. That is electromagnetic induction. One coil drives the other without touching it: mutual induction." | Field lines thread the bulb coil; arrows run round its turns; the bulb glows. Caption: **Mutual induction** |
| 31–41 s | "With a steady current from a cell, nothing happens. The needle kicks only at the moment we switch on, and again when we switch off. No change, no current." | Swap in the cell, tap key and galvanometer. Key down: needle kicks right, then returns. Key up: kicks left. Caption: **No change, no current** |
| 41–51 s | "Lift the coil and the bulb dims, because less of the field reaches it. Double the turns, and the voltage roughly doubles. That is how a transformer works." | Bulb coil slides up the core and fades. Then the 300-turn and 600-turn coils on the multimeter: second reading about twice the first. Caption: **More turns, more volts** |
| 51–60 s | "Now an aluminium ring. It is a coil with just one turn. The induced current makes the ring a magnet that opposes the coil, and it jumps." | Ring dropped over the core onto the primary. Arrow runs round the ring. Press the switch: the ring shoots up the core. Slow-motion replay |
| 60–67 s | "Cut a slot in the ring and it stays put. No complete path, no current, no force." | Split ring on the core. Press the switch: nothing. Highlight the slot. Caption: **No loop, no current** |
| 67–76 s | "Chargers, transformers and induction cooktops all use this. Next: why does the ring get hot?" | Three small icons: phone charger, transformer, cooktop. Then **Next: eddy currents** |

Narration is about 185 words. Times are taken from the recorded voiceover:
`kits/induction_kit/voiceover/voiceover.mp3`, with the start of every sentence
in `timings.json` beside it (`python kits/induction_kit/make_voiceover.py`).

## Notes for the animation

- The field lines and current arrows are the only things that are not real
  objects; keep them one colour each (field blue, current yellow) throughout.
- "Roughly doubles" is deliberate: the open core leaks field, so the real kit
  will not give an exact 2:1 ratio.
- The ring jump at 24 V is tens of centimetres, not a launch off the core.
  Animate it to stay on the core so the video matches what students will see.

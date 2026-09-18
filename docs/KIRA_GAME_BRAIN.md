# Kira Game Brain

Game Brain is a constrained controller for Kira's isolated desktop. It targets single-player/offline games.

Implemented: allow-listed keyboard input, relative mouse look, click, bounded hold durations, strategic step limits, and a planner interface.

Important: the current Kira LLM is text-only. The agent can capture frames, but autonomous visual gameplay requires a local vision-language model or a game-specific state adapter. The code intentionally does not pretend screenshot bytes are understood by a text-only model.

Competitive multiplayer automation is outside the default design. Kira Cloud should be used for single-player games, sandboxes, emulators where permitted, and browser games.

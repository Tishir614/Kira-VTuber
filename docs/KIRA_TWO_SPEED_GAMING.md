# Two-speed Kira Game Brain

Kira now separates gameplay into two clocks.

The strategic clock uses local multimodal vision, memory and the LLM to understand goals and plan. The reflex clock does not call an LLM. It consumes the latest structured observation and can make tiny bounded reactions such as creating distance from a clearly visible threat.

This design avoids pretending a large vision model can run at action-game frame rate. Actual frequency depends on hardware and Cloud capture latency. The default target is 12 Hz for the lightweight reflex loop, while strategic reasoning remains much slower.

Reflexes are deliberately conservative and intended for single-player/offline games.

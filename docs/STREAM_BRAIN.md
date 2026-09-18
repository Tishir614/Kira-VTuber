# Stream brain

Kira's stream brain sits between normalized platform events and the AI response pipeline.

Modes:
- `quiet`: conservative, primarily direct mentions.
- `active`: normal mention-driven interaction.
- `chaos`: reserved for more spontaneous behavior once non-mention selection is enabled.

Global and per-viewer cooldowns prevent reply floods. Platform events such as subscriptions, raids, cheers and gifts use the same normalized queue so Twitch/YouTube-specific code stays outside the AI personality layer.

The "chaos" name changes response frequency only. It does not bypass safety, platform rules, moderation or privacy controls.

# Stream chat architecture

Twitch and YouTube messages are normalized into one local queue. Kira tracks a lightweight in-memory viewer roster, deduplicates repeated events and, by default, responds only when her name is mentioned.

Credentials are never committed. Platform adapters are isolated under `kira/integrations/`.

A local injection endpoint exists for development so the complete queue -> audience -> Kira response pipeline can be tested before platform OAuth is configured. The production Twitch/YouTube adapters must use their supported authenticated APIs rather than scraping chat.

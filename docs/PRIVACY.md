# Privacy

Kira is local-first. LLM inference, STT and TTS are designed to run on the user's machine.

Persistent local memory is stored under runtime/ and is ignored by Git. Supabase synchronization is optional and must be configured explicitly.

Do not commit API keys, Supabase secrets, voice recordings, private chat logs, or model assets to Git.

The publishable Supabase key may be used by an authenticated client with correct RLS policies. Never place a service-role/secret key in the desktop or browser client.

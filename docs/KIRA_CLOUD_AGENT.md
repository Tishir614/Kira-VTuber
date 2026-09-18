# Kira Cloud Agent

The agent controls only Kira's isolated desktop. It does not automate the host user's desktop.

Current capabilities: browser open/search/screenshot, state reporting, and launching explicitly allow-listed games. Browser data and game saves live inside Kira Cloud's persistent volume.

The game launcher intentionally accepts executable names only from KIRA_GAME_ALLOWLIST. Do not mount the host home directory or copy host browser credentials into the cloud desktop.

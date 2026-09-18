# YouTube OAuth

Kira uses Google OAuth 2.0 with the YouTube scope and a localhost callback:
http://127.0.0.1:8765/auth/youtube/callback

After authorization Kira calls liveBroadcasts.list with mine=true and broadcastStatus=active, reads snippet.liveChatId, and starts the YouTube chat adapter automatically. The refresh token is stored locally in runtime/youtube_oauth.json.

Configure the same redirect URI in the Google Cloud OAuth client. Kira Core must be reachable on localhost:8765 while completing the browser authorization.

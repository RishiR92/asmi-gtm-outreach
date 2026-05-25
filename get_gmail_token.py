"""
One-time script to get Gmail OAuth2 refresh token.
Run this ONCE locally, then add the output values to Railway environment variables.

Usage:
    pip install google-auth-oauthlib
    python get_gmail_token.py
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Paste your Client ID and Client Secret from Google Cloud Console below
CLIENT_ID     = input("Paste your Client ID: ").strip()
CLIENT_SECRET = input("Paste your Client Secret: ").strip()

client_config = {
    "installed": {
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
        "token_uri":     "https://oauth2.googleapis.com/token",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=0)

print("\n✅ Add these 3 values to Railway → your service → Variables:\n")
print(f"GMAIL_CLIENT_ID     = {CLIENT_ID}")
print(f"GMAIL_CLIENT_SECRET = {CLIENT_SECRET}")
print(f"GMAIL_REFRESH_TOKEN = {creds.refresh_token}")

from linkedin_api.client import LinkedInClient
from linkedin_api.profile import fetch_above_activity


client = LinkedInClient(
    li_at="YOUR_LI_AT",
    jsessionid="ajax:YOUR_JSESSIONID",
)

raw = fetch_above_activity(
    client,
    "prerona-basak",
)

print(raw)
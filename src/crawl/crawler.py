# %%
import os

from dotenv import load_dotenv
from praw import Reddit
from psaw import PushshiftAPI

# %%
load_dotenv()

# %%
reddit = Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)
print(reddit.auth.scopes())

psaw_api = PushshiftAPI(reddit)
psaw_api.search_submissions()

# %%
for sub in reddit.subreddit("learnpython").hot(limit=10000):
    print(sub, sub.title)


# %%
res = reddit.get("/r/learnpython", params={"limit": 10, "after": "t3_x3v2sk"})
# %%

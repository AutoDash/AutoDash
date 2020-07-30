import os
import praw
from dotenv import load_dotenv

from utils import get_project_root


CRAWLABLE_SUBREDDITS = [
    'CarCrash'
]

# Retrieves posts from specified Reddit pages
class RedditAccessor:
    reddit = None
    loaded_posts = []

access = RedditAccessor()


def __init_reddit_access():
    load_dotenv(os.path.join(get_project_root(), '.env'))
    access.reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                                user_agent='CarCrashScraper')


def reload_posts():
    if access.reddit is None:
        __init_reddit_access()

    access.loaded_posts = []
    for subreddit in CRAWLABLE_SUBREDDITS:
        hot_posts = access.reddit.subreddit(subreddit).hot(limit=1000)
        access.loaded_posts.extend(hot_posts)


def get_posts():
    if len(access.loaded_posts) == 0:
        reload_posts()
    return access.loaded_posts

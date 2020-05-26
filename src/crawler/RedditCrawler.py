import os
import praw
from dotenv import load_dotenv

from src.crawler.iCrawler import iCrawler, CrawlerException
from src.data.MetaDataItem import MetaDataItem
from src.utils import get_project_root

CRAWLABLE_SUBREDDITS = [
    'CarCrash'
]

class RedditCrawler(iCrawler):

    def __init__(self):
        super().__init__()
        load_dotenv(os.path.join(get_project_root(), '.env'))
        self.reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                                  client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                                  user_agent='CarCrashScraper')
        self.reload_posts()

    def reload_posts(self):
        self.posts = []
        for subreddit in CRAWLABLE_SUBREDDITS:
            hot_posts = self.reddit.subreddit(subreddit).hot(limit=1000)
            self.posts.extend(hot_posts)

    async def find_next_downloadable(self) -> MetaDataItem:
        while len(self.posts):
            post = self.posts.pop(0)
            if post.media is not None and 'oembed' in post.media.keys():
                if await self.check_new_url(post.url):
                    title = post.media['oembed']['title']
                    video_source = post.media['type']
                    reddit_tag = {
                        'id': post.id,
                        'title': post.title
                    }
                    metadata = MetaDataItem(title, post.url, video_source)
                    metadata.add_tag('reddit_post_info', reddit_tag)
                    return metadata

        raise CrawlerException("Reddit crawler could not find any new videos")

    async def next_downloadable(self) -> MetaDataItem:
        try:
            return await self.find_next_downloadable()
        except CrawlerException:
            self.reload_posts()
        # Try to find a new downloadable after updating posts, but if this fails then give up
        return await self.find_next_downloadable()

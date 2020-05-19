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
        load_dotenv(os.path.join(get_project_root(), '.env'))
        self.reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                                  client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                                  user_agent='CarCrashScraper')

    async def next_downloadable(self) -> MetaDataItem:
        for subreddit in CRAWLABLE_SUBREDDITS:
            hot_posts = self.reddit.subreddit(subreddit).hot()
            for index, post in enumerate(hot_posts):
                if post.media is not None and 'oembed' in post.media.keys():
                    if await self.check_new_url(post.url):
                        title = post.media['oembed']['title']
                        video_source = post.media['type']
                        reddit_tag = {
                            'id': post.id,
                            'title': post.title
                        }
                        metadata = MetaDataItem(title, post.url, video_source, "", "", "")
                        metadata.add_tag('reddit_post_info', reddit_tag)
                        return metadata

        raise CrawlerException("Reddit crawler could not find any new videos")

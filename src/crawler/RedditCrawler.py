import os
import praw
from dotenv import load_dotenv

from src.crawler.iCrawler import iCrawler, CrawlerException
from src.data.MetaDataItem import MetaDataItem

CRAWLABLE_SUBREDDITS = [
    'CarCrash'
]



class RedditCrawler(iCrawler):

    def __init__(self):
        load_dotenv(os.path.join(get_root_dir, '.env'))
        self.reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                                  client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                                  user_agent='CarCrashScraper')

    async def next_downloadable(self) -> MetaDataItem:
        for subreddit in CRAWLABLE_SUBREDDITS:
            hot_posts = self.reddit.subreddit(subreddit).hot()
            for index, post in enumerate(hot_posts):
                if post.media is not None and 'oembed' in post.media.keys():
                    download_info = {
                        'reddit_title': post.title,
                        'video_title': post.media['oembed']['title'],
                        'post_id': post.id,
                        'video_url': post.url,
                        'video_type': post.media['type']
                    }

                    if iCrawler.check_new_url(post.url):
                        return MetaDataItem()


        raise CrawlerException("Reddit crawler could not find any new videos")


r = RedditCrawler()
r.next_downloadable()
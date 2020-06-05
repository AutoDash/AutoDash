from src.crawler.RedditAccessor import get_posts, reload_posts
from src.crawler.iCrawler import iCrawler, CrawlerException
from src.data.MetaDataItem import MetaDataItem


class RedditCrawler(iCrawler):

    def __init__(self):
        super().__init__()


    async def find_next_downloadable(self, posts) -> MetaDataItem:
        while len(posts):
            post = posts.pop(0)
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
        posts = get_posts()

        try:
            return await self.find_next_downloadable(posts)
        except CrawlerException:
            reload_posts()
            posts = get_posts()
        # Try to find a new downloadable after updating posts, but if this fails then give up
        return await self.find_next_downloadable(posts)

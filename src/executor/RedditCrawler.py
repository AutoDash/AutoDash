from ..crawler.RedditAccessor import get_posts, reload_posts
from ..crawler.iCrawler import iCrawler, CrawlerException
from ..data.MetaDataItem import MetaDataItem


class RedditCrawler(iCrawler):

    def __init__(self, *parents):
        super().__init__(*parents)


    def find_next_downloadable(self, posts) -> MetaDataItem:
        print("RedditCrawler.find_next_downloadable")
        while len(posts):
            print("RedditCrawler.find_next_downloadable post: {}, size: {}".format(posts[0], len(posts)))
            post = posts.pop(0)
            if post.media is not None and 'oembed' in post.media.keys():
                print("RedditCrawler.find_next_downloadable post.media is not None")
                if self.check_new_url(post.url):
                    print("RedditCrawler.find_next_downloadable check_new_url is True")
                    title = post.media['oembed']['title']
                    video_source = post.media['type']
                    reddit_tag = {
                        'id': post.id,
                        'title': post.title
                    }
                    metadata = MetaDataItem(title=title, url=post.url, download_src=video_source)
                    metadata.add_tag('reddit_post_info', reddit_tag)
                    return metadata

        print("RedditCrawler.find_next_downloadable exception")
        raise CrawlerException("Reddit crawler could not find any new videos")

    def next_downloadable(self) -> MetaDataItem:
        print("RedditCrawler.next_downloadable")
        posts = get_posts()

        try:
            return self.find_next_downloadable(posts)
        except CrawlerException:
            print("RedditCrawler.next_downloadable exception")
            reload_posts()
            posts = get_posts()
        # Try to find a new downloadable after updating posts, but if this fails then give up
        return self.find_next_downloadable(posts)

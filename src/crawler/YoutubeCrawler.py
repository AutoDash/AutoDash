from src.crawler.iCrawler import iCrawler, CrawlerException
from src.data.MetaDataItem import MetaDataItem
from src.pipeline import StatefulExecutorProxy
import youtube_dl

class YoutubeCrawler(iCrawler):
    YOUTUBE_SRC_IDENTIFIER = "YouTube"

    def __init__(self, search_terms: list, log_func=print, check_url=True, lock=None):
        super().__init__()
        self.search_terms = search_terms
        self.log_func = log_func
        self.check_url = check_url  # If true, will not return MetaDataItem if already exists in database

        if len(search_terms) == 0:
            raise ValueError("Must provide at least 1 search term")

        self.search_results = []
        self.skip_n = 0
        self.get_n = 100
        self.log("init")
        self.stateful = True
        self.lock = lock

    def __update_search_results(self):
        ydl_opts = {'quiet': True}
        total_results = []
        for search_term in self.search_terms:
            query = "ytsearch{0}:{1}".format(self.get_n, search_term)
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                results = ydl.extract_info(query, process=False, download=False)
            total_results += results['entries'][self.skip_n:]

        self.search_results = total_results
        self.log("Crawled {0}".format(self.get_n*len(self.search_terms)))
        self.skip_n = self.get_n
        self.get_n *= 2

    async def next_downloadable(self) -> MetaDataItem:
        while True:  # Loop until return
            self.log(self.search_results[:5])
            
            with self.lock:
                zero_cases = 0
                while len(self.search_results) == 0:
                    if zero_cases > 3:
                        raise CrawlerException("YouTube crawler could not find more results")
                    self.__update_search_results()
                    zero_cases += 1


                res = self.search_results[0]
                self.search_results = self.search_results[1:]

                if not self.check_url or await self.check_new_url(res['url']):
                    url = "https://www.youtube.com/watch?v={0}".format(res["url"])
                    title = res.get("title", None)
                    id = res["id"]
                    tags = {'id': id}

                    if title is None:
                        self.log("Failed to extract title: Got {0}".format(res))
                        title = "TitleUnknown"
                        tags['title_extraction_failed'] = True

                    return MetaDataItem(title, url, self.YOUTUBE_SRC_IDENTIFIER, tags=tags)

    def log(self, log):
        self.log_func("[Youtube Crawler] {0}".format(log))

    def register_shared(self, manager):
        manager.register('YoutubeCrawler', lambda: self, proxytype=StatefulExecutorProxy, exposed=['run', 'get_next', 'set_lock'])

    def share(self, manager):
        return manager.YoutubeCrawler()

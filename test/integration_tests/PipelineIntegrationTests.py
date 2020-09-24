import unittest
import os

from src.PipelineConfiguration import PipelineConfiguration
from src.executor.iExecutor import iExecutor
from src.downloader.UniversalDownloader import UniversalDownloader
from src.downloader.YoutubeDownloader import YoutubeDownloader
from src.crawler.YoutubeCrawler import YoutubeCrawler
from src.data.VideoItem import VideoItem
from src.pipeline import run as Administrator

from test.mock.MockDataAccessor import MockDataAccessor

dest_dir = './youtube_videos'
assert(not os.path.exists(dest_dir))

class PipelineIntegrationTest(unittest.TestCase):

    def tearDown(self):
        os.system(f'rm -r {dest_dir}')
        video_item = None

    def test_youtube_crawl_and_download_and_modify(self):
       
        search_terms = ["car accident"]

        pc = PipelineConfiguration()

        x = YoutubeCrawler(search_terms) \
                .set_database(MockDataAccessor())
        x = UniversalDownloader(x) \
                .register_downloader(".*youtube.*", YoutubeDownloader()) \
                .set_pathname(dest_dir)
        x = TestExecutorGenericVideoModification(x) 

        pc.load_graph(x)
        Administrator(pc, max_iterations=2, n_workers=2)

        downloaded_videos = os.listdir(dest_dir)
        self.assertEqual(len(downloaded_videos), 2)
        for vid_name in downloaded_videos:
            self.assertTrue('.mp4' in vid_name)

if __name__ == '__main__':
    unittest.main()



        

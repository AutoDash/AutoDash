import unittest

from src.PipelineConfiguration import PipelineConfiguration
from src.executor.iExecutor import iExecutor
from src.downloader.UniversalDownloader import UniversalDownloader
from src.downloader.YoutubeDownloader import YoutubeDownloader
from src.data.VideoItem import VideoItem
from src.pipeline import run as Administrator

from test.mock.MockDataAccessor import MockDataAccessor

class TestExecutorGenericVideoModification(iExecutor):
    def run(self, item: VideoItem):
        item.npy[..., 0] = 0
        return item

class PipelineIntegrationTest(unittest.TestCase):

    def test_imgur_video_download_and_modify(self):
        search_terms = ["car accident"]

        pc = PipelineConfiguration()

        x = YoutubeCrawler(search_terms) \
                .set_database(MockDataAccessor())
        x = UniversalDownloader(x) \
                .register_downloader(".*youtube.*", YoutubeDownloader())
        x = TestExecutorGenericVideoModification(x)

        pc.load_graph(x)
        Administrator(pc, max_iterations=5, n_workers=1)




        

from downloader.iDownloader import iDownloader
from data.VideoItem import VideoItem
from imgur_downloader import ImgurDownloader as imgur

class ImgurDownloader(iDownloader):
    async def download(self, link:str) -> VideoItem:
        downloader = imgur(link, dir_download=self.pathname, file_name=link)
        downloader.on_image_download(self.on_download_callback)
        downloader.save_images()
        return VideoItem(self.file_name)

    def on_download_callback(self, pos, url, file):
        self.file_name = file

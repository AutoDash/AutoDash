from .iDownloader import iDownloader, DownloadException
from ..data.MetaDataItem import MetaDataItem
from ..data.VideoItem import VideoItem
import youtube_dl
import os

class YoutubeDownloader(iDownloader):

    def __init__(self, parents=[], *args, dl_archive=os.path.join(os.getcwd(), 'ydl_archive.txt'), **kwargs):
        super().__init__(parents, *args, **kwargs)
        self.file_name = None
        self.dl_opts = {
            'nocheckcertificate': True,
            'progress_hooks': [self.on_download_callback],
            'restrictfilenames': True,
            'format': 'mp4'
        }

    async def download(self, md_item: MetaDataItem) -> VideoItem:
        if not os.path.exists(self.pathname):
            os.system(f'mkdir -p {self.pathname}')

        ydl = youtube_dl.YoutubeDL(self.dl_opts)

        link = md_item.url
        ydl.download([link])
        # TODO self.file_name doesn't initialize when file already exists locally
        if self.file_name is None:
            raise DownloadException("Failed to download youtube link " + link)

        base_filename, ext = os.path.splitext(self.file_name)
        os.system(f"mv {base_filename}* {self.pathname}")

        return VideoItem(os.path.join(self.pathname, self.file_name))

    def on_download_callback(self, download):
        print("In callback: ", download)
        if download['status'] == 'finished':
            self.file_name = download['filename']
        else:
            self.file_name = None

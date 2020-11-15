from .iDownloader import iDownloader, DownloadException
from ..data.MetaDataItem import MetaDataItem
from ..data.VideoItem import VideoItem
import youtube_dl
import os

class YoutubeDownloader(iDownloader):

    def __init__(self, parents=None, *args, dl_archive=os.path.join(os.getcwd(), 'ydl_archive.txt'), **kwargs):
        super().__init__(parents if parents is not None else [], *args, **kwargs)
        self.file_name = None
        self.dl_opts = {
            'nocheckcertificate': True,
            'progress_hooks': [self.on_download_callback],
            'restrictfilenames': True,
            'format': 'mp4'
        }

    def download(self, md_item: MetaDataItem) -> VideoItem:
        ydl = youtube_dl.YoutubeDL(self.dl_opts)
        
        link = md_item.url
        try:
            ydl.download([link])
        except youtube_dl.utils.YoutubeDLError:
            raise DownloadException("Failed to download youtube link " + link)
        # TODO self.file_name doesn't initialize when file already exists locally
        if self.file_name is None:
            raise DownloadException("Failed to download youtube link " + link)

        base_filename, ext = os.path.splitext(self.file_name)
        new_name = self.video_storage.get_file_name(md_item)
        self.video_storage.move_video(self.file_name, new_name + ext)

        return VideoItem(metadata=md_item, filepath=(self.video_storage.get_file(md_item) + ext))

    def on_download_callback(self, download):
        print("In callback: ", download)
        if download['status'] == 'finished':
            self.file_name = download['filename']
        else:
            self.file_name = None

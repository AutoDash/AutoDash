#!/usr/bin/env python3
from src.downloader.iDownloader import iDownloader, DownloadException
from src.data.VideoItem import VideoItem
import youtube_dl


class YoutubeDownloader(iDownloader):

    def __init__(self):
        self.ydl = youtube_dl.YoutubeDL({
            'nocheckcertificate': True,
            'progress_hooks': [self.on_download_callback]
        })

    async def download(self, link:str) -> VideoItem:
        self.ydl.download([link])
        if self.file_name is None:
            raise DownloadException("Failed to download youtube link " + link)
        return VideoItem(self.file_name)

    def on_download_callback(self, download):
        if download['status'] == 'finished':
            self.file_name = download['filename']
        else:
            self.file_name = None
#!/usr/bin/env python3
from src.downloader.iDownloader import iDownloader, DownloadException
from src.data.MetaDataItem import MetaDataItem
from src.data.VideoItem import VideoItem
import youtube_dl
import os
import asyncio


class YoutubeDownloader(iDownloader):

    def __init__(self, *args, dl_archive=os.path.join(os.getcwd(), 'ydl_archive.txt'), **kwargs):
        super().__init__(*args, **kwargs)
        self.file_name = None
        self.dl_opts = {
            'nocheckcertificate': True,
            'progress_hooks': [self.on_download_callback],
            'restrictfilenames': True
        }

    async def download(self, md_item: MetaDataItem) -> VideoItem:
        ydl = youtube_dl.YoutubeDL(self.dl_opts)

        link = md_item.url
        ydl.download([link])
        # TODO self.file_name doesn't initialize when file already exists locally
        if self.file_name is None:
            raise DownloadException("Failed to download youtube link " + link)

        return VideoItem(self.file_name)

    def on_download_callback(self, download):
        print("In callback: ", download)
        if download['status'] == 'finished':
            self.file_name = download['filename']
        else:
            self.file_name = None

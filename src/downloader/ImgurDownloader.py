from ..downloader.iDownloader import iDownloader, DownloadException
from ..data.VideoItem import VideoItem
from ..data.MetaDataItem import MetaDataItem
from imgur_downloader import ImgurDownloader as imgur
import os, re, shutil


class ImgurDownloader(iDownloader):

    async def download(self, md_item: MetaDataItem) -> VideoItem:
        link = md_item.url
        pathname = self.video_storage.get_storage_dir()
        filename = self.video_storage.get_file_name(md_item)

        print(f"downloading file {filename}")
        downloader = imgur(link,
                           dir_download=pathname,
                           file_name=filename)
        files, idx = downloader.save_images()
        print(f"downloaded {files}")

        # album downloaded, extract video from album
        if len(files) > 1:
            # for each of the files downloaded
            for file in files:
                fname, ext = os.path.splitext(file)
                print(fname, ext)
                if ext in ['.mp4']:
                    src = os.path.join(pathname, filename, file)
                    dest = os.path.join(pathname,filename) + ".mp4"
                    print(f"moving from {src} to {dest}")
                    os.rename(src, dest)
                    break
            # remove old directory
            shutil.rmtree(os.path.join(pathname, filename))

        filepath = os.path.join(pathname, filename) + ".mp4"

        if not os.path.exists(filepath):
            raise DownloadException(f"could not download video from {link}")

        return VideoItem(filepath=filepath, metadata=md_item)

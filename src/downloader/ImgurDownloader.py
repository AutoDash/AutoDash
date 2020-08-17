from ..downloader.iDownloader import iDownloader, DownloadException
from ..data.VideoItem import VideoItem
from ..data.MetaDataItem import MetaDataItem
from imgur_downloader import ImgurDownloader as imgur
import os, re, shutil


class ImgurDownloader(iDownloader):
    allowed_chars = re.compile('\W')

    async def download(self, md_item: MetaDataItem) -> VideoItem:
        link = md_item.url
        filename = self.get_filename(link)

        print(f"downloading file {filename}")
        downloader = imgur(link, dir_download=self.pathname, file_name=filename)
        files, idx = downloader.save_images()
        print(f"downloaded {files}")

        # album downloaded, extract video from album
        if len(files) > 1:
            # for each of the files downloaded
            for file in files:
                fname, ext = os.path.splitext(file)
                print(fname, ext)
                if ext in ['.mp4']:
                    src = os.path.join(self.pathname, filename, file)
                    dest = os.path.join(self.pathname,filename) + ".mp4"
                    print(f"moving from {src} to {dest}")
                    os.rename(src, dest)
                    break
            # remove old directory
            shutil.rmtree(os.path.join(self.pathname, filename))

        filepath = os.path.join(self.pathname, filename) + ".mp4"

        if not os.path.exists(filepath):
            raise DownloadException(f"could not download video from {link}")

        return VideoItem(filepath=filepath, metadata=md_item)

    def get_filename(self, link):
        return ImgurDownloader.allowed_chars.sub('', link)

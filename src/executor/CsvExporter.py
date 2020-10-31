from .iExecutor import iExecutor
from ..data.VideoItem import VideoItem
from ..signals.StopSignal import StopSignal
from ..utils import get_project_root
import os
import csv
from pathlib import Path

STORAGE_DIR = Path(os.path.join(get_project_root(), "data_files"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

class CsvExporter(iExecutor):
    def run(self, item: VideoItem):
        print("Start exporting file")
        metadata = iExecutor.get_metadata(item)
        bbs = metadata.bb_fields
        if (bbs is None) or ("frames" not in bbs):
            raise StopSignal("No bounding box fields for this item")

        filename = str(metadata.id) + ".csv"
        with open(STORAGE_DIR / filename, 'w') as f:
            writer = csv.writer(f)
            for i in range(len(bbs['frames'])):
                writer.writerow([
                    bbs['frames'][i],
                    bbs['ids'][i],
                    bbs['clss'][i],
                    bbs['x1s'][i],
                    bbs['y1s'][i],
                    bbs['x2s'][i],
                    bbs['y2s'][i],
                    bbs['has_collision'][i],
                ])
        print(f"Done exporting file {filename}")
        return item


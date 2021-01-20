from ..data.MetaDataItem import MetaDataItem
from ..data.VideoItem import VideoItem
from .iExecutor import iExecutor
import numpy as np

class BBInterpolator(iExecutor):
    def __init__(self, *parents, slack_pixels=0):
        super().__init__(*parents)

    def run(self, item: MetadataItem):
        metadata = self.get_metadata(item)
        if len(metadata.get('bb_fields'), {}) == 0:
            return item
        bb_fields = metadata['bb_fields']
        boxes = np.array([*zip(bb_fields['x1s'], bb_fields['x2s'], bb_fields['y1s'], bb_fields['y2s'])])
        ids = np.array(bb_fields['ids'])
        frames = np.array(bb_fields['ids'])
        values = []
        for iden in np.unique(ids):
            bbs = boxes[ids == iden]
            frms = frames[ids == iden]
            holes = np.where(np.any(np.isnan(bbs), axis=0))
            for segment in np.split(bbs, holes):
                if np.isnan(segment[0]):
                    segment = segment[1:]
                values = np.append(values, np.interp(segment))
        return item

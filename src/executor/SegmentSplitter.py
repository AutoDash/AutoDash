from ..data.VideoItem import VideoItem
from .iExecutor import iExecutor
from ..signals.SkipSignal import SkipSignal
import re
import numpy as np

class SegmentSplitter(iExecutor):
    def __init__(self, *parents, clip_length='5s', length_threshold='3s'):
        super().__init__(*parents)
        self.clip_len_s = SegmentSplitter.parse_time(clip_length)
        self.len_thresh_s = SegmentSplitter.parse_time(length_threshold)
    
    def split_segment(self, item):
        metadata = iExecutor.get_metadata(item)
        # First we find the length of BBs
        bbs = metadata.bb_fields.get_bbs_as_arrs()
        fps = item.fps
        collision_locations = metadata.bb_fields.collision_locations
        if len(collision_locations) < 1:
            raise SkipSignal("Item has no collision_locations")
        if len(bbs) == 0:
            raise SkipSignal("Item has no bounding boxes")
        dtype = [
            ('frame', np.int),
            ('id', np.int),
            ('class', object),
            ('x1', np.int),        
            ('y1', np.int),        
            ('x2', np.int),        
            ('y2', np.int),        
            ('has_collision', np.bool),        
        ]
        bbs = np.array(bbs, dtype=dtype)
        collision_locations = np.sort(collision_locations)
        frames = np.unique(bbs['frame'])
        segments = [ ]
        segments += self.create_positives(collision_locations, frames, fps)
        segments += self.create_negatives(segments, collision_locations, frames, fps)        
        items = [ ]
        for idx, (begin, end) in enumerate(segments):
            item = metadata.clone()
            item.bb_fields.crop_range(begin, end)
            item.id = metadata.id + f'-{idx}'
            item.start_i = begin
            item.end_i = end
            items.append(item)
        return items

    def create_positives(self, ALs, frames, fps):
        cover = [ ]
        begin = 0
        for al in ALs:
            # Check for minimum range
            if (al - begin) < self.len_thresh_s * fps:
                continue
            begin = max(0, int(al - self.clip_len_s * fps))
            it_begin = np.searchsorted(frames, begin)
            it_end = np.searchsorted(frames, al)
            it_end = min(frames.shape[0] - 1, it_end) # Prevent out of index access for ALs with no BBs
            # Add coverage
            cover.append((frames[it_begin], frames[it_end]))
            begin = frames[it_end]
        return cover

    def create_negatives(self, positive_cover, ALs, frames, fps):
        cover = [ ]
        begin = 0
        end = frames[-1]
        for prange in positive_cover + [(end, end)]:
            end, next_begin = prange
            it_begin = np.searchsorted(frames, begin)
            it_end = np.searchsorted(frames, end)
            n_covers = int((it_end - it_begin) / fps / self.clip_len_s)
            if n_covers < 1:
                continue
            delta = (it_end - it_begin) / n_covers
            cover += [ (int(it_begin + i * delta), int(it_begin + (i+ 1) * delta)) 
                    for i in range(0, n_covers) ]
            begin = next_begin
        return cover
            

    def parse_time(time):
        pattern = r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
        result = re.match(pattern, time)
        if not result:
            raise ValueError(f'Invalid time: {time}. Expected digit followed by [smh]')
        hours, minutes, seconds = result.groups()
        time_s = int(hours or 0)
        time_s *= 60
        time_s += int(minutes or 0)
        time_s *= 60
        time_s += int(seconds or 0)
        if time_s <= 0:
            raise ValueError(f'Invalid time: {time}. Expected a non-zero positive value')
        return time_s

    
    def run(self, item: VideoItem):
        return map(
            lambda mdi: VideoItem(mdi, filepath=item.filepath),
            self.split_segment(item)
            )

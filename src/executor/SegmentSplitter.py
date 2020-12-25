from ..data.VideoItem import VideoItem
from .iExecutor import iExecutor
import re
import numpy as np

class SegmentSplitter(iExecutor):
    def __init__(self, *parents, clip_length='5s', length_threshold='3s'):
        super().__init__(*parents)
        self.clip_len_s = SegmentSplitter.parse_time(clip_length)
        self.len_thresh_s = SegmentSplitter.parse_time(length_threshold)
    
    def split_segment(self, metadata):
        # First we find the length of BBs
        bbs = metadata.bb_fields.get_bbs_as_arrs()
        begin = metadata.start_i
        fps = 30 # TODO: Should store fps in bb_fields... metadata.bb_fields.fps
        accident_locations = metadata.bb_fields.accident_locations
        if len(accident_locations) < 1:
            raise StopSignal("Item has no accident_locations")
        dtype = [
            ('frame', np.int),
            ('id', np.int),
            ('class', object),
            ('x1', np.int),        
            ('y1', np.int),        
            ('x2', np.int),        
            ('y2', np.int),        
        ]
        bbs = np.array(bbs, dtype=dtype)
        accident_locations = np.sort(accident_locations)
        frames = np.unique(bbs['frame'])
        segments = [ ]
        breakpoint()
        segments += self.create_positives(begin, accident_locations, frames, fps)
        segments += self.create_negatives(begin, segments, accident_locations, frames, fps)        
        items = [ ]
        for begin, end in segments:
            item = metadata.clone()
            item.bb_fields.crop_range(begin, end)
            items.append(item)
        return items

    def create_positives(self, begin, ALs, frames, fps):
        cover = [ ]
        for al in ALs:
            # Check for minimum range
            if (al - begin) < self.len_thresh_s * fps:
                continue
            begin += max(0, al - self.clip_len_s)
            # Check for minimum BB coverage
            it_begin = np.searchsorted(frames, begin)
            it_end = np.searchsorted(frames, begin + al, 'right')
            if (it_end - it_begin + 1) < self.len_thresh_s * fps:
                continue
            # Add coverage
            cover.append((frames[it_begin], frames[it_end]))
            begin = frames[it_end]
        return cover

    def create_negatives(self, begin, positive_cover, ALs, frames, fps):
        cover = [ ]
        for cover in positive_cover:
            end, next_begin = cover
            it_begin = np.searchsorted(frames, begin)
            it_end = np.searchsorted(frames, end)
            n_covers = int((it_end - it_begin) / fps / self.clip_len_s)
            if n_covers < 1:
                continue
            delta = (it_end - it_begin) / n_covers
            cover += [ (it_begin + i * delta, it_begin + (i+ 1) * delta) 
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
            self.split_segment(item.metadata)
            )

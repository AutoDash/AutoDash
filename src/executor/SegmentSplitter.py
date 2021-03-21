from ..data.VideoItem import VideoItem
from ..data.VideoFile import VideoFile
from .iExecutor import iExecutor
from ..signals.SkipSignal import SkipSignal
import re
import numpy as np

class SegmentSplitter(iExecutor):
    def __init__(self, *parents, clip_length='5s', 
            length_threshold='3s', frames_after_al=10,
            post_collision_delay='5s'):
        super().__init__(*parents)
        self.clip_len_s = SegmentSplitter.parse_time(clip_length)
        self.len_thresh_s = SegmentSplitter.parse_time(length_threshold)
        self.frames_after_al = max(0, frames_after_al)
        self.post_collision_delay = SegmentSplitter.parse_time(post_collision_delay)

    def split_segment(self, item):
        metadata = iExecutor.get_metadata(item)
        video = VideoFile(item.filepath)
        # First we find the length of BBs
        bbs = metadata.bb_fields.get_bbs_as_arrs()
        collision_locations = metadata.bb_fields.collision_locations
        if len(bbs) == 0:
            raise SkipSignal("Item has no bounding boxes")
        if metadata.start_i is None:
            metadata.start_i = 0
        if metadata.end_i is None:
            metadata.end_i = video.true_length
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
        segments += self.create_positives(collision_locations, frames, metadata, video)
        segments += self.create_negatives(segments, collision_locations, frames, metadata, video)        
        items = [ ]
        for idx, (begin, end) in enumerate(segments):
            item = metadata.clone()
            item.bb_fields.crop_range(begin, end)
            item.id = metadata.id + f'-{idx}'
            item.start_i = begin + metadata.start_i
            item.end_i = end + metadata.start_i
            items.append(item)
        return items

    def create_positives(self, ALs, frames, metadata, video):
        cover = [ ]
        begin = 0
        for al in ALs:
            min_end = video.get_frame_after_time_elapsed(begin + metadata.start_i, self.len_thresh_s * 1000)
            # Check for minimum range
            if al + metadata.start_i + self.frames_after_al < min_end:
                begin = al
                raise SkipSignal("Not enough time before first collision")
                continue
            begin = video.get_frame_after_time_elapsed(metadata.start_i + al + self.frames_after_al, -self.clip_len_s * 1000)
            begin = max(0, begin - metadata.start_i)
            end = min(metadata.end_i - metadata.start_i, al + self.frames_after_al)
            it_begin = np.searchsorted(frames, begin)
            it_end = np.searchsorted(frames, end)
            it_end = min(frames.shape[0] - 1, it_end) # Prevent out of index access for ALs with no BBs
            # Add coverage
            cover.append((frames[it_begin], frames[it_end]))
            begin = frames[it_end]
        return cover

    def create_negatives(self, positive_cover, ALs, frames, metadata, video):
        cover = [ ]
        begin = 0
        end = frames[-1]
        for prange in positive_cover + [(end, end)]:
            end, next_begin = prange
            it_begin = np.searchsorted(frames, begin)
            it_end = np.searchsorted(frames, end)
            total_delta = video.get_time_delta(begin + metadata.start_i, end + metadata.start_i) / 1000
            n_covers = int(total_delta / self.clip_len_s)
            begin = video.get_frame_after_time_elapsed(next_begin + metadata.start_i, 
                    self.post_collision_delay * 1000)
            begin -= metadata.start_i
            if n_covers < 1:
                continue
            cover_frames = [ it_begin ]
            for _ in range(0, n_covers):
                next_frame = video.get_frame_after_time_elapsed(cover_frames[-1], self.clip_len_s * 1000)
                cover_frames.append(next_frame)
            cover += [ (int(cover_frames[i]), int(cover_frames[i+1])) 
                    for i in range(0, n_covers) ]
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
            lambda mdi: VideoItem(mdi, filepath=item.filepath), self.split_segment(item))

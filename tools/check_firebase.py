from src.database.FirebaseAccessor import FirebaseAccessor
from src.data.FilterCondition import FilterCondition


def get_num_metadata_item():
    f = FirebaseAccessor()
    ids = f.fetch_video_id_list()
    return len(ids)


def get_metadata_with_url(url):
    f = FirebaseAccessor()
    fc = FilterCondition("url == '{}'".format(url))
    data = f.fetch_newest_videos(filter_cond=fc)
    return data

videos = get_metadata_with_url('https://www.youtube.com/watch?v=vhACO_m5pH0')
print(len(videos))
for video in videos:
    print(video.id, video.start_i, video.end_i, len(video.bb_fields.objects) != 0)

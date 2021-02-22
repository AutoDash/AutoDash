from src.database.FirebaseAccessor import FirebaseAccessor
from src.data.FilterCondition import FilterCondition


# Firebase Scripts
def get_num_metadata_item():
    f = FirebaseAccessor()
    ids = f.fetch_video_id_list()
    return len(ids)


def get_metadata_with_id(id):
    f = FirebaseAccessor()
    fc = FilterCondition("id == '{}'".format(id))
    data = f.fetch_newest_videos(filter_cond=fc)
    return data


def get_metadata_with_url(url):
    f = FirebaseAccessor()
    fc = FilterCondition("url == '{}'".format(url))
    data = f.fetch_newest_videos(filter_cond=fc)
    return data


from src.database.LocalStorageAccessor import LocalStorageAccessor
from src.data.FilterCondition import FilterCondition


def get_num_metadata_item():
    l = LocalStorageAccessor()
    ids = l.fetch_video_id_list()
    return len(ids)


def get_metadata_with_id(id):
    l = LocalStorageAccessor()
    fc = FilterCondition("id == '{}'".format(id))
    data = l.fetch_newest_videos(filter_cond=fc)
    return data

def get_metadata_with_fc(fc):
    l = LocalStorageAccessor()
    data = l.fetch_newest_videos(filter_cond=fc)
    return data



def get_metadata_with_url(url):
    l = LocalStorageAccessor()
    fc = FilterCondition("url == '{}'".format(url))
    data = l.fetch_newest_videos(filter_cond=fc)
    return data

fc = FilterCondition("url == '{}' and start_i == {}".format('https://www.youtube.com/watch?v=vhACO_m5pH0', 71))
print(get_metadata_with_fc(fc))
from src.database.FirebaseAccessor import FirebaseAccessor

def get_num_metadata_item():
    f = FirebaseAccessor()
    ids = f.fetch_video_id_list()
    return len(ids)

print(get_num_metadata_item())
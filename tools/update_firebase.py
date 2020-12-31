from src.database.FirebaseAccessor import FirebaseAccessor
from src.data.FilterCondition import FilterCondition
from src.executor.FirebaseUpdater import FirebaseUpdater

def update_states_of_in_progress_metadata():
    f = FirebaseAccessor()
    fu = FirebaseUpdater()

    fc = FilterCondition( "state == 'in-progress'")

    all_videos = f.fetch_newest_videos(filter_cond=fc)
    print("Num videos to go: " + str(len(all_videos)))

    for video in all_videos:
        print(video)
        inp = input()

        if inp == "c":
            # clear state
            video.state = ''
            fu.run(video)
        elif inp == "f":
            # Finished
            video.state = 'processed'
            fu.run(video)


update_states_of_in_progress_metadata()


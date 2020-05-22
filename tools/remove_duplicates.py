#!/usr/bin/env python3

from database.FirebaseAccessor import FirebaseAccessor
import asyncio

def main():
    fb = FirebaseAccessor()
    #fb.initial_firebase()
    metadata_items = asyncio.run(fb.fetch_video_url_list())
    duplicates = set([ item 
        for item in metadata_items 
        if metadata_items.count(item) > 1])
    if(len(duplicates) == 0): 
        print("We found no duplicate elements in the Firebase store.")
        return
    print("We found the following duplicate elements in the Firebase store:")
    print(duplicates.join('\n'))
    answer = input("Do you want to delete them? (y/n)")
    if answer != 'y' or answer != 'yes':
        return
    print("Deleting...")
    for item in duplicates:
        try:
            asyncio.run(fb.delete_metadata(item))
        except NotExistingException as e:
            print(f"ERROR: Couldn't delete item {item} - ", e)

if __name__ == '__main__':
    main()

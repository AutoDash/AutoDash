#!/usr/bin/env python3

from database.FirebaseAccessor import FirebaseAccessor
import asyncio
from argparse import ArgumentParser

class CLIParser(ArgumentParser):
    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)
        self.add_argument("--strategy", choices=["latest"], default="latest")

def get_merger(strategy):
    if strategy == 'latest':
        return latest_merger
    raise ValueError(f"Unknown merge strategy: {strategy}")

def latest_merger(items):
    return items[-1]

def main(args):
    fb = FirebaseAccessor()
    metadata_list = asyncio.run(fb.fetch_all_metadata())
    duplicates = {}
    for (key, item) in metadata_list:
        if item['url'] in duplicates:
            duplicates[item['url']].append((key, item))
        else:
            duplicates[item['url']] = [(key, item)]
    duplicates = {
        key: item
        for (key, item) in duplicates.items()
        if len(item) > 2
    }
    if(len(duplicates) == 0): 
        print("We found no duplicate elements in the Firebase store.")
        return
    print("We found the following duplicate elements in the Firebase store:")
    print('\n'.join(duplicates.keys()))
    answer = input("Do you want to merge them? (y/n)")
    if answer != 'y' or answer != 'yes':
        return
    merge = get_merger(args['strategy'])
    for item in duplicates:
        to_delete = [ key for (key, item) in duplicates[item]]
        dupes = [item for (key, item) in duplicates[item]]
        merged = merge(dupes)
        for key in to_delete:
            fb.delete_metadata(key)
        fb.publish_new_metadata(MetaDataItem(**merged))

if __name__ == '__main__':
    arguments = CLIParser().parse_args()
    main({ **vars(arguments) })

import json
import os.path as path
from typing import List
import yaml

class ListCacheManager(object):
    FIELD_DELIMITER = "\n"
    SUB_FIELD_PREFIX = "  "
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.data = {}
        self.__file_name = path.join(path.dirname(path.abspath(__file__)), "store_" + self.name + ".cache")
        self.retrieve()


    def retrieve(self):
        if not path.isfile(self.__file_name):
            self.__store()
        with open(self.__file_name, "r") as file:
            self.data = yaml.load(file, Loader=yaml.FullLoader)
        return list(self.data.keys())

    def __store(self):
        with open(self.__file_name, "w") as file:
            file.write(yaml.dump(self.data))

    def insert(self, value):
        if value in self.data:
            return
        self.data[value] = None
        if len(self.data) > self.capacity:
            del self.data[list(self.data.keys())[0]]
        self.__store()

    def has_subfield(self, single_data: str, field: str) -> bool:
        return single_data in self.data and \
               self.data[single_data] is not None and \
               field in self.data[single_data]

    def contains_subfield(self, data: List[str], field: str) -> bool:
        for d in data:
            if self.has_subfield(d, field):
                return True
        return False

if __name__ == "__main__":
    m = ListCacheManager("test", capacity=3)
    for i in [1,2,3,2,3,4,3,4,5]:
        m.insert(i)
        print(m.retrieve(), m.sub_fields)


















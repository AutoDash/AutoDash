import json
import os.path as path
from typing import List

class ListCacheManager(object):
    FIELD_DELIMITER = "\n"
    SUB_FIELD_PREFIX = "  "
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.data = []
        self.sub_fields = {}
        self.__file_name = path.join(path.dirname(path.abspath(__file__)), "store_" + self.name + ".cache")
        self.retrieve()


    def retrieve(self):
        def parse(str_data):
            sub_fields = {}
            data = []
            for line in str_data.split(self.FIELD_DELIMITER):
                if line == "":
                    continue
                if not line.startswith(self.SUB_FIELD_PREFIX):
                    data.append(line)
                    sub_fields[line] = []
                else:
                    sub_field = line[len(self.SUB_FIELD_PREFIX):]
                    sub_fields[data[-1]].append(sub_field)
            return data, sub_fields

        if not path.isfile(self.__file_name):
            self.__store()

        with open(self.__file_name, "r") as file:
            str_data = file.read()

        self.data, self.sub_fields = parse(str_data)
        return self.data

    def __store(self):
        def encode():
            res = ""
            for d in self.data:
                res += d + "\n"
                for sf in self.sub_fields[d]:
                    res += self.SUB_FIELD_PREFIX + sf + self.FIELD_DELIMITER
            return res
        with open(self.__file_name, "w") as file:
            file.write(encode())

    def insert(self, value):
        if value in self.data:
            return
        self.data.append(value)
        self.sub_fields[value] = []
        if len(self.data) > self.capacity:
            self.data = self.data[-self.capacity:]
        self.__store()

    # def __remove_element(self, value):
    #     for i, v in enumerate(self.data):
    #         if v == value:
    #             del self.data[i]
    #             del self.sub_fields[value]
    #             return

    def has_subfield(self, single_data: str, field: str) -> bool:
        return single_data in self.sub_fields and field in self.sub_fields[single_data]

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


















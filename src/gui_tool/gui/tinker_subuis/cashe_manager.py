import json
import os.path as path

class ListCacheManager(object):
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.data = []
        self.__file_name = path.join(path.dirname(path.abspath(__file__)), "store_" + self.name + ".cache")
        self.retrieve()


    def retrieve(self):
        if not path.isfile(self.__file_name):
            self.__store()

        with open(self.__file_name, "r") as file:
            data = json.load(file)

        self.data = data
        return data

    def __store(self):
        with open(self.__file_name, "w") as file:
            json.dump(self.data, file)

    def insert(self, value):
        if value in self.data:
            self.__remove_element(value)
        self.data.append(value)
        if len(self.data) > self.capacity:
            self.data = self.data[-self.capacity:]
        self.__store()

    def __remove_element(self, value):
        for i, v in enumerate(self.data):
            if v == value:
                del self.data[i]
                return

if __name__ == "__main__":
    m = ListCacheManager("test", capacity=3)
    for i in [1,2,3,2,3,4,3,4,5]:
        m.insert(i)
        print(m.retrieve())

















